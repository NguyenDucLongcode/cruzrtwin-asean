# Phân loại bất thường dựa trên ngưỡng cảm biến
def classify_anomaly(temp, humidity, smoke, co2, power):
    """
    Phân loại bất thường thành 5 loại chính
    """
    
    # 1. CHÁY (khói + nhiệt độ cao)
    if smoke > 300 and temp > 35:
        return {
            "type": "FIRE",
            "severity": "critical",
            "message": f"CẢNH BÁO CHÁY! Nhiệt độ {temp}°C, Khói {smoke}ppm",
            "action": "EVACUATE",
            "robot_instruction": "Di chuyển đến khu vực cháy, báo động sơ tán, gọi cứu hỏa 114"
        }
    
    # 2. KHÔNG KHÍ ĐỘC HẠI (CO2 cao hoặc khói độc)
    elif co2 > 1000 or smoke > 200:
        return {
            "type": "AIR_QUALITY_HAZARD",
            "severity": "high",
            "message": f"😷 Ô NHIỄM KHÔNG KHÍ! CO2: {co2}ppm, Khói: {smoke}ppm",
            "action": "VENTILATE",
            "robot_instruction": "Mở cửa sổ, kích hoạt quạt hút, thông báo đeo khẩu trang"
        }
    
    # 3. NHIỆT ĐỘ NGUY HIỂM (quá nóng hoặc quá lạnh)
    elif temp > 40:
        return {
            "type": "TEMPERATURE_DANGER",
            "severity": "high",
            "message": f"NHIỆT ĐỘ NGUY HIỂM! {temp}°C",
            "action": "COOL_DOWN",
            "robot_instruction": "Di chuyển đến khu vực nóng, bật điều hòa/quạt, phát nước uống"
        }
    elif temp < 10:
        return {
            "type": "TEMPERATURE_DANGER", 
            "severity": "high",
            "message": f"❄️ NHIỆT ĐỘ QUÁ THẤP! {temp}°C",
            "action": "HEAT_UP",
            "robot_instruction": "Kiểm tra hệ thống sưởi, thông báo mặc ấm"
        }
    
    # 4. LÃNG PHÍ ĐIỆN (thiết bị idle)
    elif power < 10 and power > 0:
        return {
            "type": "ENERGY_WASTE",
            "severity": "info",
            "message": f"💡 LÃNG PHÍ ĐIỆN! Thiết bị đang idle: {power}W",
            "action": "TURN_OFF",
            "robot_instruction": "Đến kiểm tra, đề xuất tắt thiết bị"
        }
    
    # 5. QUÁ TẢI ĐIỆN
    elif power > 500:
        return {
            "type": "OVERLOAD",
            "severity": "warning",
            "message": f"⚡ QUÁ TẢI ĐIỆN! Công suất: {power}W",
            "action": "REDUCE_LOAD",
            "robot_instruction": "Đến tủ điện, kiểm tra dòng tải"
        }
    
    # 6. BÌNH THƯỜNG
    else:
        return {
            "type": "NORMAL",
            "severity": "none",
            "message": "Mọi thứ bình thường",
            "action": "MONITOR",
            "robot_instruction": "Tiếp tục giám sát"
        }


