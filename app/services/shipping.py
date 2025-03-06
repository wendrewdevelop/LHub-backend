# services/shipping.py
import httpx
from uuid import UUID
from typing import List
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
from geopy.adapters import AioHTTPAdapter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.config import Settings
from app.schemas import (
    ShippingCalculateRequest, 
    ShippingOptionResponse,
    LocalDeliveryResponse
)
from app.models import StoreModel, ShippingRuleModel


class LocalDeliveryCalculator:
    def __init__(self, base_fee: float = 9.90):
        self.base_fee = base_fee
        self.km_rate = 2.50  # Taxa por km adicional

    async def calculate(
        self,
        store: StoreModel,
        destination_cep: str
    ) -> LocalDeliveryResponse:
        # Verificar se é mesma cidade
        if not await self._is_same_city(store.cep, destination_cep):
            return LocalDeliveryResponse(
                is_local=False,
                delivery_fee=0,
                estimated_time=""
            )

        # Calcular distância
        distance = await self._calculate_distance(
            destination_cep,
            store.cep
        )
        print(f'DESTINATION CEP::: {destination_cep}')
        print(f'STORE CEP::: {store.cep}')
        print(f'STORE FIXED TAX::: {store.delivery_fee}')
        print(f'DISTANCE::: {distance}')

        # Calcular taxa
        fee = store.delivery_fee or self.base_fee
        if distance > 5:  # Taxa adicional após 5km
            fee += (distance - 5) * self.km_rate

        return LocalDeliveryResponse(
            is_local=True,
            delivery_fee=round(fee, 2),
            estimated_time=self._estimate_time(distance),
            distance_km=round(distance, 2)
        )

    async def _is_same_city(self, cep1: str, cep2: str) -> bool:
        """Consulta API de CEP para verificar cidade"""
        async with httpx.AsyncClient() as client:
            res1 = await client.get(f"https://viacep.com.br/ws/{cep1}/json/")
            res2 = await client.get(f"https://viacep.com.br/ws/{cep2}/json/")
            
            data1 = res1.json()
            data2 = res2.json()
            
            return data1.get("localidade") == data2.get("localidade")

    async def _calculate_distance(self, destination_cep: str, origin_cep: str) -> float:
        """Calcula a distância em km entre a origem e o destino"""
        try:
            origin_coords = await self._get_coordinates(origin_cep)     
            dest_coords = await self._get_coordinates(destination_cep)

            return geodesic(origin_coords, dest_coords).km
        except ValueError as e:
            print(f"Erro ao calcular distância: {str(e)}")
            return 0.0  # Retorno seguro para erros

    async def _get_coordinates(self, cep: str) -> tuple:
        """Obtém lat/long do CEP usando geocodificação"""
        try:
            # Primeiro obtemos o endereço completo
            async with httpx.AsyncClient() as client:
                viacep_response = await client.get(
                    f"https://viacep.com.br/ws/{cep}/json/"
                )
                viacep_response.raise_for_status()
                address_data = viacep_response.json()

                if "erro" in address_data:
                    raise ValueError("CEP não encontrado")

            # Monta o endereço para geocodificação
            address = (
                f"{address_data.get('logradouro', '')}, "
                f"{address_data.get('bairro', '')}, "
                f"{address_data.get('localidade', '')}, "
                f"{address_data.get('uf', '')}"
            )

            # Usa Nominatim para obter coordenadas
            async with Nominatim(
                user_agent="luhub-app",  # Substitua com seu user-agent
                adapter_factory=AioHTTPAdapter
            ) as geolocator:
                location = await geolocator.geocode(address)
                
                if not location:
                    raise ValueError("Endereço não encontrado")
                    
                return (location.latitude, location.longitude)

        except httpx.HTTPError as e:
            raise ValueError(f"Erro na API: {str(e)}")
        except KeyError as e:
            raise ValueError(f"Dados de resposta inválidos: {str(e)}")

    def _estimate_time(self, distance: float) -> str:
        """Estima tempo de entrega com base na distância"""
        if distance <= 2:
            return "15-30 minutos"
        elif distance <= 5:
            return "30-45 minutos"
        else:
            return f"{int(distance * 10)}-{int(distance * 12)} minutos"


