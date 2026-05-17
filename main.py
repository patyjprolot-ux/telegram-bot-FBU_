import os
import telebot
from telebot import types
import time

# --- НАЛАШТУВАННЯ ---

TOKEN = os.getenv("TOKEN")
ADMIN_ID = 5012323355
bot = telebot.TeleBot(TOKEN)

# Сховище для захисту від спаму (5 хвилин)
user_last_submission = {}

# --- ПЕРЕВОД КНОПОК В НОРМАЛЬНЫЕ НАЗВАНИЯ ---
SERVICE_MAP = {
    "border_1": "Білорусь — Детальний маршрут (500$)",
    "border_2": "Білорусь — Піший перехід (30–45 км) (3500-4000$)",
    "border_3": "Молдова — 18 км (6500$)",
    "border_4": "Молдова — 15 км (7500$)",
    "border_5": "Молдова — 9 км (9000$)",
    "border_6": "Молдова — 3 км (10 500$)",
    "border_7": "Молдова — «Усе включено» (19 000$)",
    "border_8": "Угорщина — 9 км (4000$)",
    "border_9": "Румунія (13 500$)",

    "bron_full": "Бронювання — повний пакет (7500$)",
    "bron_search": "Лише зняття з розшуку (4500$)"
}

# --- ТЕКСТИ ---
WAIT_MESSAGE = (
    "Дякуємо за вибір! Ваша заявка прийнята.\n\n"
    "Очікуйте, адміністратор зв'яжеться з вами найближчим часом. "
    "Будь ласка, переконайтеся, що у вас дозволено надсилання повідомлень від невідомих номерів."
)

SPAM_WARNING = (
    "⚠️ <b>Захист системи:</b>\n"
    "Будь ласка, зачекайте 5 хвилин перед наступним запитом."
)

TEXT_BORDER = (
    "<b>Доступні варіанти та вартість послуг:</b>\n\n"
    "1. <b>Білорусь — Детальний маршрут</b> (500$)\n"
    "2. <b>Білорусь — Піший перехід (30–45 км)</b> (3500-4000$)\n"
    "3. <b>Молдова — 18 км</b> (6500$)\n"
    "4. <b>Молдова — 15 км</b> (7500$)\n"
    "5. <b>Молдова — 9 км</b> (9000$)\n"
    "6. <b>Молдова — 3 км</b> (10 500$)\n"
    "7. <b>Молдова — «Усе включено»</b> (19 000$)\n"
    "8. <b>Угорщина — 9 км</b> (4000$)\n"
    "9. <b>Румунія</b> (13 500$)\n\n"
    "⚠️ <b>Обов'язкова перевірка:</b> 250$ (вираховується із суми)."
)

TEXT_BRON = (
    "🛡️ <b>Оформлення відстрочки (Бронювання)</b>\n\n"
    "💰 <b>Вартість повного пакета:</b> 7500$\n"
    "🔍 <b>Окремо зняття з розшуку:</b> 4500$\n\n"
    "❗ <b>Важливо:</b> послуга надається лише після ретельної перевірки.\n\n"
    "<i>Оберіть потрібний варіант:</i>"
)

# --- ФУНКЦІЇ ---
def check_spam_5min(user_id):
    current_time = time.time()
    last_time = user_last_submission.get(user_id, 0)
    if current_time - last_time < 300:
        return False
    user_last_submission[user_id] = current_time
    return True


def send_admin_notification(user, text):
    username = f"@{user.username}" if user.username else "прихований"
    user_link = f"tg://user?id={user.id}"

    admin_text = (
        f"🔔 <b>НОВА ЗАЯВКА!</b>\n\n"
        f"👤 <b>Клієнт:</b> {user.first_name}\n"
        f"🔗 <b>Профіль:</b> {username}\n"
        f"📝 <b>Деталі:</b> {text}\n\n"
        f"👉 <a href='{user_link}'>ВІДКРИТИ ДІАЛОГ</a>"
    )

    try:
        bot.send_message(ADMIN_ID, admin_text, parse_mode='HTML')
    except Exception as e:
        print(f"Помилка надсилання адміну: {e}")


def main_menu():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("✈️ Перетин кордону", callback_data='menu_border'),
        types.InlineKeyboardButton("🛡️ Зняття з розшуку та бронювання", callback_data='menu_bron'),
        types.InlineKeyboardButton("❓ Інше запитання", callback_data='menu_other'),
        types.InlineKeyboardButton("🔄 Почати заново", callback_data='restart_all')
    )
    return markup


# --- ОБРОБНИКИ ---
@bot.message_handler(commands=['start'])
def start_cmd(message):
    bot.clear_step_handler_by_chat_id(message.chat.id)

    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("❌", callback_data='wrong'),
        types.InlineKeyboardButton("🔓 Натисніть для входу", callback_data='captcha_ok'),
        types.InlineKeyboardButton("❌", callback_data='wrong')
    )

    bot.send_message(message.chat.id, "🔐 Підтвердіть, що ви не бот:", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    bot.answer_callback_query(call.id)

    if call.data in ['captcha_ok', 'restart_all', 'back_to_main']:
        bot.edit_message_text(
            "Вітаємо. Оберіть потрібний розділ:",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=main_menu()
        )

    elif call.data == 'menu_border':
        markup = types.InlineKeyboardMarkup(row_width=3)

        btns = [
            types.InlineKeyboardButton(str(i), callback_data=f'final_border_{i}')
            for i in range(1, 10)
        ]

        markup.add(*btns)
        markup.add(types.InlineKeyboardButton("⬅️ Назад", callback_data='back_to_main'))

        bot.edit_message_text(
            TEXT_BORDER,
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup,
            parse_mode='HTML'
        )

    elif call.data == 'menu_bron':
        markup = types.InlineKeyboardMarkup(row_width=1)

        markup.add(
            types.InlineKeyboardButton("📦 Весь пакет послуг", callback_data='final_bron_full'),
            types.InlineKeyboardButton("🔍 Лише зняття з розшуку", callback_data='final_bron_search'),
            types.InlineKeyboardButton("⬅️ Назад", callback_data='back_to_main')
        )

        bot.edit_message_text(
            TEXT_BRON,
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup,
            parse_mode='HTML'
        )

    elif call.data.startswith('final_'):

        if check_spam_5min(call.from_user.id):

            res = call.data.replace('final_', '')

            service_name = SERVICE_MAP.get(res, res)

            send_admin_notification(
                call.from_user,
                f"Вибір послуги: {service_name}"
            )

            bot.edit_message_text(
                WAIT_MESSAGE,
                call.message.chat.id,
                call.message.message_id
            )

        else:
            bot.send_message(
                call.message.chat.id,
                SPAM_WARNING,
                parse_mode='HTML'
            )

    elif call.data == 'menu_other':
        msg = bot.send_message(
            call.message.chat.id,
            "Будь ласка, напишіть своє запитання:"
        )

        bot.register_next_step_handler(msg, process_custom_question)


def process_custom_question(message):
    if message.text == '/start':
        start_cmd(message)
        return

    if check_spam_5min(message.from_user.id):

        send_admin_notification(
            message.from_user,
            f"ЗАПИТАННЯ: {message.text}"
        )

        bot.send_message(message.chat.id, WAIT_MESSAGE)

    else:
        bot.send_message(message.chat.id, SPAM_WARNING, parse_mode='HTML')


if __name__ == '__main__':
    bot.infinity_polling()
