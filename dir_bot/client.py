from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputFile
from aiogram import types
from dir_bot import create_bot
from dir_OpenIA import get_data_OpenIA, translate
from dir_sound import voice_fun
from data_base import sqlite_db
from hashlib import md5, sha256
import os, random, requests, main
dp = create_bot.dp
bot = create_bot.bot
button_one = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text='🔈 Прослушать', callback_data='voice'))
button_two = InlineKeyboardMarkup()\
    .row((InlineKeyboardButton(text='🔈 Прослушать', callback_data='voice')),
         (InlineKeyboardButton(text='🔣 Перевести', callback_data='translate')))
URL_Group = '<a href="https://t.me/learn_english_with_ease">Into English</a>'
Name_Group = "@learn_english_with_ease"


@dp.message_handler(commands=['start'])
async def commands_start(message: types.Message):
    try:
        if not await sqlite_db.sql_read_id(message.from_user.id):
            await bot.send_message(message.from_user.id, f'Добрый день, {message.from_user.first_name}!')
            await sqlite_db.sql_add_command(message.from_user.id, message.from_user.username)
            await bot.send_message(message.from_user.id, f'Подпишитесь на канал {URL_Group},'
                                                         f'чтобы получить доступ к боту. '
                                                         f'На канале собрано большое количество полезных разговорных выражений. '
                                                         f'Вам там понравится!', parse_mode="HTML")
        else:
            await bot.send_message(message.from_user.id, f'Бот готов к общению! \nНапишите ему сообщение 😉')
    except:
        await message.delete()
        await message.reply('Напишите мне в личные сообщения')


@dp.message_handler(commands=['info'])
async def commands_info(message: types.Message):
    read_user_bd = (await sqlite_db.sql_read_id(message.from_user.id))[0]
    if read_user_bd[3]:
        if read_user_bd[3] > 4:
            await bot.send_message(message.from_user.id, f"Осталось {read_user_bd[3]} дней подписки!")
        elif read_user_bd[3] == 1:
            await bot.send_message(message.from_user.id, f"Осталось {read_user_bd[3]} день подписки!")
        else:
            await bot.send_message(message.from_user.id, f"Осталось {read_user_bd[3]} дня подписки!")
    else:
        await bot.send_message(message.from_user.id, f"Осталось {read_user_bd[2]} запросов сегодня!")


@dp.message_handler(commands=['info_all'])
async def commands_info_all(message: types.Message):
    person_use, person_use_all, person_all, sub, = 0, 0, 0, 0
    bd_read = await sqlite_db.sql_read_left()
    for bd_data in bd_read:
        requests_left = bd_data[2]
        days_left = bd_data[1]
        person_all += 1
        if days_left:
            sub += 1
        elif requests_left != 5:
            person_use += 1
            if requests_left == 0:
                person_use_all += 1
    await bot.send_message(message.from_user.id, f"Всего пользователей: {person_all} человек.\n"
                                                 f"Платных подписчиков: {sub} человек.\n\n"
                                                 f"1+ запрос сегодня: {person_use} человек.\n"
                                                 f"Потратили все запросы: {person_use_all} человек.\n")


@dp.message_handler(commands=['info_pay'])
async def commands_info_pay(message: types.Message):
    await bot.send_message(message.from_user.id, f"Сегодня хотели опалатить: {main.sum_button_pay} человек.")


@dp.message_handler(content_types=['voice', 'text'])
async def voice(message):
    if not await check_sub(message.from_user.id):
        return

    if not await sqlite_db.sql_read_id(message.from_user.id):
        await sqlite_db.sql_add_command(message.from_user.id, message.from_user.username)

    read_user_bd = (await sqlite_db.sql_read_id(message.from_user.id))[0]
    if await check_left(message.from_user.id, read_user_bd[2], read_user_bd[3]):
        if message.voice:
            file = await bot.get_file(message.voice.file_id)
            file_dir = f"dir_sound/{file.file_path.replace('.oga', f'_{message.from_user.id}.ogg')}"
            new_file_dir = file_dir.replace('ogg', 'wav')
            await bot.download_file(file.file_path, file_dir)

            text_voice = await voice_fun.voice_to_text(file_dir, new_file_dir)
            if not text_voice:
                await bot.send_message(message.from_user.id, "I do not understand you 🤨")
                return
            await bot.send_message(message.from_user.id, f"Вы сказали:\n {text_voice}")
            message_en = await translate.translate_fun(text_voice, 'auto', 'en')
        else:
            message_en = await translate.translate_fun(message.text, 'auto', 'en')

        answer_gpt = await get_data_OpenIA.get_data(read_user_bd[4], read_user_bd[5], message_en)
        if answer_gpt:
            await bot.send_message(chat_id=message.from_user.id, text=answer_gpt, reply_markup=button_two)
            await sqlite_db.sql_update_text(message_en, answer_gpt, message.from_user.id)
            if not read_user_bd[3]:
                await sqlite_db.sql_update_left(read_user_bd[2] - 1, message.from_user.id, 'requests_left')
        else:
            await bot.send_message(message.from_user.id, "Oh, I'm confused. Try again 🤔")


