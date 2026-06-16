# NovaCare Health API - Project Structure

## Overview
This project is structured following best practices with separation of concerns and modular organization.

## Directory Structure

```
novacare_demo/
├── main.py                 # Application entry point with FastAPI setup
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variable template
├── models/               # Data models (Pydantic schemas)
│   ├── __init__.py
│   └── schemas.py
├── utils/                # Utility modules
│   ├── __init__.py
│   ├── auth.py          # Authentication logic
│   └── audit.py         # Audit logging
├── routes/               # API route handlers
│   ├── __init__.py
│   ├── health.py        # Health check endpoints
│   ├── identity.py      # Identity verification
│   ├── appointments.py  # Appointment management
│   └── admin.py         # Admin & testing endpoints
└── data/                 # Data management
    ├── __init__.py
    ├── data_manager.py   # Excel data operations
    └── novacare_data.xlsx  # Excel with 'default' & 'working' sheets

```

## Key Features

### 1. Excel-Based Data Storage
- **Default Sheet**: Contains original seed data (never modified)
- **Working Sheet**: Demo data that can be modified during demos
- **Data Refresh**: `/data/refresh` endpoint resets working data from default

### 2. Data Flow
1. **Startup**: Application loads data from 'working' sheet into memory
2. **Runtime**: All operations work with in-memory data
3. **Modifications**: Changes are automatically saved back to 'working' sheet
4. **Reset**: Call `/data/refresh` to restore working data from default

### 3. API Endpoints

#### Health & Status
- `GET /` - Service information
- `GET /healthz` - Health check with statistics

#### Identity & Appointments
- `POST /v1/verify-identity` - Verify patient identity
- `GET /v1/patients/{patient_id}/appointments` - Get patient appointments
- `GET /v1/appointments/available-slots` - Get available appointment slots
- `PUT /v1/appointments/{appointment_id}` - Reschedule appointment

#### Admin & Demo Management
- `GET /v1/audit` - View audit logs
- `POST /v1/admin/reset` - Reload data from working sheet
- `POST /data/refresh` - Reset working data from default (demo reset)

#### Testing
- `GET /v1/simulate/timeout` - Simulate timeout
- `GET /v1/simulate/503` - Simulate service unavailable
- `GET /v1/simulate/429` - Simulate rate limit

## Environment Variables

Create a `.env` file from `.env.example`:
```bash
cp .env.example .env
```

Required variables:
- `MOCK_API_TOKEN`: Bearer token for API authentication

## Running the Application

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the server:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

3. Access API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Demo Workflow

1. **Initial State**: Server starts and loads working data
2. **During Demo**: Make API calls that modify data (e.g., reschedule appointments)
3. **Reset for Next Demo**: Call `POST /data/refresh` to restore default state
4. **Verify Reset**: Check `/healthz` to see current data statistics

## Development

### Adding New Endpoints
1. Create route handler in appropriate file under `routes/`
2. Register router in `main.py`

### Modifying Data Schema
1. Update Pydantic models in `models/schemas.py`
2. Update default data in `data/data_manager.py`
3. Delete existing Excel file to regenerate with new schema

### Testing Authentication
All protected endpoints require Bearer token:
```bash
curl -H "Authorization: Bearer dev-token-replace-in-production" http://localhost:8000/v1/audit
```
