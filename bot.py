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
from datetime import datetime

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
    caption = f"⚙️<b>{messages.bot_name}</b>\n\n<i>Buy Bot with Top Trending @BuyBotTrending and Automatic & Customizable Games. (Bot Tracks Cumulative Buys for Biggest Buy Comp)</i>"
    if setting == "buybot":
        keyb = keyboards.Keyboards().settings_buybot(comps[gid])
    elif setting == "buycomp":
        keyb = keyboards.Keyboards().settings_buycomp(comps[gid])
    elif setting == "lastcomp":
        keyb = keyboards.Keyboards().settings_lastcomp(comps[gid])
    elif setting == "tokengroup":
        caption = f"⚙️<b>{messages.bot_name}</b>\n\n<i>Attach your Telegram Group Link to make it clickable if you Trend at @BuyBotTrending</i>"
        keyb = keyboards.Keyboards().settings_tokengroup(comps[gid]["token_group_pref"])
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
    if comps[gid]['alt_token_name']=="" or comps[gid]['token_address']=="":
        await bot.send_message(gid, "Firstly type /add to start tracking your coin", reply_to_message_id=message.message_id)
        return
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
    elif comps[gid]["status"] == "wait_grouplink":
        if not message.text.startswith("https://"):
            await message.reply(f"❌Link not valid ({message.text}). Try again\nFormat: `https://t.me/mygroup`",parse_mode=aiogram.types.ParseMode().MARKDOWN)
        else:
            comps[gid]['token_group_pref']['group_link'] = message.text
            keyb = keyboards.Keyboards().settings_tokengroup(comps[gid]['token_group_pref'])
            await message.reply(f"⚙️<b>{messages.bot_name}</b>\n<i>Attach your Telegram Group Link to make it clickable if you Trend at @BuyBotTrending</i>", reply_markup=keyb)
    elif comps[gid]["status"]=="wait_csupply":
        if not message.text.isnumeric():
            await message.reply(f"❌Circualting supply value not valid ({message.text}). Try again")
        elif message.text == "0":
            comps[gid]['token_group_pref']['circulating_supply']=''
            c,k = get_settings_menuvalue("tokengroup",gid)
            await message.reply(c,reply_markup=k)
        else:
            comps[gid]['token_group_pref']['circulating_supply']=message.text
            c,k = get_settings_menuvalue("tokengroup",gid)
            await message.reply(c,reply_markup=k)
    elif comps[gid]["status"] == "wait_bot_gif":
        pass
    elif comps[gid]["status"] == "wait_bot_minbuy":
        if message.text.isnumeric() and int(message.text)>0:
            comps[gid]["min_buy"] = int(message.text)
            c, k = get_settings_menuvalue("buybot", gid)
            await bot.send_message(gid,c,reply_markup=k)
        else:
            await message.reply("❗️ Min buy amount to show value not valid")
    elif comps[gid]["status"] == "wait_bot_emoji":
        if message.text[0]==":" and message.text[-1]==":":
            comps[gid]["buy_emoji"] = message.text
            c, k = get_settings_menuvalue("buybot", gid)
            await bot.send_message(gid,c,reply_markup=k)
        else:
            await message.reply("❗️ Emoji not valid")
    elif comps[gid]["status"] == "wait_bot_buystep":
        if message.text.isnumeric() and int(message.text)>0:
            comps[gid]["buy_step"] = int(message.text)
            c, k = get_settings_menuvalue("buybot", gid)
            await bot.send_message(gid,c,reply_markup=k)
        else:
            await message.reply("❗️ Buy step value not valid")
    elif comps[gid]['status']=="wait_buycomp_length":
        if message.text.isnumeric() and int(message.text)>0:
            comps[gid]["big_buy_comp"]['length'] = int(message.text)
            c, k = get_settings_menuvalue("buycomp", gid)
            await bot.send_message(gid,c,reply_markup=k)
        else:
            await message.reply("❌Enter valid number (e.g 3, 15)...\n➡️Send me length (minute)")
    elif comps[gid]['status']=="wait_buycomp_minbuy":
        if all(c.isdigit() or c=="." for c in message.text) and float(message.text)>0:
            comps[gid]["big_buy_comp"]['min_buy'] = float(message.text)
            c, k = get_settings_menuvalue("buycomp", gid)
            await bot.send_message(gid,c,reply_markup=k)
        else:
            await message.reply(f"❌Enter valid {comps[gid]['alt_token_name']} (e.g 0.05, 0.2)..\n➡️Minimum Buy?")
    elif comps[gid]['status']=="wait_buycomp_prize1":
        
        if all(c.isdigit() or c=="." for c in message.text) and float(message.text)>0:
            comps[gid]["big_buy_comp"]['prize'][0] = float(message.text)
            c, k = get_settings_menuvalue("buycomp", gid)
            await bot.send_message(gid,c,reply_markup=k)
        else:
            await message.reply(f"❌Enter valid {comps[gid]['alt_token_name']} (e.g 0.05, 0.2)..\n➡️Winning Prize?")
    elif comps[gid]['status']=="wait_buycomp_prize2":
        
        if all(c.isdigit() or c=="." for c in message.text) and float(message.text)>0:
            comps[gid]["big_buy_comp"]['prize'][1] = float(message.text)
            c, k = get_settings_menuvalue("buycomp", gid)
            await bot.send_message(gid,c,reply_markup=k)
        else:
            await message.reply(f"❌Enter valid {comps[gid]['alt_token_name']} (e.g 0.05, 0.2)..\n➡️Second Place Prize?")
    elif comps[gid]['status']=="wait_buycomp_prize3":
        if all(c.isdigit() or c=="." for c in message.text) and float(message.text)>0:
            comps[gid]["big_buy_comp"]['prize'][2] = float(message.text)
            c, k = get_settings_menuvalue("buycomp", gid)
            await bot.send_message(gid,c,reply_markup=k)
        else:
            await message.reply(f"❌Enter valid {comps[gid]['alt_token_name']} (e.g 0.05, 0.2)..\n➡️Third Place Prize?")
    elif comps[gid]['status']=="wait_buycomp_musthold":
        if message.text.isnumeric() and int(message.text)>0:
            comps[gid]["big_buy_comp"]['must_hold'] = int(message.text)
            c, k = get_settings_menuvalue("buycomp", gid)
            await bot.send_message(gid,c,reply_markup=k)
        else:
            await message.reply(f"❌Enter valid time (in hours) (e.g 12, 24)...\n➡️Send me 'must hold' in hours?")



    elif comps[gid]['status']=="wait_lastcomp_length":
        if message.text.isnumeric() and int(message.text)>0:
            comps[gid]["last_buy_comp"]['countdown'] = int(message.text)
            c, k = get_settings_menuvalue("lastcomp", gid)
            await bot.send_message(gid,c,reply_markup=k)
        else:
            await message.reply("❌Enter valid number (e.g 3, 15)...\n➡️Send me countdown (minute) for Last Buy Competition")
    elif comps[gid]['status']=="wait_lastcomp_minbuy":
        if all(c.isdigit() or c=="." for c in message.text) and float(message.text)>0:
            comps[gid]["last_buy_comp"]['min_buy'] = float(message.text)
            c, k = get_settings_menuvalue("lastcomp", gid)
            await bot.send_message(gid,c,reply_markup=k)
        else:
            await message.reply(f"❌Enter valid {comps[gid]['alt_token_name']} amount (e.g 0.05, 0.2)..\n➡️Minimum Buy for Last Competition?")
    elif comps[gid]['status']=="wait_lastcomp_prize1":
        
        if all(c.isdigit() or c=="." for c in message.text) and float(message.text)>0:
            comps[gid]["last_buy_comp"]['prize'] = float(message.text)
            c, k = get_settings_menuvalue("lastcomp", gid)
            await bot.send_message(gid,c,reply_markup=k)
        else:
            await message.reply(f"❌Enter valid {comps[gid]['alt_token_name']} amount (e.g 0.75, 2)..\n➡️Winning Prize for Last Buy Competition?")
    elif comps[gid]['status']=="wait_lastcomp_musthold":
        if message.text.isnumeric() and int(message.text)>0:
            comps[gid]["last_buy_comp"]['must_hold'] = int(message.text)
            c, k = get_settings_menuvalue("lastcomp", gid)
            await bot.send_message(gid,c,reply_markup=k)
        else:
            await message.reply(f"❌Enter valid time (in hours) (e.g 12, 24)...\n➡️Send me 'must hold' in hours for Last Buy Competition?")
    reset_status(gid)
    

        
    
