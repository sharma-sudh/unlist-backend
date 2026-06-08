import requests
import re

def get_appointment_id(url):
    # handle short URLs like cars24.world/y9amwk
    if "cars24.world" in url:
        response = requests.get(url, allow_redirects=True)
        url = response.url
    match = re.search(r'-(\d{10,})(?:/|$|\?)', url)
    return match.group(1) if match else None

def fetch_report(listing_url):
    appointment_id = get_appointment_id(listing_url)
    if not appointment_id:
        return None

    headers = {
        "accept": "application/json",
        "accept-language": "en-US,en;q=0.9",
        "x-client-type": "APP_ANDROID",
        "content-type": "application/json",
        "appversion": "601",
        "osname": "android",
        "source": "MobileApp",
        "useragent": "cars24CustomerApp/601",
        "user-agent": "okhttp/4.12.0",
    }

    response = requests.post(
        "https://car-catalog-gateway-in.c24.tech/detail/v1/",
        headers=headers,
        json={"appointmentId": appointment_id}
    )
    data = response.json()["detail"]

    car_info = {
        "title": f"{data['year']} {data['make']} {data['model']} {data['variant']}",
        "km": data["odometerReading"],
        "fuel": data["fuelType"],
        "city": data["city"]["name"],
        "price": data["listingPrice"],
        "transmission": data["transmission"],
        "owner_number": data["ownerNumberDisplay"],
    }

    # inspection report
    car_condition = data.get("carCondition", {})
    categories = {}
    for cat in car_condition.get("categories", []):
        categories[cat["key"]] = {
            "label": cat["label"],
            "status": cat["status"],
            "issues": cat["value"],
            "description": cat.get("description", "")
        }

    checkpoints = {}
    for cp in car_condition.get("checkpoints", []):
        cat = cp["category"]
        if cat not in checkpoints:
            checkpoints[cat] = []
        checkpoints[cat].append({
            "key": cp["key"],
            "label": cp["label"],
            "status": cp["status"],
            "infos": cp.get("infos", [])
        })

    return {
        "appointment_id": appointment_id,
        "car": car_info,
        "repainted": car_condition.get("repainted", False),
        "categories": categories,
        "checkpoints": checkpoints,
        "tyre_life": {
            cp["key"]: {"label": cp["label"], "value": cp.get("value"), "status": cp["status"]}
            for cp in car_condition.get("checkpoints", [])
            if cp.get("category") == "tyresLife"
        }
    }