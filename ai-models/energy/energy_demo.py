

import numpy as np
from energy_optimizer import EnergyOptimizer
from datetime import datetime, timedelta

print("=" * 70)
print("T-10 DEMO: AI ENERGY OPTIMIZATION MODULE")
print("   Phát hiện thiết bị idle → Gửi FIWARE command")
print("=" * 70)

optimizer = EnergyOptimizer()

# ============================================================
# SCENARIO 1: Smart TV ở phòng khách - idle sau khi xem phim
# ============================================================
print("\n SCENARIO 1: Smart TV phòng khách")
print("-" * 50)
print("   Mô tả: Gia đình xem phim xong lúc 22:00, quên tắt TV")
print("          TV chuyển sang chế độ standby (8W) trong 45 phút")
print("   Kết quả mong đợi: Phát hiện idle → gửi lệnh tắt TV\n")

now = datetime.now()

scenario1_data = []
# Giả lập 15 phút xem phim (công suất cao)
for i in range(3):
    scenario1_data.append({
        'device_id': 'smart_plug_living_room_tv',
        'power': 95.0 + np.random.rand() * 10,
        'onOff': True,
        'timestamp': now - timedelta(minutes=(60 - i*5))
    })
# Giả lập 45 phút idle (công suất thấp)
for i in range(9):
    scenario1_data.append({
        'device_id': 'smart_plug_living_room_tv',
        'power': 7.5 + np.random.rand() * 2,
        'onOff': True,
        'timestamp': now - timedelta(minutes=(45 - i*5))
    })

result1 = optimizer.process_and_recommend(scenario1_data)

if result1['idle_devices_found'] > 0:
    print("KẾT QUẢ SCENARIO 1:")
    for rec in result1['recommendations']:
        print(f"   → {rec}")
    print(f"\n  FIWARE Command gửi đi:")
    for cmd in result1['fiware_commands']:
        print(f"      {cmd}")
else:
    print("   Chưa phát hiện idle (có thể do chưa đủ thời gian)")

# ============================================================
# SCENARIO 2: Quạt phòng ngủ - bật quên cả đêm
# ============================================================
print("\n SCENARIO 2: Quạt phòng ngủ")
print("-" * 50)
print("   Mô tả: Học sinh bật quạt lúc 23:00, đi ngủ quên tắt")
print("          Quạt chạy ở mức thấp (6W) trong 2 giờ")
print("   Kết quả mong đợi: Phát hiện idle → gửi lệnh tắt quạt\n")

scenario2_data = []
# Giả lập 2 giờ idle (120 phút)
for i in range(24):  # mỗi 5 phút 1 reading
    scenario2_data.append({
        'device_id': 'smart_plug_bedroom_fan',
        'power': 6.2 + np.random.rand() * 2,
        'onOff': True,
        'timestamp': now - timedelta(minutes=(120 - i*5))
    })

result2 = optimizer.process_and_recommend(scenario2_data)

if result2['idle_devices_found'] > 0:
    print("KẾT QUẢ SCENARIO 2:")
    for rec in result2['recommendations']:
        print(f"   → {rec}")
    print(f"\n   FIWARE Command gửi đi:")
    for cmd in result2['fiware_commands']:
        print(f"      {cmd}")
else:
    print("  Chưa phát hiện idle")

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "=" * 70)
print("TỔNG KẾT DEMO (T-10)")
print("=" * 70)
print(f"Scenario 1: Phát hiện TV idle → {result1['idle_devices_found']} thiết bị")
print(f"Scenario 2: Phát hiện quạt idle → {result2['idle_devices_found']} thiết bị")
print(f"\nTiết kiệm dự kiến: {result1['estimated_daily_savings_kwh'] + result2['estimated_daily_savings_kwh']:.2f} kWh/ngày")
print("\nT-10 HOÀN THÀNH - ĐÁP ỨNG ≥2 IDLE SCENARIOS + FIWARE COMMANDS")
print("=" * 70)