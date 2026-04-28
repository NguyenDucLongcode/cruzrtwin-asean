import requests
import json
import os

FIWARE_URL = "http://localhost:1026/v2/entities"

# Đường dẫn folder entities
current_dir = os.path.dirname(os.path.abspath(__file__))
entities_dir = os.path.join(current_dir, 'entities')


# Helper function để lấy entity theo ID
def get_entity(entity_id):
    url = f"{FIWARE_URL}/{entity_id}"
    res = requests.get(url)
    return res


# Xóa entity nếu đã tồn tại (để đảm bảo dữ liệu sạch cho test)
def delete_entity(entity_id):
    url = f"{FIWARE_URL}/{entity_id}"
    res = requests.delete(url)
    if res.status_code == 204:
        print(f"Deleted: {entity_id}")
    else:
        print(f"Delete fail: {entity_id} ({res.status_code})")

# Tạo entity mới trên FIWARE
def create_entity(entity):
    res = requests.post(FIWARE_URL, headers={"Content-Type": "application/json"}, json=entity)
    if res.status_code == 201:
        print(f"Created: {entity['id']}")
    else:
        print(f"Create fail: {entity['id']} ({res.status_code})")
        print(res.text)


# Main seeding function - đọc tất cả file JSON trong folder entities và tạo entity tương ứng trên FIWARE
def seed_entities():
    print("=" * 60)
    print(" Seeding FIWARE Entities...")
    print("=" * 60)

    files = [f for f in os.listdir(entities_dir) if f.endswith(".json")]

    for file_name in files:
        file_path = os.path.join(entities_dir, file_name)

        with open(file_path, 'r', encoding='utf-8') as f:
            entity = json.load(f)

        entity_id = entity.get("id")

        print(f"\n Processing: {file_name}")

        # 1. Check tồn tại
        res = get_entity(entity_id)

        if res.status_code == 200:
            print(f"   Already exists → deleting...")
            delete_entity(entity_id)
        elif res.status_code == 404:
            print(f"   Not exists → creating...")
        else:
            print(f"   Unexpected GET: {res.status_code}")

        # 2. Tạo mới
        create_entity(entity)

    print("\n" + "=" * 60)
    print(" Done seeding all entities!")
    print("=" * 60)


if __name__ == "__main__":
    seed_entities()