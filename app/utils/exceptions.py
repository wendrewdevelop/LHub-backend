from uuid import UUID


class InsufficientStockError(Exception):
    def __init__(self, product_id: UUID):
        self.product_id = product_id
        super().__init__(f"Insufficient stock for product {product_id}")


class PaymentProcessingError(Exception):
    pass