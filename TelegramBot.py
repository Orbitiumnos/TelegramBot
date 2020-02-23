# pip install pytelegrambotapi
# pip install python-telegram-bot


# ПРОВЕРКА СОЕДИНЕНИЯ, НО НУЖНО ПРЕДВАРИТЕЛЬНО ВКЛЮЧИТ VPN
import config2
import currency
import pytz
import json
import traceback
import telebot
import datetime
import os
import logging
from telebot import apihelper
from telebot import types

import pickle
import feedparser
from time import sleep


logger = logging.getLogger('log')
logger.setLevel(logging.INFO)
fh = logging.FileHandler('someTestBot.log')
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s | %(levelname)-7s | %(message)s")
fh.setFormatter(formatter)
logger.addHandler(fh)

PROXY = 'socks5h://geek:socks@t.geekclass.ru:7777' #'socks5h://telegram.vpn99.net:55655' #'socks5://login:pass@12.11.22.33:8000'
apihelper.proxy = {'https': PROXY}
feed_list =["http://baikalinform.ru/obyavki-rss",]
#last_feeds = pickle.load(open(r'C:/Users/Nikolay/Documents/SCRIPTS/Python Scripts/TelegramBot/db.p', 'rb'))
fee_links = []

def check():
    proxies = {'http': 'http://10.10.1.10:3128','https': 'http://10.10.1.10:1080',}
    BASE_URL = 'https://api.telegram.org/bot1055265676:AAEPCH_3nFhyMDUlkK2W9FqDX7bACvtDlVQ/'
    r = requests.get(f'{BASE_URL}getMe', proxies=proxies)
    r.json()
    return
#check()

#TOKEN = '1055265676:AAEPCH_3nFhyMDUlkK2W9FqDX7bACvtDlVQ'
bot = telebot.TeleBot(config2.TOKEN)

# КОД ДЛЯ БОТА

### Функция проверки авторизации

'''
def autor(chatid):
    strid = str(chatid)
    users = ['id-user1','id-user2']
    #for item in users:
        #if item == strid:
    return True
    #return False
'''

### Функция приветствия
@bot.message_handler(commands=['start'])
def start_message(message):
    user_name = message.from_user.first_name
    bot.send_message(message.chat.id,'Привет, ' + user_name + '! Я могу показывать курсы валют!\n' +
    'Чтобы получить курсы валют, нажми кнопку /exchange.\n' +
    'Если нужна помощь, напиши /help.')
    bot.send_sticker(message.chat.id, 'CAADAgAD6CQAAp7OCwABx40TskPHi3MWBA')

### Функция help
@bot.message_handler(commands=['help'])
def help_command(message):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(
        telebot.types.InlineKeyboardButton('Написать разработчику', url='t.me/Orbitiumnos')
    )
    bot.send_message(
        message.chat.id,
        '1) Чтобы получить курс валют нажми на /exchange.\n' +
        '2) Выбери интересующую валюту.\n' +
        '3) Нажми “Обновить” чтобы обновить информацию. \n' +
        '4) Бот поддерживает ссылки. Напиши @OrbiBot в любом чате и наименование валюты.',
        reply_markup=keyboard
    )

### Клавиатура

'''
keyboard1 = telebot.types.ReplyKeyboardMarkup()
keyboard1.row('Привет', 'Пока')


@bot.message_handler(content_types=['text'])
def send_text(message):
    if autor(message.chat.id):
        if message.text == 'Привет':
            bot.send_message(message.chat.id, 'Привет, мой создатель', reply_markup=keyboard1)
        elif message.text == 'Пока':
            bot.send_message(message.chat.id, 'Прощай, создатель', reply_markup=keyboard1)
        elif message.text == 'Пока':
            bot.send_message(message.chat.id, 'Я тебя не понимаю. Напиши /help', reply_markup=keyboard1)
'''


### Прием документов
@bot.message_handler(content_types=['document'])
def handle_docs_photo(message):
    try:
        chat_id = message.chat.id

        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        src = r'C:/Users/Nikolay/Documents/SCRIPTS/Python Script/TelegramBot/' + message.document.file_name;
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)
        bot.reply_to(message, 'Документ сохранен')
    except Exception as e:
        bot.reply_to(message, e)

