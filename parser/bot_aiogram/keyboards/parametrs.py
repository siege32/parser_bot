from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

def get_filters_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="Добавить параметры")
    kb.button(text="Искать без параметров")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)

def which_get_filtres_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="Город")
    kb.button(text="Минимальная стоимость")
    kb.button(text="Максимальная стоимость")
    kb.button(text="Поиск")
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)

def stop_search_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="Остановить поиск")
    return kb.as_markup(resize_keyboard=True)

def back_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="Назад")
    return kb.as_markup(resize_keyboard=True)