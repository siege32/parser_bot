import requests
from bs4 import BeautifulSoup
import json

# url = "https://www.avito.ru/krasnoyarsk/avtomobili/audi-ASgBAgICAUTgtg3elyg?cd=1&radius=200&searchRadius=200"

# headers = {
#     "Accept": "application/json, text/plain, */*",
#     "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
# }

# req = requests.get(url, headers=headers)
# src = req.text
# print(src)

# with open("answers_on_quest", "w", encoding="utf-8") as file:
#     file.write(src)

with open("answers_on_quest", "r", encoding="utf-8") as file:
    src = file.read()

soup = BeautifulSoup(src, "lxml")

all_cars = soup.find_all("div", {"data-marker": "item"})

all_cars_dict = {}
for car in all_cars:
    header = car.find("h3").text
    link = "https://www.avito.ru" + car.find("a").get("href")
    all_cars_dict[header] = link

with open("all_cars", "w", encoding="utf-8") as file:
    json.dump(all_cars_dict, file, indent=4, ensure_ascii=False)