# NovaCare Health - Epic EHR Mock API

## Demo Purpose
This is a mock healthcare API simulating **Epic EHR** integration for Zendesk FDE (Field Day Experience) demonstrations. It provides realistic patient identity verification, appointment viewing, and appointment rescheduling workflows to showcase Zendesk's Action Flows and Field Day capabilities.

**Live Demo API**: [https://novacare-demo.vercel.app](https://novacare-demo.vercel.app)  
**API Documentation**: [https://novacare-demo.vercel.app/docs](https://novacare-demo.vercel.app/docs)

---

## 🎯 Key Demo Features

### 1. **Patient Identity Verification**
Verify patient identity using Patient ID and Date of Birth before showing sensitive health information.

**Endpoint**: `POST /v1/verify-identity`

**Demo Flow**:
- Agent receives patient request in Zendesk
- Action Flow calls identity verification
- If verified, shows patient appointments
- If failed, displays error message

### 2. **View Patient Appointments**
Retrieve all upcoming appointments for a verified patient.

**Endpoint**: `GET /v1/patients/{patient_id}/appointments`

**Demo Scenario**: Show patient their upcoming appointments (Follow-up, Annual Check-up, etc.)

### 3. **Browse Available Slots**
Query available appointment slots with optional filters (date range, provider).

**Endpoint**: `GET /v1/appointments/available-slots`

**Demo Scenario**: Patient wants to reschedule - show available time slots

### 4. **Reschedule Appointment**
Move an existing appointment to a new available slot.

**Endpoint**: `PUT /v1/appointments/{appointment_id}`

**Demo Scenario**: 
- Patient selects new slot
- System validates availability
- Updates appointment and marks slot as booked

### 5. **Demo Reset**
Reset all data back to initial state for the next demo.

**Endpoint**: `POST /data/refresh`

**Use Case**: Between demo sessions, restore all appointments and slots to default

---

## 🔐 Authentication

All endpoints require Bearer token authentication:

```bash
Authorization: Bearer <your-token>
```

**Default Token** (development): `dev-token-replace-in-production`  
**Production Token**: Set via environment variable `MOCK_API_TOKEN`

---

## 📋 Demo Data

### Test Patients
- **PAT-001**: Jane Smith (DOB: 1985-03-15) - 3 appointments
- **PAT-002**: Robert Johnson (DOB: 1978-11-22) - 2 appointments  
- **PAT-003**: Maria Garcia (DOB: 1992-07-08) - 2 appointments

### Sample Workflow for Demo

**Step 1: Verify Identity**
```bash
POST /v1/verify-identity
{
  "patient_id": "PAT-001",
  "dob": "1985-03-15"
}
```

**Step 2: Get Appointments**
```bash
GET /v1/patients/PAT-001/appointments
```

**Step 3: View Available Slots**
```bash
GET /v1/appointments/available-slots?from_date=2026-06-25
```

**Step 4: Reschedule Appointment**
```bash
PUT /v1/appointments/APT-101
{
  "slot_id": "SLOT-003"
}
```

**Step 5: Reset for Next Demo**
```bash
POST /data/refresh
```

---

## 🏗️ Technical Architecture

### Project Structure
```
novacare_demo/
├── main.py              # FastAPI application entry point
├── config.py            # Configuration settings
├── requirements.txt     # Python dependencies
├── models/              # Pydantic data models
├── utils/               # Authentication & audit logging
├── routes/              # API endpoint handlers
│   ├── health.py        # Health checks
│   ├── identity.py      # Identity verification
│   ├── appointments.py  # Appointment management
│   └── admin.py         # Admin & testing endpoints
└── data/                # In-memory data management
```

### In-Memory Storage (Vercel-Compatible)
- **Default Data**: Source of truth stored in memory on startup
- **Working Copy**: Active data that can be modified during demos
- **Data Refresh**: Restores working copy from default (for demo resets)
- **No File I/O**: Optimized for Vercel's read-only serverless environment

### Data Persistence
- Changes persist in memory during the serverless function lifecycle
- Each cold start gets fresh default data
- Perfect for demos - each session can be independent

---

## 🚀 Running Locally

### Prerequisites
- Python 3.10+
- pip

### Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Create environment file (optional)
cp .env.example .env

# Start the server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Access
- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/healthz

---

## 🧪 Testing Endpoints

### Error Simulation (for Action Flow testing)
- `GET /v1/simulate/timeout` - Simulate slow response
- `GET /v1/simulate/503` - Simulate service unavailable
- `GET /v1/simulate/429` - Simulate rate limit

### Audit Logging
- `GET /v1/audit` - View all API access logs (HIPAA compliance demo)

---

## 📦 Deployment

### Vercel (Current)
Deployed via GitHub integration. Each push to `main` triggers automatic deployment.

**Configuration**: `vercel.json` or Vercel dashboard settings
- Set `MOCK_API_TOKEN` environment variable in Vercel dashboard

### Docker (Alternative)
```bash
docker build -t novacare-api .
docker run -p 8000:8000 -e MOCK_API_TOKEN=your-token novacare-api
```

---

## 🎬 Demo Tips

1. **Start Fresh**: Call `/data/refresh` before each demo
2. **Check Health**: Use `/healthz` to verify data is loaded
3. **Show Errors**: Use wrong DOB to demonstrate identity verification failure
4. **Demonstrate Booking**: Book multiple slots to show availability updates
5. **Show Audit**: Display `/v1/audit` logs for compliance discussion

---

## 📝 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MOCK_API_TOKEN` | Bearer token for API authentication | `dev-token-replace-in-production` |

---

## 🔗 Integration with Zendesk

This API is designed to be called from:
- **Zendesk Action Flows**: For automated workflows
- **Field Day Editor**: For custom app experiences
- **Zendesk Apps**: Via HTTP requests

**CORS**: Configured to allow `*.zendesk.com` origins

---

## 📄 License

This is a demo/mock API for educational and demonstration purposes.
