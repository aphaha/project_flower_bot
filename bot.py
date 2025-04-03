import telebot
from telebot import types

API_TOKEN = '7947805536:AAHMl3RuCqSIwSwOGQvuEXG_M32ZHcHkCwg'
bot = telebot.TeleBot(API_TOKEN)

ADMINS = [788277490]

catalog = {
    'roses': {'name': 'Червоні троянди', 'price': 150, 'description': 'Букет із 9 червоних троянд'},
    'tulips': {'name': 'Весняні тюльпани', 'price': 120, 'description': '10 різнокольорових тюльпанів'},
    'orchids': {'name': 'Орхідеї', 'price': 200, 'description': 'Елегантні білі орхідеї'}
}

orders = []

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('/catalog', '/info', '/feedback', '/order')
    bot.send_message(message.chat.id, "🌸 Вітаємо у боті квіткового магазину!", reply_markup=markup)
    bot.send_message(message.chat.id, "Ви можете переглянути каталог або залишити відгук.")

@bot.message_handler(commands=['info'])
def send_info(message):
    bot.send_message(message.chat.id, "Цей бот дозволяє замовити квіти онлайн. Ми пропонуємо красиві букети на будь-який смак!")

@bot.message_handler(commands=['help'])
def send_help(message):
    bot.send_message(message.chat.id, "/start - Почати\n/catalog - Переглянути букети\n/info - Інформація про магазин\n/feedback - Залишити відгук\n/order - Переглянути замовлення\n/add_item - Додати товар (адмін)\n/remove_item - Видалити товар (адмін)\n/orders - Усі замовлення (адмін)")

@bot.message_handler(commands=['catalog'])
def send_catalog(message):
    markup = types.InlineKeyboardMarkup()
    for key, item in catalog.items():
        btn = types.InlineKeyboardButton(text=f"{item['name']} - {item['price']} грн", callback_data=key)
        markup.add(btn)
    bot.send_message(message.chat.id, "Оберіть букет:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data in catalog)
def show_item_details(call):
    item = catalog[call.data]
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text="Замовити", callback_data=f"order_{call.data}"))
    bot.send_message(call.message.chat.id, f"{item['name']}\n{item['description']}\nЦіна: {item['price']} грн", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("order_"))
def confirm_order(call):
    item_key = call.data.split('_')[1]
    item = catalog[item_key]
    user = call.from_user
    order = {
        'user_id': user.id,
        'username': user.username,
        'item': item['name'],
        'price': item['price'],
        'status': 'очікує оплату'
    }
    orders.append(order)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text="💳 Оплатити", callback_data=f"pay_{len(orders)-1}"))
    bot.send_message(call.message.chat.id, "🌷 Дякуємо за ваше замовлення! Натисніть кнопку нижче, щоб оплатити.", reply_markup=markup)
    for admin_id in ADMINS:
        bot.send_message(admin_id, f"Нове замовлення: @{user.username} (ID: {user.id})\nТовар: {item['name']} - {item['price']} грн")

@bot.callback_query_handler(func=lambda call: call.data.startswith("pay_"))
def fake_payment(call):
    index = int(call.data.split('_')[1])
    if 0 <= index < len(orders):
        orders[index]['status'] = 'оплачено'
        bot.send_message(call.message.chat.id, "✅ Оплату отримано! Ваше замовлення буде оброблено найближчим часом.")
        for admin_id in ADMINS:
            bot.send_message(admin_id, f"💰 Замовлення №{index+1} оплачено користувачем @{call.from_user.username}.")

@bot.message_handler(commands=['order'])
def show_order_instruction(message):
    bot.send_message(message.chat.id, "Щоб зробити замовлення, перейдіть у /catalog, оберіть букет та натисніть кнопку 'Замовити'.")

@bot.message_handler(commands=['feedback'])
def get_feedback(message):
    msg = bot.send_message(message.chat.id, "✍️ Напишіть свій відгук:")
    bot.register_next_step_handler(msg, process_feedback)

def process_feedback(message):
    for admin_id in ADMINS:
        bot.send_message(admin_id, f"Відгук від @{message.from_user.username}:\n{message.text}")
    bot.send_message(message.chat.id, "Дякуємо за ваш відгук!")

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id in ADMINS:
        bot.send_message(message.chat.id, "🔐 Адмін-панель:\n/add_item - Додати товар\n/remove_item - Видалити товар\n/orders - Переглянути всі замовлення")
    else:
        bot.send_message(message.chat.id, "У вас немає доступу до цієї команди.")

@bot.message_handler(commands=['add_item'])
def add_item(message):
    if message.from_user.id in ADMINS:
        msg = bot.send_message(message.chat.id, "Введіть назву товару, опис і ціну у форматі:\nназва;опис;ціна")
        bot.register_next_step_handler(msg, process_add_item)
    else:
        bot.send_message(message.chat.id, "⛔ Ви не маєте доступу до цієї функції.")

def process_add_item(message):
    try:
        name, desc, price = message.text.split(';')
        key = name.lower().replace(' ', '_')
        catalog[key] = {'name': name, 'description': desc, 'price': int(price)}
        bot.send_message(message.chat.id, f"✅ Товар '{name}' додано до каталогу.")
    except:
        bot.send_message(message.chat.id, "❌ Помилка формату. Спробуйте ще раз у форматі: назва;опис;ціна")

@bot.message_handler(commands=['remove_item'])
def remove_item(message):
    if message.from_user.id in ADMINS:
        msg = bot.send_message(message.chat.id, "Введіть ключ товару для видалення (наприклад, roses):")
        bot.register_next_step_handler(msg, process_remove_item)
    else:
        bot.send_message(message.chat.id, "⛔ Ви не маєте доступу до цієї функції.")

def process_remove_item(message):
    key = message.text.strip()
    if key in catalog:
        del catalog[key]
        bot.send_message(message.chat.id, f"✅ Товар '{key}' видалено з каталогу.")
    else:
        bot.send_message(message.chat.id, f"❌ Товар з ключем '{key}' не знайдено.")

@bot.message_handler(commands=['orders'])
def show_orders(message):
    if message.from_user.id in ADMINS:
        if orders:
            for i, o in enumerate(orders, 1):
                bot.send_message(message.chat.id, f"{i}. @{o['username']} - {o['item']} ({o['price']} грн) - Статус: {o.get('status', 'не вказано')}")
        else:
            bot.send_message(message.chat.id, "Немає замовлень.")
    else:
        bot.send_message(message.chat.id, "⛔ Ви не маєте доступу до цієї команди.")

@bot.message_handler(commands=['hello'])
def say_hello(message):
    bot.send_message(message.chat.id, "Привіт! Радий вас бачити 🌼")

@bot.message_handler(func=lambda message: message.text.lower() in ["як зробити замовлення?", "як замовити?"])
def answer_order_question(message):
    bot.send_message(message.chat.id, "Щоб зробити замовлення: \n1. Введіть /catalog.\n2. Оберіть букет.\n3. Натисніть кнопку 'Замовити'.")

print("Bot is running...")
bot.infinity_polling()