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
import schedule
import threading
import urllib3
from datetime import datetime

bot = aiogram.Bot(token=config.API_TOKEN,
                  parse_mode=aiogram.types.ParseMode.HTML)

loop = asyncio.get_event_loop()
dp = aiogram.Dispatcher(bot, loop=loop)


def format_address(addr):
    return addr[0:6]+"..."+addr[-4:]


def get_winners_message(winners, alt_token_name, chain, prize):
    # winner_address = winners[0]['_id']
    win_message = ""
    win_order_gif = {
        0: "🥇",
        1: "🥈",
        2: "🥉"
    }
    for i, winner in enumerate(winners):
        win_message += f"\n{win_order_gif[i]}<code>{format_address(winner['_id'])}</code> ➖ <code>{winner['amount']}{alt_token_name}</code>"
    winner_list_info = win_message

    for i, winner in enumerate(winners):
        winner_address = winners[i]['_id']
        if 'pay_tx' in winner and winner['pay_tx']:
            pay_info = f"<a href ='{winner['pay_tx']}'>Payment Transaction</a>"
        else:
            pay_info = "All winners info... /winners"

        win_message += f"\n\n🎊Congrats to <code>{winner_address}</code>wins <code>{prize[i]}{alt_token_name}</code>\n🎖Winner address{winner_address}\n#️⃣{pay_info}\n"

    return winner_list_info, win_message


def record_winners(winners, gid):
    prize = comps[gid][comps[gid]['comp_type']]['prize']
    if comps[gid]['comp_type'] == "last_buy_comp":
        prize = [prize]
    for i, winner in enumerate(winners):

        comps[gid]['winners'][winner['hash']] = {
            "address": winner['_id'],
            "amount": winner["amount"],
            "token_name": comps[gid]["token_name"],
            "token_address": comps[gid]["token_address"],
            "prize": prize[i],
            "alt_token_name": comps[gid]["alt_token_name"],
            "chain": comps[gid]["chain"],
            "comp_type": comps[gid]["comp_type"],
            "pay_tx": ""
        }


def record_winners_pay_tx(gid):
    winners = comps[gid]['winners']
    if not bool(winners):
        return ""

    params = {}
    for key in winners.keys():
        winner_hash = key
        if comps[gid]['winners'][key]['pay_tx'] == "":
            params[key] = ""
    if not bool(params):
        return ""
    r = requests.Session()
    url = "https://tetra.tg.api.cryptosnowprince.com/api/getPayInfoByHash"
    res = r.post(url, data=params, verify=False)
    print("getPayInfo_response :", res)
    text = ""
    if res.status_code == 200:
        try:
            res = res.json()
            print("getPayInfo_response :", res)
            res = res['value']

            for key, val in res.items():
                print(key, " -------- ", val)
                if val == "":
                    continue
                comps[gid]['winners'][key]['pay_tx'] = val
                winner_info = comps[gid]['winners'][key]
                comps[gid]['winners'][key]['pay_tx'] = val
                text += f"🎊Congrats to <code>{winner_info['address']}</code>\n You received <code>{winner_info['prize']}{winner_info['alt_token_name']}</code> as prize\n"
        except KeyError:
            print("get winners pay_tx: ", "data error")
    else:
        print("get winners pay_tx: ", "fail")
    return text


def run_continuously(interval=1):
    """Continuously run, while executing pending jobs at each
    elapsed time interval.
    @return cease_continuous_run: threading. Event which can
    be set to cease continuous run. Please note that it is
    *intended behavior that run_continuously() does not run
    missed jobs*. For example, if you've registered a job that
    should run every minute and you set a continuous run
    interval of one hour then your job won't be run 60 times
    at each interval but only once.
    """
    cease_continuous_run = threading.Event()

    class ScheduleThread(threading.Thread):
        @classmethod
        def run(cls):
            while not cease_continuous_run.is_set():
                schedule.run_pending()
                time.sleep(interval)

    continuous_thread = ScheduleThread()
    continuous_thread.start()
    return cease_continuous_run


comps = {}


