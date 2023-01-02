from telebot import types
from dataBase import DB
import telebot
import datetime
import json

# 381228176,
# Старт бота
with open("./config.json", 'r', encoding='utf-8') as f:
    config = json.load(f)
db = DB()
bot = telebot.TeleBot(config["tokenMainBot"])
bot.set_webhook()
admins = config["admins"]
admins_dict = {}
for admin in admins:
    admins_dict[admin] = [{
        "title": "",
        "image": "",
        "stopped": False,
        "date": datetime.datetime.now(),

    }, "", 0]
print("Bot is runing ...")
# --------------------------------------------

bot_commands_to_admins = [types.BotCommand("/start", "перезапустить бота ")]

for admin in admins:
    bot.set_my_commands(commands=bot_commands_to_admins, scope=types.BotCommandScopeChat(chat_id=admin))
    bot.set_chat_menu_button(chat_id=admin, menu_button=types.MenuButtonDefault(type="commands"))

# Кнопки и меню
main_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
main_keyboard.row(types.KeyboardButton(text=config["buttons_admin"]["add"]),
                  types.InlineKeyboardButton(text=config["buttons_admin"]["update"]))
main_keyboard.row(types.KeyboardButton(text=config["buttons_admin"]["stop"]),
                  types.InlineKeyboardButton(text=config["buttons_admin"]["mailing"]))
main_keyboard.row(types.KeyboardButton(text=config["buttons_admin"]["addUser"]),
                  types.InlineKeyboardButton(text=config["buttons_admin"]["deleteUser"]))


def keyboard_subscribe(id):
    key_suscribe = types.InlineKeyboardMarkup()
    key_suscribe.row(types.InlineKeyboardButton(text="Подписаться", callback_data=f"+ {id}"))
    return key_suscribe


def keyboard_describe(id):
    key_describe = types.InlineKeyboardMarkup()
    key_describe.row(types.InlineKeyboardButton(text="Отписаться", callback_data=f"- {id}"))
    return key_describe


def keyboard_active_machs_to_update():
    machs = db.get_maches()
    keyboard_machs = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for mach in machs:
        keyboard_machs.row(types.InlineKeyboardButton(text=f"{mach[1]}#{mach[0]}"))
    return keyboard_machs


def keyboard_active_machs_to_stop():
    machs = db.get_maches()
    keyboard_machs = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for mach in machs:
        keyboard_machs.row(types.InlineKeyboardButton(text=f"{mach[1]}#{mach[0]}"))
    return keyboard_machs


def users_keyboard():
    users = db.get_all_temp_users()
    if users:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for user in users:
            keyboard.row(types.InlineKeyboardButton(text=f"{user[0]} @{user[1]}#{user[2]}"))
    else:
        keyboard = False
    return keyboard


def users_in_base_keyboard():
    users = db.get_all_users()
    if users:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for user in users:
            keyboard.row(types.InlineKeyboardButton(text=f"{user[0]} @{user[1]}#{user[2]}"))
    else:
        keyboard = False
    return keyboard

# Обработка команд админа
@bot.message_handler(func=lambda message: message.from_user.id in admins, commands=["start"])
def get_messages(message):
    global admins_dict
    bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
    msg = bot.send_message(
        chat_id=message.from_user.id,
        text="Добро пожаловать! Вы являетесь администратором бота.",
        reply_markup=main_keyboard
    )
    admins_dict[message.from_user.id][2] = msg.id
    print(f"Админ {message.from_user.id} запустил бота ")


