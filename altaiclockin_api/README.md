# Altaiclockin API

Automates clock-in and clock-out on https://app.altaiclockin.com/ using Selenium and exposes a simple REST API with FastAPI. Designed to easily integrate with Home Assistant or any system that can make HTTP requests.

> **💡 Looking for manual execution?** Check the [standalone version](../README.md) in the parent directory for running the script manually without Docker or API.


## Available endpoints
- `POST /checkin` - Clock in
- `POST /checkout` - Clock out  
- `GET /status` - Health check

## Requirements
- Docker
- (Optional) Home Assistant for integration

## Configuration

### Environment variables
You can configure credentials and other parameters via environment variables in the `.env` file:

```bash
# Service port
PORT=8990

# Timezone
TZ=Europe/Madrid

# Resource limits
MEMORY_LIMIT=512M
CPU_LIMIT=0.5

# Altaiclockin credentials
ALTAICLOCKIN_USERNAME=your_username
ALTAICLOCKIN_PASSWORD=your_password
```

## How to build and run

<details>
<summary><strong>Option 1: Local build (Windows/Linux/macOS)</strong></summary>

1. Clone or copy the project and enter the folder:
   ```bash
   cd altaiclockin_api
   ```
2. **Configure your credentials** in the `.env` file:
   ```bash
   ALTAICLOCKIN_USERNAME=your_username
   ALTAICLOCKIN_PASSWORD=your_password
   ```
3. Build the optimized Docker image:
   ```bash
   docker build -f Dockerfile.slim -t altaiclockin-api-slim .
   ```
4. Run with docker-compose:
   ```bash
   docker-compose up -d
   ```

</details>

<details>
<summary><strong>Option 2: For Proxmox LXC (precompiled image)</strong></summary>

1. **On Windows**: Export the image to .tar file:
   ```powershell
   docker save altaiclockin-api-slim -o altaiclockin-api-slim.tar
   ```

2. **Transfer to your LXC** via SSH the necessary files:
   ```bash
   scp altaiclockin-api-slim.tar user@lxc-ip:/opt/
   scp docker-compose.yml user@lxc-ip:/opt/
   scp .env user@lxc-ip:/opt/
   scp install-altaiclockin.sh user@lxc-ip:/opt/
   ```

3. **On the LXC**: Configure credentials and run:
   ```bash
   cd /opt
   # Edit the .env file with your real credentials
   nano .env
   
   # Run the installation
   chmod +x install-altaiclockin.sh
   ./install-altaiclockin.sh
   ```

</details>

## How to test that it works

<details>
<summary><strong>On Linux/macOS:</strong></summary>

- Check that the API is alive:
  ```bash
  curl http://localhost:8990/status
  # Expected response: {"alive": true}
  ```

- Clock in:
  ```bash
  curl -X POST http://localhost:8990/checkin
  # Expected response: {"status": "ok"} (if everything goes well)
  ```

- Clock out:
  ```bash
  curl -X POST http://localhost:8990/checkout
  # Expected response: {"status": "ok"} (if everything goes well)
  ```
If there's any error, the response will be a JSON with the failure details.

</details>
<details>
<summary><strong>On Windows PowerShell:</strong></summary>

- Check that the API is alive:
  ```powershell
  Invoke-WebRequest -Uri http://localhost:8990/status -Method GET
  # Expected response: {"alive": true}
  ```

- Clock in:
  ```powershell
  Invoke-WebRequest -Uri http://localhost:8990/checkin -Method POST
  # Expected response: {"status": "ok"} (if everything goes well)
  ```

- Clock out:
  ```powershell
  Invoke-WebRequest -Uri http://localhost:8990/checkout -Method POST
  # Expected response: {"status": "ok"} (if everything goes well)
  ```

If there's any error, the response will be a JSON with the failure details.
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

## Troubleshooting

<details>
<summary><strong>Common Issues</strong></summary>

### Error "port is already allocated"
If you get this error when running docker-compose, it means port 8990 is already in use. Change the port in the `.env` file:
```bash
PORT=8991  # or any other free port
```

### Credentials error
If clocking fails, verify that the `ALTAICLOCKIN_USERNAME` and `ALTAICLOCKIN_PASSWORD` variables are correctly configured in the `.env` file.

</details>

---

Questions? Modify or expand this README according to your needs.