class ShippingCalculator:
    def __init__(self):
        self.correios_url = "https://api.correios.com.br/preco/v1"
        self.cache = {}  # Implementar Redis em produção

    async def _get_store(self, store_id: UUID, session) -> StoreModel:
        result = await session.execute(
            select(StoreModel)
            .where(StoreModel.id == store_id)
        )
        store = result.scalar_one_or_none()
        
        if not store:
            raise "Loja não encontrada"
        
        return store

    async def calculate(
        self, 
        request: ShippingCalculateRequest,
        session
    ) -> List[ShippingOptionResponse]:
        options = []
        
        # 1. Calcular frete dos Correios
        correios_options = await self._calculate_correios(request)
        options.extend(correios_options)
        
        # 2. Calcular regras customizadas
        custom_options = await self._calculate_custom(request)
        options.extend(custom_options)

        local_service = await LocalDeliveryCalculator().calculate(
            store=await self._get_store(request.store_id, session),
            destination_cep=request.destination_cep
        )
        
        if local_service.is_local:
            return [local_service]
        
        return sorted(options, key=lambda x: x.cost)

    async def _calculate_correios(
        self, 
        request: ShippingCalculateRequest
    ) -> List[ShippingOptionResponse]:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.correios_url}/calcular",
                    json={
                        "cepOrigem": request.origin_cep,
                        "cepDestino": request.destination_cep,
                        "peso": request.weight,
                        "dimensoes": {
                            "comprimento": request.length,
                            "altura": request.height,
                            "largura": request.width
                        },
                        "servicos": ["04014"]
                    },
                    headers={
                        "Authorization": f"Bearer {Settings.CORREIOS_API_KEY}"
                    }
                )
                response.raise_for_status()
                
                return [
                    ShippingOptionResponse(
                        carrier="Correios",
                        service=item["nome"],
                        cost=float(item["valor"]),
                        delivery_time=item["prazo"],
                        description=item["descricao"]
                    )
                    for item in response.json()["servicos"]
                ]
                
        except Exception as e:
            # Logar erro e retornar lista vazia
            return []

    async def _calculate_custom(
        self, 
        request: ShippingCalculateRequest
    ) -> List[ShippingOptionResponse]:
        # Consultar regras ativas do banco de dados
        rules = await self._get_active_rules()
        
        options = []
        for rule in rules:
            if self._validate_rule(rule, request):
                cost = eval(rule.formula, {
                    "peso": request.weight,
                    "volume": request.length * request.height * request.width
                })
                options.append(ShippingOptionResponse(
                    carrier="Custom",
                    service=rule.name,
                    cost=round(cost, 2),
                    delivery_time=3,  # Exemplo fixo
                    description=f"Regra: {rule.formula}"
                ))
        
        return options

    async def _get_active_rules(self):
        # Implementar consulta ao banco de dados
        return [
            ShippingRuleModel(
                name="Frete Fixo SP",
                formula="50",
                max_weight=10,
                min_dimension=0,
                max_dimension=100
            )
        ]
    
    def _cep_matches_ranges(self, cep: str, ranges: list):
        if not ranges:
            return True
            
        cep_num = int(cep[:5])  # Primeiros 5 dígitos
        for range_str in ranges:
            if '-' in range_str:
                start, end = map(int, range_str.replace('-', '').split(' a '))
                if start <= cep_num <= end:
                    return True
            elif '*' in range_str:  # Ex: "SP*"
                state = cep[:2]
                return range_str.startswith(state)
        return False

    def _validate_rule(self, rule, request):
        origin_valid = self._cep_matches_ranges(
            request.origin_cep, 
            rule.origin_cep_ranges
        )
        return origin_valid and (
            request.weight <= rule.max_weight and
            min([request.length, request.height, request.width]) >= rule.min_dimension and
            max([request.length, request.height, request.width]) <= rule.max_dimension
        )