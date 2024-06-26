import logging
from aiogram import Bot, Dispatcher, types
import asyncio
import time 
import g4f
from aiogram.utils import executor
from config import API_TOKEN

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

conversation_history = {}

last_api_request_time = 0

def trim_history(history, max_length=4096):
    current_length = sum(len(message["content"]) for message in history)
    while history and current_length > max_length:
        removed_message = history.pop(0)
        current_length -= len(removed_message["content"])
    return history


@dp.message_handler(commands=['clear'])
async def process_clear_command(message: types.Message):
    user_id = message.from_user.id
    conversation_history[user_id] = []
    await message.reply("История диалога очищена.")

@dp.message_handler()
async def send_welcome(message: types.Message):
    global last_api_request_time  
    
    user_id = message.from_user.id
    user_input = message.text
    current_time = time.time() 

    await message.reply("Подождите пожалуйста, я обрабатываю ваш запрос...")

    # Добавляем ожидание только если с последнего запроса прошло менее 10 секунд
    if current_time - last_api_request_time < 10:
        await asyncio.sleep(10 - (current_time - last_api_request_time))
    last_api_request_time = time.time()

    if user_id not in conversation_history:
        conversation_history[user_id] = []

    conversation_history[user_id].append({"role": "user", "content": user_input})
    conversation_history[user_id] = trim_history(conversation_history[user_id])

    chat_history = conversation_history[user_id]

    try:
        response = await g4f.ChatCompletion.create_async(
            model=g4f.models.default,
            messages=chat_history,
            provider=g4f.Provider.GeekGpt,
        )
        chat_gpt_response = response
    except Exception as e:
        print(f"{g4f.Provider.GeekGpt.__name__}:", e)
        chat_gpt_response = "Извините, произошла ошибка."

    conversation_history[user_id].append({"role": "assistant", "content": chat_gpt_response})
    print(conversation_history)
    length = sum(len(message["content"]) for message in conversation_history[user_id])
    print(length)
    await message.answer(chat_gpt_response)


# Запуск бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)








