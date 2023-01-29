import aiogram
import asyncio
import config
import messages
import json
from downloader import SongsDownloader
import keyboards

bot = aiogram.Bot(token = config.API_TOKEN,
                  parse_mode = aiogram.types.ParseMode.HTML)
loop = asyncio.get_event_loop()
dp = aiogram.Dispatcher(bot, loop = loop)

users = {}


@dp.message_handler(commands = ['start'])
async def start_message(message: aiogram.types.Message):
    if message.from_user.id in users.keys():
        start_message_lang = messages.start_messages[users[
            message.from_user.id]['language']]
        await bot.send_message(message.chat.id, start_message_lang)

    elif message.from_user.id not in users.keys():
        keyb = keyboards.Keyboards().select_lang()
        await bot.send_message(message.chat.id, "Выбери язык\nChoose a language\nElige un idioma", reply_markup = keyb)
        users[message.from_user.id] = {
            "language": "EN",
            "show_bitrate": "On",
            "show_hearts": "On",
            "show_audio_format": "On",
            "results_count": "10",
            "favourites_list": [],
            "last_list": "",
            "last_page": "",
            "last_urls_page": "",
            "urls": "",
            "without_formating": "",
            "hearts_buttons": "On",

        }
        update_users_write()


@dp.message_handler(commands = ['song'])
async def search_by_song_title(message: aiogram.types.Message):
    config.search_field = "title"
    await message.reply(
        messages.song_messages[users[message.from_user.id]['language']])


@dp.message_handler(
    lambda message: message.text not in config.commands and not message.text.startswith("/"))
async def search_song(message: aiogram.types.Message):
    global number_page_message, you_in_first_page
    print("user",message.from_user.id)
    if not message.from_user.id in users.keys():
        print("unknown user",message.from_user.id)
        # keyb = keyboards.Keyboards().select_lang()
        # await bot.send_message(message.chat.id, "Выбери язык\nChoose a language\nElige un idioma", reply_markup = keyb)
        users[message.from_user.id] = {
            "language": "EN",
            "show_bitrate": "On",
            "show_hearts": "On",
            "show_audio_format": "On",
            "results_count": "10",
            "favourites_list": [],
            "last_list": "",
            "last_page": "",
            "last_urls_page": "",
            "urls": "",
            "without_formating": "",
            "hearts_buttons": "On",

        }
        update_users_write()
        start_message_lang = messages.start_messages[users[
            message.from_user.id]['language']]
        await bot.send_message(message.chat.id, start_message_lang)
        return
    song_list, urls_list, without_formating = SongsDownloader(
        f"{message.text}").get_songs_list(int(users[message.from_user.id]['results_count']))
    you_in_first_page = messages.you_in_first_page_message[users[
        message.from_user.id]['language']]
    number_page_message = messages.number_page_message[users[
        message.from_user.id]['language']]

    if song_list == False:
        await bot.send_message(message.chat.id,
                               messages.nothing_messages[users[message.from_user.id]['language']])
    elif not song_list and not urls_list:
        pass
    else:
        users[message.from_user.id
        ]["without_formating"] = without_formating
        # Списки ссылок на песни
        users[message.from_user.id]["urls"] = urls_list
        users[message.from_user.id
        ]["last_list"] = song_list  # Списки песен
        users[message.from_user.id]["last_page"] = 0  # Последняя страница
        # Последний список ссылок на песни
        users[message.from_user.id]["last_urls_page"] = "0"
        list_len = len(users[message.from_user.id]
                       ["last_list"])  # Длинна списка

        keyb = keyboards.Keyboards().for_songs_list(urls_list[0],
                                                               message.chat.id,
                                                               int(users[message.from_user.id]["results_count"]))

        await bot.send_message(message.chat.id, number_page_message.format("1",
                                                                           str(list_len)) + '\n'.join(song_list[0]),
                               reply_markup = keyb)