async def get_latest_buyinfo():  # message: aiogram.types.Message=None):
    while 1:

        await asyncio.sleep(5)
        # await bot.send_message(-1001661521028, "hhhhh")

        start_time = datetime.now().strftime("%H:%M:%S")
        # print(start_time)

        r = requests.Session()
        url = "https://tetra.tg.api.cryptosnowprince.com/api/"
        lengths = {
            "big_buy_comp": "length",
            "last_buy_comp": "countdown"
        }
        buyer_domain = {
            "BSC": "bscscan.com",
            "ETH": "etherscan.io"
        }
        for gid in comps.keys():

            g_data = comps[gid]
            chain = g_data['chain']
            token_address = g_data['token_address']

            if not (token_address and chain and g_data['pair_address']):
                continue

            comp_type = g_data['comp_type']
            comp_info = g_data[comp_type]
            length = comp_info[lengths[comp_type]]
            s_time = comp_info['start_time']
            e_time = s_time + length*60
            r_time = e_time - time.time()

            start_time = datetime.utcfromtimestamp(s_time).strftime("%H:%M:%S")
            end_time = datetime.utcfromtimestamp(e_time).strftime("%H:%M:%S")
            minbuy = comp_info['min_buy']
            alt_token_name = g_data['alt_token_name']
            token_name = g_data['token_name']
            s_chart = g_data['token_group_pref']['selected_chart']
            link_track = 'https://t.me/aiogrambottest2023'
            link_chart = f'https://poocoin.app/tokens/{token_address}'
            link_event = f'https://t.me/BuyBotTracker'

            congrate_m = record_winners_pay_tx(gid)
            if congrate_m:
                await bot.send_message(gid, congrate_m)
            if g_data['show_buys_w/out_comp'] == "on" or g_data['ongoing'] == 'on':
                emoji = g_data['buy_emoji']
                params = {'groupId': gid}
                res = r.post(url+"/getLatestEvent", data=params, verify=False)
                print("get_lastbuy_response:", res)
                if res.status_code == 200:
                    try:
                        res = res.json()
                        buy_info = res["event"]
                        print("get_lastbuy:", res)

                        if bool(buy_info) and float(buy_info['value']) >= g_data['min_buy']:
                            link_buyer = f"https://{buyer_domain[chain]}/address/{buy_info['buyer_address']}"
                            link_txn = f"https://{buyer_domain[chain]}/tx/{buy_info['txn']}"

                            emoji_count = int(
                                float(buy_info['value'])/g_data['buy_step'])
                            if emoji_count > 100:
                                emoji_count = 100
                            buy_message = f"<b>{token_name} ({chain}) </b>Buy!\n{emoji*emoji_count}\n\n💵{buy_info['alt_token_amount']}{alt_token_name} (${buy_info['value']})\n🪙{buy_info['token_amount']} {g_data['token_name']}\n🪪<a href='{link_buyer}'>{buy_info['buyer_address'][0:5]}...{buy_info['buyer_address'][-3:]}</a><code>|</code><a href='{link_txn}'>Txn</a><code>|</code><a href='{link_track}'>Track</a>\n🔘Market Cap ${buy_info['marketcap']}\n\n📊<a href='{link_chart}'>Chart</a>"

                            image_fn = open(
                                f"images/{g_data['gif_image']}", 'rb')
                            # print("buy_message ", buy_message)
                            await bot.send_photo(gid, image_fn, buy_message, aiogram.types.ParseMode.HTML)

                    except KeyError:
                        pass
                        print("get_lastbuy : data error")
                else:
                    pass
                    print("get_lastbuy : fail")

            if g_data['ongoing'] == 'off':
                continue
            if comp_type == "big_buy_comp":
                if r_time < 0:
                    comps[gid]["ongoing"] = "off"
                    prize = comp_info['prize']
                    winners_message = "➡️There was no buyer in competition"
                    params = {"groupId": str(
                        gid), "compType": comp_type, "pay": True}
                    res = r.post(url+"/winners", data=params, verify=False)
                    print("get_winners_response: ", res)
                    if res.status_code == 200:
                        try:
                            res = res.json()
                            print("get_winners", res)
                            winners = res['winners']
                            if len(winners) > 0:
                                _, winners_message = get_winners_message(
                                    winners, alt_token_name, chain, prize)
                                record_winners(winners, gid)

                        except KeyError:
                            print("get_winners : data error")

                    image_fn = open(f"images/{g_data['gif_image']}", 'rb')
                    comp_text = f"🏁Biggest Buy Competition Finished\n\n🕓 Start at <code>{start_time} UTC</code>\n⏳Ends <code>{end_time} UTC</code>\n⏫Minimum Buy <code>{minbuy}</code>{alt_token_name}\n{winners_message}"
                    text = f"{comp_text}\n\n📊<a href='{link_chart}'>Chart</a>"

                    finish_message = await bot.send_photo(gid, image_fn, text, parse_mode=aiogram.types.ParseMode.HTML)
                    # print("finish_message: ", finish_message)
                    await bot.pin_chat_message(gid, finish_message.message_id, False)
                    image_fn.close()
                    comps[gid]['comp_text'] = comp_text
                    update_comps_write()
                    # res = BotAPI(gid, g_data).stop()
                    # print("stop_response :", res)

            elif comp_type == "last_buy_comp":
                r_time = int(r_time)
                if r_time <= 0:
                    r_time = 0
                endin_time = [int(r_time/60), r_time % 60]
                caption = f"🎉Last Buy Competition (LIVE)\n\n⏳<code>{endin_time[0]}:{endin_time[1]}</code>remaining time!\n⏫Minimum Buy <code>{comp_info['min_buy']}{alt_token_name}</code>\n💰Winning Prize <code>{comp_info['prize']}</code>{alt_token_name} 🚀\n\n📊<a href='{link_chart}'>Chart</a>"
                await bot.edit_message_text(caption, gid, comp_info['message_id'])

                if r_time == 0:
                    comps[gid]["ongoing"] = "off"

                    prize = [comp_info['prize']]
                    winners_message = "🙁There is no winner"

                    params = {"groupId": str(
                        gid), "compType": comp_type, "pay": True}
                    res = r.post(url+"/winners", data=params, verify=False)
                    print("get_winners_response: ", res)
                    if res.status_code == 200:
                        try:
                            res = res.json()
                            print("get_winners", res)
                            winners = res['winners']
                            if len(winners) > 0:
                                _, winners_message = get_winners_message(
                                    winners, alt_token_name, chain, prize)
                                record_winners(winners, gid)
                        except KeyError:
                            print("get_winners : data error")

                    comp_text = f"🎉Last Buy Competition Finished\n\n⏫Minimum Buy <code>{comp_info['min_buy']}{alt_token_name}</code>\n💰Winning Prize <code>{comp_info['prize']}</code>{alt_token_name} 🚀\n{winners_message}"
                    caption = f"{comp_text}\n\n📊<a href='{link_chart}'>Chart</a>"
                    comps[gid]['comp_text'] = comp_text
                    update_comps_write()
                    # res = BotAPI(gid, g_data).stop()
                    # print("stop_response :", res)
                    await bot.edit_message_text(caption, gid, comp_info['message_id'])
                    await bot.forward_message(gid, gid, comp_info['message_id'])

            # await bot.send_message(0,"buy fail")


def verify_token_address(addr):
    return addr.startswith("0x") and len(addr[2:]) == 40 and all(c in string.hexdigits for c in addr[2:].lower())


def if_init(gid):
    # print(comps.keys())
    if gid not in comps.keys():
        comps[gid] = messages.initialcompvalue
        update_comps_write()


def reset_status(gid):
    comps[gid]["status"] = ""
    update_comps_write()


def get_settings_menuvalue(setting, gid):
    caption = f"⚙️<b>{messages.bot_name}</b>\n\n<i>Buy Bot and Automatic & Customizable Games. (Bot Tracks Cumulative Buys for Biggest Buy Comp)</i>"
    if setting == "buybot":
        keyb = keyboards.Keyboards().settings_buybot(comps[gid])
    elif setting == "buycomp":
        keyb = keyboards.Keyboards().settings_buycomp(comps[gid])
    elif setting == "lastcomp":
        keyb = keyboards.Keyboards().settings_lastcomp(comps[gid])
    elif setting == "tokengroup":
        caption = f"⚙️<b>{messages.bot_name}</b>\n\n<i>Attach your Telegram Group Link to make it clickable</i>"
        keyb = keyboards.Keyboards().settings_tokengroup(
            comps[gid]["token_group_pref"])
    comps[gid]['status'] = ""
    return caption, keyb


@dp.message_handler(commands=['payment'])
async def payment_message(message: aiogram.types.Message):
    gid = message.chat.id
    gname = message.chat.username
    if_init(gid)
    text = f"<a href='https://tetra.tg.api.cryptosnowprince.com?groupId={gid}&groupName={gname}'>Insert payment wallet infomation</a>"
    c_m = await bot.get_chat_member(gid, message['from']['id'])
    if not c_m.is_chat_admin():
        await message.reply("❌Only admins can remove token from chat")
        return
    await bot.send_message(gid, text)


