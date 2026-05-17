"""
Simple ULID Seeder
Uses existing SQLAlchemy models with ULID support
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import sessionmaker
from app.core.database import SessionLocal, engine
from app.core.security import get_password_hash
from app.models.user import User
from app.models.role import Role, Permission
from app.utils.ulid import generate_ulid
from app.utils.audit import set_audit_fields


def create_permissions(db):
    """Create basic permissions"""
    permissions_data = [
        # User management permissions
        {"name": "create_user", "resource": "users", "action": "create", "description": "Create new users"},
        {"name": "read_user", "resource": "users", "action": "read", "description": "Read user information"},
        {"name": "update_user", "resource": "users", "action": "update", "description": "Update user information"},
        {"name": "delete_user", "resource": "users", "action": "delete", "description": "Delete users"},
        
        # Role management permissions
        {"name": "create_role", "resource": "roles", "action": "create", "description": "Create new roles"},
        {"name": "read_role", "resource": "roles", "action": "read", "description": "Read role information"},
        {"name": "update_role", "resource": "roles", "action": "update", "description": "Update role information"},
        {"name": "delete_role", "resource": "roles", "action": "delete", "description": "Delete roles"},
        
        # Customer management permissions
        {"name": "create_customer", "resource": "customers", "action": "create", "description": "Create new customers"},
        {"name": "read_customer", "resource": "customers", "action": "read", "description": "Read customer information"},
        {"name": "update_customer", "resource": "customers", "action": "update", "description": "Update customer information"},
        {"name": "delete_customer", "resource": "customers", "action": "delete", "description": "Delete customers"},
        
        # Package management permissions
        {"name": "create_package", "resource": "packages", "action": "create", "description": "Create new packages"},
        {"name": "read_package", "resource": "packages", "action": "read", "description": "Read package information"},
        {"name": "update_package", "resource": "packages", "action": "update", "description": "Update package information"},
        {"name": "delete_package", "resource": "packages", "action": "delete", "description": "Delete packages"},
        
        # Coverage management permissions
        {"name": "create_coverage", "resource": "coverages", "action": "create", "description": "Create new coverage areas"},
        {"name": "read_coverage", "resource": "coverages", "action": "read", "description": "Read coverage information"},
        {"name": "update_coverage", "resource": "coverages", "action": "update", "description": "Update coverage information"},
        {"name": "delete_coverage", "resource": "coverages", "action": "delete", "description": "Delete coverage areas"},
        
        # Segment management permissions
        {"name": "create_segment", "resource": "segments", "action": "create", "description": "Create new segments"},
        {"name": "read_segment", "resource": "segments", "action": "read", "description": "Read segment information"},
        {"name": "update_segment", "resource": "segments", "action": "update", "description": "Update segment information"},
        {"name": "delete_segment", "resource": "segments", "action": "delete", "description": "Delete segments"},
        
        # Operator management permissions
        {"name": "create_operator", "resource": "operators", "action": "create", "description": "Create new operators"},
        {"name": "read_operator", "resource": "operators", "action": "read", "description": "Read operator information"},
        {"name": "update_operator", "resource": "operators", "action": "update", "description": "Update operator information"},
        {"name": "delete_operator", "resource": "operators", "action": "delete", "description": "Delete operators"},
        
        # Fiber optic management permissions
        {"name": "create_fiber_optic", "resource": "fiber_optics", "action": "create", "description": "Create new fiber optic infrastructure"},
        {"name": "read_fiber_optic", "resource": "fiber_optics", "action": "read", "description": "Read fiber optic information"},
        {"name": "update_fiber_optic", "resource": "fiber_optics", "action": "update", "description": "Update fiber optic information"},
        {"name": "delete_fiber_optic", "resource": "fiber_optics", "action": "delete", "description": "Delete fiber optic infrastructure"},
        
        # System admin permissions
        {"name": "system_admin", "resource": "system", "action": "admin", "description": "System administration"},
    ]
    
    created_permissions = []
    for perm_data in permissions_data:
        permission = db.query(Permission).filter(Permission.name == perm_data["name"], Permission.is_deleted == False).first()
        if not permission:
            permission = Permission(**perm_data)
            set_audit_fields(permission, created_by=None)  # System created, no user
            db.add(permission)
            created_permissions.append(permission)
    
    db.commit()
    print(f"Created {len(created_permissions)} permissions")
    return created_permissions


def create_roles(db):
    """Create basic roles"""
    roles_data = [
        {"name": "admin", "description": "Full access and configuration"},
        {"name": "operator", "description": "Create/update operational data"},
        {"name": "viewer", "description": "Read-only access"},
    ]
    
    created_roles = []
    for role_data in roles_data:
        role = db.query(Role).filter(Role.name == role_data["name"], Role.is_deleted == False).first()
        if not role:
            role = Role(**role_data)
            set_audit_fields(role, created_by=None)  # System created, no user
            db.add(role)
            created_roles.append(role)
    
    db.commit()
    print(f"Created {len(created_roles)} roles")
    return created_roles


def assign_permissions_to_roles(db):
    """Assign permissions to roles"""
    admin_role = db.query(Role).filter(Role.name == "admin", Role.is_deleted == False).first()
    operator_role = db.query(Role).filter(Role.name == "operator", Role.is_deleted == False).first()
    viewer_role = db.query(Role).filter(Role.name == "viewer", Role.is_deleted == False).first()
    
    # Get all permissions
    all_permissions = db.query(Permission).filter(Permission.is_deleted == False).all()
    
    # Admin gets all permissions
    if admin_role:
        admin_role.permissions = all_permissions
        print("Assigned all permissions to admin role")
    
    # Operator gets create, read, update permissions for operational data (customers, packages, coverages, segments, operators, fiber_optics)
    if operator_role:
        operator_permissions = [
            p for p in all_permissions 
            if p.action in ["create", "read", "update"] 
            and p.resource in ["customers", "packages", "coverages", "segments", "operators", "fiber_optics"]
        ]
        operator_role.permissions = operator_permissions
        print(f"Assigned {len(operator_permissions)} permissions to operator role")
    
    # Viewer gets only read permissions
    if viewer_role:
        viewer_permissions = [
            p for p in all_permissions if p.action == "read" and p.resource not in ["users", "roles", "permissions"]
        ]
        viewer_role.permissions = viewer_permissions
        print(f"Assigned {len(viewer_permissions)} permissions to viewer role")
    
    db.commit()


def create_sample_users(db):
    """Create sample users for each role"""
    admin_role = db.query(Role).filter(Role.name == "admin", Role.is_deleted == False).first()
    operator_role = db.query(Role).filter(Role.name == "operator", Role.is_deleted == False).first()
    viewer_role = db.query(Role).filter(Role.name == "viewer", Role.is_deleted == False).first()
    
    created_users = []
    
    # Create admin user
    admin_user = db.query(User).filter(User.username == "admin", User.is_deleted == False).first()
    if not admin_user:
        admin_password = "admin123"
        admin_user = User(
            id=generate_ulid(),
            email="admin@example.com",
            username="admin",
            full_name="System Administrator",
            hashed_password=get_password_hash(admin_password),
            is_active=True
        )
        set_audit_fields(admin_user, created_by=None)
        db.add(admin_user)
        created_users.append(admin_user)
        print("Created admin user")
    
    # Create operator user
    operator_user = db.query(User).filter(User.username == "operator", User.is_deleted == False).first()
    if not operator_user:
        operator_password = "operator123"
        operator_user = User(
            id=generate_ulid(),
            email="operator@example.com",
            username="operator",
            full_name="Network Operator",
            hashed_password=get_password_hash(operator_password),
            is_active=True
        )
        set_audit_fields(operator_user, created_by=None)
        db.add(operator_user)
        created_users.append(operator_user)
        print("Created operator user")
    
    # Create viewer user
    viewer_user = db.query(User).filter(User.username == "viewer", User.is_deleted == False).first()
    if not viewer_user:
        viewer_password = "viewer123"
        viewer_user = User(
            id=generate_ulid(),
            email="viewer@example.com",
            username="viewer",
            full_name="Network Viewer",
            hashed_password=get_password_hash(viewer_password),
            is_active=True
        )
        set_audit_fields(viewer_user, created_by=None)
        db.add(viewer_user)
        created_users.append(viewer_user)
        print("Created viewer user")
    
    db.commit()
    
    # Assign roles to users
    for user in created_users:
        db.refresh(user)
        if user.username == "admin" and admin_role:
            user.roles = [admin_role]
        elif user.username == "operator" and operator_role:
            user.roles = [operator_role]
        elif user.username == "viewer" and viewer_role:
            user.roles = [viewer_role]
        db.commit()
    
    return created_users


def main():
    """Simple ULID seeder function"""
    print("Starting simple ULID database seeding...")
    
    # Create all tables using SQLAlchemy models (which already have ULID support)
    from app.core.database import Base
    Base.metadata.create_all(bind=engine)
    print("Database tables created with ULID support")
    
    # Get database session
    db = SessionLocal()
    
    try:
        # Create permissions
        create_permissions(db)
        
        # Create roles
        create_roles(db)
        
        # Assign permissions to roles
        assign_permissions_to_roles(db)
        
        # Create sample users for each role
        create_sample_users(db)
        
        print("\nSimple ULID database seeding completed successfully!")
        print("\nUser credentials:")
        print("   Admin - Username: admin, Password: admin123, Email: admin@example.com")
        print("   Operator - Username: operator, Password: operator123, Email: operator@example.com")
        print("   Viewer - Username: viewer, Password: viewer123, Email: viewer@example.com")
        print("\nPlease change passwords after first login!")
        
    except Exception as e:
        print(f"Error during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
