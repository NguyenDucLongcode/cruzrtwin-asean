from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# Dữ liệu từ thiết bị IoT
class SensorData(BaseModel):
    device_id: str              # ID duy nhất của thiết bị
    device_type: str            # Loại thiết bị (temp_sensor, air_sensor,...)

    temperature: Optional[float] = None  # Nhiệt độ (°C)
    humidity: Optional[float] = None     # Độ ẩm (%)
    smokeLevel: Optional[float] = None   # Mức khói
    pm25: Optional[float] = None         # Bụi mịn PM2.5
    pm10: Optional[float] = None         # Bụi PM10
    co2: Optional[float] = None          # Nồng độ CO2
    tvoc: Optional[float] = None         # TVOC
    aqi: Optional[int] = None            # Chỉ số chất lượng không khí
    power: Optional[float] = None        # Công suất tiêu thụ (W)
    voltage: Optional[float] = None      # Điện áp (V)
    current: Optional[float] = None      # Dòng điện (A)
    energyToday: Optional[float] = None  # Điện năng tiêu thụ hôm nay (kWh)
    onOff: Optional[bool] = None         # Trạng thái thiết bị (bật/tắt)
    battery: Optional[float] = None      # Mức pin (%)
    status: Optional[str] = None         # Trạng thái online/offline
    alarm: Optional[bool] = None         # Cảnh báo khói

    timestamp: datetime          # Thời gian ghi nhận dữ liệu

# Điểm rủi ro của thiết bị
class RiskScore(BaseModel):
    score: int                   # Điểm rủi ro (0 - 100)
    level: str                  # Mức độ: low | medium | high | critical
    reasons: List[str]          # Danh sách nguyên nhân gây rủi ro

# Thông tin rủi ro theo thiết bị
class DeviceRisk(BaseModel):
    device_id: str              # ID thiết bị
    device_type: str            # Loại thiết bị
    risk: RiskScore             # Thông tin rủi ro

# Thống kê năng lượng
class EnergyStats(BaseModel):
    total_power: float          # Tổng công suất tiêu thụ (W)
    idle_devices: List[str]     # Danh sách thiết bị đang không hoạt động
    estimated_savings: float    # Ước tính tiết kiệm điện (W hoặc %)
    timestamp: datetime         # Thời gian thống kê

# Message WebSocket realtime
class WebSocketMessage(BaseModel):
    type: str                   # Loại message: "alert" | "data" | "pong"

    severity: Optional[str] = None   # Mức độ cảnh báo (low, medium, high)
    device_id: Optional[str] = None  # ID thiết bị liên quan
    message: Optional[str] = None    # Nội dung thông báo

    timestamp: datetime        # Thời gian gửi message