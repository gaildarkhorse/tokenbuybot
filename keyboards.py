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
            return keyboards['pair_buttons']

        for pair in pairs:
            caption = "✅" + pair['name']
            if pair['dex']:
                caption+=f"  ({pair['dex']})"
            c_data = f"pair_{str(button_num)}_{pair['name']}_{pair['address']}"

            button = types.InlineKeyboardButton(text=caption, callback_data=c_data)
            keyboards['pair_buttons'].add(button)
            button_num += 1
        
        return keyboards['pair_buttons']

    def select_chart(self, s_chart):
        keyboards['select_chart'] = types.InlineKeyboardMarkup()
        if s_chart == "DexView":
            caption = "✅DexView"
        else:
            caption ="DexView"
        btn1 = types.InlineKeyboardButton(
            text=caption, callback_data=f"select_chart_DexView")   
        if s_chart == "ProofOfX":
            caption = "✅ProofOfX"
        else:
            caption ="ProofOfX"
        btn2 = types.InlineKeyboardButton(
            text=caption, callback_data=f"select_chart_ProofOfX")
        if s_chart == "PooCoin":
            caption = "✅PooCoin"
        else:
            caption ="PooCoin"
        btn3 = types.InlineKeyboardButton(
            text=caption, callback_data=f"select_chart_PooCoin")
        if s_chart == "DexScreener":
            caption = "✅DexScreener"
        else:
            caption ="DexScreener"
        btn4 = types.InlineKeyboardButton(
            text=caption, callback_data=f"select_chart_DexScreener")
        
        btn5 = types.InlineKeyboardButton(
            text="🔙Go Back Group & Token Prefs", callback_data=f"select_chart_back")
        
        keyboards['select_chart'].row(btn1,btn2)
        keyboards['select_chart'].row(btn3,btn4)
        keyboards['select_chart'].row(btn5)

        return keyboards['select_chart']

    def select_settings_menu(self):
        keyboards['settings_menu'] = types.InlineKeyboardMarkup()

        btn1 = types.InlineKeyboardButton(
            text="🟢Buy Bot Settings", callback_data=f"settings_menu_buybot")   
             
        btn2 = types.InlineKeyboardButton(
            text="#️⃣Portal or Group Link", callback_data=f"settings_menu_grouplink")
        btn3 = types.InlineKeyboardButton(
            text="⚙️Buy Competition Settings", callback_data=f"settings_menu_buycomp")
        
        btn4 = types.InlineKeyboardButton(
            text="⏱Last Buy Settings", callback_data=f"settings_menu_lastcomp")
        
        keyboards['settings_menu'].row(btn1)
        keyboards['settings_menu'].row(btn2)
        keyboards['settings_menu'].row(btn3)
        keyboards['settings_menu'].row(btn4)

        return keyboards['settings_menu']

    def settings_tokengroup(self, tokengroup_data):
        on_off_text ={
            "on":"✅",
            "off":"🚫",
        }
        keyboards['settings_tokengroup'] = types.InlineKeyboardMarkup()

        if tokengroup_data["group_link"]=="":
            caption = "#️⃣Portal or Group Link"
        else:
            caption = f"#️⃣{tokengroup_data['group_link']}"

        btn1 = types.InlineKeyboardButton(
            text=caption, callback_data=f"settings_tokengroup_grouplink")   
             
        btn2 = types.InlineKeyboardButton(
            text=f"{on_off_text[tokengroup_data['notify_whale_buy']]}Notify Whale Buy's", callback_data=f"settings_tokengroup_notifywhalebuy")
        btn3 = types.InlineKeyboardButton(
            text=f"📊 Selected Chart: {tokengroup_data['selected_chart']}", callback_data=f"settings_tokengroup_selectedchart")
        
        if tokengroup_data['circulating_supply']=="":
            caption=f"🔄Circulating Supply"
        else:
            caption=f"🔄C.Supply: {tokengroup_data['circulating_supply']}"
        btn4 = types.InlineKeyboardButton(
            text=caption, callback_data=f"settings_tokengroup_csupply")

        btn5 = types.InlineKeyboardButton(
            text="🔙Go Back to Bot Settings", callback_data=f"settings_tokengroup_back")
        
        keyboards['settings_tokengroup'].row(btn1)
        keyboards['settings_tokengroup'].row(btn2)
        keyboards['settings_tokengroup'].row(btn3)
        keyboards['settings_tokengroup'].row(btn4)
        keyboards['settings_tokengroup'].row(btn5)

        return keyboards['settings_tokengroup']

    def settings_buycomp(self,g_data):
        onComp = g_data['ongoing']=="off" 
        keyboards['settings_buycomp'] = types.InlineKeyboardMarkup()

        btn1 = types.InlineKeyboardButton(
            text=("⏳" if onComp else "🔒")+f"Length ({g_data['big_buy_comp']['length']} minute)", callback_data=f"settings_buycomp_length")   
             
        btn2 = types.InlineKeyboardButton(
            text=("#️⃣" if onComp else "🔒")+f"Min Buy ({g_data['big_buy_comp']['min_buy']} {g_data['alt_token_name']})", callback_data=f"settings_buycomp_minbuy")
        btn3 = types.InlineKeyboardButton(
            text=("🥇" if onComp else "🔒")+f"Prize ({g_data['big_buy_comp']['prize'][0]} {g_data['alt_token_name']})", callback_data=f"settings_buycomp_prize1")
        
        btn4 = types.InlineKeyboardButton(
            text=("💎" if onComp else "🔒")+f"Must Hold ({g_data['big_buy_comp']['must_hold']} hours)", callback_data=f"settings_buycomp_musthold")

        btn5 = types.InlineKeyboardButton(
            text=("🥈" if onComp else "🔒")+f"2nd Pr. ({g_data['big_buy_comp']['prize'][1]} {g_data['alt_token_name']})", callback_data=f"settings_buycomp_prize2")   
             
        btn6 = types.InlineKeyboardButton(
            text=("🥉" if onComp else "🔒")+f"3rd Pr. ({g_data['big_buy_comp']['prize'][2]} {g_data['alt_token_name']})", callback_data=f"settings_buycomp_prize3") 
        
        btn7 = types.InlineKeyboardButton(
            text=("🏆" if onComp else "🔒")+f"Start Biggest Buy Competition!"+("🏆" if onComp else "🔒"), callback_data=f"settings_buycomp_start")
        
        btn8 = types.InlineKeyboardButton(
            text=f"🔙Go Back to Bot Settings", callback_data=f"settings_buycomp_back")
        
        keyboards['settings_buycomp'].row(btn1,btn2)
        keyboards['settings_buycomp'].row(btn3,btn4)
        keyboards['settings_buycomp'].row(btn5,btn6)
        keyboards['settings_buycomp'].row(btn7)
        keyboards['settings_buycomp'].row(btn8)
        return keyboards['settings_buycomp']

    def settings_lastcomp(self,g_data):
        keyboards['settings_lastcomp'] = types.InlineKeyboardMarkup()
        onComp = g_data['ongoing']=="off"
        btn1 = types.InlineKeyboardButton(
            text=("⏳" if onComp else "🔒")+f"Countdown ({g_data['last_buy_comp']['countdown']} minutes)", callback_data=f"settings_lastcomp_length")   
             
        btn2 = types.InlineKeyboardButton(
            text=("#️⃣" if onComp else "🔒")+f"Minimum Buy ({g_data['last_buy_comp']['min_buy']} {g_data['alt_token_name']})", callback_data=f"settings_lastcomp_minbuy")
        btn3 = types.InlineKeyboardButton(
            text=("🥇" if onComp else "🔒")+f"Prize ({g_data['last_buy_comp']['prize']} {g_data['alt_token_name']})", callback_data=f"settings_lastcomp_prize1")
        
        btn4 = types.InlineKeyboardButton(
            text=("💎" if onComp else "🔒")+f"Must Hold {g_data['last_buy_comp']['must_hold']} hours)", callback_data=f"settings_lastcomp_musthold")
        
        btn5 = types.InlineKeyboardButton(
            text=("🏆" if onComp else "🔒")+"Start Last Buy Competition!"+("🏆" if onComp else "🔒"), callback_data=f"settings_lastcomp_start")
        
        btn6 = types.InlineKeyboardButton(
            text=f"🔙Go Back to Bot Settings", callback_data=f"settings_lastcomp_back")
        
        keyboards['settings_lastcomp'].row(btn1)
        keyboards['settings_lastcomp'].row(btn2)
        keyboards['settings_lastcomp'].row(btn3,btn4)
        keyboards['settings_lastcomp'].row(btn5)
        keyboards['settings_lastcomp'].row(btn6)
        return keyboards['settings_lastcomp']

    def remove(self):
        keyboards['remove'] = types.InlineKeyboardMarkup()

        removebtn = types.InlineKeyboardButton(
            text="➡️ YES! Remove Token", callback_data=f"remove_token")   
        
        keyboards['remove'].row(removebtn)

        return keyboards['remove']

    def show_winners(self):
        keyboards['show_winners'] = types.InlineKeyboardMarkup()

        btn1 = types.InlineKeyboardButton(
            text="⏫SEND TXN TO PROVE PAYMENT", callback_data=f"show_winners_sendtxn")   
        
        keyboards['show_winners'].row(btn1)

        return keyboards['show_winners']
    
    def disq_keys(self):
        keyboards['disq_keys'] = types.InlineKeyboardMarkup()

        btn1 = types.InlineKeyboardButton(
            text="➡️Biggest Buy", callback_data=f"disq_keys_bigbuy") 
        btn2 = types.InlineKeyboardButton(
            text="➡️Last Buy", callback_data=f"disq_keys_lastbuy")   
        
        keyboards['disq_keys'].row(btn1,btn2)

        return keyboards['disq_keys']
    
    def settings_buybot(self,g_data):
        keyboards['settings_buybot'] = types.InlineKeyboardMarkup()
        on_off_text ={
            "on":"✅",
            "off":"🚫",
        }
        showbuysbtn = types.InlineKeyboardButton(
            text=f"❔ Show Buys w/out Comp{on_off_text[g_data['show_buys_w/out_comp']]}", callback_data=f"settings_buybot_showbuyswithorwithoutcomp")   
             
        gifimagebtn = types.InlineKeyboardButton(
            text=f"✅Gif/Image", callback_data=f"settings_buybot_gif")
        minbuybtn = types.InlineKeyboardButton(
            text=f"⏫Min Buy ${g_data['min_buy']}", callback_data=f"settings_buybot_minbuy")
        
        buyemojibtn = types.InlineKeyboardButton(
            text=f"{g_data['buy_emoji']}Buy Emoji", callback_data=f"settings_buybot_emoji")
        buystepbtn = types.InlineKeyboardButton(
            text=f"💲Buy Step ${g_data['buy_step']}", callback_data=f"settings_buybot_buystep")

        tokengroupPrefBtn = types.InlineKeyboardButton(
            text="⚙️Token & Group Preferences", callback_data=f"settings_buybot_tokengrouppref")
                
        bigbuycompbtn = types.InlineKeyboardButton(
            text="Big Buy Comp⏩", callback_data=f"settings_buybot_bigbuycomp")        
        lastbuycompbtn = types.InlineKeyboardButton(
            text="Last Buy Comp⏩", callback_data=f"settings_buybot_lastbuycomp")

        keyboards['settings_buybot'].add(showbuysbtn)
        keyboards['settings_buybot'].add(gifimagebtn, minbuybtn)
        keyboards['settings_buybot'].add(buyemojibtn, buystepbtn)
        keyboards['settings_buybot'].add(tokengroupPrefBtn)
        keyboards['settings_buybot'].add(bigbuycompbtn, lastbuycompbtn)

        return keyboards['settings_buybot']

    def select_chain(self):
        keyboards['select_chain'] = types.InlineKeyboardMarkup()
        ethBtn = types.InlineKeyboardButton(
            text="Ethereum (ETH)", callback_data=f"select_chain_eth")   
        bscBtn = types.InlineKeyboardButton(
            text="Binance Smart Chain (BSC)", callback_data=f"select_chain_bsc")
        bscTestnetBtn = types.InlineKeyboardButton(
            text="Binance Smart Chain Testnet(BSC)", callback_data=f"select_chain_bsctest")
                
        keyboards['select_chain'].add(ethBtn)
        keyboards['select_chain'].add(bscBtn)
        # keyboards['select_chain'].add(bscTestnetBtn)
        return keyboards['select_chain']