@dp.callback_query_handler(lambda call: call.data == "remove_token")
async def remove_token(call: aiogram.types.CallbackQuery):
    gid = call.message.chat.id
    if_init(gid)
    
    print(gid,call.message.from_user.first_name, call.data)
    if comps[gid]["token_address"] != "":
        await bot.send_message(gid, messages.remove_done_message[0])
    else:
        await bot.send_message(gid, messages.remove_done_message[1])
    comps[gid]["token_address"] = ""
    comps[gid]["token_name"] = ""
    comps[gid]["alt_token_name"] = ""
    comps[gid]["pair_address"] = ""
    comps[gid]["chain"] = ""
    if comps[gid]["ongoing"]=="on":BotAPI(gid,comps[gid]).stop()
    comps[gid]["ongoing"] = "off"
    reset_status(gid)

@dp.callback_query_handler(lambda call: call.data.startswith("pair") and len(call.data.split("_"))==4)
async def select_pair(call: aiogram.types.CallbackQuery):
    gid = call.message.chat.id
    if_init(gid)
    
    print(gid,call.message.from_user.first_name, call.data)
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
        comps[gid]['status'] = "wait_bot_minbuy"
        await bot.send_message(gid,"➡️Send min buy amount to show")
    elif c_data == "emoji":
        comps[gid]['status'] = "wait_bot_emoji"
        await bot.send_message(gid,"➡️Send me new emoji")
    elif c_data == "buystep":
        comps[gid]['status'] = "wait_bot_buystep"
        await bot.send_message(gid,"➡️Send new buy step")
    elif c_data == "gif":
        comps[gid]['status'] = "wait_bot_buystep"
        await bot.send_message(gid,"➡️Send Buy Gif")
    elif c_data == "tokengrouppref":
        comps[gid]['status'] = ""
        c,k = get_settings_menuvalue("tokengroup", gid)
        await bot.edit_message_text(c,gid,call.message.message_id,parse_mode=aiogram.types.ParseMode.HTML, reply_markup=k)

    elif c_data == "bigbuycomp":
        comps[gid]['status'] = ""
        c, k = get_settings_menuvalue('buycomp', gid)
        await bot.edit_message_reply_markup(gid, call.message.message_id,reply_markup=k)
    elif c_data == "lastbuycomp":
        comps[gid]['status'] = ""
        c, k = get_settings_menuvalue('lastcomp', gid)
        await bot.edit_message_reply_markup(gid, call.message.message_id,reply_markup=k)
    update_comps_write()

