from fastapi import APIRouter

from app.api.v1.endpoints import (
    admin,
    auth,
    cart,
    categories,
    health,
    monitoring,
    orders,
    products,
    users,
)

api_router = APIRouter()

# Public/System Routes
api_router.include_router(health.router)
api_router.include_router(auth.router)

# User Routes
api_router.include_router(users.router)

# E-Commerce Routes
api_router.include_router(categories.router)
api_router.include_router(products.router)
api_router.include_router(cart.router)
api_router.include_router(orders.router)

# Admin Routes
api_router.include_router(admin.router)

# Monitoring Routes
api_router.include_router(monitoring.router)