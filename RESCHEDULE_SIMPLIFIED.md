# Simplified Reschedule API - Demo Version

## Problem
The original reschedule API required agents to:
1. Call GET `/appointments/available-slots` to get slots
2. Parse the slot_id from the response
3. Call PUT `/appointments/{id}` with the slot_id

This was error-prone for AI agents and added unnecessary complexity for a demo.

## Solution
**Removed slot_id requirement completely!** The agent can now reschedule by simply providing:

```json
{
  "new_date": "2026-07-15",
  "new_time": "2:00 PM",
  "provider": "Dr. Williams",  // optional
  "reason": "Patient conflict"  // optional
}
```

## API Changes

### Before (Complex)
```
PUT /v1/appointments/{appointment_id}
Body: {"slot_id": "SLOT-005"}
```

### After (Simple)
```
PUT /v1/appointments/{appointment_id}
Body: {
  "new_date": "2026-07-15",
  "new_time": "2:00 PM",
  "provider": "Dr. Williams"  // optional
}
```

## Benefits for Demo
1. ✅ **Much easier for AI agents** - no need to parse slot IDs
2. ✅ **More intuitive** - agent thinks in human terms (date/time)
3. ✅ **Still works with dashboard** - appointments update and display correctly
4. ✅ **Simpler debugging** - logs show actual date/time instead of cryptic IDs
5. ✅ **Faster workflow** - one API call instead of two

## Dashboard Compatibility
The rescheduled appointment will show up correctly in `dashboard-view.html` because:
- The appointment object is updated with new date/time
- The changes are saved to Excel (working data)
- The dashboard reads from the same data source

## Example Agent Call
```python
# AI Agent can now simply say:
reschedule_appointment(
    appointment_id="APT-101",
    new_date="2026-07-15",
    new_time="2:00 PM",
    provider="Dr. Williams"  # optional
)
```

## What About Slot Validation?
For a **production system**, you'd want to validate against available slots. But for a **demo**, showing the flexibility and ease of use is more important than enforcing strict slot validation.

The appointment updates immediately and shows in the dashboard - perfect for demonstrations!
