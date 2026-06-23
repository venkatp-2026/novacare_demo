# How Rescheduled Appointments Show in Dashboard

## Complete Data Flow

### 1. **Agent Reschedules Appointment**
```
AI Agent → PUT /v1/appointments/APT-101
Body: {
  "new_date": "2026-07-15",
  "new_time": "2:00 PM",
  "provider": "Dr. Williams"
}
```

### 2. **API Updates Data**
```python
# In routes/appointments.py
appointment["date"] = request.new_date
appointment["time"] = request.new_time
appointment["provider"] = request.provider
save_working_data()  # Saves to Excel
```

### 3. **Dashboard Auto-Refreshes (Every 30 seconds)**
```javascript
// Auto-refresh runs every 30 seconds
loadAllData()
  → GET /v1/patients/PAT-001/appointments
  → GET /v1/patients/PAT-002/appointments
  → ... (for all patients)
```

### 4. **Dashboard Renders Updated Data**
- **Appointments Tab**: Shows all appointments with new date/time
- **Patient Sidebar**: Click patient → see their updated appointments
- **Facilities Tab**: Grouped by location
- **Doctors Tab**: Grouped by provider

## Where Rescheduled Appointments Appear

### ✅ Appointments Tab
```
Shows card with:
- Appointment ID
- Patient name
- NEW date and time ← UPDATED!
- Provider
- Location
- Status: "confirmed"
```

### ✅ Patient Details Sidebar
```
Click patient name → sidebar opens showing:
- Patient info
- Medical history
- List of appointments ← Includes rescheduled one!
```

### ✅ Facilities Tab
```
Grouped by facility location
Shows appointment count per facility
```

### ✅ Doctors Tab
```
Grouped by provider
Shows appointment count per doctor
```

## Auto-Refresh Features

### Settings:
- **Interval**: 30 seconds
- **Behavior**: Fetches fresh data from API
- **Optimization**: Pauses when tab is hidden (saves resources)
- **Console Logs**: Shows "🔄 Auto-refreshing data..."

### Manual Refresh:
Users can also click "Refresh Data" button anytime for immediate refresh.

## Example Timeline

```
00:00 - AI agent reschedules APT-101
00:01 - API updates Excel data
00:15 - Dashboard auto-refreshes
00:15 - User sees updated appointment! ✅
```

## For Immediate Visibility

If you want the change to show **instantly** after reschedule:
1. User clicks "Refresh Data" button manually
2. Or wait max 30 seconds for auto-refresh

## Debug Checklist

If appointment doesn't show:
1. ✅ Check Vercel logs - see API call with new date/time
2. ✅ Check browser console - see "✅ Data loaded: X appointments"
3. ✅ Verify Excel data was saved (save_working_data called)
4. ✅ Check appointment status = "confirmed"
5. ✅ Verify patient_id matches dashboard patient list

## Data Persistence

- ✅ **In-Memory**: Updated immediately in Python data structures
- ✅ **Excel File**: Saved via save_working_data()
- ✅ **API Response**: Next GET returns updated data
- ✅ **Dashboard**: Fetches and displays updated data

The rescheduled appointment is **guaranteed to show** because:
1. Data is saved persistently
2. Dashboard fetches from same data source
3. Auto-refresh ensures changes appear within 30 seconds
