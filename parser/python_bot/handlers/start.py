from aiogram import Router, F, types
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
import requests
from bs4 import BeautifulSoup
import time
import random



headers = {
    "Accept": "*/*",
    "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
}

dict_with_cars = {}

def car_monitoring(value):
    while True:
        time.sleep(random.uniform(0.5, 2))
        
        url_drom = f"https://auto.drom.ru/all/?maxprice={value}"

        req = requests.get(url_drom, headers=headers)

        soup = BeautifulSoup(req.text, 'lxml')
        cars_data = soup.find_all('div', class_='css-1f68fiz')
        # print(cars_data)

        for car in cars_data:
            car_name =  car.find("h3").text
            car_link = car.find("a").get("href")
            if car_link not in dict_with_cars.keys():
                dict_with_cars[car_link] = car_name
                print(dict_with_cars[car_link])

start_router = Router()
user_data = {}

@start_router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer('Введите ВЕРРХНЮЮ стоимость авто')
    user_data[message.from_user.id] = "awaiting_price"

@start_router.message(F.text)
async def process_price(message: Message):
    user_id = message.from_user.id

    if user_id == "awaiting_price":
        try:
            price = int(message.text)
            await message.answer(f"Вы ввели корректную стоимость: {price}")
            
            # Очищаем состояние для пользователя
            user_data.pop(user_id, None)
        except ValueError:
            # Сообщение не является числом
            await message.answer("Пожалуйста, введите корректное число")

    car_monitoring(price)