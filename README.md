# Fiberku - Network Monitoring System

A comprehensive FastAPI backend for managing network infrastructure with spatial data capabilities using PostGIS. This system provides complete CRUD operations for network components including customers, packages, coverage areas, segments, operators, and fiber optic infrastructure with geospatial data support.

## 🌟 Features

### Core Framework
- **FastAPI** with automatic API documentation and OpenAPI/Swagger
- **SQLAlchemy** ORM with advanced database operations
- **PostgreSQL + PostGIS** for spatial data storage and geospatial queries
- **ULID Primary Keys** for globally unique, time-sortable identifiers
- **Pydantic** schemas for robust data validation

### Authentication & Security
- **JWT Authentication** with secure token-based access
- **Refresh Token Mechanism** with automatic token renewal (access: 30 min, refresh: 7 days)
- **Role-Based Access Control (RBAC)** with granular permissions
- **Password Hashing** using bcrypt for secure credential storage
- **CORS** middleware for cross-origin requests

### Data Management
- **Soft Delete** functionality for data retention (deleted records can be restored)
- **Audit Trail** with created_by, updated_by, deleted_by tracking
- **JSON Structured Logging** with comprehensive error tracking
- **Standardized API Response Format** for all endpoints

### Error Handling
All error responses follow a consistent structure:
```json
{
  "status": false,
  "code": "400",
  "message": "Error description",
  "data": null
}
```

## 🏗️ Project Architecture

```
arcgis-backend/
├── app/
│   ├── core/                    # Core configuration and database
│   │   ├── config.py           # Settings and environment variables
│   │   ├── database.py         # Database connection and session management
│   │   └── security.py         # Authentication utilities and password hashing
│   ├── models/                  # SQLAlchemy models
│   │   ├── user.py             # User and role models
│   │   ├── customer.py         # Customer model with location data
│   │   ├── package.py          # Service package models
│   │   ├── coverage.py         # Coverage area models (polygons)
│   │   ├── segment.py          # Network segment models
│   │   ├── operator.py         # Network operator models
│   │   ├── role.py             # Role model
│   │   └── fiber_optic.py      # Fiber optic infrastructure models
│   ├── schemas/                 # Pydantic schemas for API validation
│   ├── services/                # Business logic layer
│   ├── routers/                 # API endpoint definitions
│   ├── middleware/              # Custom middleware (auth, RBAC, logging)
│   ├── utils/                  # Utility functions
│   └── exceptions/             # Custom exception classes
├── logs/                       # Application logs (JSON format)
├── main.py                     # FastAPI application entry point
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker container configuration
├── docker-compose.yml          # Multi-service Docker setup
└── .env.example                # Environment variables template
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL with PostGIS extension
- Docker (optional)

### Local Development

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your database and configuration
   ```

3. **Database Setup (PostgreSQL + PostGIS):**
   ```sql
   -- Create database with PostGIS extension
   CREATE DATABASE argis;
   \c argis;
   CREATE EXTENSION IF NOT EXISTS postgis;
   CREATE EXTENSION IF NOT EXISTS postgis_topology;
   ```

4. **Run application:**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

5. **Access API:**
   - API: `http://localhost:8000`
   - Documentation: `http://localhost:8000/docs`
   - Alternative docs: `http://localhost:8000/redoc`

### Docker Deployment

1. **Build and run with Docker Compose:**
   ```bash
   docker-compose up --build
   ```

## 📡 API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/login` | User login (returns access_token + refresh_token) |
| POST | `/api/v1/auth/refresh` | Refresh access token using refresh token |
| POST | `/api/v1/auth/logout` | User logout |
| POST | `/api/v1/auth/check-permission` | Verify user permissions |

### User Management
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/users/` | List users |
| POST | `/api/v1/users/` | Create user |
| GET | `/api/v1/users/me` | Get current user profile |
| GET | `/api/v1/users/{user_id}` | Get user by ID |
| PUT | `/api/v1/users/{user_id}` | Update user |
| DELETE | `/api/v1/users/{user_id}` | Soft delete user |
| POST | `/api/v1/users/{user_id}/restore` | Restore soft-deleted user |

### Role Management
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/roles/` | List roles |
| POST | `/api/v1/roles/` | Create role |
| GET | `/api/v1/roles/{role_id}` | Get role by ID |
| PUT | `/api/v1/roles/{role_id}` | Update role |
| DELETE | `/api/v1/roles/{role_id}` | Delete role |

### Permission Management
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/permissions/` | List all permissions |
| GET | `/api/v1/permissions/modules` | List permission modules |

### Customer Management
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/customers/` | List customers |
| POST | `/api/v1/customers/` | Create customer |
| GET | `/api/v1/customers/{customer_id}` | Get customer by ID |
| PUT | `/api/v1/customers/{customer_id}` | Update customer |
| DELETE | `/api/v1/customers/{customer_id}` | Soft delete customer |
| POST | `/api/v1/customers/{customer_id}/restore` | Restore soft-deleted customer |