@dp.message_handler(commands=['remove'])
async def remove_message(message: aiogram.types.Message):
    keyb = keyboards.Keyboards().remove()
    gid = message.chat.id
    if_init(gid)
    c_m = await bot.get_chat_member(gid, message['from']['id'])
    if not c_m.is_chat_admin():
        await message.reply("❌Only admins can remove token from chat")
        return
    reset_status(gid)
    print(gid, message.from_user.first_name, message.text)
    await bot.send_message(gid, messages.remove_confirm_message, reply_to_message_id=message.message_id, reply_markup=keyb)


@dp.message_handler(commands=['help'])
async def help_message(message: aiogram.types.Message):
    gid = message.chat.id
    if_init(gid)
    reset_status(gid)

    print(gid, message.from_user.first_name, message.text)
    await bot.send_message(gid, messages.help_message, reply_to_message_id=message.message_id)


@dp.message_handler(commands=['start'])
async def start_message(message: aiogram.types.Message):
    await help_message(message)


@dp.message_handler(commands=['settings'])
async def change_settings(message: aiogram.types.Message):
    gid = message.chat.id
    if_init(gid)
    # if not c_m.is_chat_admin():
    #     await message.reply("❌Only admins can remove token from chat")
    #     return
    reset_status(gid)
    if comps[gid]['alt_token_name'] == "" or comps[gid]['token_address'] == "":
        await bot.send_message(gid, "Firstly type /add to start tracking your coin", reply_to_message_id=message.message_id)
        return
    c, k = get_settings_menuvalue("buybot", gid)
    await bot.send_message(gid, c, reply_markup=k)


@dp.message_handler(commands=['comp'])
async def show_comp(message: aiogram.types.Message):
    gid = message.chat.id
    if_init(gid)
    reset_status(gid)

    comps[gid]['status'] = ''
    if comps[gid]['ongoing'] == 'off':
        if comps[gid]['comp_text'] == '':
            await message.reply("❗️ There is no competion yet")
        else:
            # +"\n\n🕓Last Buy Competition Finished!")
            await message.reply(comps[gid]['comp_text'])
    else:
        comp_type = comps[gid]['comp_type']
        if comp_type == "big_buy_comp":
            comp_data = comps[gid]['big_buy_comp']
            start_time = datetime.utcfromtimestamp(
                comp_data['start_time']).strftime("%H:%M:%S %Z")
            remain_t = comp_data['start_time'] + \
                comp_data['length']*60-time.time()
            endin_time = [int(remain_t/60), int(remain_t) % 60]

            winners_message = "➡️There was no buyer in competition"
            r = requests.Session()
            url = "https://tetra.tg.api.cryptosnowprince.com/api"
            params = {"groupId": str(gid), "compType": comp_type, "pay": False}
            res = r.post(url+"/winners", data=params, verify=False)
            print("get_winners_response: ", res)
            alt_token_name = comps[gid]['alt_token_name']
            prize = comp_data['prize']
            chain = comps[gid]['chain']
            winner_list_info = ""
            current_winner_address = ""
            if res.status_code == 200:
                try:
                    res = res.json()
                    print("get_winners", res)
                    winners = res['winners']

                    if len(winners) > 0:
                        winner_list_info, _ = get_winners_message(
                            winners, alt_token_name, chain, prize)
                        current_winner_address = winners[0]['_id']
                        # record_winners(winners,gid)
                except KeyError:
                    print("get_winners : data error")
            current_winner_m = ""
            if current_winner_address:
                current_winner_m = f"\n🎖Current Winner <code>{current_winner_address}</code>"
            comp_text = f"🎉Biggest Buy Competition Started\n\n🕓 Start at <code>{start_time} UTC</code>\n⏳Ends in <code>{endin_time[0]}</code>min <code>{endin_time[1]}</code>sec\n⏫Minimum Buy <code>{comp_data['min_buy']}{alt_token_name}</code>\n\n{winner_list_info}\n\n💰Winning Prize <code>{comp_data['prize'][0]}</code>{alt_token_name} <i>(2nd</i> <code>{comp_data['prize'][1]}</code><i>{alt_token_name},3rd</i> <code>{comp_data['prize'][2]}</code><i>{alt_token_name})</i>🚀{current_winner_m}\n💎Winner must hold at least <code>{comp_data['must_hold']}</code> hours\n\n🪄Use /disq to disqualify a wallet from ongoing competition"

            comp_m = await message.reply(comp_text)
        else:
            comp_data = comps[gid]['last_buy_comp']
            start_time = datetime.utcfromtimestamp(
                comp_data['start_time']).strftime("%H:%M:%S %Z")
            remain_t = comp_data['start_time'] + \
                comp_data['countdown']*60-time.time()
            endin_time = [int(remain_t/60), int(remain_t) % 60]

            winners_message = "➡️There was no buyer in competition"
            r = requests.Session()
            url = "https://tetra.tg.api.cryptosnowprince.com/api"
            params = {"groupId": str(gid), "compType": comp_type, "pay": False}
            res = r.post(url+"/winners", data=params, verify=False)
            print("get_winners_response: ", res)
            alt_token_name = comps[gid]['alt_token_name']
            prize = [comp_data['prize']]
            chain = comps[gid]['chain']
            winner_list_info = ""
            current_winner_address = ""
            if res.status_code == 200:
                try:
                    res = res.json()
                    print("get_winners", res)
                    winners = res['winners']

                    if len(winners) > 0:
                        winner_list_info, _ = get_winners_message(
                            winners, alt_token_name, chain, prize)
                        current_winner_address = winners[0]['_id']
                        # record_winners(winners,gid)
                except KeyError:
                    print("get_winners : data error")
            current_winner_m = ""
            if current_winner_address:
                current_winner_m = f"\n🎖Current Winner <code>{current_winner_address}</code>"
            comp_text = f"🎉Last Buy Competition Started\n\n🕓 Start at <code>{start_time} UTC</code>\n⏳Ends in <code>{endin_time[0]}</code>min <code>{endin_time[1]}</code>sec\n⏫Minimum Buy <code>{comp_data['min_buy']}{alt_token_name}</code>\n\n{winner_list_info}\n\n💰Winning Prize <code>{comp_data['prize']}</code>{alt_token_name}🚀{current_winner_m}\n💎Winner must hold at least <code>{comp_data['must_hold']}</code> hours\n\n🪄Use /disq to disqualify a wallet from ongoing competition"

            comp_m = await message.reply(comp_text)
    update_comps_write()


@dp.message_handler(commands=['disq'])
async def show_winners(message: aiogram.types.Message):
    gid = message.chat.id
    if_init(gid)
    c_m = await bot.get_chat_member(gid, message['from']['id'])
    if not c_m.is_chat_admin():
        await message.reply("❌Only admins can set this")
        return
    reset_status(gid)
    keyb = keyboards.Keyboards().disq_keys()
    await message.reply("⬇️Select competition type to disqualify a wallet from ongoing competition", reply_markup=keyb)


