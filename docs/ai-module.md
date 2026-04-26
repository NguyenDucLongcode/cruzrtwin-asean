# 🤖 AI Module – Anomaly Detection + Energy Optimization

Thư mục `ai-models/` chứa 2 phần xử lý AI chính:

- `training/`: phát hiện bất thường (anomaly detection) từ dữ liệu sensor
- `energy/`: tối ưu năng lượng bằng cách phát hiện thiết bị idle và đề xuất/tạo lệnh điều khiển

---

## 📁 Cấu trúc thư mục

```text
ai-models/
├── energy/
│   ├── energy_optimizer.py           # Module T-10: phát hiện idle + tạo FIWARE command
│   └── energy_demo.py                # Demo 2 kịch bản idle thực tế
└── training/
    ├── generate_sensor_data.py       # Tạo dữ liệu giả lập (normal + anomaly)
    ├── train_anomaly_model.py        # Train model Isolation Forest
    ├── anomaly_detection.py          # So sánh nhiều thuật toán phát hiện bất thường
    ├── data/
    │   └── sensor_data.csv           # Dataset sau khi generate
    ├── models/
    │   └── anomaly_model.pkl         # Model đã train (joblib)
    └── test/
        ├── run_all_tests.py          # Chạy toàn bộ test
        ├── test_model_working.py     # Test model load + predict
        ├── test_latency.py           # Test tốc độ dự đoán
        ├── test_with_csv.py          # Test với dữ liệu CSV
        └── test_realtime_simulation.py # Mô phỏng realtime
```

---

## ⚙️ Luồng hoạt động

```text
Generate Data → Train Model → Save Model → Test → Detect Anomaly → Energy Idle Detection → FIWARE Command
```

---

## 🚀 Hướng dẫn sử dụng

### 1. Tạo dữ liệu

```bash
python ai-models/training/generate_sensor_data.py
```

👉 Kết quả:

- Tạo file `ai-models/training/data/sensor_data.csv`
- Bao gồm:
  - 1000 mẫu bình thường
  - 50 mẫu bất thường

---

### 2. Train model

```bash
python ai-models/training/train_anomaly_model.py
```

👉 Kết quả:

- Train mô hình `Isolation Forest`
- In ra metrics:
  - Accuracy (độ chính xác tổng thể)
  - Precision (độ chính xác khi báo bất thường)
  - Recall (khả năng phát hiện đầy đủ bất thường)
  - F1-score (cân bằng giữa Precision và Recall)
- Lưu model tại:

```text
ai-models/training/models/anomaly_model.pkl
```

---

### 3. Phân tích bất thường

```bash
python ai-models/training/anomaly_detection.py
```

👉 Script sẽ:

- Đọc dữ liệu từ `ai-models/training/data/sensor_data.csv`
- So sánh các thuật toán:
  - Isolation Forest
  - One-Class SVM
  - Local Outlier Factor
- In bảng kết quả gồm:
  - Train Time
  - Predict Time
  - Total Latency
  - Accuracy / Precision / Recall / F1-score
- Chọn model tốt nhất theo F1-score

---

## 🧠 4. Features sử dụng

Model sử dụng 5 đặc trưng:

- temperature (°C)
- humidity (%)
- smoke (ppm)
- co2 (ppm)
- power (W)

---

## 🤖 5. Cấu hình model chính

- Thuật toán: **Isolation Forest**
- contamination: 5%
- n_estimators: 100

---

## 📊 6. Ý nghĩa ứng dụng

- Phát hiện bất thường trong môi trường IoT:
  - Nhiệt độ cao bất thường
  - Khói tăng đột biến
  - CO2 ở mức nguy hiểm
  - Thiết bị hoạt động bất thường

---

## ✅ 7. Test system

### 7.1 Mục tiêu test

- Kiểm tra model load đúng
- Kiểm tra predict chính xác
- Kiểm tra dữ liệu CSV
- Kiểm tra tốc độ (latency)
- Mô phỏng realtime system

```bash
python ai-models/training/test/run_all_tests.py
```

Lưu ý: Script `run_all_tests.py` chạy tuần tự và sẽ chờ nhấn Enter trước mỗi bài test.

---

## ⚡ 8. Energy Optimization (T-10)

### 8.1 Thành phần chính

