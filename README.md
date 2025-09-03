# Altaiclockin Automation

Automates clock-in and clock-out on https://app.altaiclockin.com/ using Selenium. Available in two modes: **Standalone script** for manual execution and **Docker API service**  [`altaiclockin_api/README.md`](altaiclockin_api/README.md) for automation and Home Assistant integration.

## 📁 Project Structure

```
Altaiclockin-Automation/
├── altaiclockin.py      # Standalone script for manual execution
├── requirements.txt     # Dependencies for standalone version
├── README.md           # This file
└── altaiclockin_api/   # Docker API service
    ├── .env            # Environment configuration
    ├── .gitignore      # Git ignore rules for API directory
    ├── app.py          # FastAPI API
    ├── altaiclockin.py # Selenium script (API version)
    ├── docker-compose.yml # Docker Compose configuration
    ├── Dockerfile.slim # Optimized Docker image definition
    ├── requirements.txt # Dependencies for API version
    ├── install-altaiclockin.sh # Installation script for Proxmox LXC
    └── README.md       # Detailed Docker documentation
```

## 🚀 Quick Start

<details>
<summary><strong>Option 1: Standalone Script (Manual execution)</strong></summary>

Perfect for running manually or integrating with your own scripts.

##### Requirements
- Python 3.8+
- Firefox browser
- Selenium WebDriver

##### Installation
```bash
# Clone the repository
git clone <repository-url>
cd altaiclockin_loger

# Install dependencies
pip install -r requirements.txt

# Set your credentials (recommended)
export ALTAICLOCKIN_USERNAME="your_username"
export ALTAICLOCKIN_PASSWORD="your_password"

# Or edit the script directly (lines 31-32 in altaiclockin.py)
```

##### Usage
```bash
# Clock in
python3 altaiclockin.py checkin

# Clock out
python3 altaiclockin.py checkout
```





</details>

<details>
<summary><strong>Option 2: Docker API Service (Automation)</strong></summary>

Perfect for Home Assistant integration and automated environments.

#### Features
- 🐳 Docker containerized service
- 🌐 REST API endpoints
- 🏠 Home Assistant integration ready
- 📊 Health check endpoints
- 🔧 Environment variable configuration
- 💾 Optimized image size (1.04GB)

For detailed Docker setup instructions, see: [`altaiclockin_api/README.md`](altaiclockin_api/README.md)

</details>



## 🔧 Configuration

<details>
<summary><strong>Standalone Version Configuration</strong></summary>

Set environment variables:
```bash
export ALTAICLOCKIN_USERNAME="your_username"
export ALTAICLOCKIN_PASSWORD="your_password"
```

Or edit the script directly (lines 31-32):
```python
USERNAME = os.getenv("ALTAICLOCKIN_USERNAME", "your_username")
PASSWORD = os.getenv("ALTAICLOCKIN_PASSWORD", "your_password")
```

</details>

<details>
<summary><strong>Docker API Version Configuration</strong></summary>

Configure via `.env` file in `altaiclockin_api/` directory:
```bash
ALTAICLOCKIN_USERNAME=your_username
ALTAICLOCKIN_PASSWORD=your_password
PORT=8990
```

</details>

## 🏠 Home Assistant Integration

<details>
<summary><strong>Step 1: Update configuration.yaml</strong></summary>

First, add the REST commands to your Home Assistant `configuration.yaml`:

```yaml
rest_command:
  altaiclockin_checkin:
    url: "http://<docker_host_ip>:8990/checkin"  # Replace with your server IP
    method: POST
    headers:
      Content-Type: "application/json"
    payload: "{}"
    timeout: 120

  altaiclockin_checkout:
    url: "http://<docker_host_ip>:8990/checkout"  # Replace with your server IP
    method: POST
    headers:
      Content-Type: "application/json"
    payload: "{}"
    timeout: 120
```

</details>

<details>
<summary><strong>Step 2: Create Automations</strong></summary>

#### Automatic check-in when entering work zone:
```yaml
alias: "Register Check-in"
description: "Automatically clock in when entering work zone"
triggers:
  - trigger: zone
    entity_id: person.your_name  # Replace with your person entity
    zone: zone.work  # Replace with your work zone
    event: enter
conditions: []
actions:
  - action: rest_command.altaiclockin_checkin
    data: {}
    response_variable: altaiclockin_response
  - if:
      - condition: template
        value_template: "{{ altaiclockin_response.content.status == 'ok' }}"
    then:
      - action: notify.mobile_app_your_device  # Replace with your notification service
        data:
          title: "Altaiclockin Check-in"
          message: >-
            Check-in '{{ altaiclockin_response.content.status }}'
            completed successfully
    else:
      - action: notify.mobile_app_your_device
        data:
          title: "Altaiclockin ERROR"
          message: "Could not register check-in: {{ altaiclockin_response }}"
mode: single
```

#### Automatic check-out when leaving work zone:
```yaml
alias: "Register Check-out"
description: "Automatically clock out when leaving work zone"
triggers:
  - trigger: zone
    entity_id: person.your_name  # Replace with your person entity
    zone: zone.work  # Replace with your work zone
    event: leave
conditions: []
actions:
  - action: rest_command.altaiclockin_checkout
    data: {}
    response_variable: altaiclockin_response
  - if:
      - condition: template
        value_template: "{{ altaiclockin_response.content.status == 'ok' }}"
    then:
      - action: notify.mobile_app_your_device
        data:
          title: "Altaiclockin Check-out"
          message: >-
            Check-out '{{ altaiclockin_response.content.status }}'
            completed successfully
    else:
      - action: notify.mobile_app_your_device
        data:
          title: "Altaiclockin ERROR"
          message: "Could not register check-out: {{ altaiclockin_response }}"
mode: single
```

### Configuration Notes:
- Replace `<docker_host_ip>` with your actual server IP address
- Replace `person.your_name` with your actual person entity ID
- Replace `zone.work` with your actual work zone entity ID
- Replace `mobile_app_your_device` with your actual notification service
- The `timeout: 120` gives the Selenium automation enough time to complete
</details>


### Docker API Version
See [`altaiclockin_api/README.md`](altaiclockin_api/README.md) for Docker-specific troubleshooting.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test both standalone and Docker versions
5. Submit a pull request

## 📄 License

This project is open source. Use responsibly and in accordance with your company's policies.

## ⚠️ Disclaimer

This tool is for automating your own legitimate clock-in/out activities. Ensure you comply with your company's policies and local labor laws.
