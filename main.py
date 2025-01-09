import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import CommandStart
import httpx
from dotenv import load_dotenv
load_dotenv()

"""Укажите в .env токен вашего бота из BotFather"""
BOT_TOKEN = os.getenv('BOT_TOKEN')

"""Укажите в .env ваш API-ключ DEXtools"""
DEXTOOLS_API_KEY = os.getenv('DEXTOOLS_API_KEY')

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

"""URL для запроса данных с DEXtools API"""
DEXTOOLS_API_URL = "https://public-api.dextools.io/free/v2/token/{token_address}"


async def get_token_info(token_address: str) -> str:
    """Получает информацию о токене с DEXtools."""
    try:
        async with httpx.AsyncClient(headers={'x-api-key': DEXTOOLS_API_KEY}) as client:
            response = await client.get(DEXTOOLS_API_URL.format(token_address=token_address))
            response.raise_for_status()
            data = response.json()

            name = data.get("name", "Неизвестно")
            trading_pair = data.get("trading_pair", "Не указана")
            market_cap = data.get("market_cap", "Не указано")
            holders = data.get("holders", "Не указано")
            largest_holder = data.get("largest_holder", {}).get("value", "Не указано")
            volume_24h = data.get("volume_24h", "Не указано")

            return (f"Информация о токене:\n"
                    f"Название: {name}\n"
                    f"Валютная пара: {trading_pair}\n"
                    f"Рыночная капитализация: {market_cap} USD\n"
                    f"Количество холдеров: {holders}\n"
                    f"Самый крупный холдер: {largest_holder} USD\n"
                    f"Объем торгов за 24 часа: {volume_24h} USD")
    except httpx.RequestError:
        return "Не удалось подключиться к API DEXtools."
    except httpx.HTTPStatusError:
        return "Не удалось получить данные для указанного токена. Проверьте адрес токена."


@dp.message(CommandStart())
async def start_command(message: Message):
    await message.answer(
        "Привет! Я бот для работы с DEXtools. Отправь мне адрес токена, и я предоставлю информацию о нём."
    )


@dp.message()
async def token_info_handler(message: Message):
    """Обработчик для получения информации о токене"""
    token_address = message.text.strip()
    info_message = await get_token_info(token_address)
    await message.answer(info_message)


async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
