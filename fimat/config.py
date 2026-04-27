#  Cấu hình cho FIWARE Orion Context Broker và các thiết bị mô phỏng
FIWARE_ORION_URL = "http://localhost:1026/v2"

# Danh sách các thiết bị mô phỏng với ID, loại và khoảng thời gian gửi dữ liệu (tính bằng giây)
SIMULATED_DEVICES = [
    {"id": "matter_temp_sensor_001", "type": "TemperatureSensor", "interval": 5},
    {"id": "matter_humid_sensor_001", "type": "HumiditySensor", "interval": 5},
    {"id": "matter_smoke_sensor_001", "type": "SmokeSensor", "interval": 3},
    {"id": "matter_airquality_001", "type": "AirQualitySensor", "interval": 10},
    {"id": "matter_smartplug_001", "type": "SmartPlug", "interval": 2},
]