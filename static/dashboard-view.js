// Dashboard View JavaScript
let allPatients = [];
let allAppointments = [];
let allSlots = [];
let activityLogs = [];

// API Base URL
const API_BASE = window.location.origin + '/v1';
let API_TOKEN = null;

// Fetch API token from backend
async function loadConfig() {
    try {
        const response = await fetch(`${window.location.origin}/api/config`);
        if (!response.ok) {
            throw new Error(`Failed to load config: ${response.status}`);
        }
        const config = await response.json();
        API_TOKEN = config.apiToken;
        console.log('Configuration loaded successfully');
        return config;
    } catch (error) {
        console.error('Failed to load configuration:', error);
        API_TOKEN = 'dev-token-replace-in-production';
        throw error;
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', async () => {
    await loadConfig();
    initTabs();
    loadAllData();
});

// Tab Switching
function initTabs() {
    document.querySelectorAll('.tab').forEach(tab => {
        tab.addEventListener('click', () => {
            const tabName = tab.dataset.tab;

            // Update tab active state
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            tab.classList.add('active');

            // Update content active state
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });
            document.getElementById(`tab-${tabName}`).classList.add('active');
        });
    });
}

// Load All Data
async function loadAllData() {
    document.getElementById('loading').style.display = 'block';

    try {
        const authHeader = `Bearer ${API_TOKEN}`;

        // Fetch all patients
        const patientsRes = await Promise.all(['PAT-001', 'PAT-002', 'PAT-003', 'PAT-004', 'PAT-005', 'PAT-006'].map(id =>
            fetch(`${API_BASE}/patients/${id}/appointments`, {
                headers: { 'Authorization': authHeader }
            }).then(r => r.json())
        ));

        // Fetch patient details
        const patientDetailsRes = await Promise.all(['PAT-001', 'PAT-002', 'PAT-003', 'PAT-004', 'PAT-005', 'PAT-006'].map(id =>
            fetch(`${API_BASE}/patients/${id}`, {
                headers: { 'Authorization': authHeader }
            }).then(r => r.json())
        ));

        allPatients = patientDetailsRes;

        // Flatten all appointments
        allAppointments = patientsRes.flat();

        // Fetch available slots
        const slotsRes = await fetch(`${API_BASE}/appointments/available-slots`, {
            headers: { 'Authorization': authHeader }
        });
        allSlots = await slotsRes.json();

        // Render all sections
        renderPatients();
        renderAppointments();
        renderFacilities();
        renderDoctors();
        renderAvailability();
        renderLogs();

        // Initialize filters
        populateFilters();

    } catch (error) {
        console.error('Error loading data:', error);
        alert('Error loading data. Please refresh the page.');
    } finally {
        document.getElementById('loading').style.display = 'none';
    }
}

// Render Patients
function renderPatients() {
    const list = document.getElementById('patients-grid');
    list.innerHTML = '';

    allPatients.forEach(patient => {
        const item = document.createElement('div');
        item.className = 'patient-list-item';
        item.onclick = () => showPatientDetails(patient);

        // Get initials for avatar
        const initials = patient.name.split(' ').map(n => n[0]).join('').toUpperCase();

        item.innerHTML = `
            <div class="patient-avatar">${initials}</div>
            <div class="patient-name">${patient.name}</div>
            <div class="patient-id-badge">${patient.patient_id}</div>
        `;

        list.appendChild(item);
    });

    // Search functionality
    document.getElementById('search-patients').addEventListener('input', (e) => {
        const search = e.target.value.toLowerCase();
        document.querySelectorAll('.patient-list-item').forEach(item => {
            const text = item.textContent.toLowerCase();
            item.style.display = text.includes(search) ? 'flex' : 'none';
        });
    });
}

