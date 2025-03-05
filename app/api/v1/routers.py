from fastapi import APIRouter
from .endpoints import (
    account_router, 
    auth_router,
    store_router,
    product_router
)


router = APIRouter()
router.include_router(account_router)
router.include_router(auth_router)
router.include_router(store_router)
router.include_router(product_router)