@dp.callback_query_handler(lambda call: call.data in ("to_left", "close", "to_right"))
async def change_page(call: aiogram.types.CallbackQuery):
    user_lang = users[call.from_user.id]['language']  # Язык пользователя
    # Последний список песен для пользователя
    user_list_now = users[call.from_user.id]["last_list"]
    # Последний список ссылок на песни
    user_link_list_now = users[call.from_user.id]["urls"]
    # Последняя просмотренная страница
    last_page = users[call.from_user.id]["last_page"]
    if call.data == "to_left":  # Листать влево
        if users[call.from_user.id]["last_page"] == 0:
            await bot.answer_callback_query(call.id,
                                            messages.you_in_first_page_message[
                                                user_lang])  # Вы уже на первой странице

        else:
            keyb = keyboards.Keyboards().for_songs_list(
                user_link_list_now[users[call.from_user.id]["last_page"] - 1],
                call.message.chat.id, int(users[call.from_user.id]["results_count"]))

            users[call.from_user.id]["last_page"] -= 1
            await bot.edit_message_text(chat_id = call.message.chat.id,
                                        text = messages.number_page_message[user_lang].format(
                                            users[call.from_user.id]["last_page"] + 1, len(user_list_now)) +
                                               "\n".join(
                                                   user_list_now[users[call.from_user.id]["last_page"]]),
                                        message_id = call.message.message_id,
                                        reply_markup = keyb)

    elif call.data == "to_right":  # Листать вправо
        if users[call.from_user.id]["last_page"] == len(user_list_now) - 1:
            await bot.answer_callback_query(call.id,
                                            messages.nothing_messages[user_lang])  # Ничего не нашлось
        else:
            keyb = keyboards.Keyboards().for_songs_list(
                user_link_list_now[users[call.from_user.id]["last_page"] + 1],
                call.message.chat.id, int(users[call.from_user.id]["results_count"]))

            users[call.from_user.id]["last_page"] += 1
            await bot.edit_message_text(chat_id = call.message.chat.id,
                                        text = messages.number_page_message[user_lang].format(
                                            users[call.from_user.id]["last_page"] + 1, len(user_list_now)) +
                                               "\n".join(
                                                   user_list_now[users[call.from_user.id]["last_page"]]),
                                        message_id = call.message.message_id,
                                        reply_markup = keyb)
    elif call.data == "close":
        await bot.delete_message(call.message.chat.id, call.message.message_id)


@dp.callback_query_handler(
    lambda call: call.data.startswith("select") and call.data.split("_")[1] not in ("ru", "en", "es"))
async def select_sound(call: aiogram.types.CallbackQuery):
    # print("select", users[call.from_user.id])
    get_song_num = call.data.split('_')
    song_num = int(get_song_num[1]) - 1
    page = users[call.from_user.id]["last_page"]
    name = users[call.from_user.id]["without_formating"][page][song_num]["artist"]
    song_name = users[call.from_user.id]["without_formating"][page][song_num]["songTitle"]

    song = SongsDownloader().download_song(
        users[call.from_user.id]["urls"][page][song_num])
    # print("song", song)
    duration = users[call.from_user.id]["without_formating"][page][song_num]["duration"]
    keyb = keyboards.Keyboards().like_unlike_keyboard(
        users[call.from_user.id]["hearts_buttons"])
    msg = await bot.send_audio(call.message.chat.id, audio = song, title = f"{name} - {song_name}",
                               performer = song_name,
                               caption = '<a href="https://t.me/Oxkingofchamps">🎧Oxkingofchamps©</a>',protect_content=True, reply_markup = keyb)


@dp.callback_query_handler(lambda call: call.data in ["like", "unlike"])
async def like_or_unlike(call: aiogram.types.CallbackQuery):
    user_lang = users[call.from_user.id]['language']

    if call.data == "like":
        users[call.from_user.id]["favourites_list"].append(
            {call.message.audio.title: call.message.audio.file_id})
        users[call.from_user.id]["last_list"] = ""
        users[call.from_user.id]["last_urls_list"] = ""
        users[call.from_user.id]["urls"] = ""
        users[call.from_user.id]["without_formating"] = ""
        update_users_write()
        await bot.answer_callback_query(call.id, messages.add_to_favourite[user_lang])
    elif call.data == "unlike":

        for item in users[call.from_user.id]["favourites_list"]:
            for key in item.keys():
                if key == call.message.audio.title:
                    song = users[call.from_user.id
                    ]["favourites_list"].index(item)
                    del users[call.from_user.id]["favourites_list"][song]
        await bot.answer_callback_query(call.id, messages.del_from_favourite[user_lang])
        users[call.from_user.id]["last_list"] = ""
        users[call.from_user.id]["last_urls_list"] = ""
        users[call.from_user.id]["urls"] = ""
        users[call.from_user.id]["without_formating"] = ""
        update_users_write()


