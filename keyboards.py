from aiogram import types
import messages

keyboards = {
    "move_and_delete_buttons": types.InlineKeyboardMarkup()
}


class Keyboards:

    def __init__(self, keyboards=keyboards):

        self.keyboards = keyboards

    def for_songs_list(self, list_page, user_id, count):
        self.list_page = list_page
        self.user_id = user_id
        self.count = count

        buttons = []
        button_num = 1

        for item in list_page:
            buttons.append(types.InlineKeyboardButton(
                text=str(button_num), callback_data=f"select_{button_num}_{self.user_id}"))
            button_num += 1

        rows = {
            6: 6,
            8: 4,
            10: 5
        }

        try:
            keyboards[f"song_select_{self.user_id}"] = types.InlineKeyboardMarkup(row_width=len(buttons))
        except KeyError:

            keyboards[f"song_select_{self.user_id}"] = types.InlineKeyboardMarkup(
                row_width=len(buttons))

        if not list_page:
            return False

        elif len(buttons) == 1:
            keyboards[f"song_select_{self.user_id}"].add(
                buttons[0])

        elif len(buttons) == 2:
            keyboards[f"song_select_{self.user_id}"].add(
                buttons[0], buttons[1])

        elif len(buttons) == 3:
            keyboards[f"song_select_{self.user_id}"].add(
                buttons[0], buttons[1], buttons[2])

        elif len(buttons) == 4:
            keyboards[f"song_select_{self.user_id}"].add(
                buttons[0], buttons[1], buttons[2],
                buttons[3])

        elif len(self.list_page) == 5:
            
            keyboards[f"song_select_{self.user_id}"].add(
                buttons[0], buttons[1], buttons[2],
                buttons[3], buttons[4])

        elif len(buttons) == 6:
            keyboards[f"song_select_{self.user_id}"].add(
                buttons[0], buttons[1], buttons[2],
                buttons[3], buttons[4], buttons[5])

        elif len(buttons) == 7:
            keyboards[f"song_select_{self.user_id}"].add(
                buttons[0], buttons[1], buttons[2],
                buttons[3], buttons[4], buttons[5], buttons[6])

        elif len(buttons) == 9:
            keyboards[f"song_select_{self.user_id}"].add(
                buttons[0], buttons[1], buttons[2], buttons[3],
                buttons[4], buttons[5], buttons[6], buttons[7], buttons[8])

        elif len(buttons) == 8:
            keyboards[f"song_select_{self.user_id}"].add(
                buttons[0], buttons[1], buttons[2], buttons[3],
                buttons[4], buttons[5], buttons[6], buttons[7])

        elif len(buttons) == 10:

            keyboards[f"song_select_{self.user_id}"].add(
                buttons[0], buttons[1], buttons[2], buttons[3], buttons[4],
                buttons[5], buttons[6], buttons[7], buttons[8], buttons[9])

        to_left = types.InlineKeyboardButton(
            text="⬅️", callback_data=f"to_left")
        close = types.InlineKeyboardButton(text="❌", callback_data=f"close")
        to_right = types.InlineKeyboardButton(
            text="➡️", callback_data=f"to_right")
        keyboards[f"song_select_{self.user_id}"].row(to_left, close, to_right)

        return keyboards[f"song_select_{self.user_id}"]

    def like_unlike_keyboard(self, status):
        self.status = status
        if self.status == "On":
            like = types.InlineKeyboardButton(text="❤️", callback_data="like")
            close = types.InlineKeyboardButton(
                text="❌", callback_data=f"close")
            unlike = types.InlineKeyboardButton(
                text="💔", callback_data="unlike")

            keyboards["likeunlike"] = types.InlineKeyboardMarkup(row_width=3)
            keyboards[f"likeunlike"].row(like, close, unlike)

            return keyboards["likeunlike"]
        else:
            keyboards["likeunlike"] = types.InlineKeyboardMarkup()
            return keyboards["likeunlike"]

    def for_user_playlist(self, list_page, user_id, count):
        self.list_page = list_page
        self.user_id = user_id
        self.count = count

        buttons = []
        button_num = 1

        for item in list_page:
            buttons.append(types.InlineKeyboardButton(
                text=str(button_num), callback_data=f"playlist_{button_num}_{self.user_id}"))
            button_num += 1

        rows = {
            6: 6,
            8: 4,
            10: 5
        }

        try:
            keyboards[f"playlist_{self.user_id}"] = types.InlineKeyboardMarkup(
                row_width=rows[len(buttons)])
        except KeyError:
            keyboards[f"playlist_{self.user_id}"] = types.InlineKeyboardMarkup(
                row_width=len(buttons))

        if not list_page:
            return False

        elif len(buttons) == 1:
            keyboards[f"playlist_{self.user_id}"].add(
                buttons[0])

        elif len(buttons) == 2:
            keyboards[f"playlist_{self.user_id}"].add(
                buttons[0], buttons[1])

        elif len(buttons) == 3:
            keyboards[f"playlist_{self.user_id}"].add(
                buttons[0], buttons[1], buttons[2])

        elif len(buttons) == 4:
            keyboards[f"playlist_{self.user_id}"].add(
                buttons[0], buttons[1], buttons[2],
                buttons[3])

        elif len(self.list_page) == 5:
            keyboards[f"playlist_{self.user_id}"].add(
                buttons[0], buttons[1], buttons[2],
                buttons[3], buttons[4])

        elif len(buttons) == 6:
            keyboards[f"playlist_{self.user_id}"].add(
                buttons[0], buttons[1], buttons[2],
                buttons[3], buttons[4], buttons[5])

        elif len(buttons) == 7:
            keyboards[f"playlist_{self.user_id}"].add(
                buttons[0], buttons[1], buttons[2],
                buttons[3], buttons[4], buttons[5], buttons[6])

        elif len(buttons) == 9:
            keyboards[f"playlist_{self.user_id}"].add(
                buttons[0], buttons[1], buttons[2], buttons[3],
                buttons[4], buttons[5], buttons[6], buttons[7], buttons[8])

        elif len(buttons) == 8:
            keyboards[f"playlist_{self.user_id}"].add(
                buttons[0], buttons[1], buttons[2], buttons[3],
                buttons[4], buttons[5], buttons[6], buttons[7])

        elif len(buttons) == 10:

            keyboards[f"playlist_{self.user_id}"].add(
                buttons[0], buttons[1], buttons[2], buttons[3], buttons[4],
                buttons[5], buttons[6], buttons[7], buttons[8], buttons[9])

        to_right = types.InlineKeyboardButton(
            text="➡️", callback_data=f"to_right_playlist")
        keyboards[f"playlist_{self.user_id}"].row(to_right)
        return keyboards[f"playlist_{self.user_id}"]

    def select_lang(self):
        keyboards['lang_buttons'] = types.InlineKeyboardMarkup(row_width=3)

        ru_button = types.InlineKeyboardButton(
            text="Русский🇷🇺", callback_data=f"select_ru")
        en_button = types.InlineKeyboardButton(
            text="English🇬🇧", callback_data=f"select_en")
        es_button = types.InlineKeyboardButton(
            text="Español🇪🇸", callback_data=f"select_es")

        keyboards['lang_buttons'].row(es_button, ru_button, en_button)

        return keyboards['lang_buttons']

    def settings(self, lang, count, button_status):
        self.lang = lang
        self.count = count
        self.button_status = button_status

        keyboards['settings'] = types.InlineKeyboardMarkup()

        change_lang = types.InlineKeyboardButton(
            text=messages.change_language[self.lang], callback_data=f"change_lang")

        change_lang = types.InlineKeyboardButton(
            text=messages.change_language[self.lang], callback_data=f"change_lang")
        change_lang = types.InlineKeyboardButton(
            text=messages.change_language[self.lang], callback_data=f"change_lang")
        change_lang = types.InlineKeyboardButton(
            text=messages.change_language[self.lang], callback_data=f"change_lang")        

        count_result = types.InlineKeyboardButton(
            text=messages.change_count_results[self.lang]+str(self.count), callback_data=f"count_result")
        heart_buttons = types.InlineKeyboardButton(
            text=messages.del_button_with_hearts[self.lang]+self.button_status, callback_data=f"heart_buttons")
        close = types.InlineKeyboardButton(text="❌", callback_data=f"close")

        keyboards['settings'].add(change_lang)
        keyboards['settings'].add(count_result)
        keyboards['settings'].add(heart_buttons)
        keyboards['settings'].add(close)

        return keyboards['settings']
