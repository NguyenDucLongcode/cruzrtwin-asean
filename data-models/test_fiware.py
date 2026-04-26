import requests
import json
import os

# Chỉnh đường dẫn đến file JSON (nằm trong thư mục data-models)
current_dir = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(current_dir, 'entities', 'TemperatureSensor.json')

with open(json_path, 'r', encoding='utf-8') as f:
    entity = json.load(f)

# Gửi POST lên FIWARE Orion
url = "http://localhost:1026/v2/entities"
headers = {"Content-Type": "application/json"}

response = requests.post(url, headers=headers, json=entity)

if response.status_code == 201:
    print("Entity đã được tạo thành công!")
else:
    print(f"Lỗi: {response.status_code}")
    print(response.text)

# GET để kiểm tra
get_url = "http://localhost:1026/v2/entities/urn:ngsi-ld:TemperatureSensor:sensor_001"
response2 = requests.get(get_url)

if response2.status_code == 200:
    print("\nDữ liệu từ FIWARE:")
    print(json.dumps(response2.json(), indent=2))
else:
    print(f"Lỗi GET: {response2.status_code}")