@dp.callback_query_handler(lambda call: call.data in ["select_ru", "select_en", "select_es"])
async def select_lang(call: aiogram.types.CallbackQuery):
    if call.data == "select_ru":
        users[call.from_user.id]['language'] = "RU"
    if call.data == "select_en":
        users[call.from_user.id]['language'] = "EN"
    if call.data == "select_es":
        users[call.from_user.id]['language'] = "ES"
    users[call.from_user.id]["last_list"] = ""
    users[call.from_user.id]["last_urls_list"] = ""
    users[call.from_user.id]["urls"] = ""
    users[call.from_user.id]["without_formating"] = ""
    update_users_write()
    start_message_lang = messages.start_messages[users[
        call.from_user.id]['language']]
    await bot.send_message(call.message.chat.id, start_message_lang)


@dp.message_handler(commands = ['artist'])
async def search_for_artist_name(message: aiogram.types.Message):
    """Искать по артисту"""
    config.search_field = "artist"
    await message.reply(
        messages.artist_messages[users[message.from_user.id]['language']])

@dp.message_handler(commands = ['category'])
async def search_for_category_name(message: aiogram.types.Message):
    config.search_field = "category"
    await message.reply(
        messages.category_messages[users[message.from_user.id]['language']])


@dp.message_handler(commands = ['setlang'])
async def change_language(message: aiogram.types.Message):
    """Изменить язык"""
    keyb = keyboards.Keyboards().select_lang()

    await bot.send_message(message.chat.id, "Выбери язык\nChoose a language\nElige un idioma", reply_markup = keyb)


@dp.message_handler(commands = ['settings'])
async def change_settings(message: aiogram.types.Message):
    """Меню настроек"""

    setting_keyb = keyboards.Keyboards().settings(users[message.from_user.id]['language'],
                                                             users[message.from_user.id
                                                             ]['results_count'],
                                                             users[message.from_user.id]['hearts_buttons'])

    await bot.send_message(message.chat.id,
                           messages.settings_menu[users[message.from_user.id]['language']],
                           reply_markup = setting_keyb)


@dp.message_handler(commands = ['my'])
async def user_playlist(message: aiogram.types.Message):
    user_lang = users[message.from_user.id]['language']
    playlist = users[message.from_user.id]['favourites_list']
    users[message.from_user.id]["playlist_page"] = 0

    if not playlist:
        await bot.send_message(message.chat.id, messages.no_playlist[user_lang])

    else:
        users[message.from_user.id]["playlist_page"] = 0
        f = lambda A, n=int(users[message.from_user.id]['results_count']): [
            A[i:i + n] for i in range(0, len(A), n)]
        cut_playlist = f(playlist)

        keyb = keyboards.Keyboards().for_user_playlist(
            cut_playlist[users[message.from_user.id]["playlist_page"]],
            message.chat.id, int(users[message.from_user.id]["results_count"]))
        user_playlist = []
        i = 1
        for item in cut_playlist[0]:
            for key, val in item.items():
                user_playlist.append(f"{i}. {key}")
                i += 1

        await bot.send_message(message.chat.id, '\n'.join(user_playlist), reply_markup = keyb)


@dp.callback_query_handler(lambda call: call.data == "to_right_playlist")
async def to_right_user_playlisy(call: aiogram.types.CallbackQuery):
    playlist = users[call.from_user.id]['favourites_list']
    playlist_page = users[call.from_user.id]["playlist_page"]
    user_lang = users[call.from_user.id]['language']
    try:

        if len(playlist) > 1 and playlist_page != len(playlist) - 1:
            users[call.from_user.id]["playlist_page"] += 1
            f = lambda A, n=int(users[call.from_user.id]['results_count']): [
                A[i:i + n] for i in range(0, len(A), n)]
            cut_playlist = f(playlist)
            keyb = keyboards.Keyboards().for_user_playlist(
                playlist[users[call.from_user.id]["playlist_page"]],
                call.message.chat.id, int(users[call.from_user.id]["results_count"]))
            user_playlist = []
            i = 1

            for item in cut_playlist[users[call.from_user.id]["playlist_page"]]:
                for key, val in item.items():
                    user_playlist.append(f"{i}. {key}")
                    i += 1

            await bot.edit_message_text(chat_id = call.message.chat.id,
                                        text = '\n'.join(user_playlist),
                                        message_id = call.message.message_id,
                                        reply_markup = keyb)

        else:
            await bot.answer_callback_query(call.id, messages.nothing_messages[user_lang])

    except IndexError:
        await bot.answer_callback_query(call.id, messages.nothing_messages[user_lang])


