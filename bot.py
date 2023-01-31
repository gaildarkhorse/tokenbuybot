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

status = ""
users = {}
chain = ""
token = "1234"

@dp.message_handler(commands = ['remove'])
async def help_message(message: aiogram.types.Message):
    print(message["from"]["first_name"], message["text"])
    keyb = keyboards.Keyboards().remove()
    await bot.send_message(message.chat.id, messages.remove_confirm_message, reply_to_message_id=message.message_id,reply_markup = keyb)

@dp.message_handler(commands = ['help'])
async def help_message(message: aiogram.types.Message):
    print(message["from"]["first_name"], message["text"])
    await bot.send_message(message.chat.id, messages.help_message,reply_to_message_id=message.message_id)
    
@dp.message_handler(commands = ['start'])
async def start_message(message: aiogram.types.Message):
    await help_message(message)

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
    
@dp.message_handler(commands = ['add'])
async def search_for_artist_name(message: aiogram.types.Message):
    """Искать по артисту"""
    print("/add")    
    setting_keyb = keyboards.Keyboards().select_chain(users[message.from_user.id]['language'],
                                                             users[message.from_user.id
                                                             ]['results_count'],
                                                             users[message.from_user.id]['hearts_buttons'])
    await bot.send_message(message.chat.id,
                           messages.select_chain_menu[users[message.from_user.id]['language']],
                           reply_markup = setting_keyb)



  
@dp.callback_query_handler(lambda call: call.data == "remove_token")
async def remove_token(call: aiogram.types.CallbackQuery):
    if token != "":
        await bot.send_message(call.message.chat.id, messages.remove_done_message[0])
    await bot.send_message(call.message.chat.id, messages.remove_done_message[1])
    
        
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


@dp.message_handler(commands = ['comp'])
async def search_for_artist_name(message: aiogram.types.Message):
    """Искать по артисту"""
    config.search_field = "artist"
    await message.reply(
        messages.artist_messages[users[message.from_user.id]['language']])

@dp.message_handler(commands = ['winners'])
async def search_for_category_name(message: aiogram.types.Message):
    config.search_field = "category"
    await message.reply(
        messages.category_messages[users[message.from_user.id]['language']])


@dp.message_handler(commands = ['info'])
async def change_language(message: aiogram.types.Message):
    """Изменить язык"""
    keyb = keyboards.Keyboards().select_lang()

    await bot.send_message(message.chat.id, "Выбери язык\nChoose a language\nElige un idioma", reply_markup = keyb)



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
    