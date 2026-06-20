# Backend API Enhancement - Query Parameters for Smart Filtering

**Date:** 2026-06-20  
**Enhancement:** Added time_of_day filtering to available slots endpoint  
**Status:** ✅ Complete

---

## 🎯 WHAT WAS ENHANCED

### GET /v1/appointments/available-slots

**New Query Parameters:**

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `from_date` | string | Start date filter (YYYY-MM-DD) | `2026-07-01` |
| `to_date` | string | End date filter (YYYY-MM-DD) | `2026-07-15` |
| `time_of_day` | string | Filter by time period | `morning`, `afternoon`, `evening` |
| `provider` | string | Filter by provider name | `Dr. Williams` |

### Time of Day Definitions:

- **morning**: 6:00 AM - 12:00 PM (6-11:59)
- **afternoon**: 12:00 PM - 5:00 PM (12-16:59)
- **evening**: 5:00 PM - 9:00 PM (17-20:59)

---

## 📋 EXAMPLE API CALLS

### Get all morning slots next week:
```bash
curl "https://novacare-demo.vercel.app/v1/appointments/available-slots?from_date=2026-06-23&to_date=2026-06-30&time_of_day=morning" \
  -H "Authorization: Bearer dcJuI3Tx+VQq9IfCJ7egXiGcDj2uof8xqNqemktrp5c="
```

### Get afternoon slots with Dr. Williams:
```bash
curl "https://novacare-demo.vercel.app/v1/appointments/available-slots?time_of_day=afternoon&provider=Dr. Williams" \
  -H "Authorization: Bearer dcJuI3Tx+VQq9IfCJ7egXiGcDj2uof8xqNqemktrp5c="
```

### Get slots in specific date range:
```bash
curl "https://novacare-demo.vercel.app/v1/appointments/available-slots?from_date=2026-07-01&to_date=2026-07-10" \
  -H "Authorization: Bearer dcJuI3Tx+VQq9IfCJ7egXiGcDj2uof8xqNqemktrp5c="
```

### Get tomorrow's evening slots:
```bash
curl "https://novacare-demo.vercel.app/v1/appointments/available-slots?from_date=2026-06-22&to_date=2026-06-22&time_of_day=evening" \
  -H "Authorization: Bearer dcJuI3Tx+VQq9IfCJ7egXiGcDj2uof8xqNqemktrp5c="
```

---

## 🔧 UPDATED CUSTOM ACTION CONFIGURATION

### Custom Action: get_available_slots (UPDATED)

**In Zendesk: AI Agent → Actions → Custom actions → Edit "get_available_slots"**

```
Name: get_available_slots
Description: Retrieves available appointment time slots with optional filters for date range, time of day, and provider

Method: GET
URL: https://novacare-demo.vercel.app/v1/appointments/available-slots

Headers:
  Authorization: Bearer dcJuI3Tx+VQq9IfCJ7egXiGcDj2uof8xqNqemktrp5c=

Input Parameters:
  - from_date (text, optional) - Start date in YYYY-MM-DD format
  - to_date (text, optional) - End date in YYYY-MM-DD format
  - time_of_day (text, optional) - Time period: morning, afternoon, or evening
  - provider (text, optional) - Provider name to filter by

Output Parameters:
  - slots (array) - List of available slots matching filters
```

---

## 🤖 HOW AI WILL USE THIS IN PROCEDURE

### Scenario 1: "I want next week morning"

**AI reasoning:**
```
User said: "next week morning"
→ Calculate: next week = 2026-06-23 to 2026-06-30
→ Time preference: morning
→ Call API: from_date=2026-06-23, to_date=2026-06-30, time_of_day=morning
→ Get filtered results (only morning slots next week)
→ Present top 3 matches
```

### Scenario 2: "Tomorrow afternoon with Dr. Williams"

**AI reasoning:**
```
User said: "tomorrow afternoon with Dr. Williams"
→ Calculate: tomorrow = 2026-06-22
→ Time preference: afternoon
→ Provider: Dr. Williams
→ Call API: from_date=2026-06-22, to_date=2026-06-22, time_of_day=afternoon, provider=Dr. Williams
→ Get filtered results
→ Present matches
```

### Scenario 3: "Something in 2 weeks, evening time"

**AI reasoning:**
```
User said: "in 2 weeks, evening time"
→ Calculate: 2 weeks = 2026-07-05 (14 days from today)
→ Date range: 2026-07-05 to 2026-07-12 (1 week window around target)
→ Time preference: evening
→ Call API: from_date=2026-07-05, to_date=2026-07-12, time_of_day=evening
→ Get filtered results
→ Present matches
```

---

## ✅ BENEFITS

