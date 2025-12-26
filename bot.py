import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# --- НАСТРОЙКИ ---
# Вставь сюда токен, который дал BotFather
TOKEN = "8460659430:AAEQ2ZfQWGi0XI8mgtLY_U7eCCPYIkiHmDE"

# Список участников (можно менять)
ROOMMATES = ["Саша", "Паша", "Руслан", "Виталий", "Иванна"]

# Переменная для хранения индекса текущего дежурного (начинаем с первого - 0)
current_cleaner_index = 0

# Настройка логирования (чтобы видеть ошибки в консоли)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# --- ФУНКЦИИ БОТА ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Приветствие при команде /start"""
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Привет! Я бот-распределитель уборки.\n"
             "Команды:\n"
             "/status - Кто дежурит сейчас?\n"
             "/next - Сменить дежурного (передать эстафету)"
    )

async def get_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает, чья сейчас очередь"""
    global current_cleaner_index
    cleaner = ROOMMATES[current_cleaner_index]
    
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"🧹 Сейчас дежурный по квартире: **{cleaner}**"
    )

async def next_cleaner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Переключает очередь на следующего участника"""
    global current_cleaner_index
    
    # Сдвигаем индекс на 1 вперед
    current_cleaner_index += 1
    
    # Если дошли до конца списка, возвращаемся в начало (цикл)
    if current_cleaner_index >= len(ROOMMATES):
        current_cleaner_index = 0
        
    next_person = ROOMMATES[current_cleaner_index]
    
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"✅ Очередь передана! Теперь дежурит: **{next_person}**"
    )

# --- ЗАПУСК ---

if __name__ == '__main__':
    # Создаем приложение
    application = ApplicationBuilder().token(TOKEN).build()
    
    # Добавляем обработчики команд
    start_handler = CommandHandler('start', start)
    status_handler = CommandHandler('status', get_status)
    next_handler = CommandHandler('next', next_cleaner)
    
    application.add_handler(start_handler)
    application.add_handler(status_handler)
    application.add_handler(next_handler)
    
    print("Бот запущен...")
    # Запускаем бота (он будет работать, пока ты не остановишь программу)
    application.run_polling()
    