@dp.callback_query_handler(lambda call: call.data.startswith("settings_tokengroup") and len(call.data.split("_"))==3)
async def settings_tokengroup(call: aiogram.types.CallbackQuery):
    gid = call.message.chat.id
    if_init(gid)

    c_data = call.data.split("_")[2]
    if c_data == "grouplink":
        comps[gid]['status'] = "wait_grouplink"
        await bot.send_message(gid, "➡️Send me group or portal link")
    elif c_data == "notifywhalebuy":
        comps[gid]['status'] = ""
        flag = comps[gid]['token_group_pref']['notify_whale_buy']
        if flag=="on":
            flag = "off"
        else:
            flag = "on"
        comps[gid]['token_group_pref']['notify_whale_buy'] = flag
        keyb = keyboards.Keyboards().settings_tokengroup(comps[gid]['token_group_pref'])
        await call.message.edit_reply_markup(reply_markup=keyb)
    elif c_data == "selectedchart":
        comps[gid]['status'] = ""
        caption = messages.select_chart
        keyb = keyboards.Keyboards().select_chart(comps[gid]['token_group_pref']['selected_chart'])
        await bot.edit_message_text(text=caption,chat_id=gid,message_id=call.message.message_id,reply_markup=keyb)
    elif c_data == "csupply":
        comps[gid]['status'] = "wait_csupply"
        await bot.send_message(gid,"➡️Send me circulating supply. (No dots and commas allowed e.g. 111222333444, to delete existing value if was maually set before, send '0')")
    elif c_data == "back":
        comps[gid]['status'] =""
        c,k = get_settings_menuvalue("buybot", gid)
        await bot.edit_message_text(c,gid,call.message.message_id, reply_markup=k)
    update_comps_write()