@dp.message_handler(commands=['winners'])
async def show_winners(message: aiogram.types.Message):
    gid = message.chat.id
    if_init(gid)
    reset_status(gid)
    winners = comps[gid]['winners']
    token_address = comps[gid]['token_address']
    chain = comps[gid]['chain']
    if not (token_address and chain):
        await bot.send_message(gid, "❗️You must add token to chat first. Use /add command")
        return
    domains = {
        "BSC": "https://bscscan.com",
        "ETH": "https://etherscan.io"
    }
    url = domains[chain]
    token_address = comps[gid]['token_address']
    winners_count = len(winners.keys())
    if winners_count == 0:
        await bot.send_message(gid, "❕There is no completed competition yet!")
    else:
        caption = f"🏁{winners_count}competitions have been completed so far"
        for key, winner in winners.items():
            link_wallet = f"{url}/address/{winner['address']}"
            link_buytxs = f"{url}/token/{token_address}?a={winner['address']}"
            pay_tx_message = "  Waiting payment..."
            if winner['pay_tx']:
                pay_tx_message = f"<a href='{winner['pay_tx']}'>Pay Txs</a>"
            caption += f"\n\n⏳<code>{winner['address']}</code> wins <code>{winner['prize']}</code>{winner['alt_token_name']}\n<a href='{link_wallet}'>➡️Wallet </a><code>|</code><a href='{link_buytxs}'> Buy Txs </a><code>|</code>{pay_tx_message}"
        keyb = keyboards.Keyboards().show_winners()
        await bot.send_message(gid, caption, reply_markup=keyb)


@dp.message_handler(commands=['add'])
async def add_message(message: aiogram.types.Message):
    gid = message.chat.id
    if_init(gid)
    c_m = await bot.get_chat_member(gid, message['from']['id'])
    if not c_m.is_chat_admin():
        await message.reply("❌Only admins can add token from chat")
        return
    reset_status(gid)
    print(gid, message.from_user.first_name, message.text)
    if comps[gid]['token_address'] and comps[gid]['token_name']:
        await bot.send_message(gid, f"❗️ Bot already in use in this group for token\n{comps[gid]['token_address']}")
        return

    keyb = keyboards.Keyboards().select_chain()
    await bot.send_message(message.chat.id,
                           messages.select_chain_menu,
                           reply_markup=keyb,
                           reply_to_message_id=message.message_id)


@dp.message_handler(content_types=aiogram.types.ContentType.PHOTO)
async def scan_message(message: aiogram.types.Message):
    print("message ", message)
    gid = message.chat.id
    if_init(gid)
    c_m = await bot.get_chat_member(gid, message['from']['id'])
    if not c_m.is_chat_admin():
        return
    # print("status", comps[gid]["status"])
    if comps[gid]["status"] == "wait_bot_gif":
        # if comps[gid]["status"] == "":
        if message.photo:
            # print("message: ", message)
            # await bot.download_file(message.photo.file_id,f'{gid}.png')
            await bot.download_file_by_id(message.photo[-1]['file_id'], f'images/{gid}.png')
            print("photo downloaded")
            comps[gid]['gif_image'] = f"{gid}.png"
            c, k = get_settings_menuvalue("buybot", gid)
            await bot.send_message(gid, c, reply_markup=k)
        else:
            await message.reply("❌Input file not valid. Try again")
        reset_status(gid)


@dp.message_handler(
    lambda message: (message.text not in config.commands and not message.text.startswith("/")))
