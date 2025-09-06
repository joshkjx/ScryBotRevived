from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters,ContextTypes
from telegram import Update
import os
from dotenv import load_dotenv
import logging
from fastapi import FastAPI

load_dotenv()
TOKEN = os.environ.get("TELE_BOT_TOKEN")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level = logging.INFO
)

app = FastAPI()

@app.get("/")
def index():
    return {"message" : "Hello World"}    

async def start(update: Update, context = ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

def register_handlers(dispatcher):
    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)

def main():
    application = ApplicationBuilder().token(TOKEN).build()

    start_handler = CommandHandler('start', start)

    application.add_handler(start_handler)

    application.run_polling()

if __name__ == '__main__':
    main()