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
    """Start bot, shows list of commands"""

    logger.info(f'User {update.message.chat_id} started the bot')
    logger.info(update.message.from_user)

    await update.message.reply_text(
        "Привіт! Вибери команду:\n"
        "/add_subject - додати предмет\n"
        "/choose_subject - вибрати предмет\n"
        + f"Твій айді - {update.message.chat_id}"
    )

async def add_subject(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/add_subject entry point"""

    await update.message.reply_text("Введи назву предмету:\n")
    return 0

def _get_lines_from_file(filename):
    """Reads lines from file"""
    file = open(filename,'a')
    file.close()

    file = open(filename,'r')
    lines = file.readlines()
    lines = [line.strip() for line in lines]
    file.close()
    
    return lines


async def get_add_subject_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Gets subject name from user and adds it to the list"""

    msg = update.message.text
    filename = str(update.message.chat_id)+'_subjects.txt'
    lines = _get_lines_from_file(filename)

    if msg in lines:
        logger.info(f'{update.message.chat_id} tried to add subject {msg}, already exists')
        await update.message.reply_text("Предмет вже існує")
    else:
        file = open(filename,'a')
        file.write(msg+'\n')
        file.close()

        logger.info(f'{update.message.chat_id} have added subject {msg}')
        await update.message.reply_text(f"Предмет {msg} успішно доданий до списку")

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """End current conversation"""
    return ConversationHandler.END


def _delete_line(file_path, line_to_delete):
    """Delete all instances of given line from file"""

    with open(file_path, 'r') as file:
        lines = file.readlines()

    with open(file_path, 'w') as file:
        for line in lines:
            if line.strip() != line_to_delete:
                file.write(line)

async def delete_subject(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Delete subject contained in context.user_data['selected_subject']"""

    subject_name = context.user_data['selected_subject']

    filename = str(update.message.chat_id)+'_subjects.txt'
    _delete_line(filename, subject_name)

    logger.info(f'{update.message.chat_id} have deleted subject {subject_name}')
    await update.message.reply_text(f"Предмет {subject_name} був видалений зі списку")


async def get_select_subject_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    #PLACEHOLDER
    return ConversationHandler.END


def buttons(path):
    subjects = open(path+'.txt','r')
    n_subjects = len(subjects.readlines())
    buttons = []
    keyboard1 = ReplyKeyboardMarkup(resize_keyboard = True, one_time_keyboard = True)
    n = 0
    for i in subjects:
        buttons.append(KeyboardButton('i'))
        keyboard1.add(buttons[n])
        n+=1
  
    
@dp.message_handler(commands=[])
async def welc():
    await message.reply("choose subject", reply_markup = keyboard1)
@dp.message_handler():
    

#async def kb_answer(message:types.Message):

def main() -> None:
    """Run the bot"""
    application = Application.builder().token(token).build()
    
    #start
    application.add_handler(CommandHandler("start", start))

    #add subject
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("add_subject", add_subject)],
        states={
            0: [MessageHandler(filters.TEXT, get_add_subject_name)]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    application.add_handler(conv_handler)

    #select_subject
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("select_subject", add_subject)],
        states={
            0: [MessageHandler(filters.TEXT, get_select_subject_name)],
            -1: []
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    application.add_handler(conv_handler)

    #run
    application.run_polling()


if __name__ == "__main__":
    main()
