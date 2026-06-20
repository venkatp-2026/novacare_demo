# Demo Features Guide

## 📊 Professional Data Dashboard

**URL**: `https://novacare-demo.vercel.app/dashboard` (or `/dashboard` locally)

### Features:
- ✨ **Real-time Statistics**: Patients, Appointments, Slots, Audit Events
- 👥 **Patient Directory**: All active patients with appointment counts
- 📅 **Upcoming Appointments**: Sorted chronologically
- 🕐 **Available Slots**: Filterable time slots with availability status
- 📝 **Recent Activity**: Live audit log with formatted events
- 🔄 **Auto-refresh**: Updates every 10 seconds
- 🎨 **Professional Design**: Modern, clean UI with animations

### Demo Workflow:
1. Open dashboard before demo
2. Show initial state (all data visible)
3. Perform API actions (reschedule appointment via Zendesk)
4. Return to dashboard - see changes in real-time
5. Click "Reset Demo Data" to restore for next session

---

## 🎤 Voice Demo (Web Speech API)

**URL**: `https://novacare-demo.vercel.app/voice` (or `/voice` locally)

### Capabilities:
- 🗣️ **Speech-to-Text**: Browser-native Web Speech Recognition API
- 🤖 **Natural Language Processing**: Understands appointment-related commands
- 🔊 **Text-to-Speech**: Responds audibly to user requests
- 📱 **Real API Integration**: Fetches actual data from backend

### Voice Commands:
- "Show my appointments"
- "I need to reschedule my appointment"
- "What slots are available?"
- "Verify my identity"

### How It Works:
1. User clicks microphone button
2. Browser activates speech recognition
3. Transcript analyzed for intent
4. API called with appropriate endpoint
5. Response displayed and spoken aloud

### Browser Support:
- ✅ Chrome/Edge (best support)
- ✅ Safari (good support)
- ❌ Firefox (limited support)

---

## 🤔 Zendesk Sandbox vs Custom HTML Voice?

### **Recommendation: Use Custom HTML (Web Speech API)** ✅

**Why Custom HTML is Better:**

#### Pros:
- ✅ **No Zendesk Sandbox Required**: Works standalone
- ✅ **Full Control**: Customize entire experience
- ✅ **Direct API Integration**: No middleware needed
- ✅ **Free & Portable**: No licensing, works anywhere
- ✅ **Demo-Perfect**: Controlled environment, predictable behavior
- ✅ **Visual Feedback**: Show transcript, responses, processing states
- ✅ **Already Built**: Ready to use at `/voice` endpoint

#### Cons:
- ⚠️ **Browser Dependent**: Requires Chrome/Edge/Safari
- ⚠️ **Not Production**: Demo/POC only, not enterprise voice solution

### **Zendesk Voice/Talk:**

#### Pros:
- ✅ **Enterprise Grade**: Production-ready voice infrastructure
- ✅ **Call Recording**: Automatic compliance features
- ✅ **Agent Workspace**: Integrated with ticketing
- ✅ **IVR Integration**: Sophisticated routing

#### Cons:
- ❌ **Requires Zendesk Voice License**: Additional cost
- ❌ **Sandbox Complexity**: Need phone numbers, IVR setup
- ❌ **Overkill for Demo**: Too much setup for a proof of concept
- ❌ **Less Visual**: No browser UI, traditional phone experience

---

## 🎯 Demo Strategy Recommendation

### For **Proof of Concept / Sales Demo**:
**Use Custom HTML Voice Demo** (`/voice`)
- Quick to show
- Visual and interactive
- No infrastructure needed
- Highlights API capabilities

### For **Production Discussion**:
**Reference Zendesk Talk/Voice**
- Mention it as the production path
- Show how API would integrate
- Discuss IVR, call routing, compliance

### Best of Both Worlds:
1. **Start with HTML Voice Demo** - Show the concept working
2. **Transition to Dashboard** - Show data being modified
3. **Discuss Zendesk Voice** - "In production, this would integrate with Zendesk Talk..."
4. **Show Action Flows** - Demonstrate backend automation

---

## 📱 Mobile Experience

Both dashboard and voice demo are responsive:
- Works on tablets (iPad demos)
- Dashboard readable on phones
- Voice requires HTTPS (security requirement)

---

## 🚀 Quick Start

### Local Testing:
```bash
cd novacare_demo
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Visit:
- Dashboard: `http://localhost:8000/dashboard`
- Voice Demo: `http://localhost:8000/voice`
- API Docs: `http://localhost:8000/docs`

### Production (Vercel):
Already deployed! Visit:
- Dashboard: `https://novacare-demo.vercel.app/dashboard`
- Voice Demo: `https://novacare-demo.vercel.app/voice`

---

## 🎬 Demo Script Example

**Opening (30 seconds)**:
"Let me show you NovaCare Health's patient portal..."
→ Open `/dashboard`

**Voice Interaction (2 minutes)**:
"Patients can interact via voice..."
→ Open `/voice`
→ Demo: "Show my appointments"
→ Demo: "What slots are available?"

**Behind the Scenes (1 minute)**:
"Here's the real-time data..."
→ Switch back to `/dashboard`
→ Show audit log updating

**Reset for Next Demo**:
→ Click "Reset Demo Data" button
→ Verify data restored

---

## 💡 Pro Tips

1. **Pre-open tabs**: Have dashboard and voice demo ready
2. **Test audio**: Check speakers before presentation
3. **Practice commands**: Voice recognition improves with practice
4. **Use Chrome**: Most reliable for voice features
5. **Explain gracefully**: If voice fails, show it's a browser demo feature

---

## 🔧 Technical Notes

### Voice Demo Implementation:
- Uses Web Speech API (browser native)
- No server-side speech processing needed
- Intent recognition via keyword matching
- Integrates with actual API endpoints
- Fallback to text if speech unavailable

### Dashboard Implementation:
- Vanilla JavaScript (no frameworks)
- Fetches from REST API every 10 seconds
- Displays real data, not mocked
- Professional CSS with animations
- Mobile-responsive design

Both are **production-ready for demos**, not production apps.
