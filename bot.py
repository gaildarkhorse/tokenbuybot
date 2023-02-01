import aiogram
import asyncio
import config
import messages
import json
from downloader import BotAPI
import keyboards
import string
import requests
import time
import urllib3

bot = aiogram.Bot(token = config.API_TOKEN,
                  parse_mode = aiogram.types.ParseMode.HTML)
loop = asyncio.get_event_loop()
dp = aiogram.Dispatcher(bot, loop = loop)


comps ={}

def verify_token_address(addr):
    return addr.startswith("0x") and len(addr[2:])==40 and all(c in string.hexdigits for c in addr[2:].lower())
def if_init(gid):
    # print(comps.keys())
    if gid not in comps.keys():
        comps[gid] = messages.initialcompvalue
        update_comps_write()
def reset_status(gid):
    comps[gid]["status"] = ""
    update_comps_write()

def get_settings_menuvalue(setting, gid):
    caption = f"⚙️{messages.bot_name}\n\n<i>Buy Bot with Top Trending @BuyBotTrending and Automatic & Customizable Games. (Bot Tracks Cumulative Buys for Biggest Buy Comp)</i>"
    if setting == "buybot":
        keyb = keyboards.Keyboards().settings_buybot(comps[gid])
    elif setting == "buycomp":
        keyb = keyboards.Keyboards().settings_buycomp(comps[gid])
    elif setting == "lastcomp":
        keyb = keyboards.Keyboards().settings_lastcomp(comps[gid])

    comps[gid]['status']=""
    return caption, keyb

@dp.message_handler(commands = ['remove'])
async def remove_message(message: aiogram.types.Message):
    keyb = keyboards.Keyboards().remove()
    gid = message.chat.id
    if_init(gid)
    reset_status(gid)
    print(gid,message.from_user.first_name, message.text)
    await bot.send_message(gid, messages.remove_confirm_message, reply_to_message_id=message.message_id,reply_markup = keyb)
    

@dp.message_handler(commands = ['help'])
async def help_message(message: aiogram.types.Message):
    gid = message.chat.id
    if_init(gid)
    reset_status(gid)
    
    print(gid,message.from_user.first_name, message.text)
    await bot.send_message(gid, messages.help_message,reply_to_message_id=message.message_id)
    
@dp.message_handler(commands = ['start'])
async def start_message(message: aiogram.types.Message):
    await help_message(message)

@dp.message_handler(commands = ['settings'])
async def change_settings(message: aiogram.types.Message):
    gid = message.chat.id
    if_init(gid)
    reset_status(gid)
    c,k = get_settings_menuvalue("buybot",gid)
    await bot.send_message(gid, c, reply_markup=k)
    
@dp.message_handler(commands = ['add'])
async def add_message(message: aiogram.types.Message):
    gid = message.chat.id
    if_init(gid)
    reset_status(gid)
    print(gid,message.from_user.first_name, message.text)
    if comps[gid]['token_address'] and comps[gid]['token_name']:
        await bot.send_message(gid, f"❗️ Bot already in use in this group for token\n{comps[gid]['token_address']}")
        return
     
    keyb = keyboards.Keyboards().select_chain()
    await bot.send_message(message.chat.id,
                           messages.select_chain_menu,
                           reply_markup = keyb,
                           reply_to_message_id=message.message_id)
    
@dp.message_handler(
    lambda message: message.text not in config.commands and not message.text.startswith("/"))
async def handle_input(message: aiogram.types.Message):
    # print(message)
    
    gid = message.chat.id
    if_init(gid)
    print(gid,message.from_user.first_name, message.text)
    if comps[gid]["status"] == "wait_token_address":
        if verify_token_address(message.text):
            comps[gid]["token_address"] = message.text.strip()
            pairs = BotAPI(gid,comps[gid]).get_tokeninfo()
            num_pairs = len(pairs)
            
            if num_pairs > 0:
                token_name = pairs[0]["name"].split("/")[0]
                comps[gid]["token_name"] = token_name
            keyb = keyboards.Keyboards().select_pair(pairs)
            await message.reply("ℹ️Select Pair Listed Below",reply_markup=keyb)
        else:
            comps[gid]["token_address"] = ""
            await message.reply(f"❌Token address not valid({message.text}). Try again")
    
    reset_status(gid)
    

        
    
@dp.callback_query_handler(lambda call: call.data == "remove_token")
async def remove_token(call: aiogram.types.CallbackQuery):
    gid = call.message.chat.id
    if_init(gid)
    
    print(gid,call.message.from_user.first_name, call.message.text)
    if comps[gid]["token_address"] != "":
        await bot.send_message(gid, messages.remove_done_message[0])
    else:
        await bot.send_message(gid, messages.remove_done_message[1])
    comps[gid]["token_address"] = ""
    comps[gid]["token_name"] = ""
    comps[gid]["alt_token_name"] = ""
    comps[gid]["pair_address"] = ""
    comps[gid]["chain"] = ""
    comps[gid]["ongoing"] = "off"
    reset_status(gid)
    if comps[gid]["ongoing"]=="on":BotAPI(gid,comps[gid]).stop()

