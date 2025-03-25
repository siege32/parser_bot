from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
import asyncio
import sqlite3

from keyboards.parametrs import get_filters_kb, which_get_filtres_kb, stop_search_kb, back_kb

from parse_auto import monitor_drom

router = Router()

class ParseSite(StatesGroup):
    first_state = State()
    turn_filters = State()
    choosing_filters = State()
    without_filters = State()
    choose_city = State()
    choose_max_value = State()
    choose_min_value = State()
    run_parse = State()
    stop_search = State()

@router.message(Command("start")) # Состояние 1.0 СТАРТ
async def cmd_start(message: Message, state: FSMContext):
    await message.answer("Привет! Я буду уведомлять тебя о новых объявлениях на Drom.ru.")
    await state.set_state(ParseSite.first_state)
    await cmd_start2(message, state)

@router.message(ParseSite.first_state) # Состояние 1.1 СТАРТ
async def cmd_start2(message: Message, state: FSMContext):
    global connection, cursor, chat_id
    connection = sqlite3.connect('parserDB.db')
    cursor = connection.cursor()

    chat_id = message.chat.id

    cursor.execute("SELECT COUNT(*) FROM clients WHERE chat_id = ?", (chat_id,))
    result = cursor.fetchone()[0]

    if result == 0:
        cursor.execute("INSERT INTO clients (chat_id, city, min_price, max_price) VALUES (?, NULL, NULL, NULL)", (chat_id,))
        connection.commit()

    await message.answer("Необходимо добавить параметры или искать авто без параметров.", reply_markup=get_filters_kb())
    await state.set_state(ParseSite.turn_filters)

@router.message(ParseSite.turn_filters, F.text.lower() == "добавить параметры") # Состояние 2.1
async def answer_add_filters(message: Message, state: FSMContext):
    cursor.execute("SELECT city, min_price, max_price FROM clients WHERE chat_id = ?", (chat_id,))
    result = cursor.fetchone()

    city_ru, min_price, max_price = result if result else ("Не указано", "Не указано", "Не указано")

    await message.answer(f"""Выберите фильтр, который хотите установить или начните поиск.
    
Ваши текущие параметры:
Город: <b>{city_ru}</b>
Минимальная стоимость: <b>{min_price}</b>
Максимальная стоимость: <b>{max_price}</b>""", reply_markup=which_get_filtres_kb())

    await state.set_state(ParseSite.choosing_filters)

@router.message(ParseSite.choosing_filters, F.text.lower() == "город") # Состояние 2.1.1
async def get_city(message: Message, state: FSMContext): 
    await message.answer("Напишите название города, по которому хотите смотреть объявления:", reply_markup=back_kb())
    await state.set_state(ParseSite.choose_city)

@router.message(ParseSite.choose_city)
async def choose_city(message: Message, state: FSMContext):
    global city_ru
    city_ru = message.text
    if city_ru != "Назад":
        cursor.execute("SELECT city_name_en FROM cities WHERE city_name_ru = ?", (city_ru,))
        city_result = cursor.fetchone()

        if city_result:  # Если город найден
            city_en = city_result[0]  # ✅ Извлекаем строку из кортежа
            cursor.execute("UPDATE clients SET city = ? WHERE chat_id = ?", (city_en, chat_id))
            connection.commit()
            await message.answer("Город добавлен.")
        else:
            await message.answer("Город не найден в базе. Попробуйте снова.")

    await state.set_state(ParseSite.turn_filters)
    await answer_add_filters(message, state)
    
@router.message(ParseSite.choosing_filters, F.text.lower() == "минимальная стоимость") # Состояние 2.1.2
async def get_min_value(message: Message, state: FSMContext): 
    await message.answer("Напишите минимальную стоимость авто:", reply_markup=back_kb())
    await state.set_state(ParseSite.choose_min_value)

@router.message(ParseSite.choose_min_value)
async def choose_min_value(message: Message, state: FSMContext):
    min_value = message.text
    if min_value != "Назад":
        try:
            min_value = int(message.text)  # Пробуем преобразовать сообщение в число
            await message.answer(f"Вы ввели корректную стоимость: {min_value}")
            cursor.execute("UPDATE clients SET min_price = ? WHERE chat_id = ?", (min_value, chat_id))
            connection.commit()
        except ValueError:
            await message.answer("Пожалуйста, введите корректное число")
    await state.set_state(ParseSite.turn_filters)
    await answer_add_filters(message, state)

@router.message(ParseSite.choosing_filters, F.text.lower() == "максимальная стоимость") # Состояние 2.1.3
async def get_max_value(message: Message, state: FSMContext): 
    await message.answer("Напишите максимальную стоимость авто:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(ParseSite.choose_max_value)

@router.message(ParseSite.choose_max_value)
async def choose_max_value(message: Message, state: FSMContext):
    max_value = message.text
    if max_value != "Назад":
        try:
            max_value = int(message.text)  # Пробуем преобразовать сообщение в число
            await message.answer(f"Вы ввели корректную стоимость: {max_value}")
            cursor.execute("UPDATE clients SET max_price = ? WHERE chat_id = ?", (max_value, chat_id))
            connection.commit()
        except ValueError:
            await message.answer("Пожалуйста, введите корректное число")
    await state.set_state(ParseSite.turn_filters)
    await answer_add_filters(message, state)

@router.message(ParseSite.choosing_filters, F.text.lower() == "поиск") # Состояние 2.1.4
async def search_with_params(message: Message, state: FSMContext):
    await state.set_state(ParseSite.run_parse)
    await run_parse(message, state)

@router.message(ParseSite.turn_filters, F.text.lower() == "искать без параметров") # Состояние 2.2
async def search_without_params(message: Message, state: FSMContext):
    await state.set_state(ParseSite.run_parse)
    await run_parse(message, state)

@router.message(ParseSite.run_parse)  # Состояние 3
async def run_parse(message: Message, state: FSMContext):
    global chat_id
    chat_id = message.chat.id

    await message.answer("Начинаю отслеживать объявления.", reply_markup=stop_search_kb())

    # Закрываем соединение с БД
    connection.commit
    connection.close()

    # Запуск мониторинга в фоне
    asyncio.create_task(monitor_drom(chat_id))

    # Устанавливаем состояние в first_state после завершения поиска
    await state.set_state(ParseSite.stop_search)

@router.message(ParseSite.stop_search, F.text.lower() == "остановить поиск")
async def stop_search(message: Message, state: FSMContext):
    from parse_auto import stop_monitoring  # Импортируем флаг остановки

    stop_monitoring[message.chat.id] = True  # Устанавливаем флаг остановки

    await message.answer("Поиск остановлен. Возвращаюсь в главное меню.", reply_markup=get_filters_kb())

    await state.set_state(ParseSite.first_state)
    await cmd_start2(message, state)

@router.message(ParseSite.turn_filters) # Ошибка состояния 1
async def cmd_start_incorrectly(message: Message):
    await message.answer(
        text="Я не знаю такого ответа.\n\n"
             "Пожалуйста, выберите один из списка ниже:",
        reply_markup=get_filters_kb()
    )

@router.message(ParseSite.choosing_filters) # Ошибка состояния 2.1
async def answer_add_filters_incorrectly(message: Message):
    await message.answer(
        text="Я не знаю такого ответа.\n\n"
             "Пожалуйста, выберите один из списка ниже:",
        reply_markup=which_get_filtres_kb()
    )