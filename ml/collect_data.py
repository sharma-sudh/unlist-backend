import csv
import json
from scrapers.spinny_scraper import fetch_report as fetch_spinny
from parsers.spinny_parser import parse_report as parse_spinny
from scrapers.cars24_scraper import fetch_report as fetch_cars24
from parsers.cars24_parser import parse_report as parse_cars24

SPINNY_URLS = [
    "https://www.spinny.com/buy-used-cars/gurgaon/jeep/compass/limited-plus-petrol-at-sector-29-2019/28944980/?referrer=/used-cars-in-delhi-ncr/s/",
    "https://www.spinny.com/buy-used-cars/delhi/maruti-suzuki/ciaz/zxi-o-rohini-sector-10-2015/29449585/?referrer=/used-cars-in-delhi-ncr/s/",
    "https://www.spinny.com/buy-used-cars/gurgaon/maruti-suzuki/baleno/delta-mt-2022/29325079/?referrer=/used-cars-in-delhi-ncr/s/",
    "https://www.spinny.com/buy-used-cars/ghaziabad/hyundai/eon/magna-indirapuram-2014/28880871/?referrer=/used-cars-in-delhi-ncr/s/",
    "https://www.spinny.com/buy-used-cars/ghaziabad/maruti-suzuki/baleno/delta-raj-nagar-extension-2022/29264179/?referrer=/used-cars-in-delhi-ncr/s/",
    "https://www.spinny.com/buy-used-cars/faridabad/mahindra/xuv700/ax-7-petrol-at-7-str-sector-27-2021/29399917/?referrer=/used-cars-in-delhi-ncr/s/",
    "https://www.spinny.com/buy-used-cars/gurgaon/toyota/urban-cruiser/high-grade-mt-2022/28972389/?referrer=/used-cars-in-delhi-ncr/s/",
    "https://www.spinny.com/buy-used-cars/gurgaon/skoda/slavia/ambition-10l-tsi-at-2023/29517603/?referrer=/used-cars-in-delhi-ncr/s/",
    "https://www.spinny.com/buy-used-cars/delhi/hyundai/verna/sx-15-petrol-mt-2023/28823833/?referrer=/used-cars-in-delhi-ncr/s/",
    "https://www.spinny.com/buy-used-cars/ghaziabad/hyundai/venue/sx-plus-10-turbo-dct-2019/29291557/?referrer=/used-cars-in-delhi-ncr/s/",
    "https://www.spinny.com/buy-used-cars/ghaziabad/mg-motors/hector/savvy-pro-15-turbo-petrol-cvt-2023/29449270/?referrer=/used-cars-in-delhi-ncr/s/",
    "https://www.spinny.com/buy-used-cars/ghaziabad/hyundai/creta/sx-15-petrol-executive-2022/29418174/?referrer=/used-cars-in-delhi-ncr/s/",
    "https://www.spinny.com/buy-used-cars/gurgaon/maruti-suzuki/celerio/vxi-amt-2014/29593474/?referrer=/used-cars-in-delhi-ncr/s/",
    "https://www.spinny.com/buy-used-cars/gurgaon/volkswagen/taigun/topline-10-tsi-at-2022/29174710/?referrer=/used-cars-in-delhi-ncr/s/",
    "https://www.spinny.com/buy-used-cars/ghaziabad/maruti-suzuki/baleno/zeta-12-2016/29499323/?referrer=/used-cars-in-delhi-ncr/s/",
    "https://www.spinny.com/buy-used-cars/delhi/hyundai/elite-i20/asta-o-cng-outside-fitted-2018/29167440/?referrer=/used-cars-in-delhi-ncr/s/",
    "https://www.spinny.com/buy-used-cars/noida/tata/tiago/xza-plus-2023/29491312/?referrer=/used-cars-in-delhi-ncr/s/",
    "https://www.spinny.com/buy-used-cars/faridabad/maruti-suzuki/wagon-r/lxi-cng-2018/28652434/?referrer=/used-cars-in-delhi-ncr/s/",
    "https://www.spinny.com/buy-used-cars/gurgaon/kia/seltos/gtx-plus-15-turbo-petrol-dct-2025/29423431/?referrer=/used-cars-in-delhi-ncr/s/",
    "https://www.spinny.com/buy-used-cars/gurgaon/bmw/5-series/530li-m-sport-titanium-bronze-sector-29-2026/27322562/?referrer=/used-cars-in-delhi-ncr/s/",
    "https://www.spinny.com/buy-used-cars/gurgaon/jeep/compass/limited-plus-petrol-at-sector-29-2019/27955308/?referrer=/used-cars-in-delhi-ncr/s/",
    "https://www.spinny.com/buy-used-cars/gurgaon/audi/q3/40-tfsi-premium-plus-sector-29-2023/28885782/?referrer=/used-cars-in-delhi-ncr/s/",
    "https://www.spinny.com/buy-used-cars/noida/hyundai/santro/sportz-amt-2020/29069006/?referrer=/used-cars-in-delhi-ncr/s/",
    "https://www.spinny.com/buy-used-cars/gurgaon/kia/seltos/htk-plus-15-2022/29584351/?referrer=/used-cars-in-delhi-ncr/s/",
    "https://www.spinny.com/buy-used-cars/gurgaon/hyundai/venue/sx-plus-10-turbo-dct-2020/29712149/?referrer=/used-cars-in-delhi-ncr/s/",
    "https://www.spinny.com/buy-used-cars/gurgaon/mg-motors/hector/15-sharp-cvt-dual-tone-2022/29633739/?referrer=/used-cars-in-delhi-ncr/s/",
    "https://www.spinny.com/buy-used-cars/noida/hyundai/new-i20/asta-o-10-turbo-dct-2022/29626005/?referrer=/used-cars-in-delhi-ncr/s/",
    "https://www.spinny.com/buy-used-cars/noida/hyundai/verna/sx-15-turbo-petrol-dct-2023/28592652/?referrer=/used-cars-in-delhi-ncr/s/",
    "https://www.spinny.com/buy-used-cars/gurgaon/mahindra/xuv-300/w8-12-petrol-2022/29332594/?referrer=/used-cars-in-delhi-ncr/s/",
    "https://www.spinny.com/buy-used-cars/noida/hyundai/venue/sx-plus-10-turbo-dct-2020/29361391/?referrer=/used-cars-in-delhi-ncr/s/",
    "https://www.spinny.com/buy-used-cars/delhi/mg-motors/hector-plus/savvy-pro-15-turbo-petrol-cvt-6-str-dual-tone-2023/29247303/?referrer=/used-cars-in-delhi-ncr/s/",
    "https://www.spinny.com/buy-used-cars/gurgaon/honda/amaze/vx-12-petrol-cvt-2024/27928660/?referrer=/used-cars-in-delhi-ncr/s/",
    "https://www.spinny.com/buy-used-cars/ghaziabad/mg-motors/hector/savvy-pro-15-turbo-cvt-2024/29347247/?referrer=/used-cars-in-delhi-ncr/s/",
    "https://www.spinny.com/buy-used-cars/delhi/honda/city/v-petrol-2017/28849718/?referrer=/used-cars-in-delhi-ncr/s/",
    "https://www.spinny.com/buy-used-cars/gurgaon/mercedes-benz/gla/200-sport-sector-29-2018/29256979/?referrer=/used-cars-in-delhi-ncr/s/",
    "https://www.spinny.com/buy-used-cars/gurgaon/honda/city/vx-petrol-cvt-2023/29543843/?referrer=/used-cars-in-delhi-ncr/s/",
    "https://www.spinny.com/buy-used-cars/noida/volkswagen/taigun/gt-plus-15-tsi-dsg-2022/29255042/?referrer=/used-cars-in-delhi-ncr/s/",
    "https://www.spinny.com/buy-used-cars/gurgaon/skoda/octavia/18-tsi-style-at-2017/28840066/?referrer=/used-cars-in-delhi-ncr/s/",
    "https://www.spinny.com/buy-used-cars/gurgaon/tata/altroz/xt-petrol-2020/28443453/?referrer=/used-cars-in-delhi-ncr/s/",
    "https://www.spinny.com/buy-used-cars/gurgaon/maruti-suzuki/grand-vitara/zeta-smart-hybrid-2024/29250353/?referrer=/used-cars-in-delhi-ncr/s/",
    "https://www.spinny.com/buy-used-cars/gurgaon/lexus/es/300h-luxury-sector-29-2018/27655482/?referrer=/used-cars-in-delhi-ncr/s/",
    "https://www.spinny.com/buy-used-cars/gurgaon/audi/q3/40-tfsi-premium-plus-sector-29-2023/28856880/?referrer=/used-cars-in-delhi-ncr/s/",
    "https://www.spinny.com/buy-used-cars/ghaziabad/maruti-suzuki/wagon-r/vxi-10-cng-2024/29597073/?referrer=/used-cars-in-delhi-ncr/s/",
    "https://www.spinny.com/buy-used-cars/delhi/maruti-suzuki/baleno/zeta-2019/28868200/?referrer=/used-cars-in-delhi-ncr/s/",
    "https://www.spinny.com/buy-used-cars/noida/maruti-suzuki/wagon-r/vxi-2015/29332201/?referrer=/used-cars-in-delhi-ncr/s/",
    "https://www.spinny.com/buy-used-cars/gurgaon/maruti-suzuki/alto-800/lxi-2018/29272796/?referrer=/used-cars-in-delhi-ncr/s/",
    "https://www.spinny.com/buy-used-cars/noida/hyundai/grand-i10-nios/era-12-kappa-2024/29468968/?referrer=/used-cars-in-delhi-ncr/s/",
    "https://www.spinny.com/buy-used-cars/gurgaon/hyundai/grand-i10-nios/sportz-12-kappa-vtvt-2022/29403143/?referrer=/used-cars-in-delhi-ncr/s/",
    "https://www.spinny.com/buy-used-cars/delhi/skoda/octavia/18-tsi-lk-2018/25665822/?referrer=/used-cars-in-delhi-ncr/s/",
    "https://www.spinny.com/buy-used-cars/ghaziabad/tata/punch/accomplished-mt-2023/29475736/?referrer=/used-cars-in-delhi-ncr/s/"
]