### Прием фото
@bot.message_handler(content_types=['photo'])
def handle_docs_photo(message):
    try:
        chat_id = message.chat.id
        file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        src = r'C:/Users/Nikolay/Documents/SCRIPTS/Python Scripts/TelegramBot/' + file_info.file_path;
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)
        bot.reply_to(message, "Фото добавлено")
    except Exception as e:
        bot.reply_to(message, e)

@bot.message_handler(commands=['exchange'])
def exchange_command(message):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(
        telebot.types.InlineKeyboardButton('USD', callback_data='get-USD'),
        telebot.types.InlineKeyboardButton('EUR', callback_data='get-EUR'),
        telebot.types.InlineKeyboardButton('RUR', callback_data='get-RUR')
    )
    bot.send_message(
        message.chat.id,
        'Кликни на интересующую валюту:',
        reply_markup=keyboard
    )

@bot.callback_query_handler(func=lambda call: True)
def iq_callback(query):
    data = query.data
    if data.startswith('get-'):
        get_ex_callback(query)

def get_ex_callback(query):
    bot.answer_callback_query(query.id)
    send_exchange_result(query.message, query.data[4:])

def send_exchange_result(message, ex_code):
    bot.send_chat_action(message.chat.id, 'typing')
    ex = currency.get_exchange(ex_code)
    bot.send_message(
        message.chat.id, serialize_ex(ex),
        reply_markup=get_update_keyboard(ex),
	parse_mode='HTML'
    )

def get_update_keyboard(ex):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(
        telebot.types.InlineKeyboardButton(
            'Update',
	    callback_data=json.dumps({
                't': 'u',
		'e': {
                    'b': ex['buy'],
		    's': ex['sale'],
		    'c': ex['ccy']
                }
            }).replace(' ', '')
        ),
	telebot.types.InlineKeyboardButton('Share', switch_inline_query=ex['ccy'])
    )
    return keyboard

def serialize_ex(ex_json, diff=None):
    result = '<b>' + ex_json['base_ccy'] + ' -> ' + ex_json['ccy'] + ':</b>\n\n' + \
             'Buy: ' + ex_json['buy']
    if diff:
        result += ' ' + serialize_exchange_diff(diff['buy_diff']) + '\n' + \
                  'Sell: ' + ex_json['sale'] + \
                  ' ' + serialize_exchange_diff(diff['sale_diff']) + '\n'
    else:
        result += '\nSell: ' + ex_json['sale'] + '\n'
    return result


def serialize_exchange_diff(diff):
    result = ''
    if diff > 0:
        result = '(' + str(diff) + ' <img draggable="false" data-mce-resize="false" data-mce-placeholder="1" data-wp-emoji="1" class="emoji" alt="<img draggable="false" data-mce-resize="false" data-mce-placeholder="1" data-wp-emoji="1" class="emoji" alt="<img draggable="false" data-mce-resize="false" data-mce-placeholder="1" data-wp-emoji="1" class="emoji" alt="<img draggable="false" data-mce-resize="false" data-mce-placeholder="1" data-wp-emoji="1" class="emoji" alt="<img draggable="false" data-mce-resize="false" data-mce-placeholder="1" data-wp-emoji="1" class="emoji" alt="↗️" src="https://s.w.org/images/core/emoji/2.3/svg/2197.svg">" src="https://s.w.org/images/core/emoji/2.3/svg/2197.svg">" src="https://s.w.org/images/core/emoji/2.3/svg/2197.svg">" src="https://s.w.org/images/core/emoji/72x72/2197.png">" src="https://s.w.org/images/core/emoji/72x72/2197.png">)'  
    elif diff < 0:
        result = '(' + str(diff)[1:] + ' <img draggable="false" data-mce-resize="false" data-mce-placeholder="1" data-wp-emoji="1" class="emoji" alt="<img draggable="false" data-mce-resize="false" data-mce-placeholder="1" data-wp-emoji="1" class="emoji" alt="<img draggable="false" data-mce-resize="false" data-mce-placeholder="1" data-wp-emoji="1" class="emoji" alt="<img draggable="false" data-mce-resize="false" data-mce-placeholder="1" data-wp-emoji="1" class="emoji" alt="<img draggable="false" data-mce-resize="false" data-mce-placeholder="1" data-wp-emoji="1" class="emoji" alt="↘️" src="https://s.w.org/images/core/emoji/2.3/svg/2198.svg">" src="https://s.w.org/images/core/emoji/2.3/svg/2198.svg">" src="https://s.w.org/images/core/emoji/2.3/svg/2198.svg">" src="https://s.w.org/images/core/emoji/72x72/2198.png">" src="https://s.w.org/images/core/emoji/72x72/2198.png">)'  
    return result