// Show Patient Details in Sidebar
function showPatientDetails(patient) {
    const sidebar = document.getElementById('patient-sidebar');
    const overlay = document.getElementById('sidebar-overlay');
    const title = document.getElementById('modal-title');
    const body = document.getElementById('modal-body');

    title.textContent = patient.name;

    const patientAppointments = allAppointments.filter(apt => apt.patient_id === patient.patient_id);

    body.innerHTML = `
        <div class="info-grid">
            <div class="info-item">
                <div class="info-label">Patient ID</div>
                <div class="info-value">${patient.patient_id}</div>
            </div>
            <div class="info-item">
                <div class="info-label">Age</div>
                <div class="info-value">${patient.age} years old</div>
            </div>
            <div class="info-item">
                <div class="info-label">Date of Birth</div>
                <div class="info-value">${formatDate(patient.dob)}</div>
            </div>
            <div class="info-item">
                <div class="info-label">Language</div>
                <div class="info-value">${patient.language}</div>
            </div>
            <div class="info-item">
                <div class="info-label">Email</div>
                <div class="info-value">${patient.email}</div>
            </div>
            <div class="info-item">
                <div class="info-label">Phone</div>
                <div class="info-value">${patient.phone}</div>
            </div>
            <div class="info-item">
                <div class="info-label">MRN</div>
                <div class="info-value">${patient.mrn}</div>
            </div>
            <div class="info-item">
                <div class="info-label">Insurance Plan</div>
                <div class="info-value">${patient.insurance_plan}</div>
            </div>
        </div>

        <div class="section-title">
            <i class="fas fa-notes-medical"></i> Medical History
        </div>
        <div class="medical-history-box">
            ${patient.medical_history}
        </div>

        <div class="section-title">
            <i class="fas fa-calendar-check"></i> Appointments (${patientAppointments.length})
        </div>
        <div class="appointments-list">
            ${patientAppointments.length > 0 ? patientAppointments.map(apt => `
                <div class="appointment-item">
                    <strong>${formatDate(apt.date)} at ${apt.time}</strong><br>
                    ${apt.provider} - ${apt.type}<br>
                    <small>${apt.location}</small><br>
                    <span class="badge badge-${apt.status}">${apt.status}</span>
                </div>
            `).join('') : '<p style="color: #7f8c8d; padding: 15px;">No appointments scheduled</p>'}
        </div>
    `;

    sidebar.classList.add('active');
    overlay.classList.add('active');
}

function closeSidebar() {
    document.getElementById('patient-sidebar').classList.remove('active');
    document.getElementById('sidebar-overlay').classList.remove('active');
}

// Show Appointment Details in Sidebar
function showAppointmentDetails(apt, patient) {
    const sidebar = document.getElementById('patient-sidebar');
    const overlay = document.getElementById('sidebar-overlay');
    const title = document.getElementById('modal-title');
    const body = document.getElementById('modal-body');

    title.textContent = `Appointment: ${apt.appointment_id}`;

    body.innerHTML = `
        <div class="info-grid">
            <div class="info-item">
                <div class="info-label">Appointment ID</div>
                <div class="info-value">${apt.appointment_id}</div>
            </div>
            <div class="info-item">
                <div class="info-label">Status</div>
                <div class="info-value"><span class="badge badge-${apt.status}">${apt.status}</span></div>
            </div>
            <div class="info-item">
                <div class="info-label">Date</div>
                <div class="info-value">${formatDate(apt.date)}</div>
            </div>
            <div class="info-item">
                <div class="info-label">Time</div>
                <div class="info-value">${apt.time}</div>
            </div>
            <div class="info-item">
                <div class="info-label">Provider</div>
                <div class="info-value">${apt.provider}</div>
            </div>
            <div class="info-item">
                <div class="info-label">Type</div>
                <div class="info-value">${apt.type}</div>
            </div>
        </div>

        <div class="info-item" style="grid-column: 1 / -1; margin-top: 10px;">
            <div class="info-label">Location</div>
            <div class="info-value">${apt.location}</div>
        </div>

        <div class="section-title" style="margin-top: 25px;">
            <i class="fas fa-user"></i> Patient Information
        </div>
        ${patient ? `
            <div class="info-grid">
                <div class="info-item">
                    <div class="info-label">Patient Name</div>
                    <div class="info-value">${patient.name}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Patient ID</div>
                    <div class="info-value">${patient.patient_id}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Age</div>
                    <div class="info-value">${patient.age} years old</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Language</div>
                    <div class="info-value">${patient.language}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Phone</div>
                    <div class="info-value">${patient.phone}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Email</div>
                    <div class="info-value">${patient.email}</div>
                </div>
            </div>
            <div class="section-title">
                <i class="fas fa-notes-medical"></i> Medical History
            </div>
            <div class="medical-history-box">
                ${patient.medical_history}
            </div>
        ` : `<p style="color: #7f8c8d; padding: 15px;">Patient information not available</p>`}
    `;

    sidebar.classList.add('active');
    overlay.classList.add('active');
}

