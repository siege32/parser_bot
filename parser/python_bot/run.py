from aiogram import Router, F, types
from aiogram.filters import CommandStart
from aiogram.types import Message
import aiohttp
from bs4 import BeautifulSoup
import asyncio
import random

headers = {
    "Accept": "*/*",
    "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
}

dict_with_cars = {}

# Асинхронный парсер
async def car_monitoring(value, message: Message):
    while True:
        await asyncio.sleep(random.uniform(0.5, 2))
        url_drom = f"https://auto.drom.ru/all/?maxprice={value}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url_drom, headers=headers) as response:
                html = await response.text()
        soup = BeautifulSoup(html, 'lxml')
        cars_data = soup.find_all('div', class_='css-1f68fiz')

        for car in cars_data:
            car_name = car.find("h3").text
            car_link = car.find("a").get("href")
            if car_link not in dict_with_cars.keys():
                dict_with_cars[car_link] = car_name
                await message.answer(dict_with_cars[car_link])

# Настройка роутера
start_router = Router()
user_data = {}

@start_router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer('Введите ВЕРРХНЮЮ стоимость авто')
    user_data[message.from_user.id] = "awaiting_price"

@start_router.message(F.text)
async def process_price(message: Message):
    user_id = message.from_user.id

    # Проверяем, ожидает ли пользователь ввода стоимости
    if user_data.get(user_id) == "awaiting_price":
        try:
            price = int(message.text)  # Пробуем преобразовать сообщение в число
            await message.answer(f"Вы ввели корректную стоимость: {price}")

            # Удаляем состояние пользователя
            user_data.pop(user_id, None)

            # Запускаем асинхронный парсер
            await car_monitoring(price, message)  # Ожидаем выполнения асинхронного кода

        except ValueError:
            # Удаляем состояние только в случае некорректного ввода
            user_data.pop(user_id, None)
            await message.answer("Пожалуйста, введите корректное число")
