import subprocess
import os
import sys

print("BẮT ĐẦU TEST TOÀN BỘ HỆ THỐNG")
print("=" * 60)

# Chuyển đến thư mục test
os.chdir(os.path.dirname(__file__))

tests = [
    ("test_model_working.py", "Kiểm tra model hoạt động"),
    ("test_latency.py", "Đo tốc độ dự đoán"),
    ("test_with_csv.py", "Kiểm tra với dữ liệu CSV"),
    ("test_realtime_simulation.py", "Mô phỏng real-time")
]

for test_file, description in tests:
    input(f"\nNhấn Enter để chạy: {description}")
    print("-" * 60)
    subprocess.run([sys.executable, test_file])

print("\n" + "=" * 60)
print("HOÀN THÀNH TẤT CẢ CÁC TEST!")