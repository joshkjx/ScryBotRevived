from telegram import Update
from telegram.ext import ContextTypes

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