// Render Appointments
function renderAppointments() {
    const grid = document.getElementById('appointments-grid');
    grid.innerHTML = '';
    grid.className = 'patients-list'; // Use same style as patients list

    allAppointments.forEach(apt => {
        const patient = allPatients.find(p => p.patient_id === apt.patient_id);
        const item = document.createElement('div');
        item.className = 'patient-list-item';
        item.onclick = () => showAppointmentDetails(apt, patient);

        // Use calendar icon for appointments
        const icon = '📅';

        item.innerHTML = `
            <div class="patient-avatar">${icon}</div>
            <div class="patient-name">${patient ? patient.name : apt.patient_id} - ${formatDate(apt.date)}</div>
            <div class="patient-id-badge">${apt.appointment_id}</div>
        `;

        grid.appendChild(item);
    });
}

// Render Facilities
function renderFacilities() {
    const grid = document.getElementById('facilities-grid');
    grid.innerHTML = '';

    const facilities = {};
    allAppointments.forEach(apt => {
        const facility = apt.location.split(' - ')[0];
        if (!facilities[facility]) {
            facilities[facility] = [];
        }
        facilities[facility].push(apt);
    });

    Object.entries(facilities).forEach(([facility, appointments]) => {
        const card = document.createElement('div');
        card.className = 'card';

        card.innerHTML = `
            <div class="card-header">
                <div class="card-title">${facility}</div>
                <div class="card-icon icon-purple">
                    <i class="fas fa-building"></i>
                </div>
            </div>
            <div class="card-body">
                <p><strong>Total Appointments:</strong> ${appointments.length}</p>
                <p><strong>Providers:</strong> ${[...new Set(appointments.map(a => a.provider))].length}</p>
                <p style="margin-top: 10px; font-size: 13px;">
                    ${[...new Set(appointments.map(a => a.provider))].slice(0, 3).join(', ')}
                    ${[...new Set(appointments.map(a => a.provider))].length > 3 ? '...' : ''}
                </p>
            </div>
        `;

        grid.appendChild(card);
    });
}

// Render Doctors
function renderDoctors() {
    const grid = document.getElementById('doctors-grid');
    grid.innerHTML = '';

    const doctors = {};
    allAppointments.forEach(apt => {
        if (!doctors[apt.provider]) {
            doctors[apt.provider] = {
                appointments: [],
                locations: new Set()
            };
        }
        doctors[apt.provider].appointments.push(apt);
        doctors[apt.provider].locations.add(apt.location.split(' - ')[0]);
    });

    // Add provider languages from slots
    const providerLanguages = {};
    allSlots.forEach(slot => {
        if (slot.provider_language) {
            providerLanguages[slot.provider] = slot.provider_language;
        }
    });

    Object.entries(doctors).forEach(([doctor, data]) => {
        const card = document.createElement('div');
        card.className = 'card';

        card.innerHTML = `
            <div class="card-header">
                <div class="card-title">${doctor}</div>
                <div class="card-icon icon-blue">
                    <i class="fas fa-user-md"></i>
                </div>
            </div>
            <div class="card-body">
                <p><strong>Languages:</strong> ${providerLanguages[doctor] || 'English'}</p>
                <p><strong>Appointments:</strong> ${data.appointments.length}</p>
                <p><strong>Facilities:</strong> ${Array.from(data.locations).length}</p>
                <p style="margin-top: 10px; font-size: 12px; color: #7f8c8d;">
                    ${Array.from(data.locations).join(', ')}
                </p>
            </div>
        `;

        grid.appendChild(card);
    });
}