@dp.callback_query_handler(lambda call: call.data.startswith("select_chart") and len(call.data.split("_"))==3)
async def select_chart(call: aiogram.types.CallbackQuery):
    gid = call.message.chat.id
    if_init(gid)

    c_data = call.data.split("_")[2]
    if c_data == "back":
        c,k = get_settings_menuvalue("tokengroup", gid)
        await bot.edit_message_text(c,gid,call.message.message_id,reply_markup=k)
    else:
        comps[gid]["token_group_pref"]["selected_chart"] = c_data
        keyb = keyboards.Keyboards().select_chart(c_data)
        await bot.edit_message_reply_markup(gid,call.message.message_id,reply_markup=keyb)
    reset_status(gid)

@dp.callback_query_handler(lambda call: call.data.startswith("settings_buycomp") and len(call.data.split("_"))==3)
async def settings_buybot(call: aiogram.types.CallbackQuery):
    gid = call.message.chat.id
    if_init(gid)

    c_data = call.data.split("_")[2]
    if c_data == "length":
        comps[gid]['status'] = 'wait_buycomp_length'
        await bot.send_message(gid, "➡️Send me competiton length (minute) (e.g 3)")
    if c_data == "minbuy":
        comps[gid]['status'] = 'wait_buycomp_minbuy'
        await bot.send_message(gid, "➡️Send me minimum buy (e.g 0.05)")
    if c_data == "prize1":
        comps[gid]['status'] = 'wait_buycomp_prize1'
        await bot.send_message(gid, "➡️Send me winning prize (e.g 0.05)")
    if c_data == "musthold":
        comps[gid]['status'] = 'wait_buycomp_musthold'
        await bot.send_message(gid, "➡️Send me 'must hold' in hours (e.g 24)")
        
    if c_data == "prize2":
        comps[gid]['status'] = 'wait_buycomp_prize2'
        await bot.send_message(gid, "➡️Send me second place prize (e.g 0.05)")
        
    if c_data == "prize3":
        comps[gid]['status'] = 'wait_buycomp_prize3'
        await bot.send_message(gid, "➡️Send me third place prize (e.g 0.05)")
    if c_data == "back":
        comps[gid]["status"]=""
        c,k = get_settings_menuvalue("buybot", gid)
        await bot.edit_message_text(text=c,chat_id=gid,message_id = call.message.message_id,reply_markup=k)
    
    elif c_data == "start":
        comps[gid]['status']=''
        if not (comps[gid]['pair_address'] and comps[gid]['token_name'] and comps[gid]['token_address']):
            await bot.send_message(gid, "❗️You must add token to chat first. Use /add command")
        elif comps[gid]['ongoing']=='on':
            await bot.send_message(gid, "❌Another buy competition already started")
        else:
            comps[gid]['ongoing'] = 'on'
            comps[gid]['comp_type'] = 'big_buy_comp'
            alt_token_name = comps[gid]['alt_token_name']
            comp_data = comps[gid]['big_buy_comp']
            await bot.send_message(gid, "⏳Biggest buy competition starting...\nℹ️Waiting for the next block to start competiton")
            start_time =  datetime.now().strftime("%H:%M:%S %Z")
            t1 = time.time()
            res = BotAPI(gid, comps[gid]).start()
            elapsed_t = time.time() -t1
            # print(elapsed_t)
            remain_t = comp_data['length']*60-elapsed_t
            endin_time = [int(remain_t/60), int(remain_t) % 60] 
            image_fn = open(f"images/{comps[gid]['gif_image']}",'rb')
            start_m = await bot.send_photo(gid, image_fn,
            f"🎉Biggest Buy Competition Started\n\n🕓 Start at `{start_time} UTC`\n⏳Ends in `{endin_time[0]}`min `{endin_time[1]}`sec\n⏫Minimum Buy `{comp_data['min_buy']}{alt_token_name}`\n\n💰Winning Prize `{comp_data['prize'][0]}`{alt_token_name} *(2nd* `{comp_data['prize'][1]}`*{alt_token_name})*🚀\n💎Winner must hold at least `{comp_data['must_hold']}` hours\n\n📊[Chart](https://{comps[gid]['token_group_pref']['selected_chart']}/token/{comps[gid]['token_address']})",parse_mode=aiogram.types.ParseMode.MARKDOWN)
            await start_m.pin(True)
    update_comps_write()