async def handle_input(message: aiogram.types.Message):
    print(message)

    gid = message.chat.id
    if_init(gid)
    c_m = await bot.get_chat_member(gid, message['from']['id'])
    # print(c_m.is_chat_admin())
    if not c_m.is_chat_admin():
        # await message.reply("❌Only admins can add token from chat")
        return
    print(gid, message.from_user.first_name, message.text)
    if comps[gid]["status"] == "wait_token_address":
        if verify_token_address(message.text):
            comps[gid]["token_address"] = message.text.strip()
            pairs = BotAPI(gid, comps[gid]).get_tokeninfo()
            num_pairs = len(pairs)

            if num_pairs > 0:
                token_name = pairs[0]["name"].split("/")[0]
                comps[gid]["token_name"] = token_name
            keyb = keyboards.Keyboards().select_pair(pairs)
            await message.reply("ℹ️Select Pair Listed Below", reply_markup=keyb)
        else:
            comps[gid]["token_address"] = ""
            await message.reply(f"❌Token address not valid({message.text}). Try again")
    elif comps[gid]["status"] == "wait_grouplink":
        if not message.text.startswith("https://"):
            await message.reply(f"❌Link not valid ({message.text}). Try again\nFormat: <code>https://t.me/mygroup</code>", parse_mode=aiogram.types.ParseMode().HTML)
        else:
            comps[gid]['token_group_pref']['group_link'] = message.text
            keyb = keyboards.Keyboards().settings_tokengroup(
                comps[gid]['token_group_pref'])
            await message.reply(f"⚙️<b>{messages.bot_name}</b>\n<i>Attach your Telegram Group Link to make it clickable</i>", reply_markup=keyb)
    elif comps[gid]["status"] == "wait_csupply":
        if not message.text.isnumeric():
            await message.reply(f"❌Circualting supply value not valid ({message.text}). Try again")
        elif message.text == "0":
            comps[gid]['token_group_pref']['circulating_supply'] = ''
            c, k = get_settings_menuvalue("tokengroup", gid)
            await message.reply(c, reply_markup=k)
        else:
            comps[gid]['token_group_pref']['circulating_supply'] = message.text
            c, k = get_settings_menuvalue("tokengroup", gid)
            await message.reply(c, reply_markup=k)
    elif comps[gid]["status"] == "wait_bot_gif":
        print("wait_gif")
        if message.photo:
            # print("message: ", message)
            # await bot.download_file(message.photo.file_id,f'{gid}.png')
            await bot.download_file_by_id(message.photo[0]['file_id'], f'images/{gid}.png')
            print("photo downloaded")
            comps[gid]['gif_image'] = f"{gid}.png"
            c, k = get_settings_menuvalue("buybot", gid)
            await bot.send_message(gid, c, reply_markup=k)
        else:
            await message.reply("❌Input file not valid. Try again")
    elif comps[gid]["status"] == "wait_bot_minbuy":
        if message.text.isnumeric() and int(message.text) > 0:
            comps[gid]["min_buy"] = int(message.text)
            c, k = get_settings_menuvalue("buybot", gid)
            await bot.send_message(gid, c, reply_markup=k)
        else:
            await message.reply("❗️ Min buy amount to show value not valid")
    elif comps[gid]["status"] == "wait_bot_emoji":
        if not message.text.isalnum():
            comps[gid]["buy_emoji"] = message.text
            c, k = get_settings_menuvalue("buybot", gid)
            await bot.send_message(gid, c, reply_markup=k)
        else:
            await message.reply("❗️ Emoji not valid")
    elif comps[gid]["status"] == "wait_bot_buystep":
        if message.text.isnumeric() and int(message.text) > 0:
            comps[gid]["buy_step"] = int(message.text)
            c, k = get_settings_menuvalue("buybot", gid)
            await bot.send_message(gid, c, reply_markup=k)
        else:
            await message.reply("❗️ Buy step value not valid")
    elif comps[gid]['status'] == "wait_buycomp_length":
        if message.text.isnumeric() and int(message.text) > 0:
            comps[gid]["big_buy_comp"]['length'] = int(message.text)
            c, k = get_settings_menuvalue("buycomp", gid)
            await bot.send_message(gid, c, reply_markup=k)
        else:
            await message.reply("❌Enter valid number (e.g 3, 15)...\n➡️Send me length (minute)")
    elif comps[gid]['status'] == "wait_buycomp_minbuy":
        if all(c.isdigit() or c == "." for c in message.text) and float(message.text) > 0:
            comps[gid]["big_buy_comp"]['min_buy'] = float(message.text)
            c, k = get_settings_menuvalue("buycomp", gid)
            await bot.send_message(gid, c, reply_markup=k)
        else:
            await message.reply(f"❌Enter valid {comps[gid]['alt_token_name']} (e.g 0.05, 0.2)..\n➡️Minimum Buy?")
    elif comps[gid]['status'] == "wait_buycomp_prize1":

        if all(c.isdigit() or c == "." for c in message.text) and float(message.text) > 0:
            comps[gid]["big_buy_comp"]['prize'][0] = float(message.text)
            c, k = get_settings_menuvalue("buycomp", gid)
            await bot.send_message(gid, c, reply_markup=k)
        else:
            await message.reply(f"❌Enter valid {comps[gid]['alt_token_name']} (e.g 0.05, 0.2)..\n➡️Winning Prize?")
    elif comps[gid]['status'] == "wait_buycomp_prize2":

        if all(c.isdigit() or c == "." for c in message.text) and float(message.text) > 0:
            comps[gid]["big_buy_comp"]['prize'][1] = float(message.text)
            c, k = get_settings_menuvalue("buycomp", gid)
            await bot.send_message(gid, c, reply_markup=k)
        else:
            await message.reply(f"❌Enter valid {comps[gid]['alt_token_name']} (e.g 0.05, 0.2)..\n➡️Second Place Prize?")
    elif comps[gid]['status'] == "wait_buycomp_prize3":
        if all(c.isdigit() or c == "." for c in message.text) and float(message.text) > 0:
            comps[gid]["big_buy_comp"]['prize'][2] = float(message.text)
            c, k = get_settings_menuvalue("buycomp", gid)
            await bot.send_message(gid, c, reply_markup=k)
        else:
            await message.reply(f"❌Enter valid {comps[gid]['alt_token_name']} (e.g 0.05, 0.2)..\n➡️Third Place Prize?")
    elif comps[gid]['status'] == "wait_buycomp_musthold":
        if message.text.isnumeric() and int(message.text) > 0:
            comps[gid]["big_buy_comp"]['must_hold'] = int(message.text)
            c, k = get_settings_menuvalue("buycomp", gid)
            await bot.send_message(gid, c, reply_markup=k)
        else:
            await message.reply(f"❌Enter valid time (in hours) (e.g 12, 24)...\n➡️Send me 'must hold' in hours?")

    elif comps[gid]['status'] == "wait_lastcomp_length":
        if message.text.isnumeric() and int(message.text) > 0:
            comps[gid]["last_buy_comp"]['countdown'] = int(message.text)
            c, k = get_settings_menuvalue("lastcomp", gid)
            await bot.send_message(gid, c, reply_markup=k)
        else:
            await message.reply("❌Enter valid number (e.g 3, 15)...\n➡️Send me countdown (minute) for Last Buy Competition")
    elif comps[gid]['status'] == "wait_lastcomp_minbuy":
        if all(c.isdigit() or c == "." for c in message.text) and float(message.text) > 0:
            comps[gid]["last_buy_comp"]['min_buy'] = float(message.text)
            c, k = get_settings_menuvalue("lastcomp", gid)
            await bot.send_message(gid, c, reply_markup=k)
        else:
            await message.reply(f"❌Enter valid {comps[gid]['alt_token_name']} amount (e.g 0.05, 0.2)..\n➡️Minimum Buy for Last Competition?")
    elif comps[gid]['status'] == "wait_lastcomp_prize1":

        if all(c.isdigit() or c == "." for c in message.text) and float(message.text) > 0:
            comps[gid]["last_buy_comp"]['prize'] = float(message.text)
            c, k = get_settings_menuvalue("lastcomp", gid)
            await bot.send_message(gid, c, reply_markup=k)
        else:
            await message.reply(f"❌Enter valid {comps[gid]['alt_token_name']} amount (e.g 0.75, 2)..\n➡️Winning Prize for Last Buy Competition?")
    elif comps[gid]['status'] == "wait_lastcomp_musthold":
        if message.text.isnumeric() and int(message.text) > 0:
            comps[gid]["last_buy_comp"]['must_hold'] = int(message.text)
            c, k = get_settings_menuvalue("lastcomp", gid)
            await bot.send_message(gid, c, reply_markup=k)
        else:
            await message.reply(f"❌Enter valid time (in hours) (e.g 12, 24)...\n➡️Send me 'must hold' in hours for Last Buy Competition?")
    elif comps[gid]['status'] == "wait_disq_wallet":
        if not verify_token_address(message.text):
            text = "❗️ Wallet address not valid"
        else:
            blacklist = comps[gid]['blacklist']
            if message.text in blacklist.keys() and blacklist[message.text]:
                comps[gid]['blacklist'][message.text] = False
                text = f"✅Wallet re-qualified for ongoing biggest buy competition.\n\nWallet:<code>{message.text}</code>"
            else:
                comps[gid]['blacklist'][message.text] = True
                text = f"✅Wallet disqualified for ongoing biggest buy competition.\n\nWallet:<code>{message.text}</code>"
        await message.reply(text)
    elif comps[gid]['status'] == "wait_paytxn":
        if message.text.startswith("https://etherscan.io/tx/0x") or message.text.startswith("https://bscscan.com/tx/0x"):
            chainIds = {
                "eth": "1",
                "bsc": "56"
            }
            chainId = chainIds[message.text[8:11]]
            r = requests.Session()
            url = "https://tetra.tg.api.cryptosnowprince.com/api/verify"
            params = {"tx": message.text.split("tx/")[1], "chainId": chainId}
            # print("verify_params: ", params)

            res = r.post(url, data=params, verify=False)
            print("verify_response :", res)
            if res.status_code == 200:
                try:
                    res = res.json()
                    print("verify_response :", res)
                    if res['receipent'] == '':
                        await message.reply("❗️ Not found any payment info")
                    else:
                        winner_hash = ""

                        for key in comps[gid]['winners'].keys():
                            winners_info = comps[gid]['winners'][key]
                            if winners_info['address'] == res['receipent'] and winners_info['prize'] == res['amount'] and winners_info['alt_token_name'] == res['symbol']:
                                winner_hash = key
                                comps[gid]['winners'][winner_hash]['pay_tx'] = message.text
                                await bot.send_message(gid, f"🎊Congrats to <code>{winners_info['address']}</code>\n You received <code>{winners_info['prize']}{winners_info['alt_token_name']}</code> as prize")
                                await show_winners(message)
                        if winner_hash == "":
                            await message.reply("❗️ Not found any payment info")
                except KeyError:
                    await message.reply("❗️ Not found any payment info")
            else:
                await message.reply("❗️ Not found any payment info")
        else:
            await message.reply("❗️ No tx hash found. Try again")
    reset_status(gid)