CARS24_URLS = [
    "https://www.cars24.com/buy-used-mahindra-scorpio-classic-2023-cars-gurgaon-44501867728/",
    "https://www.cars24.com/buy-used-maruti-swift-2015-cars-gurgaon-27250768708/",
    "https://www.cars24.com/buy-used-renault-kwid-2021-cars-new-delhi-19020092174/",
    "https://www.cars24.com/buy-used-maruti-swift-2014-cars-ghaziabad-18506796111/",
    "https://www.cars24.com/buy-used-hyundai-eon-2015-cars-new-delhi-13421894115/",
    "https://www.cars24.com/buy-used-ford-freestyle-2019-cars-ghaziabad-13804160718/",
    "https://www.cars24.com/buy-used-tata-nexon-2023-cars-gurgaon-13355961787/",
    "https://www.cars24.com/buy-used-honda-city-2017-cars-new-delhi-10314195150/",
    "https://www.cars24.com/buy-used-renault-kwid-2017-cars-noida-10074669750/",
    "https://www.cars24.com/buy-used-ford-ecosport-2016-cars-gurgaon-16341585724/",
    "https://www.cars24.com/buy-used-hyundai-creta-2018-cars-new-delhi-11403695190/",
    "https://www.cars24.com/buy-used-maruti-swift-2018-cars-gurgaon-11009993186/",
    "https://www.cars24.com/buy-used-renault-kwid-2017-cars-gurgaon-41330195114/",
    "https://www.cars24.com/buy-used-renault-kwid-2016-cars-noida-13806693116/",
    "https://www.cars24.com/buy-used-maruti-new-wagon-r-2021-cars-noida-13814493155/",
    "https://www.cars24.com/buy-used-mahindra-xuv700-2023-cars-gurgaon-11576261700/",
    "https://www.cars24.com/buy-used-maruti-baleno-2019-cars-new-delhi-11073391133/",
    "https://www.cars24.com/buy-used-maruti-eeco-2023-cars-gurgaon-10030062777/",
    "https://www.cars24.com/buy-used-tata-punch-2023-cars-gurgaon-12039494151/",
    "https://www.cars24.com/buy-used-hyundai-grand-i10-2018-cars-gurgaon-10110692177/",
    "https://www.cars24.com/buy-used-toyota-glanza-2023-cars-faridabad-29902666737/",
    "https://www.cars24.com/buy-used-hyundai-elite-i20-2016-cars-new-delhi-17259092186/",
    "https://www.cars24.com/buy-used-datsun-redi-go-2017-cars-new-delhi-10765441701/",
    "https://www.cars24.com/buy-used-honda-amaze-2018-cars-noida-44569663772/",
    "https://www.cars24.com/buy-used-maruti-wagon-r-1.0-2017-cars-new-delhi-15531099155/",
    "https://www.cars24.com/buy-used-hyundai-grand-i10-2017-cars-new-delhi-10083594138/",
    "https://www.cars24.com/buy-used-maruti-swift-2022-cars-gurgaon-13393969786/",
    "https://www.cars24.com/buy-used-maruti-baleno-2017-cars-new-delhi-11042564742/",
    "https://www.cars24.com/buy-used-maruti-alto-800-2013-cars-noida-25163700743/",
    "https://www.cars24.com/buy-used-tata-tiago-2020-cars-new-delhi-11281994188/",
    "https://www.cars24.com/buy-used-renault-kwid-2019-cars-noida-10044661716/",
    "https://www.cars24.com/buy-used-renault-kwid-2019-cars-noida-10044661716/",
    "https://www.cars24.com/buy-used-maruti-baleno-2019-cars-gurgaon-13381796171/",
    "https://www.cars24.com/buy-used-maruti-new-wagon-r-2019-cars-noida-10074694157/",
    "https://www.cars24.com/buy-used-honda-city-2015-cars-new-delhi-13205195196/",
    "https://www.cars24.com/buy-used-datsun-redi-go-2018-cars-new-delhi-11520364762/",
    "https://www.cars24.com/buy-used-renault-triber-2019-cars-noida-11290696197/",
    "https://www.cars24.com/buy-used-maruti-swift-2017-cars-new-delhi-11570260707/",
    "https://www.cars24.com/buy-used-hyundai-verna-2015-cars-new-delhi-10040067760/",
    "https://www.cars24.com/buy-used-renault-triber-2020-cars-new-delhi-44513399113/",
    "https://www.cars24.com/buy-used-kia-seltos-2019-cars-faridabad-10159598183/",
    "https://www.cars24.com/buy-used-ford-ecosport-2016-cars-gurgaon-10056598153/",
    "https://www.cars24.com/buy-used-honda-city-2016-cars-gurgaon-10148094157/",
    "https://www.cars24.com/buy-used-hyundai-creta-2017-cars-noida-13808399153/",
    "https://www.cars24.com/buy-used-kia-sonet-2021-cars-new-delhi-10064592180/",
    "https://www.cars24.com/buy-used-toyota-yaris-2018-cars-gurgaon-41315795150/",
    "https://www.cars24.com/buy-used-maruti-swift-dzire-2016-cars-new-delhi-11434965721/",
    "https://www.cars24.com/buy-used-toyota-innova-crysta-2018-cars-new-delhi-10006893176/",
    "https://www.cars24.com/buy-used-kia-carens-2023-cars-noida-13884597177/",
    "https://www.cars24.com/buy-used-toyota-corolla-altis-2016-cars-noida-11572392116/"
]

