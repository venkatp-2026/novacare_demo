"""Data manager for handling in-memory data storage with default and working copies."""
import os
import json
import copy
from pathlib import Path
from typing import Dict, List, Any, Optional


class DataManager:
    """Manages data storage with default and working copies in memory (Vercel-compatible)."""
    
    def __init__(self, excel_file: str = "data/novacare_data.xlsx"):
        self.excel_file = Path(excel_file)
        self.patients: Dict[str, Dict[str, Any]] = {}
        self.appointments: Dict[str, List[Dict[str, Any]]] = {}
        self.slots: Dict[str, Dict[str, Any]] = {}
        self.doctors: Dict[str, Dict[str, Any]] = {}
        self.doctor_appointments: Dict[str, List[Dict[str, Any]]] = {}
        self._default_data: Optional[Dict[str, Any]] = None
        
    def initialize_with_defaults(self) -> None:
        """Initialize in-memory data storage with defaults (no file I/O)."""
        # Store default data for resets
        self._default_data = self._get_default_data()
        print(f"Initialized in-memory data storage")
    
    def _get_default_data(self) -> Dict[str, Any]:
        """Get the default seed data."""
        return {
            "patients": {
                "PAT-001": {
                    "patient_id": "PAT-001",
                    "name": "Jane Smith",
                    "dob": "1985-03-15",
                    "age": 41,
                    "language": "English",
                    "email": "jane.smith@email.com",
                    "phone": "(555) 123-4567",
                    "mrn": "MRN-2001",
                    "insurance_member_id": "INS-123456",
                    "insurance_plan": "Blue Cross PPO",
                    "medical_history": "Type 2 Diabetes diagnosed 2020. Requires HbA1c monitoring every 3 months. Last review: 2026-03-15. Next due: 2026-06-15. Currently on Metformin 500mg twice daily. Blood glucose well controlled.",
                    "status": "active"
                },
                "PAT-002": {
                    "patient_id": "PAT-002",
                    "name": "Robert Johnson",
                    "dob": "1978-11-22",
                    "age": 47,
                    "language": "English",
                    "email": "robert.johnson@email.com",
                    "phone": "(555) 234-5678",
                    "mrn": "MRN-2002",
                    "insurance_member_id": "INS-234567",
                    "insurance_plan": "Aetna HMO",
                    "medical_history": "Hypertension managed with lifestyle modifications. Requires BP monitoring monthly. Last review: 2026-05-10. Currently on Lisinopril 10mg daily. Physical therapy for chronic lower back pain ongoing.",
                    "status": "active"
                },
                "PAT-003": {
                    "patient_id": "PAT-003",
                    "name": "Maria Garcia",
                    "dob": "1992-07-08",
                    "age": 33,
                    "language": "Spanish",
                    "email": "maria.garcia@email.com",
                    "phone": "(555) 345-6789",
                    "mrn": "MRN-2003",
                    "insurance_member_id": "INS-345678",
                    "insurance_plan": "Cigna PPO",
                    "medical_history": "Type 1 Diabetes since age 12. Insulin pump user. Requires endocrinology follow-up every 3 months. Last A1C: 7.2% (2026-04-20). Nutrition counseling ongoing for carb counting. Next review: 2026-07-20.",
                    "status": "active"
                },
                "PAT-004": {
                    "patient_id": "PAT-004",
                    "name": "John Smith",
                    "dob": "1990-05-12",
                    "age": 36,
                    "language": "English",
                    "email": "john.smith.1990@email.com",
                    "phone": "(555) 456-7890",
                    "mrn": "MRN-2004",
                    "insurance_member_id": "INS-456789",
                    "insurance_plan": "United Healthcare",
                    "medical_history": "Annual physical exam - healthy adult. No chronic conditions. Preventive care up to date. Last physical: 2025-06-28. Recommended annual screening due 2026-06-28.",
                    "status": "active"
                },
                "PAT-005": {
                    "patient_id": "PAT-005",
                    "name": "John Smith",
                    "dob": "1990-05-12",
                    "age": 36,
                    "language": "English",
                    "email": "john.smith.alt@email.com",
                    "phone": "(555) 567-8901",
                    "mrn": "MRN-2005",
                    "insurance_member_id": "INS-567890",
                    "insurance_plan": "Kaiser Permanente",
                    "medical_history": "Post-myocardial infarction (MI) February 2026. Cardiac rehabilitation ongoing. Requires cardiology follow-up every 3 months. Currently on aspirin, atorvastatin, metoprolol. Last echo: normal EF 55%. Next cardiology visit: 2026-07-12.",
                    "status": "active"
                },
                "PAT-006": {
                    "patient_id": "PAT-006",
                    "name": "Emma Thompson",
                    "dob": "2018-03-20",
                    "age": 8,
                    "language": "English",
                    "email": "parent.thompson@email.com",
                    "phone": "(555) 678-9012",
                    "mrn": "MRN-2006",
                    "insurance_member_id": "INS-678901",
                    "insurance_plan": "Blue Cross PPO",
                    "medical_history": "Pediatric asthma diagnosed age 5. Well-controlled on daily inhaled corticosteroids (Flovent 44mcg). Rescue inhaler (albuterol) as needed. Last exacerbation: 8 months ago. Annual asthma action plan review due. Pediatric follow-up every 6 months.",
                    "status": "active"
                },
            },
            "appointments": {
                "PAT-001": [
                    {
                        "appointment_id": "APT-101",
                        "patient_id": "PAT-001",
                        "date": "2026-06-20",
                        "time": "10:00 AM",
                        "provider": "Dr. Williams",
                        "type": "Follow-up",
                        "location": "Main Campus - Room 204",
                        "status": "confirmed"
                    },
                    {
                        "appointment_id": "APT-102",
                        "patient_id": "PAT-001",
                        "date": "2026-07-15",
                        "time": "2:30 PM",
                        "provider": "Dr. Chen",
                        "type": "Annual Check-up",
                        "location": "North Clinic - Suite 301",
                        "status": "confirmed"
                    },
                    {
                        "appointment_id": "APT-103",
                        "patient_id": "PAT-001",
                        "date": "2026-08-10",
                        "time": "9:00 AM",
                        "provider": "Dr. Williams",
                        "type": "Lab Results Review",
                        "location": "Main Campus - Room 204",
                        "status": "confirmed"
                    }
                ],
                "PAT-002": [
                    {
                        "appointment_id": "APT-201",
                        "patient_id": "PAT-002",
                        "date": "2026-06-22",
                        "time": "11:30 AM",
                        "provider": "Dr. Patel",
                        "type": "Consultation",
                        "location": "West Building - Office 102",
                        "status": "confirmed"
                    },
                    {
                        "appointment_id": "APT-202",
                        "patient_id": "PAT-002",
                        "date": "2026-07-05",
                        "time": "3:00 PM",
                        "provider": "Dr. Lee",
                        "type": "Physical Therapy",
                        "location": "Therapy Center - Room A",
                        "status": "confirmed"
                    }
                ],
                "PAT-003": [
                    {
                        "appointment_id": "APT-301",
                        "patient_id": "PAT-003",
                        "date": "2026-06-25",
                        "time": "1:00 PM",
                        "provider": "Dr. Rodriguez",
                        "type": "Diabetes Management",
                        "location": "Endocrinology Wing - Room 5",
                        "status": "confirmed"
                    },
                    {
                        "appointment_id": "APT-302",
                        "patient_id": "PAT-003",
                        "date": "2026-07-20",
                        "time": "10:30 AM",
                        "provider": "Dr. Kim",
                        "type": "Nutrition Counseling",
                        "location": "Wellness Center - Suite 210",
                        "status": "confirmed"
                    }
                ],
                "PAT-004": [
                    {
                        "appointment_id": "APT-400",
                        "patient_id": "PAT-004",
                        "date": "2026-06-25",
                        "time": "11:00 AM",
                        "provider": "Dr. Brown",
                        "type": "Routine Check-up",
                        "location": "Main Campus - Room 105",
                        "status": "confirmed"
                    },
                    {
                        "appointment_id": "APT-401",
                        "patient_id": "PAT-004",
                        "date": "2026-06-28",
                        "time": "9:00 AM",
                        "provider": "Dr. Brown",
                        "type": "Annual Physical",
                        "location": "Main Campus - Room 105",
                        "status": "confirmed"
                    }
                ],
                "PAT-005": [
                    {
                        "appointment_id": "APT-501",
                        "patient_id": "PAT-005",
                        "date": "2026-07-12",
                        "time": "2:00 PM",
                        "provider": "Dr. Martinez",
                        "type": "Cardiology Follow-up",
                        "location": "Heart Center - Room 3",
                        "status": "confirmed"
                    }
                ],
                "PAT-006": [
                    {
                        "appointment_id": "APT-601",
                        "patient_id": "PAT-006",
                        "date": "2026-06-24",
                        "time": "4:00 PM",
                        "provider": "Dr. Anderson",
                        "type": "Pediatric Asthma Check",
                        "location": "Pediatrics Wing - Room 12",
                        "status": "confirmed"
                    },
                    {
                        "appointment_id": "APT-602",
                        "patient_id": "PAT-006",
                        "date": "2026-12-20",
                        "time": "3:30 PM",
                        "provider": "Dr. Anderson",
                        "type": "6-Month Follow-up",
                        "location": "Pediatrics Wing - Room 12",
                        "status": "scheduled"
                    }
                ]
            },
            "slots": {
                # June 2026 - Remaining slots
                "SLOT-001": {"slot_id": "SLOT-001", "date": "2026-06-25", "time": "2:00 PM", "provider": "Dr. Williams", "provider_language": "English", "location": "Main Campus - Room 204", "available": True},
                "SLOT-002": {"slot_id": "SLOT-002", "date": "2026-06-26", "time": "9:30 AM", "provider": "Dr. Chen", "provider_language": "English, Mandarin", "location": "North Clinic - Suite 301", "available": True},
                "SLOT-003": {"slot_id": "SLOT-003", "date": "2026-06-27", "time": "11:00 AM", "provider": "Dr. Williams", "provider_language": "English", "location": "Main Campus - Room 204", "available": True},
                "SLOT-004": {"slot_id": "SLOT-004", "date": "2026-06-28", "time": "3:30 PM", "provider": "Dr. Patel", "provider_language": "English, Hindi, Gujarati", "location": "West Building - Office 102", "available": True},

                # July 2026 - Dr. Williams slots (3 slots)
                "SLOT-101": {"slot_id": "SLOT-101", "date": "2026-07-02", "time": "9:00 AM", "provider": "Dr. Williams", "provider_language": "English", "location": "Main Campus - Room 204", "available": True},
                "SLOT-102": {"slot_id": "SLOT-102", "date": "2026-07-16", "time": "2:00 PM", "provider": "Dr. Williams", "provider_language": "English", "location": "Main Campus - Room 204", "available": True},
                "SLOT-103": {"slot_id": "SLOT-103", "date": "2026-07-23", "time": "10:30 AM", "provider": "Dr. Williams", "provider_language": "English", "location": "Main Campus - Room 204", "available": True},

                # July 2026 - Dr. Chen slots (3 slots)
                "SLOT-104": {"slot_id": "SLOT-104", "date": "2026-07-06", "time": "11:00 AM", "provider": "Dr. Chen", "provider_language": "English, Mandarin", "location": "North Clinic - Suite 301", "available": True},
                "SLOT-105": {"slot_id": "SLOT-105", "date": "2026-07-14", "time": "3:30 PM", "provider": "Dr. Chen", "provider_language": "English, Mandarin", "location": "North Clinic - Suite 301", "available": True},
                "SLOT-106": {"slot_id": "SLOT-106", "date": "2026-07-22", "time": "9:30 AM", "provider": "Dr. Chen", "provider_language": "English, Mandarin", "location": "North Clinic - Suite 301", "available": True},

                # August 2026 - Dr. Williams slots (3 slots)
                "SLOT-201": {"slot_id": "SLOT-201", "date": "2026-08-04", "time": "8:30 AM", "provider": "Dr. Williams", "provider_language": "English", "location": "Main Campus - Room 204", "available": True},
                "SLOT-202": {"slot_id": "SLOT-202", "date": "2026-08-13", "time": "1:00 PM", "provider": "Dr. Williams", "provider_language": "English", "location": "Main Campus - Room 204", "available": True},
                "SLOT-203": {"slot_id": "SLOT-203", "date": "2026-08-25", "time": "3:00 PM", "provider": "Dr. Williams", "provider_language": "English", "location": "Main Campus - Room 204", "available": True},

                # August 2026 - Dr. Chen slots (3 slots)
                "SLOT-204": {"slot_id": "SLOT-204", "date": "2026-08-06", "time": "10:00 AM", "provider": "Dr. Chen", "provider_language": "English, Mandarin", "location": "North Clinic - Suite 301", "available": True},
                "SLOT-205": {"slot_id": "SLOT-205", "date": "2026-08-17", "time": "2:30 PM", "provider": "Dr. Chen", "provider_language": "English, Mandarin", "location": "North Clinic - Suite 301", "available": True},
                "SLOT-206": {"slot_id": "SLOT-206", "date": "2026-08-27", "time": "11:30 AM", "provider": "Dr. Chen", "provider_language": "English, Mandarin", "location": "North Clinic - Suite 301", "available": True},

                # September 2026 - Dr. Williams slots (3 slots)
                "SLOT-301": {"slot_id": "SLOT-301", "date": "2026-09-03", "time": "9:30 AM", "provider": "Dr. Williams", "provider_language": "English", "location": "Main Campus - Room 204", "available": True},
                "SLOT-302": {"slot_id": "SLOT-302", "date": "2026-09-15", "time": "1:30 PM", "provider": "Dr. Williams", "provider_language": "English", "location": "Main Campus - Room 204", "available": True},
                "SLOT-303": {"slot_id": "SLOT-303", "date": "2026-09-22", "time": "11:00 AM", "provider": "Dr. Williams", "provider_language": "English", "location": "Main Campus - Room 204", "available": True},

                # September 2026 - Dr. Chen slots (3 slots)
                "SLOT-304": {"slot_id": "SLOT-304", "date": "2026-09-08", "time": "10:30 AM", "provider": "Dr. Chen", "provider_language": "English, Mandarin", "location": "North Clinic - Suite 301", "available": True},
                "SLOT-305": {"slot_id": "SLOT-305", "date": "2026-09-16", "time": "3:00 PM", "provider": "Dr. Chen", "provider_language": "English, Mandarin", "location": "North Clinic - Suite 301", "available": True},
                "SLOT-306": {"slot_id": "SLOT-306", "date": "2026-09-29", "time": "9:00 AM", "provider": "Dr. Chen", "provider_language": "English, Mandarin", "location": "North Clinic - Suite 301", "available": True},

                # Other providers (keeping original slots)
                "SLOT-005": {"slot_id": "SLOT-005", "date": "2026-07-01", "time": "8:00 AM", "provider": "Dr. Lee", "provider_language": "English, Korean", "location": "Therapy Center - Room A", "available": True},
                "SLOT-006": {"slot_id": "SLOT-006", "date": "2026-07-02", "time": "1:30 PM", "provider": "Dr. Rodriguez", "provider_language": "English, Spanish", "location": "Endocrinology Wing - Room 5", "available": True},
                "SLOT-007": {"slot_id": "SLOT-007", "date": "2026-07-03", "time": "10:00 AM", "provider": "Dr. Kim", "provider_language": "English, Korean", "location": "Wellness Center - Suite 210", "available": True},
                "SLOT-010": {"slot_id": "SLOT-010", "date": "2026-07-10", "time": "2:30 PM", "provider": "Dr. Patel", "provider_language": "English, Hindi, Gujarati", "location": "West Building - Office 102", "available": True},
            },
            "doctors": {
                "DOC-001": {
                    "doctor_id": "DOC-001",
                    "name": "Dr. Sarah Williams",
                    "dob": "1978-04-15",
                    "specialty": "Primary Care",
                    "languages": "English",
                    "email": "s.williams@novacare.com",
                    "phone": "(555) 100-2001",
                    "npi": "1234567890",
                    "license": "MD-12345",
                    "location": "Main Campus - Room 204",
                    "status": "active"
                },
                "DOC-002": {
                    "doctor_id": "DOC-002",
                    "name": "Dr. Michael Chen",
                    "dob": "1982-09-22",
                    "specialty": "Internal Medicine",
                    "languages": "English, Mandarin",
                    "email": "m.chen@novacare.com",
                    "phone": "(555) 100-2002",
                    "npi": "2345678901",
                    "license": "MD-23456",
                    "location": "North Clinic - Suite 301",
                    "status": "active"
                }
            },
            "doctor_appointments": {
                "DOC-001": [
                    {
                        "appointment_id": "APT-101",
                        "doctor_id": "DOC-001",
                        "patient_id": "PAT-001",
                        "patient_name": "Jane Smith",
                        "date": "2026-06-20",
                        "time": "10:00 AM",
                        "type": "Follow-up",
                        "location": "Main Campus - Room 204",
                        "status": "confirmed"
                    },
                    {
                        "appointment_id": "APT-1001",
                        "doctor_id": "DOC-001",
                        "patient_id": "PAT-002",
                        "patient_name": "Robert Johnson",
                        "date": "2026-07-05",
                        "time": "9:00 AM",
                        "type": "Follow-up",
                        "location": "Main Campus - Room 204",
                        "status": "confirmed"
                    },
                    {
                        "appointment_id": "APT-1002",
                        "doctor_id": "DOC-001",
                        "patient_id": "PAT-004",
                        "patient_name": "John Smith",
                        "date": "2026-07-12",
                        "time": "11:00 AM",
                        "type": "Consultation",
                        "location": "Main Campus - Room 204",
                        "status": "confirmed"
                    },
                    {
                        "appointment_id": "APT-1003",
                        "doctor_id": "DOC-001",
                        "patient_id": "PAT-003",
                        "patient_name": "Maria Garcia",
                        "date": "2026-07-18",
                        "time": "2:00 PM",
                        "type": "Check-up",
                        "location": "Main Campus - Room 204",
                        "status": "confirmed"
                    },
                    {
                        "appointment_id": "APT-1004",
                        "doctor_id": "DOC-001",
                        "patient_id": "PAT-005",
                        "patient_name": "John Smith",
                        "date": "2026-07-25",
                        "time": "3:30 PM",
                        "type": "Follow-up",
                        "location": "Main Campus - Room 204",
                        "status": "confirmed"
                    },
                    {
                        "appointment_id": "APT-1005",
                        "doctor_id": "DOC-001",
                        "patient_id": "PAT-001",
                        "patient_name": "Jane Smith",
                        "date": "2026-08-03",
                        "time": "10:00 AM",
                        "type": "Lab Results Review",
                        "location": "Main Campus - Room 204",
                        "status": "confirmed"
                    },
                    {
                        "appointment_id": "APT-103",
                        "doctor_id": "DOC-001",
                        "patient_id": "PAT-001",
                        "patient_name": "Jane Smith",
                        "date": "2026-08-10",
                        "time": "9:00 AM",
                        "type": "Lab Results Review",
                        "location": "Main Campus - Room 204",
                        "status": "confirmed"
                    },
                    {
                        "appointment_id": "APT-1006",
                        "doctor_id": "DOC-001",
                        "patient_id": "PAT-006",
                        "patient_name": "Emma Thompson",
                        "date": "2026-08-15",
                        "time": "4:00 PM",
                        "type": "Pediatric Check",
                        "location": "Main Campus - Room 204",
                        "status": "confirmed"
                    },
                    {
                        "appointment_id": "APT-1007",
                        "doctor_id": "DOC-001",
                        "patient_id": "PAT-002",
                        "patient_name": "Robert Johnson",
                        "date": "2026-08-22",
                        "time": "11:30 AM",
                        "type": "Consultation",
                        "location": "Main Campus - Room 204",
                        "status": "confirmed"
                    },
                    {
                        "appointment_id": "APT-1008",
                        "doctor_id": "DOC-001",
                        "patient_id": "PAT-004",
                        "patient_name": "John Smith",
                        "date": "2026-09-02",
                        "time": "9:00 AM",
                        "type": "Annual Physical",
                        "location": "Main Campus - Room 204",
                        "status": "scheduled"
                    },
                    {
                        "appointment_id": "APT-1009",
                        "doctor_id": "DOC-001",
                        "patient_id": "PAT-003",
                        "patient_name": "Maria Garcia",
                        "date": "2026-09-10",
                        "time": "1:00 PM",
                        "type": "Follow-up",
                        "location": "Main Campus - Room 204",
                        "status": "scheduled"
                    },
                    {
                        "appointment_id": "APT-1010",
                        "doctor_id": "DOC-001",
                        "patient_id": "PAT-005",
                        "patient_name": "John Smith",
                        "date": "2026-09-18",
                        "time": "2:30 PM",
                        "type": "Cardiology Follow-up",
                        "location": "Main Campus - Room 204",
                        "status": "scheduled"
                    },
                    {
                        "appointment_id": "APT-1011",
                        "doctor_id": "DOC-001",
                        "patient_id": "PAT-001",
                        "patient_name": "Jane Smith",
                        "date": "2026-09-25",
                        "time": "10:00 AM",
                        "type": "Diabetes Review",
                        "location": "Main Campus - Room 204",
                        "status": "scheduled"
                    }
                ],
                "DOC-002": [
                    {
                        "appointment_id": "APT-601",
                        "doctor_id": "DOC-002",
                        "patient_id": "PAT-006",
                        "patient_name": "Emma Thompson",
                        "date": "2026-06-24",
                        "time": "4:00 PM",
                        "type": "Pediatric Asthma Check",
                        "location": "North Clinic - Suite 301",
                        "status": "confirmed"
                    },
                    {
                        "appointment_id": "APT-2001",
                        "doctor_id": "DOC-002",
                        "patient_id": "PAT-002",
                        "patient_name": "Robert Johnson",
                        "date": "2026-07-08",
                        "time": "9:30 AM",
                        "type": "Internal Medicine Consultation",
                        "location": "North Clinic - Suite 301",
                        "status": "confirmed"
                    },
                    {
                        "appointment_id": "APT-102",
                        "doctor_id": "DOC-002",
                        "patient_id": "PAT-001",
                        "patient_name": "Jane Smith",
                        "date": "2026-07-15",
                        "time": "2:30 PM",
                        "type": "Annual Check-up",
                        "location": "North Clinic - Suite 301",
                        "status": "confirmed"
                    },
                    {
                        "appointment_id": "APT-2002",
                        "doctor_id": "DOC-002",
                        "patient_id": "PAT-003",
                        "patient_name": "Maria Garcia",
                        "date": "2026-07-20",
                        "time": "10:00 AM",
                        "type": "Diabetes Management",
                        "location": "North Clinic - Suite 301",
                        "status": "confirmed"
                    },
                    {
                        "appointment_id": "APT-2003",
                        "doctor_id": "DOC-002",
                        "patient_id": "PAT-005",
                        "patient_name": "John Smith",
                        "date": "2026-07-28",
                        "time": "3:00 PM",
                        "type": "Cardiology Consultation",
                        "location": "North Clinic - Suite 301",
                        "status": "confirmed"
                    },
                    {
                        "appointment_id": "APT-2004",
                        "doctor_id": "DOC-002",
                        "patient_id": "PAT-004",
                        "patient_name": "John Smith",
                        "date": "2026-08-05",
                        "time": "11:00 AM",
                        "type": "Follow-up",
                        "location": "North Clinic - Suite 301",
                        "status": "confirmed"
                    },
                    {
                        "appointment_id": "APT-2005",
                        "doctor_id": "DOC-002",
                        "patient_id": "PAT-006",
                        "patient_name": "Emma Thompson",
                        "date": "2026-08-12",
                        "time": "4:30 PM",
                        "type": "Pediatric Follow-up",
                        "location": "North Clinic - Suite 301",
                        "status": "confirmed"
                    },
                    {
                        "appointment_id": "APT-2006",
                        "doctor_id": "DOC-002",
                        "patient_id": "PAT-001",
                        "patient_name": "Jane Smith",
                        "date": "2026-08-20",
                        "time": "1:00 PM",
                        "type": "Lab Review",
                        "location": "North Clinic - Suite 301",
                        "status": "confirmed"
                    },
                    {
                        "appointment_id": "APT-2007",
                        "doctor_id": "DOC-002",
                        "patient_id": "PAT-002",
                        "patient_name": "Robert Johnson",
                        "date": "2026-08-28",
                        "time": "9:00 AM",
                        "type": "Hypertension Management",
                        "location": "North Clinic - Suite 301",
                        "status": "confirmed"
                    },
                    {
                        "appointment_id": "APT-2008",
                        "doctor_id": "DOC-002",
                        "patient_id": "PAT-003",
                        "patient_name": "Maria Garcia",
                        "date": "2026-09-05",
                        "time": "10:30 AM",
                        "type": "Diabetes Follow-up",
                        "location": "North Clinic - Suite 301",
                        "status": "scheduled"
                    },
                    {
                        "appointment_id": "APT-2009",
                        "doctor_id": "DOC-002",
                        "patient_id": "PAT-005",
                        "patient_name": "John Smith",
                        "date": "2026-09-12",
                        "time": "2:00 PM",
                        "type": "Cardiac Assessment",
                        "location": "North Clinic - Suite 301",
                        "status": "scheduled"
                    },
                    {
                        "appointment_id": "APT-2010",
                        "doctor_id": "DOC-002",
                        "patient_id": "PAT-004",
                        "patient_name": "John Smith",
                        "date": "2026-09-19",
                        "time": "11:30 AM",
                        "type": "Physical Exam",
                        "location": "North Clinic - Suite 301",
                        "status": "scheduled"
                    },
                    {
                        "appointment_id": "APT-2011",
                        "doctor_id": "DOC-002",
                        "patient_id": "PAT-006",
                        "patient_name": "Emma Thompson",
                        "date": "2026-09-26",
                        "time": "4:00 PM",
                        "type": "Asthma Review",
                        "location": "North Clinic - Suite 301",
                        "status": "scheduled"
                    }
                ]
            }
        }
    
    def load_from_working_copy(self) -> None:
        """Load data from default into memory (in-memory only, no file I/O)."""
        if self._default_data is None:
            self.initialize_with_defaults()

        # Deep copy from default data
        self.patients = copy.deepcopy(self._default_data.get('patients', {}))
        self.appointments = copy.deepcopy(self._default_data.get('appointments', {}))
        self.doctors = copy.deepcopy(self._default_data.get('doctors', {}))
        self.doctor_appointments = copy.deepcopy(self._default_data.get('doctor_appointments', {}))
        self.slots = copy.deepcopy(self._default_data.get('slots', {}))
        
        print(f"Loaded data into memory: {len(self.patients)} patients, "
              f"{sum(len(appts) for appts in self.appointments.values())} appointments, "
              f"{len(self.doctors)} doctors, "
              f"{sum(len(appts) for appts in self.doctor_appointments.values())} doctor appointments, "
              f"{len(self.slots)} slots")
    
    def save_to_working_copy(self) -> None:
        """No-op for Vercel (in-memory only, no file I/O)."""
        print("Data persisted in memory (Vercel serverless mode)")
    
    def refresh_from_default(self) -> None:
        """Reset working data from default copy (in-memory)."""
        if self._default_data is None:
            self.initialize_with_defaults()
        
        # Reload from default
        self.load_from_working_copy()
        print("Refreshed working data from default")


# Global instance
_data_manager: Optional[DataManager] = None


def get_data_manager() -> DataManager:
    """Get the global data manager instance."""
    global _data_manager
    if _data_manager is None:
        _data_manager = DataManager()
    return _data_manager


def load_data_on_startup() -> None:
    """Initialize and load data on application startup."""
    dm = get_data_manager()
    dm.initialize_with_defaults()
    dm.load_from_working_copy()


def save_working_data() -> None:
    """Save current data to working sheet."""
    dm = get_data_manager()
    dm.save_to_working_copy()