@dp.callback_query_handler(lambda call: call.data == "remove_token")
async def remove_token(call: aiogram.types.CallbackQuery):

    gid = call.message.chat.id
    if_init(gid)
    c_m = await bot.get_chat_member(gid, call['from']['id'])
    if not c_m.is_chat_admin():
        await bot.answer_callback_query(call.id, "This command only available for administrators", True)
        return
    print(gid, call.message.from_user.first_name, call.data)
    if comps[gid]["token_address"] != "":
        await bot.send_message(gid, messages.remove_done_message[0])
    else:
        await bot.send_message(gid, messages.remove_done_message[1])
    comps[gid]["token_address"] = ""
    comps[gid]["token_name"] = ""
    comps[gid]["alt_token_name"] = ""
    comps[gid]["pair_address"] = ""
    comps[gid]["chain"] = ""
    BotAPI(gid, comps[gid]).stop()
    comps[gid]["ongoing"] = "off"
    comps[gid]["winners"] = {}
    comps[gid]['comp_text'] = ""
    comps[gid]['blacklist'] = {}
    reset_status(gid)


@dp.callback_query_handler(lambda call: call.data == "show_winners_sendtxn")
async def ask_for_tx(call: aiogram.types.CallbackQuery):
    gid = call.message.chat.id
    if_init(gid)
    c_m = await bot.get_chat_member(gid, call['from']['id'])
    if not c_m.is_chat_admin():
        await bot.answer_callback_query(call.id, "This command only available for administrators", True)
        return
    print(gid, call.message.from_user.first_name, call.data)
    comps[gid]["status"] = "wait_paytxn"
    await bot.send_message(gid, "➡️Send tx link to proof any payment to winner")
    update_comps_write()


@dp.callback_query_handler(lambda call: call.data.startswith("pair") and len(call.data.split("_")) == 4)
async def select_pair(call: aiogram.types.CallbackQuery):
    gid = call.message.chat.id
    if_init(gid)
    c_m = await bot.get_chat_member(gid, call['from']['id'])
    if not c_m.is_chat_admin():
        await bot.answer_callback_query(call.id, "This command only available for administrators", True)
        return
    print(gid, call.message.from_user.first_name, call.data)
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
        res = BotAPI(gid, comps[gid]).setSelectedPair()
        print("setSelectedPair_response ", res)
        keyb = keyboards.Keyboards().select_settings_menu()
        await bot.send_message(gid, f"✅{token_name}({comps[gid]['chain']}) added to <b>{messages.bot_name}!</b>\n\n<i>Attach Your Telegram by selecting “Portal or Group Link” to make it clickable!</i>", reply_markup=keyb, reply_to_message_id=call.message.message_id)
    reset_status(gid)


@dp.callback_query_handler(lambda call: call.data.startswith("disq_keys"))
async def disq_wallet_input(call: aiogram.types.CallbackQuery):
    gid = call.message.chat.id
    if_init(gid)
    c_m = await bot.get_chat_member(gid, call['from']['id'])
    if not c_m.is_chat_admin():
        await bot.answer_callback_query(call.id, "This command only available for administrators", True)
        return
    token_address = comps[gid]['token_address']
    chain = comps[gid]['chain']
    if not (token_address and chain):
        await bot.send_message(gid, "❗️You must add token to chat first. Use /add command")
        return
    if comps[gid]['ongoing'] == 'off':
        comps[gid]['status'] = ""
        await bot.send_message(gid, "❗️A wallet can only be disqualified during the ongoing competition")
    else:
        comps[gid]['status'] = "wait_disq_wallet"
        await bot.send_message(gid, "➡️Send wallet address to disqualify (or re-qualify a disqualified wallet before) from ongoing biggest buy competition")


@dp.callback_query_handler(lambda call: call.data.startswith("settings_buybot") and len(call.data.split("_")) == 3)
async def settings_buybot(call: aiogram.types.CallbackQuery):
    gid = call.message.chat.id
    if_init(gid)
    c_m = await bot.get_chat_member(gid, call['from']['id'])
    if not c_m.is_chat_admin():
        await bot.answer_callback_query(call.id, "This command only available for administrators", True)
        return
    token_address = comps[gid]['token_address']
    chain = comps[gid]['chain']
    if not (token_address and chain):
        await bot.send_message(gid, "❗️You must add token to chat first. Use /add command")
        return

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
        await bot.edit_message_reply_markup(gid, call.message.message_id, reply_markup=k)
    elif c_data == "minbuy":
        comps[gid]['status'] = "wait_bot_minbuy"
        await bot.send_message(gid, "➡️Send min buy amount to show")
    elif c_data == "emoji":
        comps[gid]['status'] = "wait_bot_emoji"
        await bot.send_message(gid, "➡️Send me new emoji")
    elif c_data == "buystep":
        comps[gid]['status'] = "wait_bot_buystep"
        await bot.send_message(gid, "➡️Send new buy step")
    elif c_data == "gif":
        comps[gid]['status'] = "wait_bot_gif"
        await bot.send_message(gid, "➡️Send Buy Gif")
    elif c_data == "tokengrouppref":
        comps[gid]['status'] = ""
        c, k = get_settings_menuvalue("tokengroup", gid)
        await bot.edit_message_text(c, gid, call.message.message_id, parse_mode=aiogram.types.ParseMode.HTML, reply_markup=k)

    elif c_data == "bigbuycomp":
        comps[gid]['status'] = ""
        c, k = get_settings_menuvalue('buycomp', gid)
        await bot.edit_message_reply_markup(gid, call.message.message_id, reply_markup=k)
    elif c_data == "lastbuycomp":
        comps[gid]['status'] = ""
        c, k = get_settings_menuvalue('lastcomp', gid)
        await bot.edit_message_reply_markup(gid, call.message.message_id, reply_markup=k)
    update_comps_write()


