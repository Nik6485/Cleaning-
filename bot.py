import logging
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# --- НАСТРОЙКИ ---
TOKEN = "8460659430:AAEQ2ZfQWGi0XI8mgtLY_U7eCCPYIkiHmDE"

# Список участников
ROOMMATES = ["Паша", "Саша", "Виталик","Руслан", "Иванна"]

# Длительность дежурства одного человека (в днях)
ROTATION_DAYS = 7 

# Дата начала самого первого дежурства (Год, Месяц, День)
# Важно: Это "якорь", от которого считается весь график.
# Укажи здесь понедельник первой недели цикла.
START_DATE = datetime(2023, 10, 23) 

# --- ЛОГИРОВАНИЕ ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---

def get_cleaner_info(target_date):
    """
    Вычисляет, кто дежурит в заданную дату, и даты начала/конца смены.
    """
    # Считаем разницу дней между целевой датой и датой начала
    delta = target_date - START_DATE
    days_passed = delta.days
    
    # Если дата в прошлом (до начала отсчета), возвращаем первого
    if days_passed < 0:
        return ROOMMATES[0], START_DATE, START_DATE + timedelta(days=ROTATION_DAYS)

    # Вычисляем номер смены (сколько полных циклов прошло)
    shift_number = days_passed // ROTATION_DAYS
    
    # Вычисляем индекс человека (остаток от деления на кол-во людей)
    person_index = shift_number % len(ROOMMATES)
    
    # Вычисляем даты начала и конца этой конкретной смены
    current_shift_start = START_DATE + timedelta(days=shift_number * ROTATION_DAYS)
    current_shift_end = current_shift_start + timedelta(days=ROTATION_DAYS - 1)
    
    return ROOMMATES[person_index], current_shift_start, current_shift_end

# --- КОМАНДЫ БОТА ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="👋 Привет! Я автоматический календарь уборки.\n\n"
             "Команды:\n"
             "/status - Кто дежурит сегодня?\n"
             "/schedule - График на ближайшие 8 недель"
    )

async def get_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает текущего дежурного на основе сегодняшней даты"""
    today = datetime.now()
    cleaner, start_d, end_d = get_cleaner_info(today)
    
    # Форматируем даты в красивый вид (День.Месяц)
    fmt_start = start_d.strftime('%d.%m')
    fmt_end = end_d.strftime('%d.%m')
    
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"📅 **Сегодня ({today.strftime('%d.%m')})**\n\n"
             f"🧹 Дежурный: **{cleaner}**\n"
             f"🕒 Смена: с {fmt_start} по {fmt_end}"
    )

async def get_schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Генерирует список на будущее"""
    today = datetime.now()
    response_text = "📋 **График на ближайшее время:**\n\n"
    
    # Показываем график на 8 смен вперед
    for i in range(8):
        # Берем дату начала следующей смены
        future_date = today + timedelta(days=i * ROTATION_DAYS)
        cleaner, start_d, end_d = get_cleaner_info(future_date)
        
        fmt_start = start_d.strftime('%d.%m')
        fmt_end = end_d.strftime('%d.%m')
        
        # Добавляем строчку в ответ
        response_text += f"🔹 **{fmt_start} - {fmt_end}**: {cleaner}\n"
        
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=response_text
    )

# --- ЗАПУСК ---

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('status', get_status))
    application.add_handler(CommandHandler('schedule', get_schedule))
    
    print("Бот с автоматическим календарем запущен...")
    application.run_polling()
    
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
    