def collect(output_file="faults.csv"):
    rows = []

    for url in SPINNY_URLS:
        try:
            raw = fetch_spinny(url)
            if not raw:
                continue
            result = parse_spinny(raw)
            for bucket in ["critical_imperfections", "non_critical_imperfections", "restored_imperfections"]:
                for fault in result[bucket]:
                    rows.append({
                        "platform": "spinny",
                        "part": fault.get("part", ""),
                        "soc": fault.get("status", ""),
                        "subcategory": fault.get("subcategory", ""),
                        "is_critical": 1 if bucket == "critical_imperfections" else 0,
                        "severity": ""  # you fill this in
                    })
            print(f"OK: {url}")
        except Exception as e:
            print(f"FAILED: {url} — {e}")

    for url in CARS24_URLS:
        try:
            raw = fetch_cars24(url)
            if not raw:
                continue
            result = parse_cars24(raw)
            for fault in result["non_critical_imperfections"]:
                rows.append({
                    "platform": "cars24",
                    "part": fault.get("part", ""),
                    "soc": fault.get("status", ""),
                    "subcategory": fault.get("category", ""),
                    "is_critical": 0,
                    "severity": ""
                })
            print(f"OK: {url}")
        except Exception as e:
            print(f"FAILED: {url} — {e}")

    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["platform", "part", "soc", "subcategory", "is_critical", "severity"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nDone. {len(rows)} faults written to {output_file}")

if __name__ == "__main__":
    collect()