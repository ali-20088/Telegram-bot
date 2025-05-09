import telebot
from telebot import types
import requests

TOKEN = '7824210014:AAH6PRpQFan9GmrtRHGiXQV2rf0RL70mkhQ'
CHANNEL_USERNAME = "@comic_nub"  # نام کانال شما

bot = telebot.TeleBot(TOKEN)

# ذخیره فایل‌ها (در اینجا فقط شناسه فایل ذخیره می‌شود)
files_db = {}

# بررسی عضویت در کانال
def check_membership(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        if member.status in ['member', 'administrator', 'creator']:
            return True
        return False
    except:
        return False

# دستور شروع
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    if check_membership(user_id):
        bot.send_message(user_id, "خوش آمدید! شما عضو کانال هستید. فایل‌های مورد نظر را ارسال کنید.")
    else:
        bot.send_message(user_id, f"برای استفاده از ربات باید عضو کانال {CHANNEL_USERNAME} شوید.")

# دریافت فایل (عکس، ویدیو یا PDF)
@bot.message_handler(content_types=['photo', 'document', 'video'])
def handle_file(message):
    user_id = message.from_user.id
    if check_membership(user_id):
        if message.photo:
            file_id = message.photo[-1].file_id  # آخرین سایز عکس
        elif message.document:
            file_id = message.document.file_id
        elif message.video:
            file_id = message.video.file_id

        # ذخیره شناسه فایل
        files_db[file_id] = {
            'type': message.content_type,
            'file_id': file_id,
            'user_id': user_id
        }

        bot.send_message(user_id, "فایل شما ذخیره شد. از دکمه‌های زیر برای دریافت فایل استفاده کنید.")
        send_file_menu(user_id)
    else:
        bot.send_message(user_id, f"برای استفاده از ربات باید عضو کانال {CHANNEL_USERNAME} شوید.")

# ارسال منو برای دریافت فایل
def send_file_menu(user_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item = types.KeyboardButton("دریافت فایل‌ها")
    markup.add(item)
    bot.send_message(user_id, "برای دریافت فایل‌های ذخیره شده، روی دکمه زیر کلیک کنید.", reply_markup=markup)

# دریافت فایل ذخیره شده
@bot.message_handler(func=lambda message: message.text == "دریافت فایل‌ها")
def send_saved_files(message):
    user_id = message.from_user.id
    if check_membership(user_id):
        if files_db:
            for file_id, file_data in files_db.items():
                if file_data['user_id'] == user_id:
                    if file_data['type'] == 'photo':
                        bot.send_photo(user_id, file_id)
                    elif file_data['type'] == 'document':
                        bot.send_document(user_id, file_id)
                    elif file_data['type'] == 'video':
                        bot.send_video(user_id, file_id)
        else:
            bot.send_message(user_id, "هیچ فایلی برای شما ذخیره نشده است.")
    else:
        bot.send_message(user_id, f"برای استفاده از ربات باید عضو کانال {CHANNEL_USERNAME} شوید.")

# راه‌اندازی ربات
bot.polling(none_stop=True)
