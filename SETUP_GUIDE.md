# NovaCare Health - API Configuration

## Overview
This application demonstrates how to properly handle API authentication with environment variables in a FastAPI + Static HTML setup.

## How It Works

### Backend (FastAPI)
1. **Environment Variable**: The API token is stored in the `MOCK_API_TOKEN` environment variable
2. **Config Endpoint**: `/api/config` endpoint exposes the token to the frontend
3. **Static Files**: HTML/CSS/JS files are served via FastAPI's StaticFiles mount

### Frontend (HTML/JavaScript)
1. **Load Config**: On page load, fetches `/api/config` to get the API token
2. **Store Token**: Saves the token in memory for subsequent API calls
3. **Authenticated Calls**: Uses the token in `Authorization: Bearer <token>` header

## Setup

### Environment Variable

#### Local Development (PowerShell)
```powershell
$env:MOCK_API_TOKEN="dcJuI3Tx+VQq9IfCJ7egXiGcDj2uof8xqNqemktrp5c="
uvicorn main:app --reload
```

#### Local Development (Bash)
```bash
export MOCK_API_TOKEN="dcJuI3Tx+VQq9IfCJ7egXiGcDj2uof8xqNqemktrp5c="
uvicorn main:app --reload
```

#### Vercel Deployment
1. Go to your Vercel project dashboard
2. Settings → Environment Variables
3. Add new variable:
   - **Name**: `MOCK_API_TOKEN`
   - **Value**: `dcJuI3Tx+VQq9IfCJ7egXiGcDj2uof8xqNqemktrp5c=`
   - **Environments**: Production, Preview, Development

## File Structure

```
novacare_demo/
├── main.py                    # FastAPI app with /api/config endpoint
├── config.py                  # Reads MOCK_API_TOKEN from environment
├── static/
│   ├── dashboard.html         # Main dashboard UI
│   ├── dashboard.js           # Fetches token from /api/config
│   ├── dashboard.css          # Styles
│   └── api-demo.html          # Simple demo showing token flow
└── .env.example              # Environment variable template
```

## Key Changes Made

### 1. Removed `vercel.json`
- No longer needed as FastAPI handles routing
- Environment variables set directly in Vercel dashboard

### 2. Updated `main.py`
```python
# Added config endpoint
@app.get("/api/config")
async def get_config():
    return JSONResponse({
        "apiToken": MOCK_API_TOKEN,  # From environment
        "apiBaseUrl": "/v1",
        "environment": "production"
    })

# Added StaticFiles mount (must be last!)
app.mount("/", StaticFiles(directory=static_path, html=True), name="static")
```

### 3. Updated `dashboard.js`
```javascript
// Load config on startup
async function loadConfig() {
    const response = await fetch(`${API_BASE_URL}/api/config`);
    const config = await response.json();
    API_TOKEN = config.apiToken;  // Token from environment!
}

// Initialize
document.addEventListener('DOMContentLoaded', async () => {
    await loadConfig();  // Load token first
    await refreshData();  // Then load data
});
```

## Testing

### 1. Start the Server
```powershell
cd novacare_demo
$env:MOCK_API_TOKEN="dcJuI3Tx+VQq9IfCJ7egXiGcDj2uof8xqNqemktrp5c="
uvicorn main:app --reload
```

### 2. Test Endpoints

**Config Endpoint** (Public):
```powershell
curl http://localhost:8000/api/config
```

**Health Check** (Requires Auth):
```powershell
$token = "dcJuI3Tx+VQq9IfCJ7egXiGcDj2uof8xqNqemktrp5c="
curl http://localhost:8000/healthz -Headers @{Authorization="Bearer $token"}
```

### 3. Open in Browser
- Main Dashboard: http://localhost:8000/dashboard.html
- API Demo: http://localhost:8000/api-demo.html
- API Docs: http://localhost:8000/docs

## Security Notes

1. **Production**: The API token should be a strong, randomly generated secret
2. **HTTPS**: Always use HTTPS in production to protect the token in transit
3. **Token Rotation**: Implement token rotation for enhanced security
4. **Rate Limiting**: Add rate limiting to prevent abuse
5. **CORS**: Restrict CORS origins in production (currently allows all for demo)

## API Endpoints

### Public Endpoints
- `GET /api/config` - Returns configuration including API token
- `GET /healthz` - Health check and system status
- `GET /` - API information

### Protected Endpoints (Require Bearer Token)
- `POST /v1/verify-identity` - Verify patient identity
- `GET /v1/patients/{id}/appointments` - Get patient appointments
- `GET /v1/appointments/available-slots` - Get available slots
- `PUT /v1/appointments/{id}` - Reschedule appointment
- `GET /v1/audit` - Get audit logs
- `POST /admin/reset` - Reset database
- `POST /data/refresh` - Refresh data

## Dashboard Features

The dashboard automatically:
1. ✅ Loads API token from environment via `/api/config`
2. ✅ Displays patient directory with appointment counts
3. ✅ Shows upcoming appointments
4. ✅ Lists available time slots
5. ✅ Displays recent activity audit log
6. ✅ Auto-refreshes every 10 seconds
7. ✅ Provides data reset functionality

## Troubleshooting

### Token Not Loading
- Ensure `MOCK_API_TOKEN` environment variable is set
- Check browser console for errors
- Verify `/api/config` endpoint returns the token

### Authentication Errors
- Verify the token is being sent in Authorization header
- Check that token matches the environment variable
- Ensure Bearer token format: `Authorization: Bearer <token>`

### Static Files Not Loading
- Verify files exist in `static/` directory
- Check that StaticFiles mount is last in main.py
- Ensure API routes are registered before static mount

## Development Workflow

1. **Set environment variable**
2. **Start server**: `uvicorn main:app --reload`
3. **Open dashboard**: http://localhost:8000/dashboard.html
4. **Check browser console** for token loading confirmation
5. **Test API calls** with authenticated requests

## Deployment Checklist

- [ ] Set `MOCK_API_TOKEN` in Vercel environment variables
- [ ] Update CORS origins in `config.py` to restrict access
- [ ] Test `/api/config` endpoint returns valid token
- [ ] Verify dashboard loads and authenticates correctly
- [ ] Test all API endpoints with Bearer token
- [ ] Check browser console for errors
- [ ] Verify auto-refresh works properly
