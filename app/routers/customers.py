from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.customer import Customer as CustomerSchema, CustomerCreate, CustomerUpdate
from app.services.customer_service import CustomerService
from app.middleware.rbac import get_current_user_with_permission
from app.models.user import User
from app.utils.ulid import validate_ulid
from app.schemas.base_response import BaseResponse
from app.exceptions.http_exception import AppException
from app.utils.logging_system import log_errors, api_logger

router = APIRouter()


@log_errors(api_logger)
@router.post("", response_model=BaseResponse[CustomerSchema], status_code=status.HTTP_201_CREATED)
def create_customer(
    customer: CustomerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_permission("create_customer"))
):
    customer_service = CustomerService(db)
    
    # Check if customer code already exists
    if customer.code and customer_service.get_customer_by_code(customer.code):
        raise AppException(
            status_code=400,
            code="400",
            message="Customer code already exists"
        )
    
    # Check if customer email already exists
    if customer.email and customer_service.get_customer_by_email(customer.email):
        raise AppException(
            status_code=400,
            code="400",
            message="Email already registered"
        )
    
    # return customer_service.create_customer(customer, created_by=current_user.id)
    created_customer = customer_service.create_customer(
        customer,
        created_by=current_user.id
    )

    return {
        "status": True,
        "code": "10001",
        "message": "Customer created successfully",
        "data": created_customer
    }


@log_errors(api_logger)
@router.get("", response_model=BaseResponse[List[CustomerSchema]])
def read_customers(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_permission("read_customer"))
):
    customer_service = CustomerService(db)
    customers = customer_service.get_customers(skip=skip, limit=limit)
    return {
        "status": True,
        "code": "10002",
        "message": "Customers fetched successfully",
        "data": customers
    }


@log_errors(api_logger)
@router.get("/{customer_id}", response_model=BaseResponse[CustomerSchema])
def read_customer(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_permission("read_customer")),
    customer_id: str = Path(..., description="ULID of the customer", pattern=r'^[0-9a-hjkmnp-tv-z]{26}$')
):
    if not validate_ulid(customer_id):
        raise AppException(
            status_code=400,
            code="400",
            message="Invalid ULID format"
        )
    
    customer_service = CustomerService(db)
    db_customer = customer_service.get_customer(customer_id)
    if db_customer is None:
        raise AppException(
            status_code=404,
            code="404",
            message="Customer not found"
        )
    return {
        "status": True,
        "code": "10003",
        "message": "Customer fetched successfully",
        "data": db_customer
    }


@log_errors(api_logger)
@router.put("/{customer_id}", response_model=BaseResponse[CustomerSchema])
def update_customer(
    customer: CustomerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_permission("update_customer")),
    customer_id: str = Path(..., description="ULID of the customer", pattern=r'^[0-9a-hjkmnp-tv-z]{26}$')
):
    if not validate_ulid(customer_id):
        raise AppException(
            status_code=400,
            code="400",
            message="Invalid ULID format"
        )
    
    customer_service = CustomerService(db)
    db_customer = customer_service.update_customer(customer_id, customer, updated_by=current_user.id)
    if db_customer is None:
        raise AppException(
            status_code=404,
            code="404",
            message="Customer not found"
        )
    return {
        "status": True,
        "code": "10002",
        "message": "Customer updated successfully",
        "data": db_customer
    }

@log_errors(api_logger)
@router.delete("/{customer_id}", response_model=BaseResponse[dict])
def delete_customer(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_permission("delete_customer")),
    customer_id: str = Path(..., description="ULID of the customer", pattern=r'^[0-9a-hjkmnp-tv-z]{26}$')
):
    if not validate_ulid(customer_id):
        raise AppException(
            status_code=400,
            code="400",
            message="Invalid ULID format"
        )
    
    customer_service = CustomerService(db)
    if not customer_service.delete_customer(customer_id, deleted_by=current_user.id):
        raise AppException(
            status_code=404,
            code="404",
            message="Customer not found"
        )
    return {
        "status": True,
        "code": "10003",
        "message": "Customer deleted successfully",
        "data": None
    }


@log_errors(api_logger)
@router.post("/{customer_id}/restore", response_model=BaseResponse[dict])
def restore_customer(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_permission("delete_customer")),
    customer_id: str = Path(..., description="ULID of the customer", pattern=r'^[0-9a-hjkmnp-tv-z]{26}$')
):
    if not validate_ulid(customer_id):
        raise AppException(
            status_code=400,
            code="400",
            message="Invalid ULID format"
        )
    
    customer_service = CustomerService(db)
    if not customer_service.restore_customer(customer_id):
        raise AppException(
            status_code=404,
            code="404",
            message="Customer not found or not deleted"
        )
    return {
        "status": True,
        "code": "10004",
        "message": "Customer restored successfully",
        "data": None
    }


@log_errors(api_logger)
@router.get("by-package/{package_id}", response_model=BaseResponse[List[CustomerSchema]])
def get_customers_by_package(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_permission("read_customer")),
    package_id: str = Path(..., description="ULID of the package", pattern=r'^[0-9a-hjkmnp-tv-z]{26}$')
):
    if not validate_ulid(package_id):
        raise AppException(
            status_code=400,
            code="400",
            message="Invalid ULID format"
        )
    
    customer_service = CustomerService(db)
    customers = customer_service.get_customers_by_package(package_id)
    return {
        "status": True,
        "code": "10005",
        "message": "Customers by package fetched successfully",
        "data": customers
    }


@log_errors(api_logger)
@router.get("by-city/{city}", response_model=BaseResponse[List[CustomerSchema]])
def get_customers_by_city(
    city: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_permission("read_customer"))
):
    customer_service = CustomerService(db)
    customers = customer_service.get_customers_by_city(city)
    return {
        "status": True,
        "code": "10006",
        "message": "Customers by city fetched successfully",
        "data": customers
    }