# Обработка сообщений от админа
@bot.message_handler(func=lambda message: message.from_user.id in admins, content_types=["text"])
def get_messages(message):
    print(message.id)
    bot.delete_message(chat_id=message.from_user.id, message_id=message.id)
    global admins_dict
    if admins_dict[message.from_user.id][2]:
        bot.delete_message(chat_id=message.from_user.id, message_id=admins_dict[message.from_user.id][2])
    if message.text == config["buttons_admin"]["add"]:
        msg = bot.send_message(
            chat_id=message.from_user.id,
            text="Напишите название матча:",
        )
        admins_dict[message.from_user.id][2] = msg.id
        bot.register_next_step_handler(msg, get_match_title)
    elif message.text == config["buttons_admin"]["stop"]:
        msg = bot.send_message(
            chat_id=message.from_user.id,
            text="Выберете какой матч завершить:",
            reply_markup=keyboard_active_machs_to_stop()
        )
        admins_dict[message.from_user.id][2] = msg.id
        bot.register_next_step_handler(msg, stop_next_step)
    elif message.text == config["buttons_admin"]["update"]:
        msg = bot.send_message(
            chat_id=message.from_user.id,
            text="Выберите матч для рассылки:",
            reply_markup=keyboard_active_machs_to_update()
        )
        admins_dict[message.from_user.id][2] = msg.id
        bot.register_next_step_handler(msg, get_match_id)
    elif message.text == config["buttons_admin"]["mailing"]:
        msg = bot.send_message(
            text="Напишите текст для рассылки",
            chat_id=message.from_user.id
        )
        admins_dict[message.from_user.id][2] = msg.id
        bot.register_next_step_handler(msg, update_all)
    elif message.text == config["buttons_admin"]["addUser"]:
        kb = users_keyboard()
        if kb:
            msg = bot.send_message(
            chat_id=message.from_user.id,
            text="Выберите пользователя",
            reply_markup=users_keyboard()
            )
            bot.register_next_step_handler(msg, add_user)
        else:
            msg = bot.send_message(
                chat_id=message.from_user.id,
                text="Нет активных заявок на добавление пользователя",
                reply_markup=main_keyboard
            )
        admins_dict[message.from_user.id][2] = msg.id

    elif message.text == config["buttons_admin"]["deleteUser"]:
        kb = users_in_base_keyboard()
        if kb:
            print(1)
            msg = bot.send_message(
            chat_id=message.from_user.id,
            text="Выберите пользователя",
            reply_markup=users_in_base_keyboard()
            )
            bot.register_next_step_handler(msg, delete_user)
        else:
            msg = bot.send_message(
                chat_id=message.from_user.id,
                text="Нет пользователей для удаления !",
                reply_markup=main_keyboard
            )
        admins_dict[message.from_user.id][2] = msg.id


# Обработка сообщений от обычных пользователей
@bot.message_handler(func=lambda message: message.from_user.id not in admins, content_types=["text"])
def get_messages(message):
    if message.text == '/start':
        bot.send_message(chat_id=message.from_user.id, text="Добро пожаловать в телеграмм бота Аппетитки !")
        if db.check_in_table_temp(message.from_user.id):
            if db.check_in_table(int(message.from_user.id)):
                db.insert_data_in_tempUsers(
                    message.from_user.id,
                    message.from_user.username,
                    message.from_user.first_name,
                    message.from_user.last_name
                )
                bot.send_message(chat_id=message.from_user.id, text="Заявка на добаление принята !\nПодождите пока админ не подтвердит действие.")
                print(f'Добавленна заявка на добавление пользователя: "{message.from_user.username}"')
            else:
                bot.send_message(message.from_user.id, "Вы уже получаете рассылку, для отсановки напишите /stop")
                print(f'Пользователь: "{message.from_user.username}" уже в базе')
        else:
            bot.send_message(message.from_user.id, "Вы уже отсавили заявку, ждите ...")

    elif message.text == '/stop':
        db.delete_user(message.from_user.id)
        bot.send_message(chat_id=message.from_user.id, text="Вы удалены из рассылки матчей !")
        print(f'Пользователь: "{message.from_user.username}" удалён из базы')


def add_user(message):
    bot.delete_message(chat_id=message.from_user.id, message_id=message.id)
    bot.delete_message(chat_id=message.from_user.id, message_id=admins_dict[message.from_user.id][2])
    s_m = message.text.split("#")
    ut_id = s_m[-1]
    db.insert_user(ut_id)
    bot.send_message(
        chat_id=config["spamGroupId"],
        text=f"АДМИН: {message.from_user.first_name}, ДОБАВИЛ ПОЛЬЗОВАТЕЛЯ: {s_m[0].split(' ')[1]}"
    )
    msg = bot.send_message(
        chat_id=message.from_user.id,
        text="Пользователь добавлен",
        reply_markup=main_keyboard
    )
    bot.send_message(
        chat_id=db.get_user_by_table_id(s_m[-1]),
        text="Вы добавлены в рассылку матчей !"
    )
    admins_dict[message.from_user.id][2] = msg.id


