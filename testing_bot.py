import json
import logging
import random

from telegram.ext import Application, CommandHandler, ConversationHandler, MessageHandler, filters
from config import BOT_TOKEN

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start(update, context):
    await update.message.reply_text(
        "Привет. Тебе будет предложен тест из 10 вопросов.\n"
        "Старайся отвечать правильно, а в конце узнаешь свой результат.\n"
        "Пиши да, если готов.\n"
        "Вы можете прервать тест в любой момент, послав команду /stop.")
    return 1


async def first_response(update, context):
    context.user_data['agreed'] = update.message.text.lower()
    if context.user_data['agreed'] == 'да':
        with open('static/json/test.json', mode='r', encoding='utf-8') as f:
            questions = json.load(f)
        random.shuffle(questions['test'])
        context.user_data['questions'] = questions
        context.user_data['score'] = 0
        context.user_data['current_question'] = 0
        await ask_question(update, context)
        return 2


async def ask_question(update, context):
    question = context.user_data['questions']['test'][context.user_data['current_question']]['question']
    await update.message.reply_text(question)


async def handle_answer(update, context):
    answer = update.message.text.lower()
    correct_answer = context.user_data['questions']['test'][context.user_data['current_question']]['response'].lower()
    if answer == correct_answer:
        context.user_data['score'] += 1
        await update.message.reply_text("Правильно!")
    else:
        await update.message.reply_text("Неправильно.")
    context.user_data['current_question'] += 1
    if context.user_data['current_question'] == len(context.user_data['questions']['test']):
        await show_result(update, context)
        return ConversationHandler.END
    await ask_question(update, context)


async def show_result(update, context):
    score = context.user_data['score']
    await update.message.reply_text(f"Тест завершен. Ваш результат: {score} из 10.\n"
                                    f"Если желаете пройти тест снова, отправляйте /start.")


async def stop(update, context):
    await update.message.reply_text("Тест прерван!\n"
                                    "Если желаете пройти тест снова, отправляйте /start.")
    return ConversationHandler.END


def main():
    application = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, first_response)],
            2: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer)]
        },
        fallbacks=[CommandHandler('stop', stop)]
    )

    application.add_handler(conv_handler)

    application.run_polling()


if __name__ == "__main__":
    main()
