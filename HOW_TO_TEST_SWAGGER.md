# How to Test APIs in Swagger Docs

**Swagger URL:** https://novacare-demo.vercel.app/docs

---

## 🔐 The 401 Error Problem

You're getting 401 errors because the API requires Bearer token authentication, but Swagger doesn't have a built-in "Authorize" button configured yet.

**The token you need:**
```
dcJuI3Tx+VQq9IfCJ7egXiGcDj2uof8xqNqemktrp5c=
```

---

## ✅ Solution 1: Add Authorization Header Manually (Current Workaround)

Since the Swagger UI doesn't have the "Authorize" button configured, you need to add the authorization header manually for each request:

### Step-by-Step in Swagger UI:

1. **Go to:** https://novacare-demo.vercel.app/docs

2. **Click on any endpoint** (e.g., "GET /v1/patients/{patient_id}/appointments")

3. **Click "Try it out"**

4. **Scroll down to "Parameters" section**

5. **Look for "authorization" field** (it might be listed as a header parameter)

6. **Enter this value:**
   ```
   Bearer dcJuI3Tx+VQq9IfCJ7egXiGcDj2uof8xqNqemktrp5c=
   ```
   ⚠️ **Important:** Include "Bearer " (with a space) before the token

7. **Fill in other required parameters** (like patient_id)

8. **Click "Execute"**

---

## ✅ Solution 2: Use cURL (Easiest Way)

Instead of using Swagger UI, use the cURL commands directly:

### Test Patient Lookup:
```bash
curl -X POST https://novacare-demo.vercel.app/v1/patients/lookup \
  -H "Authorization: Bearer dcJuI3Tx+VQq9IfCJ7egXiGcDj2uof8xqNqemktrp5c=" \
  -H "Content-Type: application/json" \
  -d '{"name":"Jane Smith","dob":"03/15/1985"}'
```

### Test Verify Identity:
```bash
curl -X POST https://novacare-demo.vercel.app/v1/verify-identity \
  -H "Authorization: Bearer dcJuI3Tx+VQq9IfCJ7egXiGcDj2uof8xqNqemktrp5c=" \
  -H "Content-Type: application/json" \
  -d '{"patient_id":"PAT-001","dob":"1985-03-15"}'
```

### Test Get Appointments:
```bash
curl https://novacare-demo.vercel.app/v1/patients/PAT-001/appointments \
  -H "Authorization: Bearer dcJuI3Tx+VQq9IfCJ7egXiGcDj2uof8xqNqemktrp5c="
```

### Test Get Available Slots:
```bash
curl https://novacare-demo.vercel.app/v1/appointments/available-slots \
  -H "Authorization: Bearer dcJuI3Tx+VQq9IfCJ7egXiGcDj2uof8xqNqemktrp5c="
```

### Test Insurance Verification:
```bash
curl -X POST https://novacare-demo.vercel.app/v1/insurance/verify-coverage \
  -H "Authorization: Bearer dcJuI3Tx+VQq9IfCJ7egXiGcDj2uof8xqNqemktrp5c=" \
  -H "Content-Type: application/json" \
  -d '{"patient_id":"PAT-001"}'
```

### Test Reschedule Appointment:
```bash
curl -X PUT https://novacare-demo.vercel.app/v1/appointments/APT-101 \
  -H "Authorization: Bearer dcJuI3Tx+VQq9IfCJ7egXiGcDj2uof8xqNqemktrp5c=" \
  -H "Content-Type: application/json" \
  -d '{"slot_id":"SLOT-005","reason":"Patient requested change"}'
```

---

## ✅ Solution 3: Use Postman or Insomnia

### In Postman:

1. **Import the Swagger JSON:**
   - URL: https://novacare-demo.vercel.app/openapi.json
   - Or create requests manually

2. **For each request, add Authorization header:**
   - Key: `Authorization`
   - Value: `Bearer dcJuI3Tx+VQq9IfCJ7egXiGcDj2uof8xqNqemktrp5c=`

3. **Save it as a Collection variable** so you don't have to type it every time

