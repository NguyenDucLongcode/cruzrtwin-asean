"""
FIWARE IoT Simulator — Realtime Sensor Data
Gia lap 5 loai thiet bi IoT gui du lieu qua IoT Agent JSON.

Cach chay:
  python fiware/iot_simulator.py                    # Normal mode (chay lien tuc)
  python fiware/iot_simulator.py --mode anomaly     # Co inject anomaly
  python fiware/iot_simulator.py --interval 3       # Gui moi 3 giay

Dung: Ctrl+C
"""

import requests
import numpy as np
import time
import argparse
import signal
import sys
from datetime import datetime

# ================== CONFIG ==================
IOT_AGENT_SOUTH_URL = "http://localhost:7896/iot/json"
API_KEY = "cruzrtwin2026"
FIWARE_SERVICE = "cruzrtwin"
FIWARE_SERVICEPATH = "/"

# ================== DEVICE DEFINITIONS ==================
DEVICES = {
    "temp_sensor_001": {
        "name": "Temperature Sensor (Room A)",
        "normal": lambda: {"t": round(25 + np.random.normal(0, 1.5), 2), "bat": 85},
        "anomaly": lambda progress: {
            "t": round(25 + progress * 25 + np.random.normal(0, 0.5), 2),
            "bat": 85
        }
    },
    "hum_sensor_001": {
        "name": "Humidity Sensor (Room A)",
        "normal": lambda: {"h": round(65 + np.random.normal(0, 3), 2), "bat": 90},
        "anomaly": lambda progress: {
            "h": round(65 - progress * 35 + np.random.normal(0, 1), 2),
            "bat": 90
        }
    },
    "smoke_sensor_001": {
        "name": "Smoke Sensor (Room A)",
        "normal": lambda: {"s": round(35 + np.random.normal(0, 5), 2), "bat": 78},
        "anomaly": lambda progress: {
            "s": round(35 + progress * 300 + np.random.normal(0, 3), 2),
            "bat": 78
        }
    },
    "air_sensor_001": {
        "name": "Air Quality Sensor (Room B)",
        "normal": lambda: {
            "co2": round(400 + np.random.normal(0, 20), 2),
            "pm25": round(15 + np.random.normal(0, 3), 2),
            "tvoc": round(50 + np.random.normal(0, 10), 2)
        },
        "anomaly": lambda progress: {
            "co2": round(400 + progress * 600 + np.random.normal(0, 10), 2),
            "pm25": round(15 + progress * 50 + np.random.normal(0, 2), 2),
            "tvoc": round(50 + progress * 200 + np.random.normal(0, 5), 2)
        }
    },
    "plug_001": {
        "name": "Smart Plug (Room A)",
        "normal": lambda: {
            "p": round(45 + np.random.normal(0, 8), 2),
            "v": round(220 + np.random.normal(0, 2), 2),
            "c": round(0.2 + np.random.normal(0, 0.02), 3),
            "on": True,
            "e": round(1.2 + np.random.uniform(0, 0.5), 2)
        },
        "anomaly": lambda progress: {
            "p": round(45 + progress * 100 + np.random.normal(0, 5), 2),
            "v": round(220 + np.random.normal(0, 3), 2),
            "c": round(0.2 + progress * 0.5 + np.random.normal(0, 0.01), 3),
            "on": True,
            "e": round(1.2 + np.random.uniform(0, 0.5), 2)
        }
    }
}

