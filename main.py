import os
import asyncio
import logging
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from groq import AsyncGroq



# Load environment variables from .env file
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TOKEN:
    raise ValueError("Токен не знайдено! Перевір файл .env та переконайся, що змінна TELEGRAM_BOT_TOKEN встановлена.")

print("Перші 10 символів токена:", TOKEN[:10])


bot = Bot(token=TOKEN)
dp = Dispatcher()
groq_client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))
user_history = {}

@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer("Привіт! Я ваш бот. Як я можу допомогти вам сьогодні?")

@dp.message()
async def echo_handler(message: types.Message):
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    chat_id = message.chat.id
    if chat_id not in user_history:
        user_history[chat_id] = []

    user_history[chat_id].append({"role": "user", "content": message.text})

    try:
        system_prompt = {'role': 'system', 'content': 'Ти корисний та розумний асистент. Відповідай українською мовою.'}
        message_for_groq = [system_prompt] + user_history[chat_id]
        
        chat_completion = await groq_client.chat.completions.create(
            messages=message_for_groq,
            model="openai/gpt-oss-20b"
        )
        
        ai_response = chat_completion.choices[0].message.content
        user_history[chat_id].append({"role": "assistant", "content": ai_response})
        
        
        
        await message.answer(ai_response)

    except Exception as e:
        print(f"Помилка при обробці повідомлення: {e}")
        await message.answer("Вибачте, сталася помилка при обробці вашого запиту. Спробуйте ще раз пізніше.")




async def main():
    print("Бот запущено. Очікую на повідомлення...")
    await dp.start_polling(bot)




if __name__ == "__main__":
    asyncio.run(main())