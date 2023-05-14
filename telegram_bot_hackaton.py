import logging
import telegram as tg
import pandas as pd
from datetime import datetime
from telegram import Update
from telegram import __version__ as TG_VER
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

import humanize
humanize.i18n.activate("uk_UA")

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
    CallbackQueryHandler,
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
        "/select_subject - вибрати предмет\n"
        "/show_report - продивитися звіт\n"
        "/cancel - перервати інтеракцію\n"
        + f"Твій айді - {update.message.chat_id}"
    )

async def add_subject(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/add_subject entry point"""

    await update.message.reply_text("Введіть назву предмету:\n")
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



GET_SELECT_SUBJECT, CHOOSE_ACTION = range(2)

async def select_subject(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    filename = str(update.message.chat_id)+'_subjects.txt'
    lines = _get_lines_from_file(filename)
    buttons = []       
        
    n = 0
    for i in lines:
        buttons.append(tg.KeyboardButton(i))

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, keyboard = [buttons,])
    await update.message.reply_text('Виберіть предмет',reply_markup = keyboard)

    return GET_SELECT_SUBJECT


async def get_select_subject_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    msg = update.message.text
    context.user_data['selected_subject'] = msg

    filename = str(update.message.chat_id)+'_subjects.txt'
    lines = _get_lines_from_file(filename)

    if msg not in lines:
        await update.message.reply_text(f'Предмет {msg} не є в списку')
        return ConversationHandler.END

    keyboard = [
        [
            tg.InlineKeyboardButton('Показати завдання', callback_data="show"),
            tg.InlineKeyboardButton('Редагувати завдання', callback_data="edit"),
        ],
        [
            tg.InlineKeyboardButton('Додати завдання', callback_data="add"),
            tg.InlineKeyboardButton('Видалити предмет', callback_data="delete"),
        ],
    ]

    reply_markup = tg.InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(f'Обраний предмет - {msg}', reply_markup=reply_markup)

    return CHOOSE_ACTION

async def choose_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return ConversationHandler.END


async def show_report(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Shows general report for user"""

    filename = str(update.effective_chat.id)+'_tasks.csv'
    df = pd.read_csv(filename)
    df['deadline'] = pd.to_datetime(df['deadline'], format="%d/%m/%Y")

    current_datetime = datetime.now()
    df['time_to_deadline'] = df.deadline - current_datetime

    pos_deadlines = df[df['time_to_deadline'] >= pd.Timedelta(0)][df.status == 0]
    neg_deadlines = df[df['time_to_deadline'] < pd.Timedelta(0)][df.status == 0]

    closest_dl = pos_deadlines['time_to_deadline'].idxmin()

    await context.bot.send_message(
        update.effective_chat.id, 
        f"Найближчий дедлайн через {humanize.naturaldelta(df.time_to_deadline.iloc[closest_dl])}, "
        f"завдання {df.task.iloc[closest_dl]}, "
        f"предмет {df.subject.iloc[closest_dl]}"
    )

    to_print = 'Просрочені дедлайни:\n'

    for index, row in neg_deadlines.iterrows():
        to_print+=f'{row.subject}, завдання {row.task}\n'
    
    await context.bot.send_message(
        update.effective_chat.id, 
        to_print
    )

async def show_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    filename = str(update.effective_chat.id)+'_tasks.csv'
    df = pd.read_csv(filename, parse_dates=['deadline'])


async def edit_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    a = 1

async def add_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
   try:
        df = pd.read_csv(str(update.effective_chat.id)+'_subjects.csv')
    except: 
        df = pd.DataFrame( {'Subject':[context.user_data['selected_subject']],
                     'Task':[''],
                     'Status':[0],
                     'Deadline':['']})
        await context.bot.send_message(update.effective_chat.id, f"Додайте завдання")
        
        df.Task = 1  #message
        await context.bot.send_message(update.effective_chat.id, f"Додайте дедлайн")
        
        df.Deadline = pd.to_datetime(str(1))#message
        df.to_csv(str(update.effective_chat.id)+'_subjects.csv')

    subj = 1#subj 
    await context.bot.send_message(update.effective_chat.id, f"Додайте завдання")        
    task = 1#task
    await context.bot.send_message(update.effective_chat.id, f"Додайте дедлайн")        
    deadline = pd.to_datetime(1) 

async def delete_subject(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Delete subject contained in context.user_data['selected_subject']"""

    subject_name = context.user_data['selected_subject']

    filename = str(update.effective_chat.id)+'_subjects.txt'
    _delete_line(filename, subject_name)

    logger.info(f'{update.effective_chat.id} have deleted subject {subject_name}')
    #await update.callback_query.answer(f"Предмет {subject_name} був видалений зі списку")
    await context.bot.send_message(update.effective_chat.id, f"Предмет {subject_name} був видалений зі списку")

    return ConversationHandler.END
    

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
        entry_points=[CommandHandler("select_subject", select_subject)],
        states={
            GET_SELECT_SUBJECT: [MessageHandler(filters.TEXT, get_select_subject_name)],
            CHOOSE_ACTION: [MessageHandler(filters.TEXT, choose_action),
                            CallbackQueryHandler(show_tasks, pattern="^show$"),
                            CallbackQueryHandler(edit_tasks, pattern="^edit$"),
                            CallbackQueryHandler(add_tasks, pattern="^add$"),
                            CallbackQueryHandler(delete_subject, pattern="^delete$")]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    application.add_handler(conv_handler)

    #show_report
    application.add_handler(CommandHandler("show_report", show_report))

    #run
    application.run_polling()


if __name__ == "__main__":
    main()