@dp.callback_query_handler(lambda call: call.data in ["change_lang", "count_result", "heart_buttons"])
async def settings_menu_changer(call: aiogram.types.CallbackQuery):
    if call.data == "change_lang":
        keyb = keyboards.Keyboards().select_lang()
        await bot.send_message(call.message.chat.id, "Выбери язык\nChoose a language\nElige un idioma",
                               reply_markup = keyb)
    elif call.data == "count_result":
        if users[call.from_user.id]["results_count"] == "10":
            users[call.from_user.id]["results_count"] = "6"
        elif users[call.from_user.id]["results_count"] == "6":
            users[call.from_user.id]["results_count"] = "8"
        elif users[call.from_user.id]["results_count"] == "8":
            users[call.from_user.id]["results_count"] = "10"

        setting_keyb = keyboards.Keyboards().settings(users[call.from_user.id]['language'],
                                                                 users[call.from_user.id]['results_count'],
                                                             users[call.from_user.id]['hearts_buttons'])
        users[call.from_user.id]["last_list"] = ""
        users[call.from_user.id]["last_urls_list"] = ""
        users[call.from_user.id]["urls"] = ""
        users[call.from_user.id]["without_formating"] = ""
        
        update_users_write()
        await bot.edit_message_text(chat_id = call.message.chat.id,
                                    text = messages.settings_menu[users[
                                        call.from_user.id]['language']],
                                    message_id = call.message.message_id,
                                    reply_markup = setting_keyb)
    elif call.data == "heart_buttons":
        if users[call.from_user.id]["hearts_buttons"] == "On":
            users[call.from_user.id]["hearts_buttons"] = "Off"
        elif users[call.from_user.id]["hearts_buttons"] == "Off":
            users[call.from_user.id]["hearts_buttons"] = "On"

        setting_keyb = keyboards.Keyboards().settings(users[call.from_user.id]['language'],
                                                                 users[call.from_user.id
                                                                 ]['results_count'],
                                                                 users[call.from_user.id]['hearts_buttons'])
        users[call.from_user.id]["last_list"] = ""
        users[call.from_user.id]["last_urls_list"] = ""
        users[call.from_user.id]["urls"] = ""
        users[call.from_user.id]["without_formating"] = ""

        update_users_write()
        await bot.edit_message_text(chat_id = call.message.chat.id,
                                    text = messages.settings_menu[users[
                                        call.from_user.id]['language']],
                                    message_id = call.message.message_id,
                                    reply_markup = setting_keyb)


@dp.message_handler(commands = ['newpost'])
async def malling(message: aiogram.types.Message):
    text_for_malling = message.text.replace('/newpost', '')
    update_users_read()

    i = 0
    for item in users.keys():
        try:
            await bot.send_message(int(item), text_for_malling)
            i += 1
        except (aiogram.exceptions.BotBlocked, aiogram.exceptions.ChatNotFound):
            pass

    await bot.send_message(message.chat.id, f'Сообщение получили <b>{i}</b> пользователей')


@dp.message_handler(commands = ['users'])
async def howusers(message: aiogram.types.Message):
    await bot.send_message(message.chat.id, f"<em>Кол-во пользователей</em>\n\n<b>{len(users)}</b> пользователей")


@dp.callback_query_handler(lambda call: call.data.startswith("playlist"))
async def select_sound(call: aiogram.types.CallbackQuery):
    get_song_num = call.data.split('_')
    playlist = users[call.from_user.id]['favourites_list']
    song_num = int(get_song_num[1]) - 1
    page = users[call.from_user.id]["playlist_page"]

    f = lambda A, n=int(users[call.from_user.id]['results_count']): [
        A[i:i + n] for i in range(0, len(A), n)]
    cut_playlist = f(playlist)
    keyb = keyboards.Keyboards().like_unlike_keyboard(
        users[call.from_user.id]["hearts_buttons"])
    for val in cut_playlist[page][song_num].values():
        await bot.send_audio(call.message.chat.id, audio = val,
                             caption = '<a href="https://t.me/Oxkingofchamps">🎧Oxkingofchamps©</a>', reply_markup = keyb)


def update_users_write():
    with open('./data/users.json', 'w') as write_users:
        json.dump(users, write_users, ensure_ascii = False, indent = 4)
        





def update_users_read():
    global users
    with open("./data/users.json", 'r') as read_users:
        users = json.load(read_users)
        temp_dict = {}
        for key, val in users.items():
            temp_dict[int(key)] = users[key]
        
        users = temp_dict
        temp_dict = {}
        

        
        import pprint; pprint.pprint(users)


if __name__ == "__main__":
    update_users_read()
    
    aiogram.executor.start_polling(dp, skip_updates = True)
