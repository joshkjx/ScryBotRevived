from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from utils.scryfall_api import ask_scryfall,get_card_info,fetch_prices

## driver function for /scry searches
async def scry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nospace = ' '.join(context.args)
    card_response = await ask_scryfall(nospace)
    await update.message.reply_text(text=card_response, parse_mode='Markdown')

## Driver Function that fetches price info given a fulltext query
async def get_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nospace = ' '.join(context.args)
    response = await get_card_info(nospace)
    cardlist = response['data']
    output = await fetch_prices(cardlist)
    await update.message.reply_text(text=output, parse_mode='Markdown')

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