@dp.callback_query_handler(lambda call: call.data.startswith("pair") and len(call.data.split("_"))==4)
async def select_pair(call: aiogram.types.CallbackQuery):
    gid = call.message.chat.id
    if_init(gid)
    
    print(gid,call.message.from_user.first_name, call.message.text)
    c_data = call.data.split("_")
    token_name = c_data[2].split("/")[0]
    alt_token_name = c_data[2].split("/")[1]
    pair_address = c_data[3]
    if not comps[gid]["token_name"]:
        await bot.send_message(gid, "❌Pair not found")
    elif comps[gid]["token_name"] != token_name:
        await bot.send_message(gid, f"❗️ Bot already in use in this group for token\n{comps[gid]['token_address']}")
    else:    
        comps[gid]["token_name"] = token_name
        comps[gid]["alt_token_name"] = alt_token_name
        comps[gid]["pair_address"] = pair_address
        keyb = keyboards.Keyboards().select_settings_menu()
        await bot.send_message(gid, f"✅{token_name}({comps[gid]['chain']}) added to <b>{messages.bot_name}!</b>\n\n<i>Attach Your Telegram by selecting “Portal or Group Link” to make it clickable if you Trend at @BuyBotTrending!</i>", reply_markup=keyb, reply_to_message_id=call.message.message_id)
    reset_status(gid)

@dp.callback_query_handler(lambda call: call.data.startswith("settings_buybot") and len(call.data.split("_"))==3)
async def settings_buybot(call: aiogram.types.CallbackQuery):
    gid = call.message.chat.id
    if_init(gid)

    c_data = call.data.split("_")[2]
    if c_data == "showbuyswithorwithoutcomp":
        flag = comps[gid]['show_buys_w/out_comp']
        # print("flag=> ", flag)
        if flag == "on":
            flag = "off"
        else:
            flag = "on"
        # print("flag=> ", flag)
        comps[gid]['show_buys_w/out_comp'] = flag
        comps[gid]['status'] = ""
        c, k = get_settings_menuvalue('buybot', gid)
        await bot.edit_message_reply_markup(gid, call.message.message_id,reply_markup=k)
    elif c_data == "minbuy":
        pass
    elif c_data == "bigbuycomp":
        comps[gid]['status'] = ""
        c, k = get_settings_menuvalue('buycomp', gid)
        await bot.edit_message_reply_markup(gid, call.message.message_id,reply_markup=k)
    update_comps_write()

@dp.callback_query_handler(lambda call: call.data.startswith("settings_buycomp") and len(call.data.split("_"))==3)
async def settings_buybot(call: aiogram.types.CallbackQuery):
    gid = call.message.chat.id
    if_init(gid)

    c_data = call.data.split("_")[2]
    if c_data == "start":
        if not (comps[gid]['pair_address'] and comps[gid]['token_name'] and comps[gid]['token_address']):
            await bot.send_message(gid, "❗️You must add token to chat first. Use /add command")
        elif comps[gid]['ongoing']=='on':
            await bot.send_message(gid, "❌Another buy competition already started")
        else:
            comps[gid]['ongoing'] = 'on'
            image_fn = open(f"images/{comps[gid]['gif_image']}",'rb')
            await bot.send_photo(gid, image_fn,
            """ Biggest Buy Competition Started

            Start at 15:35:00 UTC
            Ends in 29 min 23 sec
            Minimum Buy 0.10 BNB

            Winning Prize 1 BNB (2nd 0.05 BNB) 
            Winner must hold at least 1 hours

            Chart  Events  Trending")
            """)
    reset_status(gid)



@dp.callback_query_handler(
    lambda call: call.data.startswith("settings_menu"))
async def select_settings_menu(call: aiogram.types.CallbackQuery):
    gid = call.message.chat.id
    if_init(gid)
    print(gid,call.message.from_user.first_name, call.message.text)
    c_data = call.data.split('_')[2]
    if c_data == "grouplink":
        comps[gid]['status']="wait_grouplink"
        await bot.send_message(gid,"➡️Send me group or portal link")
    else:
        c, k = get_settings_menuvalue(c_data, gid)
        await bot.edit_message_reply_markup(gid, call.message.message_id,reply_markup=k)

    update_comps_write()


@dp.callback_query_handler(
    lambda call: call.data.startswith("select_chain"))
async def select_chain(call: aiogram.types.CallbackQuery):
    gid = call.message.chat.id
    if_init(gid)
    chain = call.data.split('_')[2].upper()
    await bot.send_message(gid,"➡️["+chain+"]"+messages.token_address_question)
    comps[gid]["status"] = "wait_token_address"
    comps[gid]["chain"] = chain
    print(gid, call["from"]["first_name"], chain + " selected")
    update_comps_write()












def update_comps_write():
    with open('./data/comps.json', 'w') as write_comps:
        json.dump(comps, write_comps, ensure_ascii = False, indent = 4)
        
def update_comps_read():
    global comps
    with open("./data/comps.json", 'r') as read_comps:
        comps = json.load(read_comps)
        temp_dict = {}
        for key, val in comps.items():
            temp_dict[int(key)] = comps[key]
        
        comps = temp_dict
        temp_dict = {}


if __name__ == "__main__":
    print("Tetra Trending Bot Started...")
    update_comps_read()
    aiogram.executor.start_polling(dp, skip_updates = True)
    