async def check_sub(user_id):
    user_channel_status = await bot.get_chat_member(chat_id=Name_Group, user_id=user_id)
    if user_channel_status["status"] != 'left':
        return 1
    else:
        await bot.send_message(user_id, f'Подпишитесь на канал {URL_Group},'
                                                     f'чтобы получить доступ к боту. '
                                                     f'На канале собрано большое количество полезных разговорных выражений. '
                                                     f'Вам там понравится!', parse_mode="HTML")


async def check_left(user_id, left_req, left_days):
    if (not left_req) and (not left_days):
        button_pay = InlineKeyboardMarkup(row_width=1).add(
            InlineKeyboardButton(text='Оплатить онлайн (149 Руб./мес)', callback_data='pay'))
        await bot.send_message(user_id, f'К сожалению, лимит в 5 сообщений в день исчерпан. '
                                        f'Вы можете оформить подписку на безлимитное общение с ботом, '
                                        f'либо вернуться к разговорной практике через 24 часа.',
                               reply_markup=button_pay)
        return False
    else:
        return True


@dp.callback_query_handler(text_contains='pay')
async def commands_create_url_pay(callback: types.CallbackQuery):
    main.sum_button_pay += 1
    message_id = callback['message']['message_id']
    id_user = callback['from']['id']
    await bot.edit_message_reply_markup(chat_id=id_user, message_id=message_id, reply_markup=None)
    await callback.answer('После оплаты - нажмите на кнопку "Уже оплатил!" ')


    url_button = InlineKeyboardMarkup(row_width=1)
    rand_int = random.randint(10000, 99999)
    project_id = create_bot.config["TOKEN"]["project_id"]
    secret_key = create_bot.config["TOKEN"]["secret_key"]
    try:
        params = {
            'merchant_id': project_id,
            'pay_id': f"{rand_int}{id_user}",
            'amount': "149.00",
            'currency': 'RUB',
        }
        sign = md5(f"{params['currency']}:{params['amount']}:{secret_key}:{params['merchant_id']}:{params['pay_id']}"
                   .encode('utf-8')).hexdigest()
        params['sign'] = sign
        url_pay = f"https://anypay.io/merchant?merchant_id={params['merchant_id']}&pay_id={params['pay_id']}&" \
                  f"currency={params['currency']}&amount={params['amount']}&sign={sign}"
        url_button.add(InlineKeyboardButton(text='Оплатить', url=url_pay))
        url_button.add(InlineKeyboardButton(text='Уже оплатил!',
                                            callback_data=f'check/{rand_int}'))
        await bot.edit_message_reply_markup(chat_id=id_user, message_id=message_id, reply_markup=url_button)
        await bot.send_message(id_user, 'После оплаты - нажмите на кнопку "Уже оплатил!"')
    except:
        await bot.send_message(id_user, 'Ошибка создания ссылки для оплаты...\n'
                                        'Попробуте позже :/')


@dp.callback_query_handler(text_contains='check')
async def commands_already_paid(callback: types.CallbackQuery):
    message_id = callback['message']['message_id']
    id_user = callback['from']['id']
    data_callback = callback['data'].split("/")[1]
    await callback.answer()

    project_id = create_bot.config["TOKEN"]["project_id"]
    API_KEY = create_bot.config["TOKEN"]["API_KEY"]
    API_ID = create_bot.config["TOKEN"]["API_ID"]
    try:

        params = {
            'project_id': project_id,
            'pay_id': f"{data_callback}{id_user}",
        }
        sign = sha256(f"payments{API_ID}{project_id}{API_KEY}".encode()).hexdigest()
        params['sign'] = sign
        responce = requests.get(f"https://anypay.io/api/payments/{API_ID}", params=params)
        payment_data = responce.json()
        try:
            payments = list(payment_data['result']['payments'])[0]
        except:
            await bot.send_message(id_user, 'Транзакция не найдена!')
            return

        if payment_data['result']['payments'][payments]['status'] == 'paid':
            await bot.send_message(id_user, '-->Оплата прошла успешно<--\n\n'
                                            'Можете 30 дней безлимитно пользоваться ботом!\n'
                                            '/info - остаток подписки')
            await bot.edit_message_reply_markup(chat_id=id_user, message_id=message_id, reply_markup=None)
            await sqlite_db.sql_update_left(30, id_user, 'days_left')
        else:
            await bot.send_message(id_user, 'Транзакция не найдена!')
    except:
        await bot.send_message(id_user, 'Ошибка проверки...\n'
                                        'Попробуте позже :/')


@dp.callback_query_handler(text_contains='voice')
async def commands_create_voice(callback: types.CallbackQuery):
    user_id = callback['from']['id']
    text_message = callback['message']['text'].split('#Перевод', 1)
    path_sound = f"dir_sound/voice_bot/gen_{user_id}.mp3"

    await callback.answer('Voice message generation')
    await voice_fun.text_to_voice(text_message[0], path_sound)
    await bot.send_voice(chat_id=user_id, voice=InputFile(path_sound))
    os.remove(path_sound)


@dp.callback_query_handler(text_contains='translate')
async def commands_translate(callback: types.CallbackQuery):
    message_id = callback['message']['message_id']
    user_id = callback['from']['id']
    text_message = callback['message']['text']
    await callback.answer()
    message_en = await translate.translate_fun(text_message, 'auto', 'ru')
    await bot.edit_message_text(chat_id=user_id, message_id=message_id,
                                text=f"{text_message}\n\n#Перевод\n{message_en}", reply_markup=button_one)


