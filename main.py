from aiogram.utils import executor
from pyfiglet import Figlet
from data_base import sqlite_db
from dir_bot import create_bot, client

import aioschedule, asyncio
sum_button_pay = 0

async def return_limit():
    global sum_button_pay
    sum_button_pay = 0
    bd_read = await sqlite_db.sql_read_left()
    for bd_data in bd_read:
        if bd_data[1] > 1:
            await sqlite_db.sql_update_left(bd_data[1]-1, bd_data[0], 'days_left')
        elif bd_data[1] == 1:
            await sqlite_db.sql_update_left(bd_data[1] - 1, bd_data[0], 'days_left')
            await sqlite_db.sql_update_left(5, bd_data[0], 'requests_left')
        else:
            await sqlite_db.sql_update_left(5, bd_data[0], 'requests_left')
    print('Return_limit!')


async def scheduler():
    aioschedule.every().day.at('00:00').do(return_limit)
    print('Timer run!')
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)

async def on_startup(_):
    sqlite_db.sql_start()
    preview_text = Figlet(font='slant')
    print(preview_text.renderText("ENGLISH BOT"))
    asyncio.create_task(scheduler())


def main():
    executor.start_polling(create_bot.dp, skip_updates=True, on_startup=on_startup)


if __name__ == '__main__':
    main()
