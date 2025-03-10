### How to use Alembic

- <b>Inicializar o Alembic no projeto: </b><code>alembic init migrations</code>
    1. <b>Inicializar o Alembic no projeto: </b><code>sqlalchemy.url = driver://user:password@localhost/dbname</code>
- <b>Atualizar env.py (migrations/env.py):</b>
```python
    import os 
    import sys 
    from logging.config import fileConfig 
    from sqlalchemy import engine_from_config 
    from sqlalchemy import pool 
    from app.core import Base 

    sys.path.append(os.path.dirname(os.path.dirname(__file__))) 
    target_metadata = Base.metadata 
```
- <b>Alterações pendentes: </b><code>alembic current</code>
- <b>Gerar migração: </b><code>alembic revision --autogenerate -m "Adiciona coluna cep"</code>
- <b>Aplicar migração: </b><code>alembic upgrade head</code>

### How to use UV

- Init project:
```bash
    $ uv init example
    Initialized project `example` at `/home/user/example`
```
```bash
    $ uv add _library_name_
```
```bash
    $ uv lock && uv sync;
```
- If installed via the standalone installer, uv can update itself to the latest version:
```bash
    $ uv self update
```

```bash
    $ uv run example.py
    Reading inline script metadata from: example.py
    Installed 5 packages in 12ms
    <Response [200]>

    # in our case we use:
    $ uv run uvicorn app.main:app --reload
```

### TO DO

- [ ] Implement Webhook for Asynchronous Updates;
    - [ ] Configurar Webhook no Dashboard do Stripe;
        1. Acesse Stripe Dashboard > Developers > Webhooks
        2. Adicione endpoint: https://sua-api.com/gateways/stripe/webhook
        3. Selecione eventos:
            - payment_intent.succeeded
            - payment_intent.payment_failed
- [ ] Improve Specific Error Handling;
- [ ] Add Data Validation in Schema;
- [ ] Complete Tests with Test Cards;
