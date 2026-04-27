"""
T-22: Demo Configuration
Cấu hình cho demo environment stabilization
"""

# Service endpoints
SERVICES = {
    "fiware_orion": {
        "url": "http://localhost:1026/version",
        "port": 1026,
        "name": "FIWARE Orion"
    },
    "backend_api": {
        "url": "http://localhost:8000/health",
        "port": 8000,
        "name": "Backend API"
    },
    "robot_api": {
        "url": "http://localhost:8001/health",
        "port": 8001,
        "name": "Robot API"
    }
}

# Demo scenarios
DEMO_SCENARIOS = [
    {
        "name": "Scenario 1: Temperature Anomaly",
        "device": "matter_temp_sensor_001",
        "attribute": "temperature",
        "normal_value": 25.0,
        "anomaly_value": 40.0,
        "threshold": 35,
        "expected_alert": "Nhiệt độ cao"
    },
    {
        "name": "Scenario 2: Smoke Anomaly",
        "device": "matter_smoke_sensor_001",
        "attribute": "smokeLevel",
        "normal_value": 50,
        "anomaly_value": 350,
        "threshold": 300,
        "expected_alert": "CẢNH BÁO CHÁY"
    },
    {
        "name": "Scenario 3: Energy Optimization",
        "device": "matter_smartplug_001",
        "attribute": "power",
        "normal_value": 50,
        "idle_value": 8,
        "threshold": 10,
        "expected_action": "idle detected"
    }
]

# Reset timeout (seconds)
RESET_TIMEOUT = 30