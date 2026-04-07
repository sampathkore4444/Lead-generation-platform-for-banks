"""
Database Migration Script
Run migrations to create/update database tables
"""

from ..config.database import Base, engine
from ..models.user import User, Branch
from ..models.lead import Lead, LeadAuditLog, DuplicateLog


def create_tables():
    """Create all database tables"""
    print("Creating database tables...")

    # Create all tables
    Base.metadata.create_all(bind=engine)

    print("Database tables created successfully!")

    # Create default branches
    from ..config.database import SessionLocal

    db = SessionLocal()
    try:
        # Check if branches exist
        existing = db.query(Branch).first()
        if not existing:
            # Create default branches
            branches = [
                Branch(
                    name="Vientiane Main",
                    code="VT001",
                    address="Ban Anou, Vientiane",
                    phone="021123456",
                ),
                Branch(
                    name="Vientiane East",
                    code="VT002",
                    address="Sokpalin, Vientiane",
                    phone="021234567",
                ),
                Branch(
                    name="Luang Prab",
                    code="LP001",
                    address="Kinnarasa, Luang Prab",
                    phone="071212345",
                ),
                Branch(
                    name="Pakse", code="PK001", address="Muang Pakse", phone="031212345"
                ),
                Branch(
                    name="Savannakhet",
                    code="SK001",
                    address="Muang Savannakhet",
                    phone="041212345",
                ),
            ]
            db.add_all(branches)
            db.commit()
            print("Default branches created!")
        else:
            print("Branches already exist, skipping...")
    except Exception as e:
        print(f"Error creating default data: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    create_tables()
