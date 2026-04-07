#!/usr/bin/env python
"""Create default users for STBank LeadGen Platform"""

import sys

sys.path.insert(0, "/app")

from src.config.database import SessionLocal
from src.models.user import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


db = SessionLocal()
try:
    # Create admin user
    admin = User(
        email="admin@stbank.la",
        username="admin",
        full_name="System Administrator",
        role="admin",
        branch_id=1,
        is_active=True,
    )
    admin.password_hash = get_password_hash("admin123")
    db.add(admin)

    # Create sales rep user
    sales = User(
        email="sales@stbank.la",
        username="sales",
        full_name="Sales Representative",
        role="sales_rep",
        branch_id=1,
        is_active=True,
    )
    sales.password_hash = get_password_hash("sales123")
    db.add(sales)

    # Create branch manager
    manager = User(
        email="manager@stbank.la",
        username="manager",
        full_name="Branch Manager",
        role="branch_manager",
        branch_id=1,
        is_active=True,
    )
    manager.password_hash = get_password_hash("manager123")
    db.add(manager)

    # Create compliance officer
    compliance = User(
        email="compliance@stbank.la",
        username="compliance",
        full_name="Compliance Officer",
        role="compliance",
        branch_id=1,
        is_active=True,
    )
    compliance.password_hash = get_password_hash("compliance123")
    db.add(compliance)

    db.commit()
    print("Default users created successfully!")
    print("")
    print("Login credentials:")
    print("  Admin: admin@stbank.la / admin123")
    print("  Sales Rep: sales@stbank.la / sales123")
    print("  Branch Manager: manager@stbank.la / manager123")
    print("  Compliance: compliance@stbank.la / compliance123")
except Exception as e:
    print(f"Error: {e}")
    db.rollback()
finally:
    db.close()
