from aiogram import types
import messages

keyboards = {
    "move_and_delete_buttons": types.InlineKeyboardMarkup()
}


class Keyboards:

    def __init__(self, keyboards=keyboards):

        self.keyboards = keyboards

    def select_pair(self, pairs):

        button_num = 0
        keyboards['pair_buttons'] = types.InlineKeyboardMarkup()
        if len(pairs) == 0:
            return False

        for pair in pairs:
            caption = "✅" + pair['name']
            if pair['dex']:
                caption+=f"  ({pair['dex']})"
            c_data = f"pair_{str(button_num)}_{pair['name']}_{pair['address']}"

            button = types.InlineKeyboardButton(text=caption, callback_data=c_data)
            keyboards['pair_buttons'].add(button)
            button_num += 1
        
        return keyboards['pair_buttons']

    def select_lang(self):
        keyboards['lang_buttons'] = types.InlineKeyboardMarkup()

        showbuysbtn = types.InlineKeyboardButton(
            text="❔ Show Buys w/out Comp✅", callback_data=f"select_ru")   
             
        gifimagebtn = types.InlineKeyboardButton(
            text="✅Gif/Image", callback_data=f"select_ru")
        minbuybtn = types.InlineKeyboardButton(
            text="⏫Min Buy $1", callback_data=f"select_ru")
        
        buyemojibtn = types.InlineKeyboardButton(
            text="🟢Buy Emoji", callback_data=f"select_en")
        buystepbtn = types.InlineKeyboardButton(
            text="💲Buy Step $1", callback_data=f"select_es")

        tokengroupPrefBtn = types.InlineKeyboardButton(
            text="⚙️Token & Group Preferences", callback_data=f"select_es")
                
        bigbuycompbtn = types.InlineKeyboardButton(
            text="Big Buy Comp⏩", callback_data=f"select_es")        
        lastbuycompbtn = types.InlineKeyboardButton(
            text="Last Buy Comp⏩", callback_data=f"select_es")
        
        keyboards['lang_buttons'].row(showbuysbtn)
        keyboards['lang_buttons'].row(gifimagebtn, minbuybtn)
        keyboards['lang_buttons'].row(buyemojibtn, buystepbtn)
        keyboards['lang_buttons'].row(tokengroupPrefBtn)
        keyboards['lang_buttons'].row(bigbuycompbtn, lastbuycompbtn)

        return keyboards['lang_buttons']

    def remove(self):
        keyboards['remove'] = types.InlineKeyboardMarkup()

        removebtn = types.InlineKeyboardButton(
            text="➡️ YES! Remove Token", callback_data=f"remove_token")   
        
        keyboards['remove'].row(removebtn)

        return keyboards['remove']
    
    def settings(self):
        keyboards['settings'] = types.InlineKeyboardMarkup()

        showbuysbtn = types.InlineKeyboardButton(
            text="❔ Show Buys w/out Comp✅", callback_data=f"select_ru")   
             
        gifimagebtn = types.InlineKeyboardButton(
            text="✅Gif/Image", callback_data=f"select_ru")
        minbuybtn = types.InlineKeyboardButton(
            text="⏫Min Buy $1", callback_data=f"select_ru")
        
        buyemojibtn = types.InlineKeyboardButton(
            text="🟢Buy Emoji", callback_data=f"select_en")
        buystepbtn = types.InlineKeyboardButton(
            text="💲Buy Step $1", callback_data=f"select_es")

        tokengroupPrefBtn = types.InlineKeyboardButton(
            text="⚙️Token & Group Preferences", callback_data=f"select_es")
                
        bigbuycompbtn = types.InlineKeyboardButton(
            text="Big Buy Comp⏩", callback_data=f"select_es")        
        lastbuycompbtn = types.InlineKeyboardButton(
            text="Last Buy Comp⏩", callback_data=f"select_es")

        keyboards['settings'].add(showbuysbtn)
        keyboards['settings'].add(gifimagebtn, minbuybtn)
        keyboards['settings'].add(buyemojibtn, buystepbtn)
        keyboards['settings'].add(tokengroupPrefBtn)
        keyboards['settings'].add(bigbuycompbtn, lastbuycompbtn)

        return keyboards['settings']

    def select_chain(self):
        keyboards['select_chain'] = types.InlineKeyboardMarkup()
        ethBtn = types.InlineKeyboardButton(
            text="Ethereum (ETH)", callback_data=f"select_chain_eth")   
        bscBtn = types.InlineKeyboardButton(
            text="Binance Smart Chain (BSC)", callback_data=f"select_chain_bsc")
                
        keyboards['select_chain'].add(ethBtn)
        keyboards['select_chain'].add(bscBtn)
        return keyboards['select_chain']