@bot.callback_query_handler(func=lambda call: True)
def iq_callback(query):
    data = query.data
    if data.startswith('get-'):
        get_ex_callback(query)
    else:
        try:
            if json.loads(data)['t'] == 'u':
                edit_message_callback(query)
        except ValueError:
            pass

def edit_message_callback(query):
    data = json.loads(query.data)['e']
    exchange_now = currency.get_exchange(data['c'])
    text = serialize_ex(
        exchange_now,
	get_exchange_diff(
            get_ex_from_iq_data(data),
	    exchange_now
        )
    ) + '\n' + get_edited_signature()
    if query.message:
        bot.edit_message_text(
            text,
	    query.message.chat.id,
	    query.message.message_id,
	    reply_markup=get_update_keyboard(exchange_now),
	    parse_mode='HTML'
	)
    elif query.inline_message_id:
        bot.edit_message_text(
            text,
	    inline_message_id=query.inline_message_id,
	    reply_markup=get_update_keyboard(exchange_now),
	    parse_mode='HTML'
	)

def get_ex_from_iq_data(exc_json):
    return {
        'buy': exc_json['b'],
	'sale': exc_json['s']
    }

def get_exchange_diff(last, now):
    return {
        'sale_diff': float("%.6f" % (float(now['sale']) - float(last['sale']))),
	'buy_diff': float("%.6f" % (float(now['buy']) - float(last['buy'])))
    }

def get_edited_signature():
    return '<i>Updated ' + \
           str(datetime.datetime.now(P_TIMEZONE).strftime('%H:%M:%S')) + \
           ' (' + TIMEZONE_COMMON_NAME + ')</i>'

@bot.inline_handler(func=lambda query: True)
def query_text(inline_query):
    bot.answer_inline_query(
        inline_query.id,
        get_iq_articles(currency.get_exchanges(inline_query.query))
    )

def get_iq_articles(exchanges):
    result = []
    for exc in exchanges:
        result.append(
            telebot.types.InlineQueryResultArticle(
                id=exc['ccy'],
	        title=exc['ccy'],
	        input_message_content=telebot.types.InputTextMessageContent(
                    serialize_ex(exc),
		    parse_mode='HTML'
		),
	        reply_markup=get_update_keyboard(exc),
	        description='Convert ' + exc['base_ccy'] + ' -> ' + exc['ccy'],
	        thumb_height=1
	    )
        )
    return result

@bot.message_handler(commands=['news'])
def feederek(message):
    for i in feed_list:
        fee = feedparser.parse(i)
        fee_title = fee.feed.title
        for x in range(10):
            fee_links.append(fee['entries'][x]['id'])
            #if fee['entries'][x]['id'] in last_feeds:
            #    pbot.send_message(message.chat.id,"Nothing new - " + fee_title)
            #else:
            sleep(5)
            entry_title = fee['entries'][x]['title']
            entry_id = fee['entries'][x]['id']
            bot.send_message(message.chat.id,"Updated - " + fee_title)

            text = str(entry_title +"\n" + entry_id)
            bot.send_message(message.chat.id, text)

    pickle.dump(fee_links, open("C:/Users/Nikolay/Documents/SCRIPTS/Python Scripts/TelegramBot/db.p", 'wb'))
    return

bot.polling(none_stop=True, interval=0)
#сообщения посылаются методом getupdates. nonestop означает что вопросы будут возвращаться, даже если api возвращает ошибку при выполнении