### Network Infrastructure
| Entity | Method | Endpoint | Description |
|--------|--------|----------|-------------|
| Packages | GET | `/api/v1/packages/` | List service packages |
| Packages | POST | `/api/v1/packages/` | Create package |
| Packages | GET | `/api/v1/packages/{package_id}` | Get package by ID |
| Packages | PUT | `/api/v1/packages/{package_id}` | Update package |
| Packages | DELETE | `/api/v1/packages/{package_id}` | Delete package |
| Coverages | GET | `/api/v1/coverages/` | List coverage areas |
| Coverages | POST | `/api/v1/coverages/` | Create coverage area |
| Coverages | GET | `/api/v1/coverages/{coverage_id}` | Get coverage by ID |
| Coverages | PUT | `/api/v1/coverages/{coverage_id}` | Update coverage |
| Coverages | DELETE | `/api/v1/coverages/{coverage_id}` | Delete coverage |
| Segments | GET | `/api/v1/segments/` | List network segments |
| Segments | POST | `/api/v1/segments/` | Create segment |
| Segments | GET | `/api/v1/segments/{segment_id}` | Get segment by ID |
| Segments | PUT | `/api/v1/segments/{segment_id}` | Update segment |
| Segments | DELETE | `/api/v1/segments/{segment_id}` | Soft delete segment |
| Segments | POST | `/api/v1/segments/{segment_id}/restore` | Restore soft-deleted segment |
| Operators | GET | `/api/v1/operators/` | List network operators |
| Operators | POST | `/api/v1/operators/` | Create operator |
| Operators | GET | `/api/v1/operators/{operator_id}` | Get operator by ID |
| Operators | PUT | `/api/v1/operators/{operator_id}` | Update operator |
| Operators | DELETE | `/api/v1/operators/{operator_id}` | Delete operator |
| Fiber Optics | GET | `/api/v1/fiber-optics/` | List fiber optic infrastructure |
| Fiber Optics | POST | `/api/v1/fiber-optics/` | Create fiber optic |
| Fiber Optics | GET | `/api/v1/fiber-optics/{fiber_id}` | Get fiber optic by ID |
| Fiber Optics | PUT | `/api/v1/fiber-optics/{fiber_id}` | Update fiber optic |
| Fiber Optics | DELETE | `/api/v1/fiber-optics/{fiber_id}` | Delete fiber optic |

### Geospatial Data (GeoJSON)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/geojson/customers` | Customer locations as GeoJSON |
| GET | `/api/v1/geojson/coverages` | Coverage areas as GeoJSON |
| GET | `/api/v1/geojson/fiber-optics` | Fiber optics as GeoJSON |

### System
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Welcome message |
| GET | `/health` | Health check |

## 📝 API Response Format

All endpoints return a consistent response format:

### Success Response
```json
{
  "status": true,
  "code": "10001",
  "message": "Operation successful",
  "data": { ... }
}
```

### Error Response
```json
{
  "status": false,
  "code": "400",
  "message": "Error description",
  "data": null
}
```

## 🔧 Configuration

### Environment Variables
```env
# Application
APP_NAME="ArcGIS Network Management"
APP_VERSION="1.0.0"
DEBUG=true
API_V1_STR="/api/v1"

# Database (PostgreSQL + PostGIS)
DATABASE_URL="postgresql://user:password@localhost:5432/arcgis"

# Authentication
SECRET_KEY="your-super-secret-jwt-key-here"
ACCESS_TOKEN_EXPIRE_MINUTES=60

# CORS
ALLOWED_ORIGINS=["http://localhost:3000", "https://yourdomain.com"]
```

## 📊 Logging & Monitoring

### Structured Logging
All events are logged in JSON format to `logs/app.log`:
```json
{
  "timestamp": "2026-05-17T07:58:10.621897",
  "level": "WARNING",
  "logger": "app",
  "message": "Request completed: status=401, duration=11.689186096191406ms",
  "module": "logging_system",
  "function": "warning",
  "line": 59,
  "correlation_id": "c987a954-fead-48a9-9d63-ba3d9d0b0c03",
  "event": "request_end",
  "status_code": 401,
  "duration": 11.689186096191406,
  "response_body": null,
  "response_headers": {
    "content-length": "113",
    "content-type": "application/json",
    "access-control-allow-origin": "http://localhost:5173",
    "access-control-allow-credentials": "true",
    "vary": "Origin"
  }
}
```

### Error Coverage
All events are logged in JSON format to `logs/error.log`:
- **HTTP exceptions (400, 401, 403, 404, etc.)**: FastAPI HTTPException handler
- **Validation errors (422)**: RequestValidationError handler
- **Database errors (400)**: SQLAlchemyError handler
- **AppException errors**: Custom application errors
- **Unhandled errors (500)**: Global exception handler

## 🔒 Security Features

### JWT Authentication
- **Bearer tokens** for API access
- **Token expiration** configurable
- **Secure password hashing** with bcrypt

### Role-Based Access Control (RBAC)
- **Granular permissions** for each endpoint
- **Role hierarchy**: super_admin, admin, manager, operator, viewer
- **Permission checking** middleware
- **Dynamic permission assignment**

## 📚 API Documentation

### Swagger/OpenAPI
- **Interactive docs** at `/docs`
- **ReDoc docs** at `/redoc`
- **Schema definitions** for all models
- **Example requests** for each endpoint