def delete_user(message):
    bot.delete_message(chat_id=message.from_user.id, message_id=message.id)
    bot.delete_message(chat_id=message.from_user.id, message_id=admins_dict[message.from_user.id][2])
    s_m = message.text.split("#")
    u_tg_id = db.get_user_by_table_id(s_m[-1])
    db.delete_user_by_table(s_m[-1])
    bot.send_message(
        chat_id=config["spamGroupId"],
        text=f"АДМИН: {message.from_user.first_name}, УДАЛИЛ ПОЛЬЗОВАТЕЛЯ: {s_m[0].split(' ')[1]}"
    )
    msg = bot.send_message(
        chat_id=message.from_user.id,
        text="Пользователь удалён",
        reply_markup=main_keyboard
    )
    bot.send_message(
        chat_id=u_tg_id,
        text="Вы удалены из рассылки (BAN)!"
    )
    admins_dict[message.from_user.id][2] = msg.id

# Общая рассылка
def update_all(message):
    bot.delete_message(chat_id=message.from_user.id, message_id=message.id)
    bot.delete_message(chat_id=message.from_user.id, message_id=admins_dict[message.from_user.id][2])
    bot.send_message(
        chat_id=message.from_user.id,
        text=f"Общая рассылка:\n_{message.text}_",
        parse_mode="Markdown",
        reply_markup=main_keyboard
    )
    users = db.get_all_users_id()
    for user in users:
        bot.send_message(text=message.text, chat_id=user)
    admins_dict[message.from_user.id][2] = 0


# Получение id матча для дальнейшей рассылки
def get_match_id(message):
    bot.delete_message(
        chat_id=message.from_user.id,
        message_id=message.id
    )
    bot.delete_message(
        chat_id=message.from_user.id,
        message_id=admins_dict[message.from_user.id][2]
    )
    msg = bot.send_message(
        chat_id=message.from_user.id,
        text="Введите текст для рассылки"
    )
    admins_dict[message.from_user.id][2] = msg.id
    match_id = message.text.split("#")
    bot.register_next_step_handler(msg, update_one, match_id)


# Рассылка по матчу
def update_one(message, id):
    bot.delete_message(
        chat_id=message.from_user.id,
        message_id=message.id
    )
    bot.delete_message(
        chat_id=message.from_user.id,
        message_id=admins_dict[message.from_user.id][2]
    )
    users = db.get_sus_machesUsers_by_machid(id[-1])
    db.insert_data_in_info_match(id[-1], message.text)
    i_m_id = db.c.lastrowid
    for user in users:
        bot.send_message(
            chat_id=db.get_user_by_table_id(user[1]),
            reply_to_message_id=user[0],
            text=message.text
        )
        db.sended_info_add(user[1], i_m_id)
    bot.send_message(
        chat_id=message.from_user.id,
        text=f"Рассылка сообщения: _«{message.text}»_\n"
             f"По матчу: *«{id[0]}»*",
        reply_markup=main_keyboard,
        parse_mode="Markdown"
    )
    admins_dict[message.from_user.id][2] = 0


# Остановка матча
def stop_next_step(message):
    bot.delete_message(chat_id=message.from_user.id, message_id=message.id)
    bot.delete_message(chat_id=message.from_user.id, message_id=admins_dict[message.from_user.id][2])
    data = message.text.split("#")
    id_match = data[-1]
    db.set_stopped_by_id(id_match)
    users = db.get_machesUsers_by_machid(id_match)
    bot.send_message(
        chat_id=message.from_user.id,
        text=f"Вы завершили матч: *{data[0]}*",
        reply_markup=main_keyboard,
        parse_mode="Markdown"
    )
    for user in users:
        bot.edit_message_caption(
            chat_id=db.get_user_by_table_id(user[1]),
            message_id=user[0],
            caption=data[0] + " завершён !",
            reply_markup=None
        )
        bot.send_message(chat_id=db.get_user_by_table_id(user[1]), reply_to_message_id=user[0],
                         text="Матч заврешён")
    admins_dict[message.from_user.id][2] = 0
    print(f"Матч: {data[0]}, завершен")


