import aiohttp
from bs4 import BeautifulSoup
import asyncio
import logging
import sqlite3
from bot import bot_token
import aiosqlite
from random import uniform

stop_monitoring = {}  # Флаг остановки парсинга для каждого пользователя

headers = {
    "Accept": "*/*",
    "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
}

async def save_initial_ads(chat_id, url):
    """Сохранение объявлений в БД при первом запуске мониторинга"""
    async with aiosqlite.connect('parserDB.db') as db:
        ads = await fetch_drom_data(url)

        for car_name, car_link, car_info, car_price in ads:
            await db.execute("INSERT OR IGNORE INTO processed_ads (chat_id, car_link) VALUES (?, ?)", (chat_id, car_link))

        await db.commit()


async def fetch_drom_data(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                soup = BeautifulSoup(await response.text(), 'lxml')
                cars_data = soup.find_all('div', class_='css-1f68fiz')

                results = []
                for car in cars_data:
                    car_name = car.find("h3").text
                    car_link = car.find("a").get("href")
                    car_info = car.find(class_='css-1fe6w6s').text
                    car_price = car.find(class_='css-1dv8s3l').text
                    results.append((car_name, car_link, car_info, car_price))
                return results
            return []


async def monitor_drom(chat_id):
    """Мониторинг новых объявлений"""
    global processed_ads
    bot = await bot_token()

    async with aiosqlite.connect('parserDB.db') as db:
        async with db.execute('SELECT city, min_price, max_price FROM clients WHERE chat_id = ?', (chat_id,)) as cursor:
            result = await cursor.fetchone()

        city, min_price, max_price = result
        url_drom = f"https://{city}.drom.ru/auto/all/?minprice={min_price}&maxprice={max_price}" if city else \
                   f"https://auto.drom.ru/all/?minprice={min_price}&maxprice={max_price}"

        await bot.send_message(chat_id, f"Начинаю поиск новых объявлений.\n<b>Город: {city or 'Все'}</b>\n<b>Мин. стоимость: {min_price or 'Не указано'}</b>\n<b>Макс. стоимость: {max_price or 'Не указано'}</b>", parse_mode="HTML")

        # ✅ Сохраняем все текущие объявления при запуске мониторинга
        await save_initial_ads(chat_id, url_drom)

        stop_monitoring[chat_id] = False  # Сбрасываем флаг остановки

        try:
            while not stop_monitoring.get(chat_id, False):
                ads = await fetch_drom_data(url_drom)

                for car_name, car_link, car_info, car_price in ads:
                    async with db.execute("SELECT 1 FROM processed_ads WHERE chat_id = ? AND car_link = ?", (chat_id, car_link)) as cursor:
                        exists = await cursor.fetchone()

                    if not exists:  # Если объявления нет в БД, отправляем
                        await bot.send_message(chat_id, f"Новое объявление:\n\n<b>{car_name}</b>\n{car_info}\n{car_price}\n<a href='{car_link}'>Ссылка</a>", parse_mode="HTML")
                        await db.execute("INSERT INTO processed_ads (chat_id, car_link) VALUES (?, ?)", (chat_id, car_link))
                        await db.commit()

                await asyncio.sleep(uniform(15, 30))
        finally:
            await bot.session.close()  # ✅ Закрываем сессию бота

    



# def transliterate(name):
#    # Слоаврь с заменами
#    slovar = {'а':'a','б':'b','в':'v','г':'g','д':'d','е':'e','ё':'yo',
#       'ж':'zh','з':'z','и':'i','й':'i','к':'k','л':'l','м':'m','н':'n',
#       'о':'o','п':'p','р':'r','с':'s','т':'t','у':'u','ф':'f','х':'h',
#       'ц':'c','ч':'ch','ш':'sh','щ':'sch','ъ':'','ы':'y','ь':'','э':'e',
#       'ю':'u','я':'ya', 'А':'A','Б':'B','В':'V','Г':'G','Д':'D','Е':'E','Ё':'YO',
#       'Ж':'ZH','З':'Z','И':'I','Й':'I','К':'K','Л':'L','М':'M','Н':'N',
#       'О':'O','П':'P','Р':'R','С':'S','Т':'T','У':'U','Ф':'F','Х':'H',
#       'Ц':'C','Ч':'CH','Ш':'SH','Щ':'SCH','Ъ':'','Ы':'y','Ь':'','Э':'E',
#       'Ю':'U','Я':'YA',',':'','?':'',' ':'_','~':'','!':'','@':'','#':'',
#       '$':'','%':'','^':'','&':'','*':'','(':'',')':'','-':'','=':'','+':'',
#       ':':'',';':'','<':'','>':'','\'':'','"':'','\\':'','/':'','№':'',
#       '[':'',']':'','{':'','}':'','ґ':'','ї':'', 'є':'','Ґ':'g','Ї':'i',
#       'Є':'e', '—':''}
        
#    # Циклически заменяем все буквы в строке
#    for key in slovar:
#       name = name.replace(key, slovar[key])
#    return name