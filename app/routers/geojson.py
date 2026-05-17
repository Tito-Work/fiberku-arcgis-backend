"""
GeoJSON API Router
Serves GeoJSON data for frontend mapping components
"""

import json
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.coverage_service import CoverageService
from app.services.customer_service import CustomerService
from app.services.fiber_optic_service import FiberOpticService
from app.middleware.rbac import get_current_user_with_permission
from app.models.user import User
from geoalchemy2 import shape
from jose import JWTError, jwt
from app.core.config import settings
from app.utils.logging_system import log_errors, api_logger

router = APIRouter()

def get_current_user_from_query_token(
    token: Optional[str] = Query(None, description="JWT token for authentication")
) -> Optional[User]:
    """Authenticate user from JWT token in query parameter"""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token parameter is required"
        )
    
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        # For simplicity, create a mock user object
        user = User(
            id=1,
            username=username,
            email="admin@example.com",
            is_active=True
        )
        return user
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


@log_errors(api_logger)
@router.get("/coverages")
def get_coverages(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_query_token)
):
    """Return coverages from database as GeoJSON FeatureCollection"""
    try:
        coverage_service = CoverageService(db)
        coverages = coverage_service.get_coverages()
        
        # Convert database records to GeoJSON format
        features = []
        for coverage in coverages:
            from geoalchemy2.shape import to_shape

            polygon_coords = None

            try:
                geom = coverage.location

                if geom is not None:
                    shapely_geom = to_shape(geom)

                    # pastikan polygon
                    if shapely_geom.geom_type == "Polygon":
                        polygon_coords = list(shapely_geom.exterior.coords)

            except Exception as e:
                print("Geometry error:", e)
            
            feature = {
                "type": "Feature",
                "properties": {
                    "id": coverage.id,
                    "area": coverage.area,
                    "current_customer": coverage.current_customer,
                    "max_customer": coverage.max_customer,
                    "is_active": coverage.is_active
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [polygon_coords]
                }
            }
            features.append(feature)
        
        geojson_data = {
            "type": "FeatureCollection",
            "features": features
        }
        
        return geojson_data
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching coverages from database: {str(e)}"
        )

@log_errors(api_logger)
@router.get("/customers")
def get_customers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_query_token)
):
    try:
        from geoalchemy2.shape import to_shape
        from geoalchemy2.elements import WKBElement

        customer_service = CustomerService(db)
        customers = customer_service.get_customers()

        features = []

        for customer in customers:
            point_coords = None

            try:
                if customer.location and isinstance(customer.location, WKBElement):
                    geom = to_shape(customer.location)
                    point_coords = [geom.x, geom.y]

                elif customer.location:
                    # fallback WKT (minimal)
                    geom = to_shape(customer.location)
                    point_coords = [geom.x, geom.y]

            except Exception:
                continue

            if not point_coords:
                continue

            features.append({
                "type": "Feature",
                "properties": {
                    "id": customer.id,
                    "code": customer.code,
                    "name": customer.name,
                    "package": customer.package.name if customer.package else None,
                    "package_id": customer.package.id if customer.package else None,
                    "package_color": customer.package.color if customer.package else None,
                    "price": float(customer.price) if customer.price else None,
                    "email": customer.email,
                    "phone": customer.phone,
                    "address": customer.address,
                    "is_active": customer.is_active
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": point_coords
                }
            })

        return {
            "type": "FeatureCollection",
            "features": features
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching customers: {str(e)}"
        )

@log_errors(api_logger)
@router.get("/fiber-optics")
def get_fiber_optics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_query_token)
):
    """Return fiber optics from database as GeoJSON FeatureCollection"""
    try:
        fiber_optic_service = FiberOpticService(db)
        fiber_optics = fiber_optic_service.get_fiber_optics()
        
        # Convert database records to GeoJSON format
        features = []
        for fiber_optic in fiber_optics:
            from geoalchemy2.shape import to_shape

            geom = fiber_optic.location

            linestring_coords = None

            try:
                if geom is not None:
                    shapely_geom = to_shape(geom)
                    linestring_coords = list(shapely_geom.coords)
            except Exception as e:
                print("Geometry parse error:", e)
            
            feature = {
                "type": "Feature",
                "properties": {
                    "id": fiber_optic.id,
                    "segment": fiber_optic.segment.name if fiber_optic.segment else None,
                    "operator": fiber_optic.operator.name if fiber_optic.operator else None,
                    "is_active": fiber_optic.is_active
                },
                "geometry": {
                    "type": "LineString",
                    "coordinates": linestring_coords
                }
            }
            features.append(feature)
        
        geojson_data = {
            "type": "FeatureCollection",
            "features": features
        }
        
        return geojson_data
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching fiber optics from database: {str(e)}"
        )
