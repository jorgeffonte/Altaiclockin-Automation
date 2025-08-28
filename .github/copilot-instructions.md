# Altaiclockin Automation - GitHub Copilot Instructions

Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.

## Project Overview

Altaiclockin Automation is a Python Selenium web automation tool that automates clock-in and clock-out on https://app.altaiclockin.com/. It has two deployment modes:

1. **Standalone script** (`altaiclockin.py`) - For manual execution
2. **Docker API service** (`altaiclockin_api/`) - FastAPI-based REST API for automation and Home Assistant integration

## Working Effectively

### Environment Setup
Run these commands to set up your development environment:

```bash
# Verify Python 3.8+ is available
python3 --version  # Should be 3.8 or higher

# Verify Firefox browser is available (required for Selenium)
which firefox || which firefox-esr  # Must have Firefox for Selenium automation

# Clone and navigate to project
cd /path/to/Altaiclockin-Automation
```

### Standalone Script Setup
Use this for testing changes to the core automation logic:

```bash
# Install dependencies - takes ~30 seconds. NEVER CANCEL.
pip3 install -r requirements.txt

# Set credentials (required for actual functionality)
export ALTAICLOCKIN_USERNAME="your_username"
export ALTAICLOCKIN_PASSWORD="your_password"

# Test the script shows usage correctly
python3 altaiclockin.py
# Expected output: Usage: python3 altaiclockin.py <checkin|checkout>

# Test without credentials (will fail at login but validates script structure)
python3 altaiclockin.py checkin  # Will show error about missing credentials
```

### Docker API Setup
Use this for testing the API service and Home Assistant integration:

```bash
# Navigate to API directory
cd altaiclockin_api

# Configure credentials in .env file
cp .env .env.backup
cat > .env << EOF
PORT=8990
TZ=Europe/Madrid
MEMORY_LIMIT=512M
CPU_LIMIT=0.5
ALTAICLOCKIN_USERNAME=test_user
ALTAICLOCKIN_PASSWORD=test_password
EOF

# Build Docker image - takes 2-5 minutes. NEVER CANCEL. Set timeout to 10+ minutes.
# NOTE: May fail in some environments due to SSL certificate issues
docker build -f Dockerfile.slim -t altaiclockin-api-slim .

# If build fails with SSL errors, this is a known environment limitation
# Document: "Docker build fails due to SSL certificate verification errors in sandboxed environments"

# Run with docker compose (if build succeeded)
docker compose up -d

# Test API endpoints (if container is running)
curl http://localhost:8990/status
# Expected response: {"alive": true}

# Stop services
docker compose down
```

## Validation Requirements

### CRITICAL: Actual Functionality Testing
After making changes to automation logic, you MUST test with real credentials:

```bash
# Set real credentials
export ALTAICLOCKIN_USERNAME="real_username"
export ALTAICLOCKIN_PASSWORD="real_password"

# Test standalone script
python3 altaiclockin.py checkin
# Should successfully log in to https://app.altaiclockin.com/ and clock in

python3 altaiclockin.py checkout
# Should successfully log in and clock out

# For API version (if Docker works in your environment)
curl -X POST http://localhost:8990/checkin
# Expected response: {"status": "ok"}
```

### Manual Validation Scenarios
Always execute these scenarios after making changes:

1. **Script Usage Validation**: Run `python3 altaiclockin.py` without arguments - should show usage help
2. **Dependency Validation**: Fresh `pip3 install -r requirements.txt` should complete in ~30 seconds
3. **Selenium Integration**: Script should start Firefox browser (headless) when run with valid credentials
4. **API Health Check**: If Docker container runs, `curl http://localhost:8990/status` should return `{"alive": true}`

## Build Times and Timeout Guidelines

### CRITICAL TIMING INFORMATION - NEVER CANCEL BUILDS
- **Dependencies install**: ~30 seconds - Set timeout to 5+ minutes
- **Docker build**: 2-5 minutes typical - **NEVER CANCEL** - Set timeout to 10+ minutes  
- **Selenium automation**: 30-60 seconds per operation - Set timeout to 3+ minutes
- **API startup**: 10-20 seconds - Set timeout to 2+ minutes

### Known Limitations
- **Docker build may fail** in sandboxed environments due to SSL certificate issues
- **Selenium requires Firefox** - automation will fail without Firefox browser
- **Real credentials needed** for full functionality testing
- **No automated test suite** exists - validation must be manual

## Repository Structure and Navigation

### Key Files and Directories
```
/
├── altaiclockin.py          # Main standalone automation script
├── requirements.txt         # Dependencies for standalone version
├── README.md               # User documentation and setup guides
└── altaiclockin_api/       # Docker API service directory
    ├── app.py              # FastAPI application with /checkin, /checkout, /status endpoints
    ├── altaiclockin.py     # Selenium automation (API version)
    ├── requirements.txt    # API dependencies (fastapi, uvicorn, selenium, webdriver-manager)
    ├── Dockerfile.slim     # Production Docker image (python:3.12-slim + firefox-esr)
    ├── docker-compose.yml  # Container orchestration with health checks
    ├── install-altaiclockin.sh  # LXC installation script
    └── .env               # Environment configuration
```

### Important Code Locations
- **Selenium automation logic**: Lines 46-120 in both `altaiclockin.py` files
- **Credentials configuration**: Lines 31-38 in standalone, environment variables for Docker
- **API endpoints**: Lines 6-24 in `altaiclockin_api/app.py`
- **Docker startup script**: Lines 27-30 in `Dockerfile.slim`

## Common Development Tasks

### Adding New Selenium Actions
1. Edit the automation logic in `altaiclockin.py` (standalone) and `altaiclockin_api/altaiclockin.py`
2. Test with: `python3 altaiclockin.py checkin` using real credentials
3. If modifying API version, rebuild Docker image and test endpoints

### Modifying API Endpoints
1. Edit `altaiclockin_api/app.py`
2. Test standalone first, then rebuild Docker container
3. Validate with `curl` commands against running container

### Environment Configuration Changes
1. Standalone: Modify lines 31-38 in `altaiclockin.py` or use environment variables
2. Docker: Update `altaiclockin_api/.env` file
3. Always test both deployment modes after configuration changes

## No CI/CD Pipeline
This repository has no automated CI/CD, tests, or linting. All validation must be manual:

- **No automated tests** - create manual test procedures
- **No linting configuration** - follow existing code style
- **No build pipeline** - manually validate all changes
- **No pre-commit hooks** - manually ensure code quality

## Home Assistant Integration
The Docker API service provides REST endpoints specifically for Home Assistant:
- `POST /checkin` - Clock in
- `POST /checkout` - Clock out  
- `GET /status` - Health check

Timeout for Home Assistant REST commands should be set to 120 seconds to allow Selenium automation to complete.

## Troubleshooting Common Issues

### "Firefox not found" errors
Install Firefox: `apt-get install firefox-esr` or equivalent for your system

### "SSL certificate verification failed" during Docker build
This is a known limitation in some environments. Document as: "Docker build not supported in this environment due to SSL certificate restrictions"

### "Connection refused" errors when testing API
Ensure Docker container is running: `docker compose ps` and check logs: `docker compose logs -f`

### Selenium timeouts
Default timeouts are 30 seconds for page loads and element waits. Increase if needed for slow networks.