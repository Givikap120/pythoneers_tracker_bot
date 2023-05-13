import logging
from telegram import Update
from telegram import __version__ as TG_VER
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

token = '6216487125:AAG-FBLzFruHkBtz-QL3B8hg3O1_V9gST9M'

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 5):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

SUBJECT_LIST, a, b, c  = range(4)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info(str(update.message.chat_id))

    await update.message.reply_text(
        "Привіт! Вибери команду:\n"
        "/add_subject - додати предмет\n"
        "/choose_subject - вибрати предмет\n"
        + f"Твій айді - {update.message.chat_id}"
    )

async def add_subject(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info(str(update.message.chat_id))

    await update.message.reply_text(
        "Введи назву предмету:\n"
    )

    return 0

async def get_subject_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logger.info(update.message.from_user)

    msg = update.message.text

    filename = str(update.message.chat_id)+'_subjects.txt'

    file = open(filename,'a')
    file.close()

    file = open(filename,'r')
    lines = file.readlines()
    lines = [line.strip() for line in lines]
    file.close()

    if msg in lines:
        await update.message.reply_text(
            "Предмет вже існує", reply_markup=ReplyKeyboardRemove()
        )
    else:
        file = open(filename,'a')
        file.write(msg+'\n')
        file.close()

        await update.message.reply_text(
            f"Предмет {msg} успішно доданий до списку", reply_markup=ReplyKeyboardRemove()
        )

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return ConversationHandler.END

def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(token).build()
    
    application.add_handler(CommandHandler("start", start))
    #application.add_handler(CommandHandler("choose_subject", choose_subject))

    #CommandHandler("add_subject", add_subject)

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("add_subject", add_subject)],
        states={
            0: [MessageHandler(filters.TEXT, get_subject_name)]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()
