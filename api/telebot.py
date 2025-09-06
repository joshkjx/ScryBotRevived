import os
from typing import Optional
from dotenv import load_dotenv
import urllib
from flask import Flask, request
import logging

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import MessageHandler, filters, CommandHandler, ApplicationBuilder, ContextTypes, CallbackQueryHandler
import requests as rq

load_dotenv()
TOKEN = os.environ.get("TELE_BOT_TOKEN")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level = logging.INFO
)

### Initialising the bot
app = Flask(__name__)
application = ApplicationBuilder().token(TOKEN).build()

### function that takes a search string (must have no spaces!) and queries scryfall API, returning a Search object, which is a json containing a list of Card objects.
### Even if there is only a single result, it's still stored in a list!
### Access the cards by doing output['data']
### If output is paginated, the GET uri for the next page is found in output['next_page']

async def get_card_info(query = str):
    url_encoded_query = urllib.parse.quote_plus(query)
    request_query = 'https://api.scryfall.com/cards/search?q=' + url_encoded_query
    response = rq.get(request_query)
    if response.status_code == 200:
        output = response.json()
    else:
        return "Error"
    return output

### async functions to tie to commands
## simple start function for testing purposes.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(text="I'm a bot, please talk to me!")
    return "Success"

async def helpfunc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = ("*List of commands:*\n/scry <search term>: Performs a Scryfall search. You can use Scryfall search syntax for this.\n" + 
    "/price <card name>: Checks the prices, in USD, of the indicated card for the day.\n" + 
    "/img <card name>: Displays an image of the indicated card. _NOTE: Currently does not work with different printings or the back sides of MDFCs_")
    await update.message.reply_text(text=help_text, parse_mode='Markdown')
    return "Success"

## driver function for /scry searches
async def scry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nospace = ' '.join(context.args)
    card_response = await ask_scryfall(nospace)
    await update.message.reply_text(text=card_response, parse_mode='Markdown')
    
## scryfall data fulltext print logic
async def ask_scryfall(query: str):
    response = await get_card_info(query)
    if response == "Error":
        return 'Something went wrong!'
    cardlist = response['data']
    if len(cardlist) > 1:
        out_text = 'More than one card found, please try another search with one of the following:'
        for i in range(len(cardlist)):
            out_text += '\n' + cardlist[i]['name']
            if i > 30:
                out_text += '...' + '\nMore than 30 entries, please refine your search.'
                break
        out_text += '\nIf you\'re looking for an exact match, you can add ! before the name to search for a match for an exact name. (e.g. /scry !greed)'
        return out_text
    else:
        cardobj = response['data'][0]
        card_name = '*' + cardobj['name'] + '*'
        out_text = card_name
        cardfaces = list()
        if 'card_faces' in cardobj:
            for i in cardobj['card_faces']:
                cardfaces.append(i)
        else:
            cardfaces.append(cardobj)
        for i in range(len(cardfaces)):
            out_text += '\n'
            out_text += (cardfaces[i]['mana_cost'].replace('{', '').replace('}','') + '\n')
            out_text += ('_' + cardfaces[i]['type_line'] + '_' + '\n')
            out_text += (cardfaces[i]['oracle_text'].replace('(','_(').replace(')',')_') + '\n')
            if "Creature" in cardfaces[i]['type_line']:
                out_text += (cardfaces[i]['power'] + '/' + cardfaces[i]['toughness'])
            elif "Planeswalker" in cardfaces[i]['type_line']:
                out_text += 'Starting Loyalty: ' + cardfaces[i]['loyalty']
            if i >= (len(cardfaces) - 1):
                break
            out_text += "\n --------"
        return out_text

## Driver Function that fetches price info given a fulltext query
async def get_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nospace = ' '.join(context.args)
    response = await get_card_info(nospace)
    cardlist = response['data']
    output = await fetch_prices(cardlist)
    await update.message.reply_text(text=output, parse_mode='Markdown')

# Logic for the price fetching
async def fetch_prices(cardlist):
    price_cats = {'usd' : 'USD', 'usd_foil' : 'USD (Foil)', 'usd_etched': 'USD (Etched)'}
    if len(cardlist) > 1:
        out_text = 'More than one card found, please try another search with one of the following:'
        for i in range(len(cardlist)):
            out_text += '\n' + cardlist[i]['name']
            if i > 30:
                out_text += '...' + '\nMore than 30 entries, please refine your search.'
                break
        out_text += '\n\nIf you\'re looking for an exact match, you can add ! before the name to search for a match for an exact name. (e.g. /scry !greed)'
        return out_text
    out_text = "Today's prices of *{cardname}* are: \n| ".format(cardname = cardlist[0]['name'])
    pricelist = cardlist[0]['prices']
    for currency in price_cats:
        out_text += ("*" + price_cats[currency] + "*: ")
        if pricelist[currency]:
            out_text += str(pricelist[currency])
        else:
            out_text += "N/A"        
        out_text += ' | '
    out_text += '\nPlease note that these prices are updated once a day, not in real time.'
    return out_text

## Function to fetch an image
async def get_card_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nospace = ' '.join(context.args)
    response = await get_card_info(nospace)
    if response == "Error":
        await update.message.reply_text(text="Something went Wrong!", parse_mode='Markdown')
        return 'Something went wrong!'
    cardlist = response['data']
    if len(cardlist) > 1:
        out_text = 'More than one card found, please try another search with one of the following:'
        for i in range(len(cardlist)):
            out_text += '\n' + cardlist[i]['name']
            if i > 30:
                out_text += '...' + '\nMore than 30 entries, please refine your search.'
                break
        out_text += '\n\nIf you\'re looking for an exact match, you can add ! before the name to search for a match for an exact name. (e.g. /scry !greed)'
        await update.message.reply_text(text=out_text, parse_mode='Markdown')
        return
    if 'card_faces' in cardlist[0]:
        keyboard = [[InlineKeyboardButton("{cardname}".format(cardname = str(cardlist[0]['card_faces'][0]['name'])), callback_data = '0')],
                    [InlineKeyboardButton("{cardname}".format(cardname = str(cardlist[0]['card_faces'][1]['name'])), callback_data = '1')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        selection = await update.message.reply_text("You seem to have named a two-faced card. Which side would you like to see? Not actually implemented yet.", reply_markup=reply_markup)
        await update.message.reply_photo(str(cardlist[0]['card_faces'][0]['image_uris']['normal']))
        card_img_uri = str(cardlist[0]['card_faces'][1]['image_uris']['normal'])
    else:
        card_img_uri = str(cardlist[0]['image_uris']['normal'])
    await update.message.reply_photo(card_img_uri)
    return "Ok"

async def mdfc_button(update: Update, context:ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    return int(query.data)

### Handlers to attach commands to async functions

start_handler = CommandHandler('start', start)
scry_handler = CommandHandler('scry', scry)
price_handler = CommandHandler('price', get_price)
help_handler = CommandHandler('help', helpfunc)
img_handler = CommandHandler('img', get_card_image)

application.add_handler(start_handler)
application.add_handler(scry_handler)
application.add_handler(price_handler)
application.add_handler(help_handler)
application.add_handler(img_handler)
application.add_handler(CallbackQueryHandler(mdfc_button))

@app.route("/", methods =['POST'])
async def webhook():
    '''
    Telegram Webhook
    '''
    # Method 1
    if request.headers.get('content-type') == 'application/json':
        async with application:
            update = Update.de_json(request.get_json(force=True),application.bot)
            await application.process_update(update)
            return('', 204)
    else:
        return ('Bad request', 400)


@app.get("/")
def index():
    return {"message": "Hello World"}