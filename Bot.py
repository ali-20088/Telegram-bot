import telebot
from telebot import types
import requests

TOKEN = '7824210014:AAH6PRpQFan9GmrtRHGiXQV2rf0RL70mkhQ'
CHANNEL_USERNAME = "@comic_nub"

bot = telebot.TeleBot(TOKEN)

files_db = {}

def check_membership(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        if member.status in ['member', 'administrator', 'creator']:
            return True
        return False
    except Exception as e:
        print(f"Error checking membership: {e}")
        return False

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    if check_membership(user_id):
        bot.send_message(user_id, "خوش آمدید! شما عضو کانال هستید. فایل‌های مورد نظر را ارسال کنید.")
    else:
        bot.send_message(user_id, f"برای استفاده از ربات باید عضو کانال {CHANNEL_USERNAME} شوید.")

@bot.message_handler(content_types=['photo', 'document', 'video'])
def handle_file(message):
    user_id = message.from_user.id
    if check_membership(user_id):
        try:
            if message.photo:
                file_id = message.photo[-1].file_id
            elif message.document:
                file_id = message.document.file_id
            elif message.video:
                file_id = message.video.file_id

            files_db[file_id] = {
                'type': message.content_type,
                'file_id': file_id,
                'user_id': user_id
            }

            bot.send_message(user_id, "فایل شما ذخیره شد. از دکمه‌های زیر برای دریافت فایل استفاده کنید.")
            send_file_menu(user_id)
        except Exception as e:
            bot.send_message(user_id, "در هنگام ذخیره فایل مشکلی پیش آمد.")
            print(f"Error handling file: {e}")
    else:
        bot.send_message(user_id, f"برای استفاده از ربات باید عضو کانال {CHANNEL_USERNAME} شوید.")

def send_file_menu(user_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item = types.KeyboardButton("دریافت فایل‌ها")
    markup.add(item)
    bot.send_message(user_id, "برای دریافت فایل‌های ذخیره شده، روی دکمه زیر کلیک کنید.", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "دریافت فایل‌ها")
def send_saved_files(message):
    user_id = message.from_user.id
    if check_membership(user_id):
        if files_db:
            for file_id, file_data in files_db.items():
                if file_data['user_id'] == user_id:
                    try:
                        if file_data['type'] == 'photo':
                            bot.send_photo(user_id, file_id)
                        elif file_data['type'] == 'document':
                            bot.send_document(user_id, file_id)
                        elif file_data['type'] == 'video':
                            bot.send_video(user_id, file_id)
                    except Exception as e:
                        bot.send_message(user_id, "در ارسال فایل مشکلی پیش آمد.")
                        print(f"Error sending file: {e}")
        else:
            bot.send_message(user_id, "هیچ فایلی برای شما ذخیره نشده است.")
    else:
        bot.send_message(user_id, f"برای استفاده از ربات باید عضو کانال {CHANNEL_USERNAME} شوید.")

bot.polling(none_stop=True)