# ------Добавление матча--------
# Получение названия матча
def get_match_title(message):
    global admins_dict
    bot.delete_message(
        message.from_user.id,
        message.id
    )
    admins_dict[message.from_user.id][0]['title'] = message.text
    msg = bot.edit_message_text(
        chat_id=message.from_user.id,
        message_id=admins_dict[message.from_user.id][2],
        text=f"Название матча «{message.text}» принято !\n"
             "Скиньте картику матча:"
    )
    admins_dict[message.from_user.id][2] = msg.id
    bot.register_next_step_handler(msg, get_match_photo)


# Получение картинки матча
def get_match_photo(message):
    global admins_dict
    bot.delete_message(
        chat_id=message.from_user.id,
        message_id=message.id
    )
    try:
        fileID = message.photo[-1].file_id
        file_info = bot.get_file(fileID)
        downloaded_file = bot.download_file(file_info.file_path)
        with open(f"./images/{fileID}.jpg", 'wb') as new_file:
            new_file.write(downloaded_file)
        admins_dict[message.from_user.id][0]["image"] = f"./images/{fileID}.jpg"
        admins_dict[message.from_user.id][0]['date'] = datetime.datetime.now()
        bot.edit_message_text(
            chat_id=message.from_user.id,
            message_id=admins_dict[message.from_user.id][2],
            text="Картинка загружена"
        )
        match_temp = admins_dict[message.from_user.id][0]
        db.insert_data_in_machs(match_temp['title'], match_temp['image'], match_temp['stopped'], match_temp['date'])
        with open(match_temp['image'], 'rb') as f:
            photo = f.read()
        bot.delete_message(
            chat_id=message.from_user.id,
            message_id=admins_dict[message.from_user.id][2]
        )
        m_id = db.c.lastrowid
        u_m_m_s = []
        for i in db.get_all_users_id():
            msg = bot.send_photo(
                chat_id=i,
                reply_markup=keyboard_subscribe(m_id),
                photo=photo,
                caption=match_temp['title']
            )
            u_m_m_s.append((db.get_user_id(i), m_id, msg.id, False))
        db.insert_many_in_usersMatchs(u_m_m_s)
        bot.send_photo(
            chat_id=message.from_user.id,
            caption=f"Добавлен матч: «{match_temp['title']}»",
            reply_markup=main_keyboard,
            photo=photo
        )
        admins_dict[message.from_user.id][2] = 0
    except Exception as e:
        bot.delete_message(
            chat_id=message.from_user.id,
            message_id=admins_dict[message.from_user.id][2]
        )
        msg = bot.send_message(message.from_user.id, "!!! Ошибка загрузки картинки матча !!!", reply_markup=main_keyboard)
        admins_dict[message.from_user.id][2] = msg.id
        print(e)
# ------------------------------


# Обработка нажатий на Inline Кнопки
@bot.callback_query_handler(func=lambda call: True)
def callback_worker(data):
    global admins_dict
    if data.from_user.id in db.get_all_users_id():
        acticon = data.data.split(" ")
        if acticon[0] == "+":
            msg = bot.edit_message_reply_markup(
                chat_id=data.from_user.id,
                message_id=data.message.id,
                reply_markup=keyboard_describe(acticon[1])
            )
            u_id = db.get_user_id(data.from_user.id)
            db.suscribe(u_id, acticon[1])
            data_info = db.get_no_send_info(u_id, acticon[1])
            if data_info:
                message_text = ""
                l = len(data_info)
                rec = []
                for i, info in enumerate(data_info):
                    rec.append((u_id, info[1]))
                    if i < l-1:
                        message_text += f"{info[0]}\n.\n"
                    else:
                        message_text += f"{info[0]}\n"
                bot.send_message(chat_id=data.from_user.id, reply_to_message_id=msg.id, text=message_text)
                db.sended_info_many_add(rec)

        elif acticon[0] == "-":
            bot.edit_message_reply_markup(
                chat_id=data.from_user.id,
                message_id=data.message.id,
                reply_markup=keyboard_subscribe(acticon[1])
            )
            db.describe(db.get_user_id(data.from_user.id), acticon[1])
        bot.send_message(chat_id=config["spamGroupId"],
                         text=f"*{data.from_user.first_name} {data.from_user.last_name}* "
                              f"{'подписался на матч' if acticon[0] == '+' else 'отписался от матча'}"
                              f" \n_{db.get_machname_by_id(acticon[1])}_",
                         parse_mode="Markdown")


bot.polling(none_stop=True, interval=0)