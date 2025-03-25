import random
import time
import random
import requests
from bs4 import BeautifulSoup

cars = []
for i in range(1, 101):
    url = f"https://krasnoyarsk.drom.ru/auto/page{i}/?maxprice=100000"
    print(url)

    response = requests.get(url)
    html_soup = BeautifulSoup(response.text, 'html.parser')
    cars_data = html_soup.find_all('div', class_='css-1f68fiz')

    if cars_data != []:
        cars.extend(cars_data)
        scaled_value = 1 + (random.random() * (9 - 5))
        print(scaled_value)
        time.sleep(scaled_value)
    else:
        print('Пусто')
        break

print(len(cars))
print()

for i in range(10):
    info = cars[i]
    price = info.find('span', {"class": "css-46itwz"}).text
    title = info.find('a', {"class": "g6gv8w4"}).text
    print(f'''
Название: {title}
Цена: {price}
          ''')