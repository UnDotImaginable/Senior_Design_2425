import requests
import threading
import time

BASE_URL = "http://3.19.232.240:8000"


# Send every 10 seconds
def send_reading(url, info):
    while True:
        try:
            # Won't wait for this to finish
            requests.post(url, info)
        except requests.exceptions.RequestException:
            pass

        time.sleep(10)


def get_switch_decision():
    return None


def confirm_switch():
    return None


if __name__ == "__main__":
    thread = threading.Thread(
        target=send_reading, kwargs={
            "url": str(BASE_URL),
            "info": {
                "battery_level": battery_level,
                "power_source": power_source,
                "voltage": voltage,
                "current": current,
                "temperature": temperature
            }
        }
    )  
    thread.start()


  