# ================== SIMULATOR ==================
class IoTSimulator:
    """Simulator gui du lieu sensor qua IoT Agent JSON."""

    def __init__(self, interval=5, mode="normal"):
        self.interval = interval
        self.mode = mode
        self.running = True
        self.tick = 0
        self.anomaly_start = None
        self.anomaly_duration = 60  # 60 ticks (~5 phut voi interval=5s)
        self.send_count = 0
        self.error_count = 0

        signal.signal(signal.SIGINT, self._handle_stop)

    def _handle_stop(self, sig, frame):
        """Xu ly Ctrl+C."""
        print(f"\n\nDung simulator. Tong: {self.send_count} readings gui, {self.error_count} loi.")
        self.running = False
        sys.exit(0)

    def send_data(self, device_id, payload):
        """Gui du lieu len IoT Agent south port."""
        url = f"{IOT_AGENT_SOUTH_URL}?k={API_KEY}&i={device_id}"
        headers = {
            "Content-Type": "application/json",
            "fiware-service": FIWARE_SERVICE,
            "fiware-servicepath": FIWARE_SERVICEPATH
        }

        try:
            r = requests.post(url, json=payload, headers=headers, timeout=5)
            if r.status_code == 200:
                self.send_count += 1
                return True
            else:
                self.error_count += 1
                print(f"      LOI {device_id}: {r.status_code} - {r.text[:100]}")
                return False
        except requests.exceptions.ConnectionError:
            self.error_count += 1
            if self.error_count <= 3:
                print(f"      KHONG KET NOI DUOC IoT Agent (port 7896)")
                print(f"      -> Chay: docker compose -f fiware/docker-compose.yml up -d")
            return False
        except Exception as e:
            self.error_count += 1
            print(f"      LOI {device_id}: {e}")
            return False

    def _get_anomaly_progress(self):
        """Tinh muc do anomaly (0.0 -> 1.0)."""
        if self.anomaly_start is None:
            return 0.0
        elapsed = self.tick - self.anomaly_start
        if elapsed >= self.anomaly_duration:
            return 1.0
        return elapsed / self.anomaly_duration

    def _should_inject_anomaly(self):
        """Kiem tra co inject anomaly hay khong."""
        if self.mode != "anomaly":
            return False

        # Bat dau anomaly sau 20 ticks (~100 giay)
        if self.anomaly_start is None and self.tick >= 20:
            self.anomaly_start = self.tick
            print("\n   !!! BAT DAU INJECT ANOMALY !!!\n")
            return True

        if self.anomaly_start is not None:
            if self.tick - self.anomaly_start < self.anomaly_duration:
                return True
            else:
                # Het anomaly -> recovery
                if self.tick - self.anomaly_start == self.anomaly_duration:
                    print("\n   >>> ANOMALY KET THUC - TRO VE BINH THUONG <<<\n")
                return False

        return False

    def run(self):
        """Chay simulator lien tuc."""
        print("=" * 70)
        print("CRUZRTWIN IoT SIMULATOR")
        print(f"   Mode: {self.mode.upper()}")
        print(f"   Interval: {self.interval}s")
        print(f"   Devices: {len(DEVICES)}")
        print(f"   IoT Agent: {IOT_AGENT_SOUTH_URL}")
        print(f"   API Key: {API_KEY}")
        print("=" * 70)
        print("\nNhan Ctrl+C de dung.\n")

        while self.running:
            self.tick += 1
            now = datetime.now().strftime("%H:%M:%S")
            is_anomaly = self._should_inject_anomaly()
            progress = self._get_anomaly_progress() if is_anomaly else 0.0

            mode_tag = "ANOMALY" if is_anomaly else "NORMAL"
            print(f"[{now}] Tick #{self.tick} ({mode_tag})", end="")
            if is_anomaly:
                print(f" progress={progress:.0%}", end="")
            print()

            for device_id, device_info in DEVICES.items():
                if is_anomaly:
                    payload = device_info["anomaly"](progress)
                else:
                    payload = device_info["normal"]()

                success = self.send_data(device_id, payload)
                if success:
                    # Hien thi 1 dong ngan gon
                    short_name = device_id.split("_")[0]
                    vals = ", ".join(f"{k}={v}" for k, v in payload.items())
                    print(f"   {short_name}: {vals}")

            print()
            time.sleep(self.interval)


# ================== MAIN ==================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CruzrTwin IoT Simulator")
    parser.add_argument("--mode", choices=["normal", "anomaly"], default="normal",
                        help="Che do: normal (binh thuong) hoac anomaly (co inject bat thuong)")
    parser.add_argument("--interval", type=int, default=5,
                        help="Khoang cach gui du lieu (giay), mac dinh: 5")
    args = parser.parse_args()

    simulator = IoTSimulator(interval=args.interval, mode=args.mode)
    simulator.run()