- `EnergyOptimizer` trong `ai-models/energy/energy_optimizer.py`
- Chức năng:
  - Theo dõi thiết bị đang bật (`onOff=True`)
  - Phát hiện idle theo profile từng loại thiết bị (`tv`, `fan`, `light`, `default`)
  - Xác nhận nhiều mẫu liên tiếp (`confirmation_readings`) trước khi đề xuất tắt
  - Dùng model anomaly đã train để xác nhận bất thường năng lượng (optional)
  - Sinh FIWARE command để tắt smart plug
  - Chống spam command: mỗi phiên idle chỉ tạo 1 khuyến nghị tắt
  - Chịu lỗi telemetry cơ bản: bỏ qua sample thiếu dữ liệu hoặc timestamp sai format

### 8.2 Chạy demo

```bash
python ai-models/energy/energy_demo.py
```

Demo hiện có 2 kịch bản:

- Smart TV standby sau khi xem phim
- Quạt phòng ngủ bật quên thời gian dài

Kết quả đầu ra gồm:

- Danh sách khuyến nghị tiết kiệm điện
- Danh sách FIWARE commands dạng NGSI-v2
- Ước tính điện năng tiết kiệm mỗi ngày

### 8.3 Điều kiện model

`energy_optimizer.py` cần file model `anomaly_model.pkl`.

Module hiện có cơ chế tự tìm model theo nhiều path fallback.

Project hiện có model ở cả 2 vị trí:

- `ai-models/training/models/anomaly_model.pkl`
- `anomaly_model.pkl` (root project)

Nếu chưa có, hãy train trước bằng:

```bash
python ai-models/training/train_anomaly_model.py
```

### 8.4 Inventory chức năng (đang có)

| Nhóm     | Chức năng                                            | Trạng thái | Mục đích                                        |
| -------- | ---------------------------------------------------- | ---------- | ----------------------------------------------- |
| Energy   | Detect idle theo ngưỡng công suất + thời gian        | ✅         | Xác định thiết bị bật nhưng ít sử dụng          |
| Energy   | Profile theo loại thiết bị (`tv/fan/light/default`)  | ✅         | Giảm báo sai khi dùng 1 ngưỡng cho mọi thiết bị |
| Energy   | Xác nhận nhiều mẫu liên tiếp trước khi tắt           | ✅         | Tránh tắt nhầm do nhiễu tức thời                |
| Energy   | Chống lặp FIWARE `off` command trong cùng phiên idle | ✅         | Tránh spam lệnh điều khiển                      |
| Energy   | Fallback path để tự tìm model                        | ✅         | Chạy ổn dù chạy script từ thư mục khác nhau     |
| Energy   | Bỏ qua sample telemetry lỗi/thiếu                    | ✅         | Tăng độ ổn định runtime                         |
| Training | Generate dữ liệu synthetic                           | ✅         | Tạo data khởi tạo cho huấn luyện                |
| Training | Train + lưu model Isolation Forest                   | ✅         | Sinh model phục vụ anomaly + energy             |
| Training | So sánh thuật toán anomaly                           | ✅         | Benchmark nhanh theo F1/latency                 |
| Training | Bộ test model/CSV/latency/realtime                   | ✅         | Kiểm tra nhanh độ sẵn sàng trước demo           |

### 8.5 Danh sách nên bổ sung tiếp (gợi ý)

| Ưu tiên    | Đề xuất                                                        | Lý do                                         |
| ---------- | -------------------------------------------------------------- | --------------------------------------------- |
| Cao        | Cooldown theo thời gian thực (vd: không gửi lại trong 15 phút) | Tăng an toàn vận hành khi trạng thái dao động |
| Cao        | Config profile theo file `.json` hoặc `.yaml`                  | Dễ tune ngưỡng mà không sửa code              |
| Cao        | Whitelist thiết bị không tự tắt                                | Tránh ảnh hưởng thiết bị quan trọng           |
| Trung bình | Logging có cấu trúc (JSON log)                                 | Dễ audit và truy vết quyết định AI            |
| Trung bình | Rule xác nhận 2 bước (recommend -> auto-off)                   | Giảm rủi ro thao tác tự động                  |
| Trung bình | Unit test cho từng rule idle/profile/dedup                     | Ổn định khi mở rộng tính năng                 |

---

## 🔗 Tích hợp hệ thống

Module này có thể tích hợp với:

```text
FIWARE Orion → AI Module (Anomaly + Energy Optimizer)
→ Kết quả anomaly + khuyến nghị tiết kiệm điện
→ FIWARE command (toggle smart plug) → API / UI
```

---

## 📌 Ghi chú

- Dữ liệu hiện tại là giả lập (synthetic data)
- Có thể thay bằng dữ liệu thật từ FIWARE
- Model có thể retrain khi có dữ liệu mới

---

## 🚀 Mở rộng

- Realtime detection (stream data)
- Visualization (matplotlib / seaborn)
- API với FastAPI
- Alert system (email / notification)
