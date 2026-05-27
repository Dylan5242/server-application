from database import SessionLocal
from models import Product


products = [
    Product(
        title="Notebook",
        price=1200.00,
        count=5,
        description="Portable computer for work and study",
    ),
    Product(
        title="Keyboard",
        price=85.50,
        count=20,
        description="Mechanical keyboard with USB connection",
    ),
]


def seed_products():
    db = SessionLocal()
    try:
        if db.query(Product).count() == 0:
            db.add_all(products)
            db.commit()
            print("Two products were added")
        else:
            print("Products table already contains records")
    finally:
        db.close()


if __name__ == "__main__":
    seed_products()
