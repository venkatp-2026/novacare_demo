# Swagger UI Testing - Quick Start Guide

**Swagger URL:** https://novacare-demo.vercel.app/docs

---

## ✅ I Just Fixed the 401 Error Issue!

**What I did:**
- Added Bearer token security scheme to the FastAPI app
- Configured Swagger UI to show the "Authorize" button (padlock icon)
- Pushed to GitHub and triggered Vercel redeployment

**Deployment Status:** 🚀 Deploying now (takes 1-2 minutes)

---

## 🔐 How to Use Swagger UI (After Deployment)

### Step 1: Wait for Deployment
The code was just pushed. Vercel is deploying now. Wait ~2 minutes, then refresh the Swagger page.

### Step 2: Click the "Authorize" Button
1. Go to: https://novacare-demo.vercel.app/docs
2. Look for the **🔓 Authorize** button at the top right of the page
3. Click it

### Step 3: Enter the Bearer Token
A popup will appear asking for the bearer token.

**Enter this:**
```
dcJuI3Tx+VQq9IfCJ7egXiGcDj2uof8xqNqemktrp5c=
```

**Important:** 
- ✅ Just paste the token (without "Bearer " prefix)
- ✅ Swagger will automatically add "Bearer " for you
- ✅ Click "Authorize"
- ✅ Close the popup

### Step 4: Test Any Endpoint
Now you can test any endpoint without getting 401 errors:

1. Click on any endpoint (e.g., **GET /v1/patients/{patient_id}/appointments**)
2. Click **"Try it out"**
3. Fill in required parameters (e.g., patient_id: `PAT-001`)
4. Click **"Execute"**
5. See the response! ✅

---

## 🧪 Quick Test Scenarios

### Test 1: Get Appointments
1. Click **GET /v1/patients/{patient_id}/appointments**
2. Try it out
3. Enter patient_id: `PAT-001`
4. Execute
5. Expected: 3 appointments for Jane Smith

### Test 2: Patient Lookup
1. Click **POST /v1/patients/lookup**
2. Try it out
3. Enter request body:
   ```json
   {
     "name": "Jane Smith",
     "dob": "03/15/1985"
   }
   ```
4. Execute
5. Expected: Returns patient_id PAT-001

### Test 3: Insurance Verification
1. Click **POST /v1/insurance/verify-coverage**
2. Try it out
3. Enter request body:
   ```json
   {
     "patient_id": "PAT-001"
   }
   ```
4. Execute
5. Expected: Blue Cross PPO details

### Test 4: Available Slots
1. Click **GET /v1/appointments/available-slots**
2. Try it out
3. Execute (no parameters needed)
4. Expected: 10 available slots

---

## 🚨 If the Authorize Button Doesn't Appear Yet

The deployment is still in progress. Use cURL for now:

### Test All Endpoints via Terminal:

```bash
# Patient Lookup
curl -X POST https://novacare-demo.vercel.app/v1/patients/lookup \
  -H "Authorization: Bearer dcJuI3Tx+VQq9IfCJ7egXiGcDj2uof8xqNqemktrp5c=" \
  -H "Content-Type: application/json" \
  -d '{"name":"Jane Smith","dob":"03/15/1985"}'

# Get Appointments
curl https://novacare-demo.vercel.app/v1/patients/PAT-001/appointments \
  -H "Authorization: Bearer dcJuI3Tx+VQq9IfCJ7egXiGcDj2uof8xqNqemktrp5c="

# Insurance Verification
curl -X POST https://novacare-demo.vercel.app/v1/insurance/verify-coverage \
  -H "Authorization: Bearer dcJuI3Tx+VQq9IfCJ7egXiGcDj2uof8xqNqemktrp5c=" \
  -H "Content-Type: application/json" \
  -d '{"patient_id":"PAT-001"}'
```

---

## 📋 Test Data Reference

### Test Patients:
- **PAT-001** - Jane Smith (DOB: 1985-03-15 or 03/15/1985)
- **PAT-002** - Robert Johnson (DOB: 1978-11-22)
- **PAT-003** - Maria Garcia (DOB: 1992-07-08)

### Available Slots:
- SLOT-001 through SLOT-010

### Bearer Token:
```
dcJuI3Tx+VQq9IfCJ7egXiGcDj2uof8xqNqemktrp5c=
```

---

## ✅ Verification Checklist

After deployment completes (2 minutes):

1. ✅ Refresh https://novacare-demo.vercel.app/docs
2. ✅ See the "Authorize" button (🔓 icon) at top right
3. ✅ Click it and enter the token
4. ✅ Test any endpoint - should work without 401 errors
5. ✅ Token persists across page refreshes

---

## 🎯 Summary

**Before:** 401 errors because no way to add auth in Swagger  
**After:** Click "Authorize" button, enter token once, test everything

**Wait Time:** 1-2 minutes for Vercel deployment  
**When Ready:** Refresh the Swagger page and look for the Authorize button

---

**Deployment Time:** 2026-06-20 (just now)  
**Expected Ready:** Within 2 minutes  
**Status:** Check https://vercel.com/venkatp-2026s-projects for deployment status