@dp.callback_query_handler(lambda call: call.data.startswith("settings_tokengroup") and len(call.data.split("_")) == 3)
async def settings_tokengroup(call: aiogram.types.CallbackQuery):
    gid = call.message.chat.id
    if_init(gid)
    c_m = await bot.get_chat_member(gid, call['from']['id'])
    if not c_m.is_chat_admin():
        await bot.answer_callback_query(call.id, "This command only available for administrators", True)
        return
    token_address = comps[gid]['token_address']
    chain = comps[gid]['chain']
    c_data = call.data.split("_")[2]
    if not (token_address and chain):
        await bot.send_message(gid, "❗️You must add token to chat first. Use /add command")
        return
    if c_data == "grouplink":
        comps[gid]['status'] = "wait_grouplink"
        await bot.send_message(gid, "➡️Send me group or portal link")
    elif c_data == "notifywhalebuy":
        comps[gid]['status'] = ""
        flag = comps[gid]['token_group_pref']['notify_whale_buy']
        if flag == "on":
            flag = "off"
        else:
            flag = "on"
        comps[gid]['token_group_pref']['notify_whale_buy'] = flag
        keyb = keyboards.Keyboards().settings_tokengroup(
            comps[gid]['token_group_pref'])
        await call.message.edit_reply_markup(reply_markup=keyb)
    elif c_data == "selectedchart":
        comps[gid]['status'] = ""
        caption = messages.select_chart
        keyb = keyboards.Keyboards().select_chart(
            comps[gid]['token_group_pref']['selected_chart'])
        await bot.edit_message_text(text=caption, chat_id=gid, message_id=call.message.message_id, reply_markup=keyb)
    elif c_data == "csupply":
        comps[gid]['status'] = "wait_csupply"
        await bot.send_message(gid, "➡️Send me circulating supply. (No dots and commas allowed e.g. 111222333444, to delete existing value if was maually set before, send '0')")
    elif c_data == "back":
        comps[gid]['status'] = ""
        c, k = get_settings_menuvalue("buybot", gid)
        await bot.edit_message_text(c, gid, call.message.message_id, reply_markup=k)
    update_comps_write()


@dp.callback_query_handler(lambda call: call.data.startswith("select_chart") and len(call.data.split("_")) == 3)
async def select_chart(call: aiogram.types.CallbackQuery):
    gid = call.message.chat.id
    if_init(gid)
    c_m = await bot.get_chat_member(gid, call['from']['id'])
    if not c_m.is_chat_admin():
        await bot.answer_callback_query(call.id, "This command only available for administrators", True)
        return
    token_address = comps[gid]['token_address']
    chain = comps[gid]['chain']
    c_data = call.data.split("_")[2]
    if not (token_address and chain):
        await bot.send_message(gid, "❗️You must add token to chat first. Use /add command")
        return
    if c_data == "back":
        c, k = get_settings_menuvalue("tokengroup", gid)
        await bot.edit_message_text(c, gid, call.message.message_id, reply_markup=k)
    else:
        comps[gid]["token_group_pref"]["selected_chart"] = c_data
        keyb = keyboards.Keyboards().select_chart(c_data)
        await bot.edit_message_reply_markup(gid, call.message.message_id, reply_markup=keyb)
    reset_status(gid)


@dp.callback_query_handler(lambda call: call.data.startswith("settings_buycomp") and len(call.data.split("_")) == 3)
async def settings_buybot(call: aiogram.types.CallbackQuery):
    gid = call.message.chat.id
    if_init(gid)
    c_m = await bot.get_chat_member(gid, call['from']['id'])
    if not c_m.is_chat_admin():
        await bot.answer_callback_query(call.id, "This command only available for administrators", True)
        return
    token_address = comps[gid]['token_address']
    chain = comps[gid]['chain']
    c_data = call.data.split("_")[2]
    if not (token_address and chain):
        await bot.send_message(gid, "❗️You must add token to chat first. Use /add command")
        return
    onComp = comps[gid]['ongoing'] == 'on'
    if c_data != "back" and c_data != "start":
        if onComp and comps[gid]['comp_type'] == "big_buy_comp":
            await bot.send_message(gid, "Biggest buy competition ongoing. No changes allowed")
            comps[gid]['status'] = ''
        else:
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
    elif c_data == "back":
        comps[gid]["status"] = ""
        c, k = get_settings_menuvalue("buybot", gid)
        await bot.edit_message_text(text=c, chat_id=gid, message_id=call.message.message_id, reply_markup=k)

    elif c_data == "start":
        comps[gid]['status'] = ''
        if not (comps[gid]['pair_address'] and comps[gid]['token_name'] and comps[gid]['token_address']):
            await bot.send_message(gid, "❗️You must add token to chat first. Use /add command")
        elif comps[gid]['ongoing'] == 'on':
            await bot.send_message(gid, "❌Another buy competition already started")
        else:
            comps[gid]['ongoing'] = 'on'
            comps[gid]['big_buy_comp']['start_time'] = time.time()
            comps[gid]['status'] = ''
            comps[gid]['comp_type'] = 'big_buy_comp'
            alt_token_name = comps[gid]['alt_token_name']
            comp_data = comps[gid]['big_buy_comp']
            await bot.send_message(gid, "⏳Biggest buy competition starting...\n\n<i>ℹ️Waiting for the next block to start competiton</i>")
            start_time = datetime.now().strftime("%H:%M:%S %Z")
            t1 = time.time()
            res = BotAPI(gid, comps[gid]).start()
            elapsed_t = time.time() - t1
            # print(elapsed_t)
            remain_t = comp_data['length']*60-elapsed_t
            endin_time = [int(remain_t/60), int(remain_t) % 60]
            link_chart = f"https://poocoin.app/token/{comps[gid]['token_address']}"
            link_event = f"https://t.me/BuyBotTracker"

            image_fn = open(f"images/{comps[gid]['gif_image']}", 'rb')
            comp_text = f"🕓 Start at <code>{start_time} UTC</code>\n⏳Ends in <code>{endin_time[0]}</code>min <code>{endin_time[1]}</code>sec\n⏫Minimum Buy <code>{comp_data['min_buy']}{alt_token_name}</code>\n\n💰Winning Prize <code>{comp_data['prize'][0]}</code>{alt_token_name} <i>(2nd</i> <code>{comp_data['prize'][1]}</code><i>{alt_token_name})</i>🚀\n💎Winner must hold at least <code>{comp_data['must_hold']}</code> hours"
            start_m = await bot.send_photo(gid, image_fn,
                                           f"🎉Biggest Buy Competition Started\n\n{comp_text}\n\n📊<a href='{link_chart}'>Chart</a>", parse_mode=aiogram.types.ParseMode.HTML)
            image_fn.close()
            await start_m.pin()
            # print("start_message: ", start_m)
            # stop_run_continuously = run_continuously()
    update_comps_write()


