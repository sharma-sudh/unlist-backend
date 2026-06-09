import requests
import re
import json

def get_car_id(listing_url):
    match = re.search(r'/(\d+)/\??', listing_url)
    return match.group(1) if match else None

def fetch_report(listing_url):
    car_id = get_car_id(listing_url)
    if not car_id:
        return None

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    base = f"https://api.spinny.com/v3/api/pdp/get/inspection-data/?format=json&lead_id={car_id}"

    # car info
    product_data = requests.get(
        f"https://www.spinny.com/api/product-detail/fetch-page-data/{car_id}/",
        headers=headers
    ).json()
    product = product_data["productDetail"]
    car_info = {
        "title": f"{product['make_year']} {product['make']} {product['model']} {product['variant']['display_name']}",
        "km": product["productMileage"],
        "fuel": product["fuel_type"],
        "city": product["city"],
        "price": product["productPrice"],
    }

    page2 = requests.get(base + "&page=2", headers=headers).json()
    page3 = requests.get(base + "&page=3", headers=headers).json()

    # from page 2: category-level summary
    categories_summary = {}
    for cat in page2["data"]["category_list"]:
        cat_name = cat["name"]
        categories_summary[cat_name] = {
            "rating": cat["rating"],
            "rating_verdict": cat["rating_verdict"],
            "brand_new_parts": [],
            "subcategories": {}
        }
        for bucket in cat.get("brand_new_part_list", []):
            for n2 in bucket.get("n2_list", []):
                categories_summary[cat_name]["brand_new_parts"].extend(n2["part_list"])
        for item in cat.get("n1_items", []):
            categories_summary[cat_name]["subcategories"][item["title"]] = {
                "statement": item["statement"],
                "flawless": item["flawless"],
                "tyre_life": item["meta_data"].get("life_remaining", [])
            }

    # from page 3: part-level faults
    faults_by_subcategory = {}
    for subcat_key, subcat_data in page3["data"].items():
        if not isinstance(subcat_data, dict):
            continue
        parts = []
        for condition in ["imperfection", "flawless"]:
            if condition not in subcat_data:
                continue
            for part in subcat_data[condition].get("part_list", []):
                parts.append({
                    "name": part["name"],
                    "soc": part.get("soc", ""),
                    "is_critical": part.get("is_critical", False),
                    "condition": condition
                })
        if parts:
            faults_by_subcategory[subcat_key] = parts

    return {
        "car_id": car_id,
        "car": car_info,
        "categories": categories_summary,
        "parts": faults_by_subcategory
    }

if __name__ == "__main__":
    url = "https://www.spinny.com/buy-used-cars/jaipur/hyundai/elite-i20/sportz-plus-12-ajmer-road-2019/29483061/?referrer=/used-cars-in-jaipur/s/"
    result = fetch_report(url)
    print(json.dumps(result, indent=2))