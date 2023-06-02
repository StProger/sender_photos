import os, json

from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from states import NewInterval
from function_dir.database import add_user, get_users
from function_dir.download_photo import download_file
from apscheduler.schedulers.asyncio import AsyncIOScheduler


scheduler = AsyncIOScheduler()
load_dotenv()

current_interval = 15

bot = Bot(os.getenv("TOKEN"))
dp = Dispatcher(bot, storage=MemoryStorage())

async def on_startup(_):

    shedule_jobs()

@dp.message_handler(commands=["start"])
async def start(message: types.Message):

    await add_user(message.from_user.id)
    if message.from_user.id == 64917407 or message.from_user.id == 1878562358:
        await message.answer("<b>Добро пожаловать! Вы вошли как администратор. Для изменения интервала воспользуйтесь кнопкой ниже.</b>.",
                             parse_mode="HTML",
                             reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add("/set_interval"))
    else:
        await message.answer(
            "<b>Добро пожаловать!</b>.",
            parse_mode="HTML")


@dp.message_handler(commands=["set_interval"])
async def get_interval(message: types.Message, state: FSMContext):

    await state.set_state(NewInterval.new_interval.state)
    await message.answer("Введите новый интервал в минутах (только число).")

@dp.message_handler(state=NewInterval.new_interval)
async def add_new_interval(message: types.Message, state: FSMContext):
    """
    Функция, которая изменяет интервал отправления фотографий
    :param message:
    :param state:
    :return:
    """

    global current_interval
    if message.text.isdigit():
        new_interval = int(message.text)
        current_interval = new_interval
        await message.answer(f"Интервал изменён на {new_interval} минут.")
        shedule_jobs()
        await state.finish()
    else:
        await message.answer("Вы ввели не число! Попробуйте ещё раз.")


async def send_img(dp: Dispatcher):
    """
    Функция, которая отправляет изображение
    :param dp:
    :return:
    """

    # Открываем json файл
    with open("id_files.json") as file:
        list_photo = list(json.load(file))

    # Проверка на наличие id фото, если нет, то фотки закончились
    if len(list_photo) == 0:
        await dp.bot.send_message(chat_id=64917407, text="Больше изображений нет.")
        return

    # Берём самый первый id
    id_ = list_photo[0].get('id')

    # Загружаем изображение с полученным id
    await download_file(id_)

    # Здесь по идее я удаляю первый словарь в  json
    list_photo.pop(0)

    # Перезаписываю json файл без использованного id
    with open('id_files.json', 'w') as file:
        json.dump(list_photo, file, ensure_ascii=False, indent=4)

    with open('photo.jpg', 'rb') as picture:
        img = picture.read()
    # Рассылка пользователям
    users = await get_users()
    for user in users:

        await dp.bot.send_photo(chat_id=int(user),
                        photo=img)






def shedule_jobs():
    """
    В функции мы сбрасываем наш планировщик и создаём новую задачу для него
    :return:
    """

    scheduler.remove_all_jobs()
    scheduler.add_job(send_img, "interval", seconds=current_interval, args=(dp,))

if __name__ == '__main__':

    scheduler.start()
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)