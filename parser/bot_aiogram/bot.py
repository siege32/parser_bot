import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram import F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from config_reader import config
from dotenv import load_dotenv
from handlers import questions



# Апдейт — любое событие из этого списка: сообщение, редактирование сообщения, колбэк, инлайн-запрос, платёж, добавление бота в группу и т.д.
# Хэндлер — асинхронная функция, которая получает от диспетчера/роутера очередной апдейт и обрабатывает его.
# Диспетчер — объект, занимающийся получением апдейтов от Telegram с последующим выбором хэндлера для обработки принятого апдейта.
# Роутер — аналогично диспетчеру, но отвечает за подмножество множества хэндлеров. Можно сказать, что диспетчер — это корневой роутер.
# Фильтр — выражение, которое обычно возвращает True или False и влияет на то, будет вызван хэндлер или нет.
# Мидлварь — прослойка, которая вклинивается в обработку апдейтов.

async def bot_token():
    return Bot(
        token=config.bot_token.get_secret_value(),
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML
            # тут ещё много других интересных настроек
        )
    )

# Запуск процесса поллинга новых апдейтов
async def main():
    # Загрузить .env перед использованием Settings
    load_dotenv()

    # Включаем логирование, чтобы не пропустить важные сообщения
    logging.basicConfig(level=logging.INFO)

    bot = await bot_token()

    # Диспетчер
    dp = Dispatcher()
    dp.include_router(questions.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)



if __name__ == "__main__":
    asyncio.run(main())
