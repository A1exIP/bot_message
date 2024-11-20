from telegram import Bot, Update, Chat, ChatMember
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import time
import os

TOKEN = "7662625231:AAFA9M_rsoFHo2DsndyyxwgGbMGlhIErk4o"

# Файл для хранения ID групп
GROUPS_FILE = "groups.txt"

# Функция для загрузки ID групп из файла
def load_group_ids():
    if os.path.exists(GROUPS_FILE):
        with open(GROUPS_FILE, "r") as file:
            return set(int(line.strip()) for line in file)
    return set()

# Функция для сохранения ID групп в файл
def save_group_ids(group_ids):
    with open(GROUPS_FILE, "w") as file:
        for group_id in group_ids:
            file.write(f"{group_id}\n")

# Инициализируем ID групп
group_ids = load_group_ids()

# Функция для команды /start
def start(update: Update, context: CallbackContext):
    update.message.reply_text("Привет! Я бот для массовой рассылки сообщений в группы. Пожалуйста, укажите текст сообщения после команды /send **текст** ")

# Функция для отправки сообщений в группы
def send_message(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("Пожалуйста, укажите текст сообщения после команды /send **текст**")
        return

    message_text = " ".join(context.args)
    sent_count = 0

    for group_id in group_ids:
        try:
            context.bot.send_message(chat_id=group_id, text=message_text)
            sent_count += 1
            time.sleep(2)  # Интервал между отправками, чтобы избежать блокировки
        except Exception as e:
            print(f"Не удалось отправить сообщение в группу {group_id}: {e}")

    update.message.reply_text(f"Сообщение отправлено в {sent_count} групп.")

# Функция для добавления текущей группы, если бот добавлен
def add_current_group(update: Update, context: CallbackContext):
    chat = update.effective_chat
    if chat.type in [Chat.GROUP, Chat.SUPERGROUP] and chat.id not in group_ids:
        group_ids.add(chat.id)
        save_group_ids(group_ids)
        update.message.reply_text("Эта группа была добавлена для рассылок.")
    else:
        update.message.reply_text("Этот чат уже добавлен или не является группой.")

# Команда для ручного добавления группы
def add_group(update: Update, context: CallbackContext):
    if context.args:
        try:
            new_group_id = int(context.args[0])
            if new_group_id not in group_ids:
                group_ids.add(new_group_id)
                save_group_ids(group_ids)
                update.message.reply_text(f"Группа {new_group_id} добавлена для рассылок.")
            else:
                update.message.reply_text("Эта группа уже добавлена.")
        except ValueError:
            update.message.reply_text("Пожалуйста, введите корректный ID группы.")
    else:
        update.message.reply_text("Использование: /add_group <group_id>")

# Основная функция
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # Команды для управления ботом
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("send", send_message))
    dp.add_handler(CommandHandler("add_group", add_group))

    # Автоматическое добавление группы, если бот был добавлен в неё
    dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, add_current_group))

    # Запуск бота
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