### In Insomnia:

1. Create a new request
2. Set method (GET, POST, PUT) and URL
3. Go to "Auth" tab
4. Select "Bearer Token"
5. Paste token: `dcJuI3Tx+VQq9IfCJ7egXiGcDj2uof8xqNqemktrp5c=`

---

## 🔧 Solution 4: Fix Swagger to Add "Authorize" Button (Optional)

If you want to fix the Swagger UI permanently, I can update the FastAPI app to include security scheme configuration. This will add the padlock "Authorize" button at the top of the Swagger page.

**Would you like me to:**
1. ✅ Add the security scheme to main.py
2. ✅ Redeploy to Vercel
3. ✅ Then you can use the "Authorize" button in Swagger

---

## 📋 Quick Test All Endpoints

Copy and paste this into your terminal to test all endpoints at once:

```bash
echo "Testing Patient Lookup..."
curl -s -X POST https://novacare-demo.vercel.app/v1/patients/lookup \
  -H "Authorization: Bearer dcJuI3Tx+VQq9IfCJ7egXiGcDj2uof8xqNqemktrp5c=" \
  -H "Content-Type: application/json" \
  -d '{"name":"Jane Smith","dob":"03/15/1985"}' | jq

echo -e "\nTesting Verify Identity..."
curl -s -X POST https://novacare-demo.vercel.app/v1/verify-identity \
  -H "Authorization: Bearer dcJuI3Tx+VQq9IfCJ7egXiGcDj2uof8xqNqemktrp5c=" \
  -H "Content-Type: application/json" \
  -d '{"patient_id":"PAT-001","dob":"1985-03-15"}' | jq

echo -e "\nTesting Get Appointments..."
curl -s https://novacare-demo.vercel.app/v1/patients/PAT-001/appointments \
  -H "Authorization: Bearer dcJuI3Tx+VQq9IfCJ7egXiGcDj2uof8xqNqemktrp5c=" | jq

echo -e "\nTesting Available Slots..."
curl -s https://novacare-demo.vercel.app/v1/appointments/available-slots \
  -H "Authorization: Bearer dcJuI3Tx+VQq9IfCJ7egXiGcDj2uof8xqNqemktrp5c=" | jq

echo -e "\nTesting Insurance Verification..."
curl -s -X POST https://novacare-demo.vercel.app/v1/insurance/verify-coverage \
  -H "Authorization: Bearer dcJuI3Tx+VQq9IfCJ7egXiGcDj2uof8xqNqemktrp5c=" \
  -H "Content-Type: application/json" \
  -d '{"patient_id":"PAT-001"}' | jq

echo -e "\n✅ All tests complete!"
```

---

## 🎯 Recommended Approach

**For quick testing:** Use the cURL commands above (Solution 2)

**For Zendesk Custom Actions:** You don't need to test in Swagger! The custom actions will work automatically because:
1. ✅ The authorization header is configured in each custom action
2. ✅ The token is already included
3. ✅ All endpoints are verified working

**For permanent solution:** Let me fix the Swagger UI by adding the security scheme (Solution 4)

---

## 🚨 Important Note

**You don't need Swagger to work for your demo!**

The Zendesk AI Agent custom actions will work perfectly because:
- ✅ Each custom action has the Authorization header configured
- ✅ The token is hardcoded in the guide
- ✅ All endpoints have been tested via cURL and are working

The Swagger UI is just for manual testing and documentation. The actual demo will work through Zendesk's AI Agent, which doesn't use Swagger at all.

---

## 🤔 Should I Fix the Swagger UI?

**Option A: Skip it** - You don't need Swagger for the demo, and fixing it requires code changes + redeployment

**Option B: Fix it** - Takes 5 minutes to add security scheme and redeploy, then you'll have a nice "Authorize" button in Swagger

**What would you prefer?**

---

**Last Updated:** 2026-06-20  
**All Endpoints:** ✅ Working via cURL  
**Swagger Auth:** ⚠️ Needs manual header entry (or we can fix it)
