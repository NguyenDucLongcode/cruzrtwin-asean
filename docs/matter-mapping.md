# 🔗 Matter → NGSI Mapping

Tài liệu này mô tả cách ánh xạ dữ liệu từ Matter clusters sang định dạng NGSI-v2 (FIWARE Orion).

---

## 📊 Mapping Table

| Matter Cluster         | Attribute     | NGSI Field  | Ghi chú       |
| ---------------------- | ------------- | ----------- | ------------- |
| TemperatureMeasurement | measuredValue | temperature | °C (chia 100) |
| RelativeHumidity       | measuredValue | humidity    | %             |
| AirQuality             | pm2_5         | pm25        | µg/m3         |
| AirQuality             | pm10          | pm10        | µg/m3         |
| AirQuality             | co2           | co2         | ppm           |
| AirQuality             | tvoc          | tvoc        | ppb           |
| OnOff                  | onOff         | onOff       | true/false    |
| ElectricalMeasurement  | power         | power       | watt          |
| ElectricalMeasurement  | voltage       | voltage     | volt          |
| ElectricalMeasurement  | current       | current     | ampere        |
| ElectricalMeasurement  | energyToday   | energyToday | kwh           |
| SmokeDetection         | smokeLevel    | smokeLevel  | ppm           |

---

## 🔄 Data Flow

Matter Device → Mapping Layer → NGSI JSON → FIWARE Orion

---

## 📌 Ghi chú

- Mapping giúp hệ thống tương thích với thiết bị IoT thực tế
- Dữ liệu Matter có thể cần scale (ví dụ: temperature /100)

---

## Living Room & SmartPlug

- `OnOff` + `ElectricalMeasurement` (power, energyToday) thường dùng cho `SmartPlug` trong phòng khách.
- Khi tạo subscription cho phòng khách, notification sẽ gửi về backend endpoint `/api/webhook/livingroom` để luồng energy optimizer và motion xử lý.