### Before Enhancement:
```
❌ API returns all 10 slots
❌ AI must filter in reasoning (less reliable)
❌ More tokens consumed (processing large response)
❌ Slower response time
❌ Filtering logic duplicated in AI prompt
```

### After Enhancement:
```
✅ API returns only matching slots (2-3 results)
✅ Backend does precise filtering
✅ Fewer tokens consumed
✅ Faster response time
✅ AI focuses on presentation, not filtering
✅ Consistent filtering logic
```

---

## 🧪 TESTING

### Test the enhanced endpoint:

```bash
# Test 1: Morning slots
curl -s "https://novacare-demo.vercel.app/v1/appointments/available-slots?time_of_day=morning" \
  -H "Authorization: Bearer dcJuI3Tx+VQq9IfCJ7egXiGcDj2uof8xqNqemktrp5c=" | jq

# Expected: Only slots with times 6:00 AM - 11:59 AM

# Test 2: Afternoon slots
curl -s "https://novacare-demo.vercel.app/v1/appointments/available-slots?time_of_day=afternoon" \
  -H "Authorization: Bearer dcJuI3Tx+VQq9IfCJ7egXiGcDj2uof8xqNqemktrp5c=" | jq

# Expected: Only slots with times 12:00 PM - 4:59 PM

# Test 3: Evening slots
curl -s "https://novacare-demo.vercel.app/v1/appointments/available-slots?time_of_day=evening" \
  -H "Authorization: Bearer dcJuI3Tx+VQq9IfCJ7egXiGcDj2uof8xqNqemktrp5c=" | jq

# Expected: Only slots with times 5:00 PM - 8:59 PM

# Test 4: Date range
curl -s "https://novacare-demo.vercel.app/v1/appointments/available-slots?from_date=2026-07-01&to_date=2026-07-05" \
  -H "Authorization: Bearer dcJuI3Tx+VQq9IfCJ7egXiGcDj2uof8xqNqemktrp5c=" | jq

# Expected: Only slots between July 1-5

# Test 5: Combined filters
curl -s "https://novacare-demo.vercel.app/v1/appointments/available-slots?from_date=2026-07-01&to_date=2026-07-10&time_of_day=morning&provider=Dr.%20Williams" \
  -H "Authorization: Bearer dcJuI3Tx+VQq9IfCJ7egXiGcDj2uof8xqNqemktrp5c=" | jq

# Expected: Only Dr. Williams morning slots July 1-10
```

---

## 🚀 DEPLOYMENT

### Step 1: Commit & Push

```bash
cd /c/ca/report/novahealth/novacare_demo
git add routes/appointments.py
git commit -m "Add time_of_day filtering to available slots endpoint

Enhances /v1/appointments/available-slots with time_of_day query parameter supporting morning (6am-12pm), afternoon (12pm-5pm), and evening (5pm-9pm) filtering. Enables AI agent to query slots based on patient time preferences.

Co-Authored-By: Claude Sonnet 4.5 (1M context) <noreply@anthropic.com>"
git push origin main
```

### Step 2: Wait for Vercel Deploy (~2 minutes)

### Step 3: Test the deployed endpoint

```bash
curl "https://novacare-demo.vercel.app/v1/appointments/available-slots?time_of_day=morning" \
  -H "Authorization: Bearer dcJuI3Tx+VQq9IfCJ7egXiGcDj2uof8xqNqemktrp5c="
```

### Step 4: Update Zendesk Custom Action

- Navigate to: AI Agent → Actions → Custom actions
- Edit: "get_available_slots"
- Add new input parameters: `from_date`, `to_date`, `time_of_day`, `provider`
- Save

---

## 📝 PROCEDURE UPDATE

### In your appointment rescheduling procedure, the AI can now call:

```
Trigger the "get_available_slots" custom action with:
- from_date: [calculated from "next week" = 2026-06-23]
- to_date: [calculated from "next week" = 2026-06-30]
- time_of_day: "morning"
- provider: [optional, if user mentioned specific provider]
```

**The API does the heavy lifting, AI does the reasoning!**

---

## ✅ VERIFICATION CHECKLIST

After deployment:

- [ ] Backend code committed and pushed
- [ ] Vercel deployment successful
- [ ] Tested: `?time_of_day=morning` returns only morning slots
- [ ] Tested: `?time_of_day=afternoon` returns only afternoon slots
- [ ] Tested: `?time_of_day=evening` returns only evening slots
- [ ] Tested: Date range filtering works
- [ ] Tested: Provider filtering works
- [ ] Tested: Combined filters work together
- [ ] Updated Zendesk custom action with new parameters
- [ ] Swagger docs show new parameters

---

**Status:** ✅ Enhanced and Ready  
**Deployment:** Pending git push  
**Impact:** 🔥 Enables truly conversational appointment scheduling
