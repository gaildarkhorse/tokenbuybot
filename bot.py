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

bot_name = "Tetra Trending Bot"
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

    setting_keyb = keyboards.Keyboards().settings()
    await bot.send_message(message.chat.id,
                           messages.settings_menu,
                           reply_markup = setting_keyb)
    
@dp.message_handler(commands = ['add'])
async def add_message(message: aiogram.types.Message):
    gid = message.chat.id
    if_init(gid)
    reset_status(gid)
    
    print(gid,message.from_user.first_name, message.text) 
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
    comps[gid]["pair_address"] = ""
    comps[gid]["chain"] = ""
    comps[gid]["ongoing"] = "off"
    reset_status(gid)
    BotAPI(gid).stop()
    
   
        
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
    