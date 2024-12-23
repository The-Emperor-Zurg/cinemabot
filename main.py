import os
import asyncio

from aiogram import Bot, types, Dispatcher
from aiogram.filters import CommandStart, Command

from movie import MovieManager, KinopoiskProvider
from sqlite import SqliteProvider

dp = Dispatcher()
sql_provider = SqliteProvider("sqlite.db")
movie_manager = MovieManager(sql_provider, KinopoiskProvider(token=os.environ['KINOPOISK_TOKEN']))


@dp.message(CommandStart())
async def send_welcome(message: types.Message):
    await message.answer(f"Привет, {message.from_user.first_name}!\n"
                         f"Я бот по поиску фильмов!)\n"
                         f"Чтобы увидеть информацию о фильме, достаточно написать его название. Если название будет некорректным, то ничем не смогу помочь(")


@dp.message(Command("help"))
async def send_help(message: types.Message):
    await message.answer("Чтобы увидеть информацию о фильме, достаточно написать его название. Если название будет некорректным, то постарайся ввести его правильно)\n\n"
                         "/stats - Статистика всех твоих запросов по фильмам\n"
                         "/history - История твоих запросов")


@dp.message(Command("history"))
async def send_history(message: types.Message):
    try:
        movies = await movie_manager.retrieve_user_history(message.from_user.id)
        answer = "История твоих запросов:\n"
        for i, movie in enumerate(movies):
            answer += f"{i + 1}. [{movie.title}]({movie.url})\n"

        await message.answer(answer, parse_mode="Markdown")

    except Exception as err:
        print(repr(err))
        await message.answer("Ошибка, повторите попытку позже")


@dp.message(Command("stats"))
async def send_stats(message: types.Message):
    try:
        movies = await movie_manager.compile_user_statistics(message.from_user.id)
        answer = "Статистика твоих запрошенных фильмов:\n"
        for i, movie_stats in enumerate(movies):
            answer += f"{i + 1}. [{movie_stats[0].title}]({movie_stats[0].url}): {movie_stats[1]}\n"

        await message.answer(answer, parse_mode="Markdown")

    except Exception as err:
        print(repr(err))
        await message.answer("Ошибка, повторите попытку позже")


@dp.message()
async def send_movie(message: types.Message):
    try:
        movie = await movie_manager.fetch_and_store_movie(message.text, message.from_user.id)
        if movie is None:
            await message.answer(text=f"Фильм *{message.text}* не найден.", parse_mode='Markdown')
        else:
            await message.answer_photo(photo=movie.photo,
                                       caption=str(movie),
                                       parse_mode='Markdown')
    except Exception as err:
        print(repr(err))
        await message.answer("Ошибка, повторите попытку позже")


async def set_commands(bot: Bot):
    commands = [
        types.BotCommand(command="/help", description="Помощь!"),
        types.BotCommand(command="/history", description="История фильмов"),
        types.BotCommand(command="/stats", description="Статистика запросов по фильмам")
    ]

    await bot.set_my_commands(commands)


async def main() -> None:
    print("Bot is starting now!")

    await sql_provider.initialize_tables()

    bot = Bot(token=os.environ['BOT_TOKEN'])
    await set_commands(bot)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