// Render Availability
function renderAvailability() {
    const grid = document.getElementById('availability-grid');
    grid.innerHTML = '';

    allSlots.filter(slot => slot.available).forEach(slot => {
        const card = document.createElement('div');
        card.className = 'card';

        card.innerHTML = `
            <div class="card-header">
                <div class="card-title">${slot.provider}</div>
                <div class="card-icon icon-green">
                    <i class="fas fa-clock"></i>
                </div>
            </div>
            <div class="card-body">
                <p><strong>Date:</strong> ${formatDate(slot.date)}</p>
                <p><strong>Time:</strong> ${slot.time}</p>
                <p><strong>Location:</strong> ${slot.location}</p>
                <p><strong>Languages:</strong> ${slot.provider_language || 'English'}</p>
                <span class="badge badge-confirmed">Available</span>
            </div>
        `;

        grid.appendChild(card);
    });
}

// Render Logs
function renderLogs() {
    const logsList = document.getElementById('logs-list');

    const logs = [
        { time: '2 min ago', action: 'Appointment rescheduled', details: 'APT-101 moved to June 27' },
        { time: '15 min ago', action: 'New patient registered', details: 'Emma Thompson (PAT-006)' },
        { time: '1 hour ago', action: 'Appointment confirmed', details: 'APT-301 with Dr. Rodriguez' },
        { time: '2 hours ago', action: 'Slot added', details: 'Dr. Chen - July 8, 9:00 AM' },
        { time: '3 hours ago', action: 'Patient record updated', details: 'Maria Garcia (PAT-003)' }
    ];

    logsList.innerHTML = logs.map(log => `
        <div style="padding: 15px; border-bottom: 1px solid #e0e0e0;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                <strong>${log.action}</strong>
                <span style="color: #95a5a6; font-size: 13px;">${log.time}</span>
            </div>
            <div style="color: #7f8c8d; font-size: 14px;">${log.details}</div>
        </div>
    `).join('');
}

// Populate Filters
function populateFilters() {
    const facilitySelect = document.getElementById('filter-facility');
    const doctorSelect = document.getElementById('filter-doctor');

    const facilities = [...new Set(allAppointments.map(apt => apt.location.split(' - ')[0]))];
    facilities.forEach(facility => {
        const option = document.createElement('option');
        option.value = facility;
        option.textContent = facility;
        facilitySelect.appendChild(option);
    });

    const doctors = [...new Set(allAppointments.map(apt => apt.provider))];
    doctors.forEach(doctor => {
        const option = document.createElement('option');
        option.value = doctor;
        option.textContent = doctor;
        doctorSelect.appendChild(option);
    });

    // Populate availability slot filters
    const slotDoctorSelect = document.getElementById('filter-slot-doctor');
    const slotLocationSelect = document.getElementById('filter-slot-location');

    const slotDoctors = [...new Set(allSlots.map(slot => slot.provider))];
    slotDoctors.forEach(doctor => {
        const option = document.createElement('option');
        option.value = doctor;
        option.textContent = doctor;
        slotDoctorSelect.appendChild(option);
    });

    const slotLocations = [...new Set(allSlots.map(slot => slot.location.split(' - ')[0]))];
    slotLocations.forEach(location => {
        const option = document.createElement('option');
        option.value = location;
        option.textContent = location;
        slotLocationSelect.appendChild(option);
    });
}

