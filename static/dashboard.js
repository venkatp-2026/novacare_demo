// Configuration
const API_BASE_URL = window.location.origin;
let API_TOKEN = null; // Will be fetched from backend
const REFRESH_INTERVAL = 10000; // 10 seconds

let refreshTimer = null;

// Fetch configuration from backend (including API token from environment)
async function loadConfig() {
    try {
        console.log('Loading configuration from backend...');
        const response = await fetch(`${API_BASE_URL}/api/config`);
        if (!response.ok) {
            throw new Error(`Failed to load config: ${response.status}`);
        }
        const config = await response.json();
        API_TOKEN = config.apiToken;
        console.log('Configuration loaded successfully. API token retrieved from environment.');
        return config;
    } catch (error) {
        console.error('Failed to load configuration:', error);
        // Fallback to a default token for development
        API_TOKEN = 'dev-token-replace-in-production';
        console.warn('Using fallback API token. Check backend /api/config endpoint.');
        throw error;
    }
}

// Utility Functions
function formatDate(dateStr) {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

function formatTime(dateStr) {
    const date = new Date(dateStr);
    return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
}

function formatDateTime(dateStr) {
    const date = new Date(dateStr);
    return date.toLocaleString('en-US', { 
        month: 'short', 
        day: 'numeric', 
        hour: '2-digit', 
        minute: '2-digit' 
    });
}

function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast show ${type}`;
    setTimeout(() => {
        toast.className = 'toast';
    }, 3000);
}

// API Functions
async function apiCall(endpoint, method = 'GET', body = null) {
    // Ensure API token is loaded
    if (!API_TOKEN) {
        throw new Error('API token not loaded. Configuration must be fetched first.');
    }
    
    const options = {
        method,
        headers: {
            'Authorization': `Bearer ${API_TOKEN}`,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    };
    
    if (body) {
        options.body = JSON.stringify(body);
    }
    
    try {
        console.log(`Making API call to: ${API_BASE_URL}${endpoint}`);
        const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
        console.log(`Response status: ${response.status}`);
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error(`API Error: ${response.status} - ${errorText}`);
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error(`API call failed for ${endpoint}:`, error);
        throw error;
    }
}

// Data Loading Functions
async function loadHealthData() {
    try {
        const data = await apiCall('/healthz');
        
        document.getElementById('total-patients').textContent = data.checks.patients_loaded;
        document.getElementById('total-appointments').textContent = data.checks.appointments_loaded;
        document.getElementById('available-slots').textContent = data.checks.slots_available;
        
        return data;
    } catch (error) {
        console.error('Failed to load health data:', error);
    }
}

async function loadPatients() {
    try {
        // Since we don't have a direct patients endpoint, we'll simulate from known patients
        const patients = [
            { id: 'PAT-001', name: 'Jane Smith', dob: '1985-03-15', mrn: 'MRN-2001' },
            { id: 'PAT-002', name: 'Robert Johnson', dob: '1978-11-22', mrn: 'MRN-2002' },
            { id: 'PAT-003', name: 'Maria Garcia', dob: '1992-07-08', mrn: 'MRN-2003' }
        ];
        
        const container = document.getElementById('patients-container');
        document.getElementById('patient-count').textContent = patients.length;
        
        // Get appointment counts for each patient
        const appointmentPromises = patients.map(p => 
            apiCall(`/v1/patients/${p.id}/appointments`)
                .catch(err => {
                    console.error(`Failed to load appointments for ${p.id}:`, err);
                    return [];
                })
        );
        const appointmentResults = await Promise.all(appointmentPromises);
        
        container.innerHTML = patients.map((patient, index) => `
            <div class="patient-item">
                <div class="patient-info">
                    <h3>${patient.name}</h3>
                    <p>ID: ${patient.id} • MRN: ${patient.mrn}</p>
                </div>
                <div class="patient-badge">${appointmentResults[index].length} appointments</div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Failed to load patients:', error);
        document.getElementById('patients-container').innerHTML = 
            '<div class="loading">Failed to load patients. Check console for details.</div>';
    }
}