@dp.callback_query_handler(lambda call: call.data.startswith("settings_lastcomp") and len(call.data.split("_"))==3)
async def settings_buybot(call: aiogram.types.CallbackQuery):
    gid = call.message.chat.id
    if_init(gid)

    c_data = call.data.split("_")[2]
    if c_data == "length":
        comps[gid]['status'] = 'wait_lastcomp_length'
        await bot.send_message(gid, "➡️Send me countdown (minute) (e.g 3) for Last Buy Competition")
    if c_data == "minbuy":
        comps[gid]['status'] = 'wait_lastcomp_minbuy'
        await bot.send_message(gid, "➡️Send me minimum buy (e.g 0.05) for Last Buy Competition")
    if c_data == "prize1":
        comps[gid]['status'] = 'wait_lastcomp_prize1'
        await bot.send_message(gid, "➡️Send me winning prize (e.g 0.05) for Last Buy Competition")
    if c_data == "musthold":
        comps[gid]['status'] = 'wait_lastcomp_musthold'
        await bot.send_message(gid, "➡️Send me 'must hold' in hours (e.g 24) for Last Buy Competition")
    if c_data == "back":
        comps[gid]["status"]=""
        c,k = get_settings_menuvalue("buybot", gid)
        await bot.edit_message_text(text=c,chat_id=gid,message_id = call.message.message_id,reply_markup=k)
    
    elif c_data == "start":
        comps[gid]['status']=''
        if not (comps[gid]['pair_address'] and comps[gid]['token_name'] and comps[gid]['token_address']):
            await bot.send_message(gid, "❗️You must add token to chat first. Use /add command")
        elif comps[gid]['ongoing']=='on':
            await bot.send_message(gid, "❌Another buy competition already started")
        else:
            comps[gid]['ongoing'] = 'on'
            comps[gid]['comp_type'] = 'last_buy_comp'
            alt_token_name = comps[gid]['alt_token_name']
            comp_data = comps[gid]['last_buy_comp']

            await bot.send_message(gid, "⏳Last buy competition starting...\nℹ️Waiting for the next block to start competiton")
            start_time =  datetime.now().strftime("%H:%M:%S %Z")
            t1 = time.time()
            res = BotAPI(gid, comps[gid]).start()
            elapsed_t = time.time() -t1
            # print(elapsed_t)
            remain_t = comp_data['countdown']*60-elapsed_t
            endin_time = [int(remain_t/60), int(remain_t) % 60] 
            # image_fn = open(f"images/{comps[gid]['gif_image']}",'rb')
            start_m = await bot.send_message(gid,
            f"🎉Last Buy Competition (LIVE)\n\n⏳`{endin_time[0]}:{endin_time[1]}`remaining time!\n⏫Minimum Buy `{comp_data['min_buy']}{alt_token_name}`\n💰Winning Prize `{comp_data['prize']}`{alt_token_name} 🚀\n\n📊[Chart](https://{comps[gid]['token_group_pref']['selected_chart']}/token/{comps[gid]['token_address']})",parse_mode=aiogram.types.ParseMode.MARKDOWN)
            await start_m.pin(True)
    update_comps_write()


@dp.callback_query_handler(
    lambda call: call.data.startswith("settings_menu"))
async def select_settings_menu(call: aiogram.types.CallbackQuery):
    gid = call.message.chat.id
    if_init(gid)
    print(gid,call.message.from_user.first_name, call.data)
    c_data = call.data.split('_')[2]
    if c_data == "grouplink":
        comps[gid]['status']="wait_grouplink"
        await bot.send_message(gid,"➡️Send me group or portal link")
    else:
        print(c_data)
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
    