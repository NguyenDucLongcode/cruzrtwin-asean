import json
import jsonschema
from jsonschema import validate
import os

# Định nghĩa schema chuẩn NGSI-v2 (phiên bản đơn giản)
ngsiv2_schema = {
    "type": "object",
    "required": ["id", "type"],
    "properties": {
        "id": {"type": "string", "pattern": "^urn:ngsi-ld:"},
        "type": {"type": "string"},
        "TimeInstant": {
            "type": "object",
            "required": ["type", "value"],
            "properties": {
                "type": {"type": "string", "enum": ["DateTime"]},
                "value": {"type": "string", "format": "date-time"}
            }
        }
    },
    "additionalProperties": True
}

# Hàm kiểm tra 1 file entity
def validate_entity(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        entity = json.load(f)
    
    try:
        validate(instance=entity, schema=ngsiv2_schema)
        print(f"{file_path}: Hợp lệ")
        return True
    except jsonschema.exceptions.ValidationError as e:
        print(f"❌ {file_path}: Không hợp lệ - {e.message}")
        return False

# Validate tất cả 5 file
files = [
    "TemperatureSensor.json",
    "HumiditySensor.json", 
    "SmokeSensor.json",
    "AirQualitySensor.json",
    "SmartPlug.json"
]

print("=== VALIDATING FIWARE NGSI-v2 ENTITIES ===\n")
all_valid = all(validate_entity(f) for f in files if os.path.exists(f))

if all_valid:
    print("\nTất cả 5 entities đều hợp lệ theo NGSI-v2 spec!")
else:
    print("\nMột số file không hợp lệ, cần sửa lại")