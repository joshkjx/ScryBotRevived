import os, asyncio
from dotenv import load_dotenv
from flask import Flask, request
import logging

from telegram import Update
from telegram.ext import CommandHandler, ApplicationBuilder, CallbackQueryHandler
import handlers as bot_functions

load_dotenv()
TOKEN = os.environ.get("TELE_BOT_TOKEN")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level = logging.INFO
)

### Initialising the bot
app = Flask(__name__)
application = ApplicationBuilder().token(TOKEN).build()

### Handlers to attach commands to async functions
start_handler = CommandHandler('start', bot_functions.start)
scry_handler = CommandHandler('scry', bot_functions.scry)
price_handler = CommandHandler('price', bot_functions.get_price)
help_handler = CommandHandler('help', bot_functions.helpfunc)
img_handler = CommandHandler('img', bot_functions.get_card_image)

application.add_handler(start_handler)
application.add_handler(scry_handler)
application.add_handler(price_handler)
application.add_handler(help_handler)
application.add_handler(img_handler)
application.add_handler(CallbackQueryHandler(bot_functions.mdfc_button))

@app.route("/", methods =['POST'])
def webhook():
    '''
    Telegram Webhook
    '''
    # Method 1
    if request.headers.get('content-type') == 'application/json':
            asyncio.run(process_tele_update())
            return('', 204)
    else:
        return ('Bad request', 400)

async def process_tele_update():
    async with application:
        update = Update.de_json(request.get_json(force=True),application.bot)
        await application.process_update(update)


@app.route("/", methods =['GET'])
def index():
    return {"message": "Hello World"}

if __name__ == "__main__":
    handler = app