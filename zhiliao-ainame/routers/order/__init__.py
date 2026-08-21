from .company import router as company_router
from .product import router as product_router
from .order import router as order_router

__all__ = [
    "company_router",
    "product_router",
    "order_router"
]