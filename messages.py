# START MESSAGES-------------------------------------------------------------------------

help_message="""
Welcome to Tetra Trending Bot 

- To begin, make me an Admin @tetratrending_bot in your Group

- Type /add to start tracking your coin

- Type /settings to show all available easy to use settings

- Attach your telegram link by going to group settings

- Type /comp to view the current buy contest leaderboard

- Type /winners to view all previous buy contests winners and add TXN as proof of payment

- Type /remove to clear settings and competitions and remove the token from chat

- To make the auto payment to winners function enable use /payment command and set wallet info

- Only group admins can operate almost all commands

"""

remove_confirm_message = """
❔Are you sure remove all settings, competitions and token from chat?
"""


remove_done_message=["✅Token and competition settings removed from chat. You can use /add command to add token to chat. To get help use /help","❌ No token added to chat yet"]

start_messages = {
    "RU": """
Просто отправьте мне имя артиста или название композиции, и я найду эту композицию!
/song — поиск по композициям
/artist — поиск по исполнителям
/category — поиск категории
/setlang — изменить язык
/settings — изменить настройки
/my — Ваш плейлист
                """,

    "EN": """
Welcome to Tetra Trending Bot

- I am a Buy-Bot that features Trending(@TetraTrendingBot) and customizable games

- To begin, make me an Admin @TetraTechTrendingBot in your Group

- Type /add to start tracking your coin

- Type /settings to show all available easy to use settings

- Attach your telegram link by going to group settings

- Type /comp to view the current buy contest leaderboard

- Type /winners to view all previous buy contests winners and add TXN as proof of payment

- Type /info to view current token info and links

- Type /remove to clear settings and competitions and remove the token from chat

- MARKETING: @TetraTrendingBot
                """,
    "ES": """
¡Mándeme un cantante o nombre de una canción y encontraré la música para usted!
/song — buscar por título
/artist — buscar por cantante
/category — buscar por categoría
/setlang — cambiar idioma
/settings — cambiar los ajustes
/my — tu lista de reproducción
"""
}

# START MESSAGES END-------------------------------------------------------------------------


# /SONG MESSAGES-----------------------------------------------------------------------------

song_messages = {
    "RU": "Какую композицию ищете?",
    "EN": "What song are you looking for?",
    "ES": "¿Qué canción está buscando?"}
# /SONG MESSAGES END-------------------------------------------------------------------------

# /ARTIST MESSAGES-----------------------------------------------------------------------------
artist_messages = {
    "RU": "Какого исполнителя ищете?",
    "EN": "What artist are you looking for?",
    "ES": "¿Qué artista buscas?"}
# /ARTIST MESSAGES END ------------------------------------------------------------------------

category_messages = {
    "RU": "Какую категорию вы ищете?",
    "EN": "What category are you looking for?",
    "ES": "¿Qué categoría estás buscando?"}
# /CATEGORY MESSAGES END-------------------------------------------------------------------------

# /SETLANG MESSAGES----------------------------------------------------------------------------
setlang_messages = {
    "RU": "Выберите новый язык",
    "EN": "Choose a new language",
    "ES": "Elige un nuevo idioma"}
# /SETLANG MESSAGES END------------------------------------------------------------------------

# /SETTINGS MESSAGES----------------------------------------------------------------------------
settings_messages = {
    "RU": "Какие опции хотите изменить?",
    "EN": "What options do you want to change?",
    "ES": "¿Qué opciones quieres cambiar?"}
# /SETTINGS MESSAGES END------------------------------------------------------------------------

# /NOTHING MESSAGE----------------------------------------------------------------------------
nothing_messages = {
    "RU": "Ничего не нашлось",
    "EN": "Nothing was found",
    "ES": "No se encontró nada"}
# /SETTINGS MESSAGES END------------------------------------------------------------------------

# IN FIRST PAGE MESSAGE-------------------------------------------------------------------------
you_in_first_page_message = {
    "RU": "Вы уже первой странице.",
    "EN": "You are already the first page.",
    "ES": "Ya eres la primera página."}
# IN FIRST PAGE MESSAGE END----------------------------------------------------------------------

# NUMBER PAGE------------------------------------------------------------------------------------
number_page_message = {
    "RU": "<b>Страница {0} из {1}</b>\n\n",
    "EN": "<b>Page {0} of {1}</b>\n\n",
    "ES": "<b>Página {0} de {1}</b>\n\n"}
# NUMBER PAGE END-------------------------------------------------------------------------------

select_chain_menu = "Select Chain"
token_address_question="Token address?"
bot_name = "Tetra Trending Bot"
select_chart = f"⚙️<b>{bot_name}</b>\n\nSelect your favorite chart to link on buy posts"
chart_links = {
            "PooCoin":"poocoin.app",
            "DexView":"www.dexview.com/bsc"
            }
initialcompvalue = {
            "status":"",
            "chain": "",
            "token_address": "",
            "token_name":"",
            "alt_token_name":"",
            "pair_address": "",
            "show_buys_w/out_comp": "on",
            "gif_image": "0.jpg",
            "buy_emoji": "😄",
            "min_buy": 10,
            "buy_step": 5,
            "token_group_pref":{
                "group_link":"",
                "notify_whale_buy":"off",
                "selected_chart":"PooCoin",
                "circulating_supply":""
            },
            "ongoing":"off",
            "comp_type":"big_buy_comp",
            "winners":{},
            "comp_text":"",
            "blacklist":{},
            "big_buy_comp": {
                "length":3,
                "min_buy":0.1,
                "must_hold":1,
                "prize":[0.0001,0.0001,0.0001],
                "start_time":0,
                "end_time":0
            },
            "last_buy_comp":{
                "countdown":3,
                "min_buy":0.1,
                "prize":0.0001,
                "must_hold":1,
                "start_time":0,
                "end_time":0,
                "message_id":0
            }
        }