// Apply Filters
function applyFilters() {
    const patientName = document.getElementById('filter-patient-name').value.toLowerCase();
    const dateFrom = document.getElementById('filter-date-from').value;
    const dateTo = document.getElementById('filter-date-to').value;
    const facility = document.getElementById('filter-facility').value;
    const doctor = document.getElementById('filter-doctor').value;

    let filtered = [...allAppointments];

    if (patientName) {
        filtered = filtered.filter(apt => {
            const patient = allPatients.find(p => p.patient_id === apt.patient_id);
            return patient && patient.name.toLowerCase().includes(patientName);
        });
    }
    if (dateFrom) {
        filtered = filtered.filter(apt => apt.date >= dateFrom);
    }
    if (dateTo) {
        filtered = filtered.filter(apt => apt.date <= dateTo);
    }
    if (facility) {
        filtered = filtered.filter(apt => apt.location.includes(facility));
    }
    if (doctor) {
        filtered = filtered.filter(apt => apt.provider === doctor);
    }

    // Re-render with filtered data
    const grid = document.getElementById('appointments-grid');
    grid.innerHTML = '';
    grid.className = 'patients-list'; // Use same style as patients list

    filtered.forEach(apt => {
        const patient = allPatients.find(p => p.patient_id === apt.patient_id);
        const item = document.createElement('div');
        item.className = 'patient-list-item';
        item.onclick = () => showAppointmentDetails(apt, patient);

        const icon = '📅';

        item.innerHTML = `
            <div class="patient-avatar">${icon}</div>
            <div class="patient-name">${patient ? patient.name : apt.patient_id} - ${formatDate(apt.date)}</div>
            <div class="patient-id-badge">${apt.appointment_id}</div>
        `;

        grid.appendChild(item);
    });
}

// Add real-time patient name filter for appointments
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => {
        const patientNameFilter = document.getElementById('filter-patient-name');
        if (patientNameFilter) {
            patientNameFilter.addEventListener('input', applyFilters);
        }
    }, 1000);
});

// Refresh Data
function refreshData() {
    loadAllData();
}

// Helper: Format Date
function formatDate(dateStr) {
    const date = new Date(dateStr + 'T00:00:00');
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

// Apply Availability Filters
function applyAvailabilityFilters() {
    const dateFrom = document.getElementById('filter-slot-date-from').value;
    const dateTo = document.getElementById('filter-slot-date-to').value;
    const doctor = document.getElementById('filter-slot-doctor').value;
    const location = document.getElementById('filter-slot-location').value;

    let filtered = allSlots.filter(slot => slot.available);

    if (dateFrom) {
        filtered = filtered.filter(slot => slot.date >= dateFrom);
    }
    if (dateTo) {
        filtered = filtered.filter(slot => slot.date <= dateTo);
    }
    if (doctor) {
        filtered = filtered.filter(slot => slot.provider === doctor);
    }
    if (location) {
        filtered = filtered.filter(slot => slot.location.includes(location));
    }

    // Re-render with filtered data
    const grid = document.getElementById('availability-grid');
    grid.innerHTML = '';

    filtered.forEach(slot => {
        const card = document.createElement('div');
        card.className = 'card';

        card.innerHTML = `
            <div class="card-header">
                <div class="card-title">${slot.provider}</div>
                <div class="card-icon icon-green">
                    <i class="fas fa-clock"></i>
                </div>
            </div>
            <div class="card-body">
                <p><strong>Date:</strong> ${formatDate(slot.date)}</p>
                <p><strong>Time:</strong> ${slot.time}</p>
                <p><strong>Location:</strong> ${slot.location}</p>
                <p><strong>Languages:</strong> ${slot.provider_language || 'English'}</p>
                <span class="badge badge-confirmed">Available</span>
            </div>
        `;

        grid.appendChild(card);
    });

    // Show message if no results
    if (filtered.length === 0) {
        grid.innerHTML = '<div style="text-align: center; padding: 40px; color: white; font-size: 18px;">No available slots match your filters</div>';
    }
}

// Clear Availability Filters
function clearAvailabilityFilters() {
    document.getElementById('filter-slot-date-from').value = '';
    document.getElementById('filter-slot-date-to').value = '';
    document.getElementById('filter-slot-doctor').value = '';
    document.getElementById('filter-slot-location').value = '';
    renderAvailability();
}