@dp.callback_query_handler(lambda call: call.data.startswith("settings_lastcomp") and len(call.data.split("_")) == 3)
async def settings_buybot(call: aiogram.types.CallbackQuery):
    gid = call.message.chat.id
    if_init(gid)
    c_m = await bot.get_chat_member(gid, call['from']['id'])
    if not c_m.is_chat_admin():
        await bot.answer_callback_query(call.id, "This command only available for administrators", True)
        return
    token_address = comps[gid]['token_address']
    chain = comps[gid]['chain']
    c_data = call.data.split("_")[2]
    if not (token_address and chain):
        await bot.send_message(gid, "❗️You must add token to chat first. Use /add command")
        return
    onComp = comps[gid]['ongoing'] == 'on'
    if c_data != "back" and c_data != "start":
        if onComp and comps[gid]['comp_type'] == "last_buy_comp":
            await bot.send_message(gid, "Last buy competition ongoing. No changes allowed")
            comps[gid]['status'] = ''
        else:
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
    elif c_data == "back":
        comps[gid]["status"] = ""
        c, k = get_settings_menuvalue("buybot", gid)
        await bot.edit_message_text(text=c, chat_id=gid, message_id=call.message.message_id, reply_markup=k)

    elif c_data == "start":
        comps[gid]['status'] = ''
        if not (comps[gid]['pair_address'] and comps[gid]['token_name'] and comps[gid]['token_address']):
            await bot.send_message(gid, "❗️You must add token to chat first. Use /add command")
        elif comps[gid]['ongoing'] == 'on':
            await bot.send_message(gid, "❌Another buy competition already started")

        else:
            comps[gid]['ongoing'] = 'on'
            comps[gid]['last_buy_comp']['start_time'] = time.time()
            comps[gid]['comp_type'] = 'last_buy_comp'
            alt_token_name = comps[gid]['alt_token_name']
            comp_data = comps[gid]['last_buy_comp']

            await bot.send_message(gid, "⏳Last buy competition starting...\n\n<i>ℹ️Waiting for the next block to start competiton</i>")
            start_time = datetime.now().strftime("%H:%M:%S %Z")
            t1 = time.time()
            res = BotAPI(gid, comps[gid]).start()
            elapsed_t = time.time() - t1
            # print(elapsed_t)
            remain_t = comp_data['countdown']*60-elapsed_t
            endin_time = [int(remain_t/60), int(remain_t) % 60]

            link_chart = f"https://poocoin.app/token/{comps[gid]['token_address']}"
            link_event = f"https://t.me/BuyBotTracker"

            # image_fn = open(f"images/{comps[gid]['gif_image']}",'rb')
            comp_text = f"⏫Minimum Buy <code>{comp_data['min_buy']}{alt_token_name}</code>\n💰Winning Prize <code>{comp_data['prize']}</code>{alt_token_name} 🚀"
            start_m = await bot.send_message(gid,
                                             f"🎉Last Buy Competition (LIVE)\n\n⏳<code>{endin_time[0]}:{endin_time[1]}</code>remaining time!\n{comp_text}\n\n📊<a href='{link_chart}'>Chart</a>", parse_mode=aiogram.types.ParseMode.HTML)
            await start_m.pin()
            comps[gid]['last_buy_comp']['message_id'] = start_m.message_id
    update_comps_write()


@dp.callback_query_handler(
    lambda call: call.data.startswith("settings_menu"))
async def select_settings_menu(call: aiogram.types.CallbackQuery):
    gid = call.message.chat.id
    if_init(gid)
    c_m = await bot.get_chat_member(gid, call['from']['id'])
    if not c_m.is_chat_admin():
        await bot.answer_callback_query(call.id, "This command only available for administrators", True)
        return
    token_address = comps[gid]['token_address']
    chain = comps[gid]['chain']
    print(gid, call.message.from_user.first_name, call.data)
    c_data = call.data.split('_')[2]
    if not (token_address and chain):
        await bot.send_message(gid, "❗️You must add token to chat first. Use /add command")
        return
    if c_data == "grouplink":
        comps[gid]['status'] = "wait_grouplink"
        await bot.send_message(gid, "➡️Send me group or portal link")
    else:
        print(c_data)
        c, k = get_settings_menuvalue(c_data, gid)
        await bot.edit_message_reply_markup(gid, call.message.message_id, reply_markup=k)

    update_comps_write()


@dp.callback_query_handler(
    lambda call: call.data.startswith("select_chain"))
async def select_chain(call: aiogram.types.CallbackQuery):
    gid = call.message.chat.id
    if_init(gid)
    c_m = await bot.get_chat_member(gid, call['from']['id'])
    if not c_m.is_chat_admin():
        await bot.answer_callback_query(call.id, "This command only available for administrators", True)
        return
    chain = call.data.split('_')[2].upper()
    await bot.send_message(gid, "➡️["+chain+"]"+messages.token_address_question)
    comps[gid]["status"] = "wait_token_address"
    comps[gid]["chain"] = chain
    print(gid, call["from"]["first_name"], chain + " selected")
    update_comps_write()


def update_comps_write():
    with open('./data/comps.json', 'w') as write_comps:
        json.dump(comps, write_comps, ensure_ascii=False, indent=4)


def update_comps_read():
    global comps
    with open("./data/comps.json", 'r') as read_comps:
        comps = json.load(read_comps)
        temp_dict = {}
        for key, val in comps.items():
            temp_dict[int(key)] = comps[key]
            temp_dict[int(key)]["ongoing"] = "off"
            temp_dict[int(key)]["status"] = ""
            temp_dict[int(key)]["blacklist"] = {}

        comps = temp_dict
        temp_dict = {}


if __name__ == "__main__":
    print("Tetra Trending Bot Started...")
    update_comps_read()
    # schedule.every(5).seconds.do(get_latest_buyinfo)
    # # ss = run_continuously(1)
    # # aiogram.executor.start(dp, job(),)
    # # asyncio.run(job())
    loop.create_task(get_latest_buyinfo())
    aiogram.executor.start_polling(dp, skip_updates=True)
    # loop.run_until_complete(coroutine)
