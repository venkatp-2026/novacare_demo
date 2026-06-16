"""Application configuration."""
import os

# API Configuration
API_TITLE = "NovaCare Health - Epic EHR Mock API"
API_DESCRIPTION = "Mock endpoints simulating Epic FHIR R4 healthcare system integration"
API_VERSION = "1.0.0"

# Security
MOCK_API_TOKEN = os.environ.get("MOCK_API_TOKEN", "dev-token-replace-in-production")

# CORS Configuration
ALLOWED_ORIGINS = [
    "https://*.zendesk.com",
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:3000",
    "http://127.0.0.1",
    "http://127.0.0.1:8000",
    "https://novacare-demo.vercel.app",
    "https://novacare-demo-*.vercel.app",  # Preview deployments
]

# Data Configuration
EXCEL_FILE_PATH = "data/novacare_data.xlsx"
