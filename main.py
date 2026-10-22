import os
import asyncio
import logging
import chromadb
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from groq import AsyncGroq
from pypdf import PdfReader




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

def load_document(chunks_size=500, overlap=50):
    reader = PdfReader("test.pdf")
    full_text = ""
    for page in reader.pages:
        full_text += page.extract_text() + '\n'

    chunks = []
    start = 0
    text_length = len(full_text)

    while start < text_length:
        end = min(start + chunks_size, text_length)
        chunk = full_text[start:end]
        chunks.append(chunk)
        start += chunks_size - overlap
    return chunks

chroma_client = chromadb.Client()
collection = chroma_client.create_collection(name='rag_documents')
text_chunks = load_document()
chunk_ids = [f'chunk_{i}' for i in range(len(text_chunks))]
print(f'Завантажуємо {len(text_chunks)} шматків у векторну базу даних...')
collection.add(documents=text_chunks, ids=chunk_ids)
print("Базу даних успішно створено!")


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
        results = collection.query(query_texts=[message.text], n_results=5)
        context_text = '\n\n'.join(results["documents"][0])

        system_prompt = {'role': 'system',
                        'content': f'Ти корисний та розумний асистент. Відповідай на питання, спираючись ТІЛЬКИ на цей текст:\n{context_text}\n\nЯкщо відповіді в тексті немає, так і скажи. Якщо питання стосується документа в цілому, узагальни всю надану інформацію'}
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