async function loadAppointments() {
    try {
        const patients = ['PAT-001', 'PAT-002', 'PAT-003'];
        const appointmentPromises = patients.map(id => 
            apiCall(`/v1/patients/${id}/appointments`).catch(() => [])
        );
        const results = await Promise.all(appointmentPromises);
        
        const allAppointments = results.flat().sort((a, b) => 
            new Date(a.date + ' ' + a.time) - new Date(b.date + ' ' + b.time)
        );
        
        const container = document.getElementById('appointments-container');
        document.getElementById('appointment-count').textContent = allAppointments.length;
        
        if (allAppointments.length === 0) {
            container.innerHTML = '<div class="loading">No appointments found</div>';
            return;
        }
        
        container.innerHTML = allAppointments.slice(0, 10).map(apt => `
            <div class="appointment-item">
                <div class="appointment-header">
                    <span class="appointment-patient">${apt.patient_id}</span>
                    <span class="appointment-status">${apt.status}</span>
                </div>
                <div class="appointment-details">
                    <span class="appointment-detail">📅 ${apt.date}</span>
                    <span class="appointment-detail">🕐 ${apt.time}</span>
                    <span class="appointment-detail">👨‍⚕️ ${apt.provider}</span>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Failed to load appointments:', error);
        document.getElementById('appointments-container').innerHTML = 
            '<div class="loading">Failed to load appointments</div>';
    }
}

async function loadSlots() {
    try {
        const slots = await apiCall('/v1/appointments/available-slots');
        
        const container = document.getElementById('slots-container');
        const availableCount = slots.filter(s => s.available).length;
        document.getElementById('slots-count').textContent = availableCount;
        
        if (slots.length === 0) {
            container.innerHTML = '<div class="loading">No slots found</div>';
            return;
        }
        
        container.innerHTML = slots.slice(0, 10).map(slot => `
            <div class="slot-item ${slot.available ? 'available' : 'unavailable'}">
                <div class="slot-header">
                    <span class="slot-time">📅 ${slot.date} • ${slot.time}</span>
                    <span class="slot-badge ${slot.available ? 'available' : 'booked'}">
                        ${slot.available ? 'Available' : 'Booked'}
                    </span>
                </div>
                <div class="slot-provider">👨‍⚕️ ${slot.provider} • ${slot.location}</div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Failed to load slots:', error);
        document.getElementById('slots-container').innerHTML = 
            '<div class="loading">Failed to load slots</div>';
    }
}

async function loadAuditLog() {
    try {
        const logs = await apiCall('/v1/audit?limit=10');
        
        const container = document.getElementById('activity-container');
        document.getElementById('activity-count').textContent = logs.length;
        document.getElementById('audit-count').textContent = logs.length;
        
        if (logs.length === 0) {
            container.innerHTML = '<div class="loading">No recent activity</div>';
            return;
        }
        
        container.innerHTML = logs.map(log => `
            <div class="activity-item">
                <div class="activity-header">
                    <span class="activity-event">${formatEventName(log.event)}</span>
                    <span class="activity-time">${formatDateTime(log.timestamp)}</span>
                </div>
                <div class="activity-details">
                    ${log.patient_id ? `Patient: ${log.patient_id}` : ''}
                    ${log.endpoint ? `• ${log.endpoint}` : ''}
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Failed to load audit log:', error);
        document.getElementById('activity-container').innerHTML = 
            '<div class="loading">Failed to load activity</div>';
    }
}

function formatEventName(event) {
    const eventNames = {
        'identity_verification': '🔐 Identity Verified',
        'appointments_accessed': '📅 Appointments Viewed',
        'slots_queried': '🕐 Slots Searched',
        'appointment_rescheduled': '🔄 Appointment Rescheduled',
        'database_reset': '🔄 Database Reset',
        'data_refreshed': '🔄 Data Refreshed',
        'auth_failed': '❌ Auth Failed'
    };
    return eventNames[event] || event;
}

// Main refresh function
async function refreshData() {
    console.log('Refreshing dashboard data...');
    
    try {
        await Promise.all([
            loadHealthData(),
            loadPatients(),
            loadAppointments(),
            loadSlots(),
            loadAuditLog()
        ]);
        
        document.getElementById('last-update').textContent = new Date().toLocaleTimeString();
        console.log('Dashboard refreshed successfully');
    } catch (error) {
        console.error('Failed to refresh dashboard:', error);
        showToast('Failed to refresh data', 'error');
    }
}

// Reset data function
async function resetData() {
    if (!confirm('Reset all data to initial state? This will restore all default appointments and slots.')) {
        return;
    }
    
    try {
        await apiCall('/v1/data/refresh', 'POST');
        showToast('Data reset successfully! Refreshing dashboard...', 'success');
        setTimeout(refreshData, 1000);
    } catch (error) {
        console.error('Failed to reset data:', error);
        showToast('Failed to reset data', 'error');
    }
}

// Auto-refresh setup
function startAutoRefresh() {
    if (refreshTimer) {
        clearInterval(refreshTimer);
    }
    refreshTimer = setInterval(refreshData, REFRESH_INTERVAL);
}

function stopAutoRefresh() {
    if (refreshTimer) {
        clearInterval(refreshTimer);
        refreshTimer = null;
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', async () => {
    console.log('Dashboard initializing...');
    
    try {
        // Load configuration first (including API token from environment)
        await loadConfig();
        console.log('✓ Configuration loaded');
        
        // Now load dashboard data with the API token
        await refreshData();
        console.log('✓ Initial data loaded');
        
        // Start auto-refresh
        startAutoRefresh();
        console.log('✓ Dashboard initialized. Auto-refresh enabled.');
    } catch (error) {
        console.error('Dashboard initialization failed:', error);
        document.getElementById('system-status').textContent = 'System Error';
        document.getElementById('system-status').style.color = '#ef4444';
    }
});

// Stop auto-refresh when page is hidden
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        stopAutoRefresh();
    } else {
        startAutoRefresh();
    }
});
