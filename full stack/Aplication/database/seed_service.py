from __future__ import annotations
from decimal import Decimal

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.roles import Role
from app.core.security import get_password_hash
from app.db.seed_data import (
DEFAULT_ADMIN,
DEFAULT_CATEGORIES,
DEFAULT_PRODUCTS,
)
from app.models.category import Category
from app.models.product import Product
from app.models.user import User

class SeedService:


    def __init__(
        self,
        db: Session,
    ) -> None:

        self.db = db

    def create_admin(
        self,
        *,
        email: str,
        password: str,
        full_name: str,
    ) -> tuple[User, bool]:

        existing = (
            self.db.query(User)
            .filter(User.email == email)
            .first()
        )

        if existing:
            return existing, False

        user = User(
            email=email,
            hashed_password=get_password_hash(password),
            full_name=full_name,
            role=Role.ADMIN,
            is_active=True,
            is_superuser=True,
        )

        self.db.add(user)

        self.db.commit()

        self.db.refresh(user)

        return user, True

    def seed_categories(
        self,
    ) -> list[Category]:

        created_or_existing: list[Category] = []

        for item in DEFAULT_CATEGORIES:

            existing = (
                self.db.query(Category)
                .filter(
                    Category.name == item["name"]
                )
                .first()
            )

            if existing:
                created_or_existing.append(
                    existing
                )
                continue

            category = Category(
                name=item["name"],
                description=item["description"],
            )

            self.db.add(category)

            self.db.flush()

            created_or_existing.append(
                category
            )

        self.db.commit()

        for category in created_or_existing:

            self.db.refresh(category)

        return created_or_existing

    def seed_products(
        self,
    ) -> list[Product]:

        categories = {
            category.name: category
            for category in (
                self.db.query(Category).all()
            )
        }

        created_or_existing: list[Product] = []

        for item in DEFAULT_PRODUCTS:

            existing = (
                self.db.query(Product)
                .filter(
                    Product.sku == item["sku"]
                )
                .first()
            )

            if existing:
                created_or_existing.append(
                    existing
                )
                continue

            category = categories[
                item["category_name"]
            ]

            product = Product(
                name=item["name"],
                description=item["description"],
                sku=item["sku"],
                price=Decimal(item["price"]),
                stock=item["stock"],
                is_active=item["is_active"],
                category_id=category.id,
            )

            self.db.add(product)

            self.db.flush()

            created_or_existing.append(
                product
            )

        self.db.commit()

        for product in created_or_existing:

            self.db.refresh(product)

        return created_or_existing

    def seed_all(
        self,
    ) -> dict:

        categories = self.seed_categories()

        products = self.seed_products()

        return {
            
            "categories_count": len(categories),
            "products_count": len(products),
        }

    def reset_public_schema(
        self,
    ) -> None:

        self.db.execute(
            text(
                "DROP SCHEMA public CASCADE"
            )
        )

        self.db.execute(
            text(
                "CREATE SCHEMA public"
            )
        )

        self.db.commit()
