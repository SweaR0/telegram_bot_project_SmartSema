# импорт нужных модулей
import dotenv
import os
import converter
import models
import telebot
from telebot import types
import wikipedia as wiki
from random import randint, choice
import json
from io import BytesIO
from PIL import Image

BOT_TOKEN = converter.BOT_TOKEN  # токен бота

bot = telebot.TeleBot(BOT_TOKEN)  # создаём переменную, через которую мы будем обращаться к боту

with open('data_mode.json', 'r') as dm_js:  # считываем словарь с данными о режимах пользователей
    data = json.load(dm_js)

# список поддерживаемых валют
list_of_supported_currencies = ['USD', 'AED', 'AFN', 'ALL', 'AMD', 'ANG', 'AOA', 'ARS', 'AUD', 'AWG', 'AZN', 'BAM',
                                'BBD', 'BDT', 'BGN', 'BHD', 'BIF', 'BMD', 'BND', 'BOB', 'BRL', 'BSD', 'BTC', 'BTN',
                                'BWP', 'BYN', 'BZD', 'CAD', 'CDF', 'CHF', 'CLF', 'CLP', 'CNH', 'CNY', 'COP', 'CRC',
                                'CUC', 'CUP', 'CVE', 'CZK', 'DJF', 'DKK', 'DOP', 'DZD', 'EGP', 'ERN', 'ETB', 'EUR',
                                'FJD', 'FKP', 'GBP', 'GEL', 'GGP', 'GHS', 'GIP', 'GMD', 'GNF', 'GTQ', 'GYD', 'HKD',
                                'HNL', 'HRK', 'HTG', 'HUF', 'IDR', 'ILS', 'IMP', 'INR', 'IQD', 'IRR', 'ISK', 'JEP',
                                'JMD', 'JOD', 'JPY', 'KES', 'KGS', 'KHR', 'KMF', 'KPW', 'KRW', 'KWD', 'KYD', 'KZT',
                                'LAK', 'LBP', 'LKR', 'LRD', 'LSL', 'LYD', 'MAD', 'MDL', 'MGA', 'MKD', 'MMK', 'MNT',
                                'MOP', 'MRU', 'MUR', 'MVR', 'MWK', 'MXN', 'MYR', 'MZN', 'NAD', 'NGN', 'NIO', 'NOK',
                                'NPR', 'NZD', 'OMR', 'PAB', 'PEN', 'PGK', 'PHP', 'PKR', 'PLN', 'PYG', 'QAR', 'RON',
                                'RSD', 'RUB', 'RWF', 'SAR', 'SBD', 'SCR', 'SDG', 'SEK', 'SGD', 'SHP', 'SLL', 'SOS',
                                'SRD', 'SSP', 'STD', 'STN', 'SVC', 'SYP', 'SZL', 'THB', 'TJS', 'TMT', 'TND', 'TOP',
                                'TRY', 'TTD', 'TWD', 'TZS', 'UAH', 'UGX', 'UYU', 'UZS', 'VES', 'VND', 'VUV', 'WST',
                                'XAF', 'XAG', 'XAU', 'XCD', 'XDR', 'XOF', 'XPD', 'XPF', 'XPT', 'YER', 'ZAR', 'ZMW',
                                'ZWL']

# список для проверки режимов админа
check_admins_mode = ['Добавить админа', 'Удалить админа', 'Статистика по id', 'Статистика по firstname',
                     'Процентная статистика режимов', 'Самая часто используемая игра', 'Количество пользователей',
                     'Рекордсмены по использованию режимов', 'Информация об администраторах']


@bot.message_handler(commands=['start'])
def start(message):
    '''
    функция приветствия и создания нужных данных для пользователя
    '''
    global data
    if str(message.chat.id) not in data:  # если пользователь зашёл 1 раз, то добавляем его в словрь data
        data[str(message.chat.id)] = {'mode': '',
                                      'pod_mode': '',
                                      'list_for_game_random_number': [],
                                      'list_for_game_random_word': [],
                                      'game_function_check': '',
                                      'wikipedia_assistant': '',
                                      'results_request': [],
                                      'original': 'RUB',
                                      'necessary': 'USD',
                                      'admins_mode': '',
                                      'admins_pod_mode': ''
                                      }
        with open('data_mode.json', 'w') as dm_jss:  # сохраняем обновлённый словарь в json файл
            json.dump(data, dm_jss)

        with models.db:  # сохраняем данные о пользователе в базу данных
            inf = {}
            path = os.path.join(os.path.dirname(__file__), '.env')  # получаем последний id и увеличваем его на 1
            if os.path.exists(path):
                dotenv.load_dotenv(path)
                id = int(os.environ.get('id')) + 1

            dotenv_file = dotenv.find_dotenv()  # меняем значение id в .env
            dotenv.load_dotenv(dotenv_file)
            os.environ["id"] = str(id)
            dotenv.set_key(dotenv_file, "id", os.environ["id"])

            inf['id'] = str(id)
            inf['chat_id'] = message.chat.id
            inf['first_name'] = str(message.from_user.first_name)
            inf['last_name'] = str(message.from_user.last_name)
            inf['username'] = str(message.from_user.username)
            inf['wikipedia'] = '0'
            inf['calculator'] = '0'
            inf['currency_converter'] = '0'
            inf['black_white_photo'] = '0'
            inf['game'] = '0'
            inf['random_number'] = '0'
            inf['random_word'] = '0'
            inf['game_dice'] = '0'
            inf['basketball'] = '0'
            inf['football'] = '0'
            inf['bowling'] = '0'
            inf['darts'] = '0'
            inf['slot_machine'] = '0'
            models.Userinf.insert_many([inf]).execute()  # добавляем информацию о пользователе в бд

    out_mess = f'<b>Привет, {message.from_user.first_name}!</b>\n' + 'Меня зовут Сёма😜\n' +\
               'Для переключения моих режимов, нажимай на соответствующие кнопки, а если что-то не понятно, '\
               + 'то напиши "/help", и я выведу подсказку по использованию 😉'

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)  # создаём кнопки меню
    btn_calculator = types.KeyboardButton('📟Калькулятор📟')  # кнопка режима калькулятора
    btn_game = types.KeyboardButton('🏆Игры🏆')  # кнопка режима игр
    btn_wikipedia = types.KeyboardButton('🌏Википедия🌏')  # кнопка режима википедии
    black_white_photo = types.KeyboardButton('🖤Чёрно-белое фото🤍')  # кнопка режима чёрно белых фото
    currency_converter = types.KeyboardButton('💰Конвертер валют💶')  # кнопка режима конвертора валют
    # добавляем все эти кнопки в кнопки меню
    markup.add(btn_wikipedia, btn_calculator, currency_converter, black_white_photo, btn_game)
    bot.send_message(message.chat.id, out_mess, reply_markup=markup, parse_mode='html')  # вывод приветствия


@bot.message_handler(commands=['help'])
def hint_output(message):
    '''
    функция для отображения подсказки по использованию бота
    '''
    bot.send_message(message.chat.id, 'Для переключения режимов нужно нажимать на соответствующие кнопки! 🙂\n\n' +
                     'В режиме "🌏Википедия🌏" я выдам вам информацию с сайта википедии по вашему запросу с ' +
                     'ссылкой на источник 🥸\n\n' + 'В режиме "📟Калькулятор 📟" я посчитаю ваше арифметическое'+
                     ' выражение 🤓\n\n' + 'В режиме "💰Конвертер валют💶" я переведу заданную сумму денег ' +
                     'в другую валюту 🤑\n\n' + 'В режиме "🖤Черно-белое фото🤍" я вашу фотографию сделаю' +
                     ' чёрно-белой 😝\n\n' + 'В режиме "🏆Игры🏆" я могу отправлять стикеры, выбирать рандомное число' +
                     ' из заданного диапазона и выбирать рандомное слово из заданного списка слов 🤪\n\n' +
                     'Подробная инструкция по использованию каждого режима будет отображаться в самом режиме,' +
                     ' поэтому заходите и пробуйте, у вас всё получится! 😉')


@bot.message_handler(commands=['exit'])
def return_request_input(message):
    '''
    функция для введения запроса заново в режиме википедии
    '''
    global data
    if data[f'{message.chat.id}']['mode'] == '🌏Википедия🌏':
        data[f'{message.chat.id}']['wikipedia_assistant'] = 'запрос'
        data[f'{message.chat.id}']['results_request'] = []
        bot.send_message(message.chat.id, 'Введите запрос 🙃')
    else:
        bot.send_message(message.chat.id, 'Эта команда работает только в режиме википедии 🙃')


@bot.message_handler(commands=['currencies'])
def list_of_currencies(message):
    global list_of_supported_currencies, data
    if data[f'{message.chat.id}']['mode'] == '💰Конвертер валют💶':  # выводим список поддерживающихся валют
        bot.send_message(message.chat.id, f'✅ Поддерживаемые валюты: {", ".join(list_of_supported_currencies)}')
    else:
        bot.send_message(message.chat.id, '❗Эта команда работает только в режиме "💰Конвертер валют💶"❗')


@bot.message_handler(commands=['!enable!admin!mode!'])
def enable_admin_mode(message):
    global data
    try:
        path = os.path.join(os.path.dirname(__file__), '.env')  # получаем список админов и добавляем туда нового
        if os.path.exists(path):
            dotenv.load_dotenv(path)
            admins_list = os.environ.get('admins_list')
    except BaseException:
        bot.send_message(message.chat.id, 'Произошла какая-то ошибка')
    if str(message.chat.id) in admins_list:  # если пользователь админ
        if data[f'{message.chat.id}']['admins_mode'] == 'on':
            data[f'{message.chat.id}']['admins_mode'] = ''
            data[f'{message.chat.id}']['admins_pod_mode'] = ''

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)  # создаём кнопки меню
            btn_calculator = types.KeyboardButton('📟Калькулятор📟')  # кнопка режима калькулятора
            btn_game = types.KeyboardButton('🏆Игры🏆')  # кнопка режима игр
            btn_wikipedia = types.KeyboardButton('🌏Википедия🌏')  # кнопка режима википедии
            black_white_photo = types.KeyboardButton('🖤Чёрно-белое фото🤍')  # кнопка режима чёрно белых фото
            currency_converter = types.KeyboardButton('💰Конвертер валют💶')  # кнопка режима конвертора валют

            # добавляем все эти кнопки в кнопки меню
            markup.add(btn_wikipedia, btn_calculator, currency_converter, black_white_photo, btn_game)

            out_mes = f'<b>Администратор</b> {message.from_user.first_name}, до свидания!'
            bot.send_message(message.chat.id, out_mes, reply_markup=markup, parse_mode='html')

        else:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)  # создаём кнопки меню админов
            add_admin = types.KeyboardButton('Добавить админа')
            del_admin = types.KeyboardButton('Удалить админа')
            st_id = types.KeyboardButton('Статистика по id')
            st_chat_id = types.KeyboardButton('Статистика по чат id')
            st_firstname = types.KeyboardButton('Статистика по firstname')
            st_pr_mode = types.KeyboardButton('Процентная статистика режимов')
            othen_game_use = types.KeyboardButton('Самая часто используемая игра')
            count_users = types.KeyboardButton('Количество пользователей')
            records_users = types.KeyboardButton('Рекордсмены по использованию режимов')
            inf_about_admins = types.KeyboardButton('Информация об администраторах')

            # добавляем все эти кнопки в кнопки меню
            markup.add(st_id, count_users, st_chat_id, st_pr_mode, st_firstname, othen_game_use,
                       inf_about_admins, records_users, add_admin, del_admin)

            data[f'{message.chat.id}']['admins_mode'] = 'on'
            out_mes = f'<b>Администратор</b> {message.from_user.first_name}, здравствуйте!'
            bot.send_message(message.chat.id, out_mes, parse_mode='html', reply_markup=markup)


@bot.message_handler(content_types=['photo'])
def sending_black_white_photo(photo):
    '''
    функция для обработки и отправки фотографий
    '''
    global data
    if data[f'{photo.chat.id}']['mode'] == '🖤Чёрно-белое фото🤍':  # проверка режима
        try:
            photo_file = bot.get_file(photo.photo[-1].file_id)  # достаём картинку
            photo_bytes = bot.download_file(photo_file.file_path)
            flow = BytesIO(photo_bytes)
            image = Image.open(flow).convert("RGB")  # создаём PIL.Image объект из  photo_bytes
            flow.close()
            bl_wi_image = black_white_photo(image)  # получаем чёрно-белое фото
            bot.send_photo(photo.chat.id, photo=bl_wi_image)  # отправляем обработанное фото
            upd = models.Userinf.update({models.Userinf.black_white_photo: models.Userinf.black_white_photo + 1}) \
                .where(models.Userinf.chat_id == photo.chat.id)  # обновляем статистику режима в бд
            upd.execute()
        except BaseException:
            bot.send_message(photo.chat.id, 'Что-то пошло не так, я не смог обработать фото 😞\n' +
                             '✅ Попробуйте отправить другое фото')
    else:
        current_mode = data[f'{photo.chat.id}']['mode']
        bot.send_message(photo.chat.id, f'📌 Я не могу обрабатывать фотографии в режиме "{current_mode}",' +
                         'я умею это делать только в режиме "🖤Чёрно-белое фото🤍"')


@bot.message_handler(content_types=['text'])
def mods_and_their_functionality(message):
    '''
    функция для смены режима бота и вызова функций выполнения этих режимов
    '''
    global data
    if message.text == '🌏Википедия🌏':  # если нажата кнопка "🌏Википедия🌏", то меняем режим на Википедия
        data[f'{message.chat.id}']['mode'] = '🌏Википедия🌏'

    elif message.text == '📟Калькулятор📟':  # если нажата кнопка "📟Калькулятор📟", то меняем режим на Калькулятор
        data[f'{message.chat.id}']['mode'] = '📟Калькулятор📟'

    elif message.text == '💰Конвертер валют💶':  # если нажата кнопка "💰Конвертер валют💶", то меняем на этот режим
        data[f'{message.chat.id}']['mode'] = '💰Конвертер валют💶'

    elif message.text == '🖤Чёрно-белое фото🤍':  # если нажата кнопка "🖤Черно-белое фото🤍", то меняем на этот режим
        data[f'{message.chat.id}']['mode'] = '🖤Чёрно-белое фото🤍'

    elif message.text == '🏆Игры🏆':  # если нажата кнопка "🏆Игры🏆", то меняем режим на Игры
        data[f'{message.chat.id}']['mode'] = '🏆Игры🏆'

    elif data[f'{message.chat.id}']['admins_mode'] == 'on' and message.text == 'Добавить админа':
        try:
            path = os.path.join(os.path.dirname(__file__), '.env')  # получаем список админов и проверяем на главного
            if os.path.exists(path):
                dotenv.load_dotenv(path)
                adm_list = os.environ.get('admins_list').split()
        except BaseException:
            bot.send_message(message.chat.id, 'Не удалось получить список админов')
        if str(message.chat.id) == adm_list[0]:
            data[f'{message.chat.id}']['admins_pod_mode'] = 'Добавить админа'
            bot.send_message(message.chat.id, 'Напишите чат id пользователя, чтобы сделать его администратором')
        else:
            bot.send_message(message.chat.id, 'Доступ к этой функции есть только у главного админа')

    elif data[f'{message.chat.id}']['admins_mode'] == 'on' and message.text == 'Удалить админа':
        try:
            path = os.path.join(os.path.dirname(__file__), '.env')  # получаем список админов и проверяем на главного
            if os.path.exists(path):
                dotenv.load_dotenv(path)
                adm_list = os.environ.get('admins_list').split()
        except BaseException:
            bot.send_message(message.chat.id, 'Не удалось получить список админов')
        if str(message.chat.id) == adm_list[0]:
            data[f'{message.chat.id}']['admins_pod_mode'] = 'Удалить админа'
            bot.send_message(message.chat.id, 'Напишите чат id пользователя, чтобы удалить этого администратора')
        else:
            bot.send_message(message.chat.id, 'Доступ к этой функции есть только у главного админа')

    elif data[f'{message.chat.id}']['admins_mode'] == 'on' and message.text == 'Статистика по id':
        data[f'{message.chat.id}']['admins_pod_mode'] = 'Статистика по id'
        bot.send_message(message.chat.id, 'Введите id для получения информации об этом пользователе')

    elif data[f'{message.chat.id}']['admins_mode'] == 'on' and message.text == 'Статистика по чат id':
        data[f'{message.chat.id}']['admins_pod_mode'] = 'Статистика по чат id'
        bot.send_message(message.chat.id, 'Введите чат id для получения информации об этом пользователе')

    elif data[f'{message.chat.id}']['admins_mode'] == 'on' and message.text == 'Статистика по firstname':
        data[f'{message.chat.id}']['admins_pod_mode'] = 'Статистика по firstname'
        bot.send_message(message.chat.id, 'Введите firstname для получения информации об этом пользователе')

    elif data[f'{message.chat.id}']['admins_mode'] == 'on' and message.text == 'Процентная статистика режимов':
        percentage_statistics_of_modes(message)

    elif data[f'{message.chat.id}']['admins_mode'] == 'on' and message.text == 'Самая часто используемая игра':
        the_most_frequently_used_game(message)

    elif data[f'{message.chat.id}']['admins_mode'] == 'on' and message.text == 'Количество пользователей':
        count_users(message)

    elif data[f'{message.chat.id}']['admins_mode'] == 'on' and message.text == 'Рекордсмены по использованию режимов':
        record_holders_for_the_use_of_modes(message)

    elif data[f'{message.chat.id}']['admins_mode'] == 'on' and message.text == 'Информация об администраторах':
        inf_about_admin(message)

    if data[f'{message.chat.id}']['mode'] == '🌏Википедия🌏':
        if message.text == '🌏Википедия🌏':  # выводим подсказку по режиму и меняем нужную перемнную на "запрос"
            data[f'{message.chat.id}']['wikipedia_assistant'] = 'запрос'
            bot.send_message(message.chat.id, 'Вы включили режим википедии 🌏🤓')
            bot.send_message(message.chat.id, 'Режим 🌏Википедия🌏\n' +
                             'Я могу вывести информацию, взятую из википедии по вашему запросу 🙂\n' +
                             'Введите запрос, а затем выберите нужный вам результат и получите информацию 🧐🥸🤓')
            bot.send_message(message.chat.id, 'Введите запрос 🙃')
        else:
            wiki_reqest(message)

    elif data[f'{message.chat.id}']['mode'] == '📟Калькулятор📟':
        if message.text == '📟Калькулятор📟':  # выводим подсказку по режиму
            bot.send_message(message.chat.id, 'Вы включили режим калькулятора 🙂')
            bot.send_message(message.chat.id, 'Режим 📟Калькулятор 📟\n' + '\n' +
                             'Я могу посчитать числовые выражения 🔢\n' + '\n' +
                             'Используйте следующие арифметические знаки:\n' + 'Сложение - "+"\n' +
                             'Вычитание - "-"\n' + 'Умножение - "*"\n' + 'Деление - "/"\n' +
                             'Целочисленное деление - "//"\n' + 'Остаток от деления - "%"\n' +
                             'Возведение в степень - "**"\n' + '\n' + '📌Подсказка📌\n' +
                             'Чтобы извлечь корень из числа, можно это число возвести в степень 0.5\n' + '\n' +
                             'Также вы можете использовать в выражениях скобки - "(" и ")"\n' + '\n' +
                             '✅Выражение будет посчитано по правилам выполнения арифметических действий✅')
        else:
            calculator(message)  # выполняем функцию калькулятора

    elif data[f'{message.chat.id}']['mode'] == '💰Конвертер валют💶' and data[f'{message.chat.id}']['pod_mode'] == '':
        if message.text == '💰Конвертер валют💶':  # выводим подсказку по режиму
            currency_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)  # создаём кнопки режима
            # кнопка для выбора исходной валюты
            source_currency = types.KeyboardButton(data[f'{message.chat.id}']['original'])
            btn_arrow = types.KeyboardButton('→')  # кнопка стрелочки
            # кнопка для выбора валюты, в которую надо перевести
            converted_currency = types.KeyboardButton(data[f'{message.chat.id}']['necessary'])
            btn_back = types.KeyboardButton('🔙Назад🔙') # кнопка выхода из режима конвертора валют
            # добавляем все эти кнопки в кнопки режима ковертора валют
            currency_markup.add(source_currency, btn_arrow, converted_currency, btn_back)  # добавляем все кнопки
            bot.send_message(message.chat.id, 'Вы включили режим конвертора валют 💸', reply_markup=currency_markup)
            bot.send_message(message.chat.id, 'Выберите исходную валюту и валюту, в которую нужно перевести 💵\n' +
                             'Затем отправьте сообщение с денежной суммой исходной валюты для перевода,' +
                             ' и я вам её переведу 💰\n' + '📌 Чтобы узнать список поддерживаемых валют, ' +
                             'напишите "/currencies"')
        elif message.text == data[f'{message.chat.id}']['original']:  # меняем под режим на нужный
            data[f'{message.chat.id}']['pod_mode'] = 'начальная'
        elif message.text == data[f'{message.chat.id}']['necessary']:  # меняем под режим на нужный
            data[f'{message.chat.id}']['pod_mode'] = 'нужная'
        else:
            currency_transfer(message)  # выполняем перевод валют

    elif data[f'{message.chat.id}']['mode'] == '🖤Чёрно-белое фото🤍':
        if message.text == '🖤Чёрно-белое фото🤍':  # выводим подсказку по режиму
            bot.send_message(message.chat.id, 'Вы включили режим чёрно-белых фото 🖤🤍')
            bot.send_message(message.chat.id, 'Просто отправьте мне фото, а я вам сделаю его чёрно-белым 😜')
        else:
            bot.send_message(message.chat.id, 'Тут я ничего не могу вам ответить 🙁\n' +
                             '✅ Просто отправьте мне фотографию, и я сделаю её чёрно-белой')

    elif data[f'{message.chat.id}']['mode'] == '🏆Игры🏆' and data[f'{message.chat.id}']['pod_mode'] == '':
        if message.text == '🏆Игры🏆':  # меняем меню кнопок и выводим подсказку о том, что режим игр включён
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
            btn_random_number = types.KeyboardButton('🔢Рандомное число🔢')
            btn_random_word = types.KeyboardButton('✏Рандомное слово🗒')
            btn_dice = types.KeyboardButton('🎲Игровые кости🎲')
            btn_basketball = types.KeyboardButton('🏀Баскетбол🏀')
            btn_football = types.KeyboardButton('⚽Футбол⚽')
            btn_bowling = types.KeyboardButton('🎳Боулинг🎳')
            btn_darts = types.KeyboardButton('🎯Дартс🎯')
            btn_slot_machine = types.KeyboardButton('🎰Игровой автомат🎰')
            btn_back = types.KeyboardButton('🔙Назад🔙')
            markup.add(btn_random_number, btn_random_word, btn_dice, btn_basketball, btn_football, btn_bowling,
                       btn_darts, btn_slot_machine, btn_back)
            bot.send_message(message.chat.id, 'Вы включили режим игр 🙂', reply_markup=markup)
        elif message.text == '🔢Рандомное число🔢':  # меняем под режим на "🔢Рандомное число🔢"
            data[f'{message.chat.id}']['pod_mode'] = '🔢Рандомное число🔢'
        elif message.text == '✏Рандомное слово🗒':  # меняем под режим на "✏Рандомное слово🗒"
            data[f'{message.chat.id}']['pod_mode'] = '✏Рандомное слово🗒'
        else:
            games(message)  # выполняем функцию игр

    if data[f'{message.chat.id}']['mode'] == '💰Конвертер валют💶' and\
            data[f'{message.chat.id}']['pod_mode'] == 'начальная':
        changing_the_initial_currency(message)  # меняем начальную валюту, из которой надо переводить

    elif data[f'{message.chat.id}']['mode'] == '💰Конвертер валют💶' and\
            data[f'{message.chat.id}']['pod_mode'] == 'нужная':
        changing_the_desired_currency(message)  # меняем нужную валюту, в которую нужно перевести

    elif data[f'{message.chat.id}']['mode'] == '🏆Игры🏆' and\
            data[f'{message.chat.id}']['pod_mode'] == '🔢Рандомное число🔢':
        random_number(message)  # выполняем функцию игры "Рандомное число"

    elif data[f'{message.chat.id}']['mode'] == '🏆Игры🏆' and\
            data[f'{message.chat.id}']['pod_mode'] == '✏Рандомное слово🗒':
        random_word(message)  # выполняем функцию игры "Рандомное слово"

    if data[f'{message.chat.id}']['admins_pod_mode'] == 'Добавить админа' and message.text != 'Добавить админа':
        add_admin(message)

    elif data[f'{message.chat.id}']['admins_pod_mode'] == 'Удалить админа' and message.text != 'Удалить админа':
        del_admin(message)

    elif data[f'{message.chat.id}']['admins_pod_mode'] == 'Статистика по id' and message.text != 'Статистика по id':
        output_of_user_statistics(message, 'id')

    elif data[f'{message.chat.id}']['admins_pod_mode'] == 'Статистика по чат id' and\
            message.text != 'Статистика по чат id':
        output_of_user_statistics(message, 'chat_id')

    elif data[f'{message.chat.id}']['admins_pod_mode'] == 'Статистика по firstname' and\
            message.text != 'Статистика по firstname':
        output_of_user_statistics(message, 'first_name')

    with open('data_mode.json', 'w') as dm_jss:  # сохраняем запись словаря с данными режимов пользователей в json файл
        json.dump(data, dm_jss)


def percentage_statistics_of_modes(message):
    '''
    функция для вывода проентной статистики режимов
    '''
    global data
    data[f'{message.chat.id}']['admins_pod_mode'] = ''
    try:  # получаем общее количество использований режимов и выводим их в процентной статистике
        wikipedia = 0
        calculator = 0
        currency_converter = 0
        black_white_photo = 0
        game = 0
        path = os.path.join(os.path.dirname(__file__), '.env')  # получаем последний id
        if os.path.exists(path):
            dotenv.load_dotenv(path)
            id = int(os.environ.get('id'))
        for i in range(1, id + 1):  # собираем всю информацию о режимах пользователя
            data_user = models.Userinf.get(models.Userinf.id == str(i))
            wikipedia += data_user.wikipedia
            calculator += data_user.calculator
            currency_converter += data_user.currency_converter
            black_white_photo += data_user.black_white_photo
            game += data_user.game
        all = wikipedia + calculator + currency_converter + black_white_photo + game
        bot.send_message(message.chat.id, f'<b>Википедия</b> ({wikipedia * 100 // all}%) - {wikipedia}\n' +
                         f'<b>Калькулятор</b> ({calculator * 100 // all}%) - {calculator}\n' +
                         f'<b>Конвертер валют</b> ({currency_converter * 100 // all}%) - {currency_converter}\n' +
                         f'<b>Чёрно-белое фото</b> ({black_white_photo * 100 // all}%) - {black_white_photo}\n' +
                         f'<b>Игры</b> ({game * 100 // all}%) - {game}\n\n' + f'Всего: {all}', parse_mode='html')
    except BaseException:
        bot.send_message(message.chat.id, 'Случилась какая-то ошибка')


def the_most_frequently_used_game(message):
    '''
    функция для вывода статистики по самой часто используемой игре
    '''
    global data
    data[f'{message.chat.id}']['admins_pod_mode'] = ''
    try:  # получаем общее количество использований всех игр и выводим их в процентной статистике
        random_number = 0
        random_word = 0
        game_dice = 0
        basketball = 0
        football = 0
        bowling = 0
        darts = 0
        slot_machine = 0
        path = os.path.join(os.path.dirname(__file__), '.env')  # получаем последний id
        if os.path.exists(path):
            dotenv.load_dotenv(path)
            id = int(os.environ.get('id'))
        for i in range(1, id + 1):  # собираем всю информацию о играх пользователя
            data_user = models.Userinf.get(models.Userinf.id == str(i))
            random_number += data_user.random_number
            random_word += data_user.random_word
            game_dice += data_user.game_dice
            basketball += data_user.basketball
            football += data_user.football
            bowling += data_user.bowling
            darts += data_user.darts
            slot_machine += data_user.slot_machine
        all = random_number + random_word + game_dice + basketball + football + bowling + darts + slot_machine
        bot.send_message(message.chat.id, f'<b>Рандомное число</b> ({random_number * 100 // all}%) - ' +
                         f'{random_number}\n' +
                         f'<b>Рандомное слово</b> ({random_word * 100 // all}%) - {random_word}\n' +
                         f'<b>Игровые кости</b> ({game_dice * 100 // all}%) - {game_dice}\n' +
                         f'<b>Баскетбол</b> ({basketball * 100 // all}%) - {basketball}\n' +
                         f'<b>Футбол</b> ({football * 100 // all}%) - {football}\n' +
                         f'<b>Боулинг</b> ({bowling * 100 // all}%) - {bowling}\n' +
                         f'<b>Дартс</b> ({darts * 100 // all}%) - {darts}\n' +
                         f'<b>Игровой автомат</b> ({slot_machine * 100 // all}%) - {slot_machine}\n\n' +
                         f'Всего: {all}', parse_mode='html')
    except BaseException:
        bot.send_message(message.chat.id, 'Случилась какая-то ошибка')


def record_holders_for_the_use_of_modes(message):
    '''
    функция для вывода статистики о рекордсменах по использованию режимов
    '''
    global data
    data[f'{message.chat.id}']['admins_pod_mode'] = ''
    result = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    try:  # получаем общее количество использований всех режимов и выводим их пользователей с наибольшим показателем
        path = os.path.join(os.path.dirname(__file__), '.env')  # получаем последний id
        if os.path.exists(path):
            dotenv.load_dotenv(path)
            id = int(os.environ.get('id'))
        for i in range(1, id + 1):  # собираем всю информацию о режимах пользователя
            data_user = models.Userinf.get(models.Userinf.id == str(i))
            if data_user.wikipedia > result[0]:
                result[0] = data_user.wikipedia
            if data_user.calculator > result[1]:
                result[1] = data_user.calculator
            if data_user.currency_converter > result[2]:
                result[2] = data_user.currency_converter
            if data_user.black_white_photo > result[3]:
                result[3] = data_user.black_white_photo
            if data_user.game > result[4]:
                result[4] = data_user.game
            if data_user.random_number > result[5]:
                result[5] = data_user.random_number
            if data_user.random_word > result[6]:
                result[6] = data_user.random_word
            if data_user.game_dice > result[7]:
                result[7] = data_user.game_dice
            if data_user.basketball > result[8]:
                result[8] = data_user.basketball
            if data_user.football > result[9]:
                result[9] = data_user.football
            if data_user.bowling > result[10]:
                result[10] = data_user.bowling
            if data_user.darts > result[11]:
                result[11] = data_user.darts
            if data_user.slot_machine > result[12]:
                result[12] = data_user.slot_machine
        wiki_rh = models.Userinf.get(models.Userinf.wikipedia == result[0])
        cal_rh = models.Userinf.get(models.Userinf.calculator == result[1])
        cc_rh = models.Userinf.get(models.Userinf.currency_converter == result[2])
        bwp_rh = models.Userinf.get(models.Userinf.black_white_photo == result[3])
        g_rh = models.Userinf.get(models.Userinf.game == result[4])
        rn_rh = models.Userinf.get(models.Userinf.random_number == result[5])
        rw_rh = models.Userinf.get(models.Userinf.random_word == result[6])
        gd_rh = models.Userinf.get(models.Userinf.game_dice == result[7])
        bas_rh = models.Userinf.get(models.Userinf.basketball == result[8])
        f_rh = models.Userinf.get(models.Userinf.football == result[9])
        bow_rh = models.Userinf.get(models.Userinf.bowling == result[10])
        dar_rh = models.Userinf.get(models.Userinf.darts == result[11])
        slm_rh = models.Userinf.get(models.Userinf.slot_machine == result[12])
        bot.send_message(message.chat.id, f'<b>Википедия</b> ({result[0]}) -\n' +
                         f'{wiki_rh.id} {wiki_rh.first_name} {wiki_rh.last_name} {wiki_rh.username}\n\n' +
                         f'<b>Калькулятор</b> ({result[1]}) -\n' +
                         f'{cal_rh.id} {cal_rh.first_name} {cal_rh.last_name} {cal_rh.username}\n\n' +
                         f'<b>Конвертер валют</b> ({result[2]}) -\n' +
                         f'{cc_rh.id} {cc_rh.first_name} {cc_rh.last_name} {cc_rh.username}\n\n' +
                         f'<b>Чёрно-белое фото</b> ({result[3]}) -\n' +
                         f'{bwp_rh.id} {bwp_rh.first_name} {bwp_rh.last_name} {bwp_rh.username}\n\n' +
                         f'<b>Игры</b> ({result[4]}) -\n' +
                         f'{g_rh.id} {g_rh.first_name} {g_rh.last_name} {g_rh.username}\n\n' +
                         f'<b>Рандомное число</b> ({result[5]}) -\n' +
                         f'{rn_rh.id} {rn_rh.first_name} {rn_rh.last_name} {rn_rh.username}\n\n' +
                         f'<b>Рандомное словоо</b> ({result[6]}) -\n' +
                         f'{rw_rh.id} {rw_rh.first_name} {rw_rh.last_name} {rw_rh.username}\n\n' +
                         f'<b>Игровые кости</b> ({result[7]}) -\n' +
                         f'{gd_rh.id} {gd_rh.first_name} {gd_rh.last_name} {gd_rh.username}\n\n' +
                         f'<b>Баскетбол</b> ({result[8]}) -\n' +
                         f'{bas_rh.id} {bas_rh.first_name} {bas_rh.last_name} {bas_rh.username}\n\n' +
                         f'<b>Футбол</b> ({result[9]}) -\n' +
                         f'{f_rh.id} {f_rh.first_name} {f_rh.last_name} {f_rh.username}\n\n' +
                         f'<b>Боулинг</b> ({result[10]}) -\n' +
                         f'{bow_rh.id} {bow_rh.first_name} {bow_rh.last_name} {bow_rh.username}\n\n' +
                         f'<b>Дартс</b> ({result[11]}) -\n' +
                         f'{dar_rh.id} {dar_rh.first_name} {dar_rh.last_name} {dar_rh.username}\n\n' +
                         f'<b>Игровой автомат</b> ({result[12]}) -\n' +
                         f'{slm_rh.id} {slm_rh.first_name} {slm_rh.last_name} {slm_rh.username}', parse_mode='html')
    except BaseException:
        bot.send_message(message.chat.id, 'Случилась какая-то ошибка')


def count_users(message):
    '''
    функция для вывода количества пользователей, которые использовали бота
    '''
    global data
    data[f'{message.chat.id}']['admins_pod_mode'] = ''
    try:
        path = os.path.join(os.path.dirname(__file__), '.env')  # получаем последний id
        if os.path.exists(path):
            dotenv.load_dotenv(path)
            bot.send_message(message.chat.id, f'Общее количество пользователей:\n<b>{os.environ.get("id")}</b>',
                             parse_mode='html')
    except BaseException:
        bot.send_message(message.chat.id, 'Случилась какая-то ошибка')


def output_of_user_statistics(message, key):
    '''
    функция для вывода статистики пользователя по ключу key (first_name, id, chat_id)
    '''
    global check_admins_mode
    if message.text not in check_admins_mode:
        try:
            with models.db:  # подключение к бд
                if key == 'id':
                    data_user = models.Userinf.get(models.Userinf.id == message.text)
                elif key == 'chat_id':
                    data_user = models.Userinf.get(models.Userinf.chat_id == message.text)
                elif key == 'first_name':
                    data_user = models.Userinf.get(models.Userinf.first_name == message.text)
            bot.send_message(message.chat.id, f'<b>id</b>: {data_user.id}\n' +
                             f'<b>chat_id</b>: {data_user.chat_id}\n' +
                             f'<b>first_name</b>: {data_user.first_name}\n' +
                             f'<b>last_name</b>: {data_user.last_name}\n' +
                             f'<b>username</b>: {data_user.username}\n' + f'<b>wikipedia</b>: {data_user.wikipedia}\n' +
                             f'<b>calculator</b>: {data_user.calculator}\n' +
                             f'<b>currency_converter</b>: {data_user.currency_converter}\n' +
                             f'<b>black_white_photo</b>: {data_user.black_white_photo}\n' +
                             f'<b>game</b>: {data_user.game}\n' +
                             f'<b>random_number</b>: {data_user.random_number}\n' +
                             f'<b>random_word</b>: {data_user.random_word}\n' +
                             f'<b>game_dice</b>: {data_user.game_dice}\n' +
                             f'<b>basketball</b>: {data_user.basketball}\n' +
                             f'<b>football</b>: {data_user.football}\n' + f'<b>bowling</b>: {data_user.bowling}\n' +
                             f'<b>darts</b>: {data_user.darts}\n' + f'<b>slot_machine</b>: {data_user.slot_machine}\n',
                             parse_mode='html')
        except BaseException:
            bot.send_message(message.chat.id, 'Случилась какая-то ошибка')


def inf_about_admin(message):
    '''
    функция для вывода информации об администраторах
    '''
    global data
    data[f'{message.chat.id}']['admins_pod_mode'] = ''
    try:
        path = os.path.join(os.path.dirname(__file__), '.env')  # получаем список админов и выводим о них информацию
        if os.path.exists(path):
            dotenv.load_dotenv(path)
            adm_list = os.environ.get('admins_list').split()
        for chat_id in adm_list:
            with models.db:  # подключение к бд
                data_admin = models.Userinf.get(models.Userinf.chat_id == chat_id)
            if chat_id == adm_list[0]:
                bot.send_message(message.chat.id, f'<b>ГЛАВНЫЙ администратор</b> (id = {data_admin.id})\n' +
                                 f'{data_admin.first_name} {data_admin.last_name} {data_admin.username}',
                                 parse_mode='html')
            else:
                bot.send_message(message.chat.id, f'<b>Администратор</b> (id = {data_admin.id}, ' +
                                 f'chat_id = {data_admin.chat_id})\n' +
                                 f'{data_admin.first_name} {data_admin.last_name} {data_admin.username}',
                                 parse_mode='html')
    except BaseException:
        bot.send_message(message.chat.id, f'Случилась какая-то ошибка')


def del_admin(message):
    '''
    функция для удаления админов
    '''
    global check_admins_mode
    if message.text not in check_admins_mode:
        try:
            path = os.path.join(os.path.dirname(__file__), '.env')  # получаем список админов и добавляем туда нового
            if os.path.exists(path):
                dotenv.load_dotenv(path)
                adm_list = os.environ.get('admins_list').split()
                adm_list.remove(message.text)
                admins_list = ' '.join(adm_list)
            dotenv_file = dotenv.find_dotenv()
            dotenv.load_dotenv(dotenv_file)
            os.environ["admins_list"] = admins_list
            dotenv.set_key(dotenv_file, "admins_list", os.environ["admins_list"])
            bot.send_message(message.chat.id, f'Пользователь "{message.text}" удалён из администраторов')
        except BaseException:
            bot.send_message(message.chat.id, f'Что-то пошло не так, возможно пользователя "{message.text}" нет ' +
                             'в списках администраторов')


def add_admin(message):
    '''
    функция для добавления админов
    '''
    global check_admins_mode
    if message.text not in check_admins_mode:
        try:
            path = os.path.join(os.path.dirname(__file__), '.env')  # получаем список админов и добавляем туда нового
            if os.path.exists(path):
                dotenv.load_dotenv(path)
                admins_list = os.environ.get('admins_list') + f' {message.text}'
            dotenv_file = dotenv.find_dotenv()
            dotenv.load_dotenv(dotenv_file)
            os.environ["admins_list"] = admins_list
            dotenv.set_key(dotenv_file, "admins_list", os.environ["admins_list"])
            bot.send_message(message.chat.id, f'Пользователь "{message.text}" сделан администратором успешно!')
        except BaseException:
            bot.send_message(message.chat.id, f'Произошла какая-то ошибка')


def wiki_reqest(req):
    '''
    функция для выполнения режима википедии
    '''
    global data
    wiki.set_lang('ru')  # устанавливаем русский язык для ответов
    if data[f'{req.chat.id}']['wikipedia_assistant'] == 'запрос':
        try:  # ищём результаты запроса и выводим их пользователю для выбоа
            search_result = wiki.search(req.text, results=5)
            data[f'{req.chat.id}']['results_request'] = search_result
            bot.send_message(req.chat.id, 'Вот что я нашёл по вашему запросу🤓\n' + f'1) {search_result[0]}\n' +
                             f'2) {search_result[1]}\n' + f'3) {search_result[2]}\n' + f'4) {search_result[3]}\n' +
                             f'5) {search_result[4]}\n' + '\n' +
                             'Введите цифру нужного результата, и я вам выдам об этом информацию 🥸\n' + '\n'
                             '✅ Чтобы заново ввести запрос, введите "/exit"')
            data[f'{req.chat.id}']['wikipedia_assistant'] = 'выбор'
        except BaseException:
            bot.send_message(req.chat.id, f'К сожалению, я ничего не нашёл по запросу: "{req.text}" ☹\n' +
                             '❗Попробуйте ввести более корректный запрос❗')
    elif data[f'{req.chat.id}']['wikipedia_assistant'] == 'выбор':
        try:
            index = int(req.text)
            if 1 <= index <= 5:  # вывод результата
                try:
                    answer = wiki.summary(data[f'{req.chat.id}']['results_request'][index - 1])
                    markup_link = types.InlineKeyboardMarkup()  # кнопка с ссылкой на википедию
                    link = 'https://ru.wikipedia.org/wiki/' + data[f'{req.chat.id}']['results_request'][index - 1]
                    url_button = types.InlineKeyboardButton(text='Открыть в википедии', url=link)
                    markup_link.add(url_button)
                    bot.send_message(req.chat.id, answer, reply_markup=markup_link)
                    bot.send_message(req.chat.id, 'Введите запрос 🙃')
                    data[f'{req.chat.id}']['results_request'] = []
                    data[f'{req.chat.id}']['wikipedia_assistant'] = 'запрос'
                    upd = models.Userinf.update({models.Userinf.wikipedia: models.Userinf.wikipedia + 1}) \
                        .where(models.Userinf.chat_id == req.chat.id)  # обновляем статистику режима в бд
                    upd.execute()
                except BaseException:
                    bot.send_message(req.chat.id, 'К сожалению, по вашему выбранному результату я ничего не нашёл ☹' +
                                     '✅ Попробуйте выбрать другую цифру')
            else:
                bot.send_message(req.chat.id, '❗Неверный формат ввода❗\n' +
                                 'Нужно ввести цифру от 1 до 5 в зависимости от нужного вам результата 🥸')
        except BaseException:
            bot.send_message(req.chat. id, '❗Неверный формат ввода❗\n' +
                             'Нужно ввести цифру от 1 до 5 в зависимости от нужного вам результата 🥸')


def calculator(expression):
    '''
    функция для выполнения режима калькулятора
    '''
    try:
        bot.send_message(expression.chat.id, eval(expression.text))
        upd = models.Userinf.update({models.Userinf.calculator: models.Userinf.calculator + 1}) \
            .where(models.Userinf.chat_id == expression.chat.id)  # обновляем статистику режима в бд
        upd.execute()
    except ZeroDivisionError:
        bot.send_message(expression.chat.id, '‼На ноль делить нельзя‼')
    except BaseException:
        bot.send_message(expression.chat.id, 'Я не могу посчитать такое 😕\n' + '‼Неверный формат ввода‼')


def currency_transfer(money):
    '''
    функция для перевода валют
    '''
    global data
    if money.text == '🔙Назад🔙':  # выходим из режима конвертора валют
        data[f'{money.chat.id}']['mode'] = ''  # меняем режим на ''
        data[f'{money.chat.id}']['pod_mode'] = ''  # меняем под режим на ''
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)  # возвращаем кнопки выбора режимов
        btn_calculator = types.KeyboardButton('📟Калькулятор📟')
        btn_game = types.KeyboardButton('🏆Игры🏆')
        btn_wikipedia = types.KeyboardButton('🌏Википедия🌏')
        black_white_photo = types.KeyboardButton('🖤Чёрно-белое фото🤍')
        currency_converter = types.KeyboardButton('💰Конвертер валют💶')
        markup.add(btn_wikipedia, btn_calculator, currency_converter, black_white_photo, btn_game)
        bot.send_message(money.chat.id, 'Режим конвертора валют выключен 🤑', reply_markup=markup)
    else:  # переводим валюты
        try:
            currency_list = converter.latest_rate()
            if data[f'{money.chat.id}']['original'] == 'USD':
                res_money = int(money.text) * currency_list[data[f'{money.chat.id}']['necessary']]
                bot.send_message(money.chat.id, res_money)
                upd = models.Userinf.update({models.Userinf.currency_converter: models.Userinf.currency_converter + 1})\
                    .where(models.Userinf.chat_id == money.chat.id)  # обновляем статистику режима в бд
                upd.execute()
            else:
                in_usd = int(money.text) / currency_list[data[f'{money.chat.id}']['original']]
                res_money = in_usd * currency_list[data[f'{money.chat.id}']['necessary']]
                bot.send_message(money.chat.id, res_money)
                upd = models.Userinf.update({models.Userinf.currency_converter: models.Userinf.currency_converter + 1})\
                    .where(models.Userinf.chat_id == money.chat.id)  # обновляем статистику режима в бд
                upd.execute()
        except BaseException:
            bot.send_message(money.chat.id, 'Что-то пошло не так ☹\n' +
                             'Возможно превышен лимит запросов на перевод валют или некорректно введена сумма❗\n' +
                             '✅ Попробуйте ввести другую сумму или попробуйте перевести позже 💰')


def changing_the_initial_currency(currency):
    '''
    функция для смены начальной валюты, из которой нужно переводить
    '''
    global list_of_supported_currencies, data
    if currency.text == data[f'{currency.chat.id}']['original']:
        bot.send_message(currency.chat.id, f'Ваша текущая валюта, из которой нужно осуществить перевод: "' +
                         data[f'{currency.chat.id}']['original'] + '"\n' +
                         '✅ Чтобы изменить её, напишите нужную вам валюту\n' + '\n' +
                         '📌 Чтобы узнать список поддерживаемых валют, напишите "/currencies"')
    elif currency.text == '🔙Назад🔙':  # выходим из режима конвертора валют
        data[f'{currency.chat.id}']['mode'] = ''  # меняем режим на ''
        data[f'{currency.chat.id}']['pod_mode'] = ''  # меняем под режим на ''
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)  # возвращаем кнопки выбора режимов
        btn_calculator = types.KeyboardButton('📟Калькулятор📟')
        btn_game = types.KeyboardButton('🏆Игры🏆')
        btn_wikipedia = types.KeyboardButton('🌏Википедия🌏')
        black_white_photo = types.KeyboardButton('🖤Чёрно-белое фото🤍')
        currency_converter = types.KeyboardButton('💰Конвертер валют💶')
        markup.add(btn_wikipedia, btn_calculator, currency_converter, black_white_photo, btn_game)
        bot.send_message(currency.chat.id, 'Режим конвертора валют выключен 🤑', reply_markup=markup)
    else:
        if currency.text.upper() in list_of_supported_currencies:
            data[f'{currency.chat.id}']['original'] = currency.text.upper()
            currency_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)  # создаём кнопки режима
            # кнопка для выбора исходной валюты
            source_currency = types.KeyboardButton(data[f'{currency.chat.id}']['original'])
            btn_arrow = types.KeyboardButton('→')  # кнопка стрелочки
            # кнопка для выбора валюты, в которую надо перевести
            converted_currency = types.KeyboardButton(data[f'{currency.chat.id}']['necessary'])
            btn_back = types.KeyboardButton('🔙Назад🔙')  # кнопка выхода из режима конвертора валют
            # добавляем все эти кнопки в кнопки режима ковертора валют
            currency_markup.add(source_currency, btn_arrow, converted_currency, btn_back)  # добавляем все кнопки
            bot.send_message(currency.chat.id, '✅ Валюта изменена успешно',reply_markup=currency_markup)
            data[f'{currency.chat.id}']['pod_mode'] = ''
        else:
            bot.send_message(currency.chat.id, 'К сожалению, такой валюты нету ☹\n' + '✅ Попробуйте ввести ещё раз')


def changing_the_desired_currency(currency):
    '''
    функция для смены нужной валюты, в которую нужно переводить
    '''
    global list_of_supported_currencies, data
    if currency.text == data[f'{currency.chat.id}']['necessary']:
        bot.send_message(currency.chat.id, f'Ваша текущая валюта, в которую нужно осуществить перевод: "' +
                         data[f'{currency.chat.id}']['necessary'] + '"\n' +
                         '✅ Чтобы изменить её, напишите нужную вам валюту\n' + '\n' +
                         '📌 Чтобы узнать список поддерживаемых валют, напишите "/currencies"')
    elif currency.text == '🔙Назад🔙':  # выходим из режима конвертора валют
        data[f'{currency.chat.id}']['mode'] = ''  # меняем режим на ''
        data[f'{currency.chat.id}']['pod_mode'] = ''  # меняем под режим на ''
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)  # возвращаем кнопки выбора режимов
        btn_calculator = types.KeyboardButton('📟Калькулятор📟')
        btn_game = types.KeyboardButton('🏆Игры🏆')
        btn_wikipedia = types.KeyboardButton('🌏Википедия🌏')
        black_white_photo = types.KeyboardButton('🖤Чёрно-белое фото🤍')
        currency_converter = types.KeyboardButton('💰Конвертер валют💶')
        markup.add(btn_wikipedia, btn_calculator, currency_converter, black_white_photo, btn_game)
        bot.send_message(currency.chat.id, 'Режим конвертора валют выключен 🤑', reply_markup=markup)
    else:
        if currency.text.upper() in list_of_supported_currencies:
            data[f'{currency.chat.id}']['necessary'] = currency.text.upper()
            currency_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)  # создаём кнопки режима
            # кнопка для выбора исходной валюты
            source_currency = types.KeyboardButton(data[f'{currency.chat.id}']['original'])
            btn_arrow = types.KeyboardButton('→')  # кнопка стрелочки
            # кнопка для выбора валюты, в которую надо перевести
            converted_currency = types.KeyboardButton(data[f'{currency.chat.id}']['necessary'])
            btn_back = types.KeyboardButton('🔙Назад🔙')  # кнопка выхода из режима конвертора валют
            # добавляем все эти кнопки в кнопки режима ковертора валют
            currency_markup.add(source_currency, btn_arrow, converted_currency, btn_back)  # добавляем все кнопки
            bot.send_message(currency.chat.id, '✅ Валюта изменена успешно', reply_markup=currency_markup)
            data[f'{currency.chat.id}']['pod_mode'] = ''
        else:
            bot.send_message(currency.chat.id, 'К сожалению, такой валюты нету ☹\n' + '✅ Попробуйте ввести ещё раз')


def black_white_photo(image):
    '''
    функция для создания чёрно-белого фото
    '''
    pixels = image.load()  # список с пикселями
    x, y = image.size  # ширина (x) и высота (y) изображения
    for i in range(x):  # делаем фото чёрно-белым
        for j in range(y):
            r, g, b = pixels[i, j]
            bw = (r + g + b) // 3
            pixels[i, j] = bw, bw, bw
    return image  # возвращаем чёрно-белое фото


def games(name_of_the_game):
    '''
    функция для выполнения режиа игр
    '''
    global data
    if name_of_the_game.text == '🔙Назад🔙':
        data[f'{name_of_the_game.chat.id}']['mode'] = ''  # меняем режим на ''
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)  # возвращаем кнопки выбора режимов
        btn_calculator = types.KeyboardButton('📟Калькулятор📟')
        btn_game = types.KeyboardButton('🏆Игры🏆')
        btn_wikipedia = types.KeyboardButton('🌏Википедия🌏')
        black_white_photo = types.KeyboardButton('🖤Чёрно-белое фото🤍')
        currency_converter = types.KeyboardButton('💰Конвертер валют💶')
        markup.add(btn_wikipedia, btn_calculator, currency_converter, black_white_photo, btn_game)
        bot.send_message(name_of_the_game.chat.id, 'Режим игр выключен 🤪', reply_markup=markup)
    elif name_of_the_game.text == '🎲Игровые кости🎲': # отправляем эмоджи "Игровые кости"
        bot.send_dice(name_of_the_game.chat.id, '🎲')

        upd = models.Userinf.update({models.Userinf.game: models.Userinf.game + 1}) \
            .where(models.Userinf.chat_id == name_of_the_game.chat.id)  # обновляем статистику режима в бд
        upd.execute()

        upd = models.Userinf.update({models.Userinf.game_dice: models.Userinf.game_dice + 1}) \
            .where(models.Userinf.chat_id == name_of_the_game.chat.id)  # обновляем статистику режима в бд
        upd.execute()
    elif name_of_the_game.text == '🏀Баскетбол🏀':  # отправляем эмоджи "Баскетбол"
        bot.send_dice(name_of_the_game.chat.id, '🏀')

        upd = models.Userinf.update({models.Userinf.game: models.Userinf.game + 1}) \
            .where(models.Userinf.chat_id == name_of_the_game.chat.id)  # обновляем статистику режима в бд
        upd.execute()

        upd = models.Userinf.update({models.Userinf.basketball: models.Userinf.basketball + 1}) \
            .where(models.Userinf.chat_id == name_of_the_game.chat.id)  # обновляем статистику режима в бд
        upd.execute()

    elif name_of_the_game.text == '⚽Футбол⚽':  # отправляем эмоджи "Футбол"
        bot.send_dice(name_of_the_game.chat.id, '⚽')

        upd = models.Userinf.update({models.Userinf.game: models.Userinf.game + 1}) \
            .where(models.Userinf.chat_id == name_of_the_game.chat.id)  # обновляем статистику режима в бд
        upd.execute()

        upd = models.Userinf.update({models.Userinf.football: models.Userinf.football + 1}) \
            .where(models.Userinf.chat_id == name_of_the_game.chat.id)  # обновляем статистику режима в бд
        upd.execute()

    elif name_of_the_game.text == '🎳Боулинг🎳':  # отправляем эмоджи "Боулинг"
        bot.send_dice(name_of_the_game.chat.id, '🎳')

        upd = models.Userinf.update({models.Userinf.game: models.Userinf.game + 1}) \
            .where(models.Userinf.chat_id == name_of_the_game.chat.id)  # обновляем статистику режима в бд
        upd.execute()

        upd = models.Userinf.update({models.Userinf.bowling: models.Userinf.bowling + 1}) \
            .where(models.Userinf.chat_id == name_of_the_game.chat.id)  # обновляем статистику режима в бд
        upd.execute()

    elif name_of_the_game.text == '🎯Дартс🎯':  # отправляем эмоджи "Дартс"
        bot.send_dice(name_of_the_game.chat.id, '🎯')

        upd = models.Userinf.update({models.Userinf.game: models.Userinf.game + 1}) \
            .where(models.Userinf.chat_id == name_of_the_game.chat.id)  # обновляем статистику режима в бд
        upd.execute()

        upd = models.Userinf.update({models.Userinf.darts: models.Userinf.darts + 1}) \
            .where(models.Userinf.chat_id == name_of_the_game.chat.id)  # обновляем статистику режима в бд
        upd.execute()

    elif name_of_the_game.text == '🎰Игровой автомат🎰':  # отправляем эмоджи "Игровой автомат"
        bot.send_dice(name_of_the_game.chat.id, '🎰')

        upd = models.Userinf.update({models.Userinf.game: models.Userinf.game + 1}) \
            .where(models.Userinf.chat_id == name_of_the_game.chat.id)  # обновляем статистику режима в бд
        upd.execute()

        upd = models.Userinf.update({models.Userinf.slot_machine: models.Userinf.slot_machine + 1}) \
            .where(models.Userinf.chat_id == name_of_the_game.chat.id)  # обновляем статистику режима в бд
        upd.execute()


def random_number(message):
    '''
    функция для выполнения игры рандомное число
    '''
    global data
    if message.text == '🔢Рандомное число🔢':  # создаём нужные кнопки и отправляем подсказку об использовании
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        btn_choose = types.KeyboardButton('🔢Выбрать число🔢')
        btn_set_the_range = types.KeyboardButton('📝Задать диапазон📝')
        btn_back = types.KeyboardButton('🔙Назад🔙')
        markup.add(btn_choose, btn_set_the_range, btn_back)
        bot.send_message(message.chat.id, 'Игра "Рандомное число" 😀', reply_markup=markup)
        bot.send_message(message.chat.id, 'Задайте нужный вам диапазон и нажмите на кнопку "🔢Выбрать число🔢",' +
                         ' и я выберу случайное число из этого диапазона, включая введённые значения 😁')
        if len(data[f'{message.chat.id}']['list_for_game_random_number']) != 0:
            ot = data[f'{message.chat.id}']['list_for_game_random_number'][0]
            do = data[f'{message.chat.id}']['list_for_game_random_number'][1]
            bot.send_message(message.chat.id, f'Сейчас у вас диапазон: от {ot} до {do}')
    elif message.text == '🔢Выбрать число🔢':  # выбираем и выводим рандомное число из заданного промежутка
        data[f'{message.chat.id}']['game_function_check'] = ''
        if len(data[f'{message.chat.id}']['list_for_game_random_number']) != 0:
            number_1 = data[f'{message.chat.id}']['list_for_game_random_number'][0]
            number_2 = data[f'{message.chat.id}']['list_for_game_random_number'][1]
            bot.send_message(message.chat.id, f'{randint(number_1, number_2)}')

            upd = models.Userinf.update({models.Userinf.game: models.Userinf.game + 1}) \
                .where(models.Userinf.chat_id == message.chat.id)  # обновляем статистику режима в бд
            upd.execute()

            upd = models.Userinf.update({models.Userinf.random_number: models.Userinf.random_number + 1}) \
                .where(models.Userinf.chat_id == message.chat.id)  # обновляем статистику режима в бд
            upd.execute()
        else:
            bot.send_message(message.chat.id, 'Чтобы я выбрал рандомное число,' +
                             ' вам сначала нужно задать диапазон 😉')
    elif message.text == '📝Задать диапазон📝':  # меняем функцию игры на нужную
        data[f'{message.chat.id}']['game_function_check'] = 'Диапазон'
        bot.send_message(message.chat.id, 'Напишите два целых числа через пробел для задания диапазона 🤠')
        if len(data[f'{message.chat.id}']['list_for_game_random_number']) != 0:
            ot = data[f'{message.chat.id}']['list_for_game_random_number'][0]
            do = data[f'{message.chat.id}']['list_for_game_random_number'][1]
            bot.send_message(message.chat.id, f'Ваш текущий диапазон: от {ot} до {do}')
    elif data[f'{message.chat.id}']['game_function_check'] == 'Диапазон' and message.text != '📝Задать диапазон📝':
        if message.text != '🔙Назад🔙':  # задаём введённый пользователем диапазон
            try:
                lst_for_data = [int(num) for num in message.text.split()]
                lst_for_data.sort()
                data[f'{message.chat.id}']['list_for_game_random_number'] = lst_for_data
                if len(data[f'{message.chat.id}']['list_for_game_random_number']) != 2:
                    data[f'{message.chat.id}']['list_for_game_random_number'] = []
                    bot.send_message(message.chat.id, 'Неправильное количество чисел для задания диапазона 🙁\n' +
                                     '❗ Нужно ввести 2 целых числа через пробел ❗')
                else:
                    bot.send_message(message.chat.id, 'Диапазон задан успешно ✅')
            except BaseException:
                bot.send_message(message.chat.id, 'Неверный формат задания диапазона ☹')
    if message.text == '🔙Назад🔙':  # возвращаем кнопки режима игр и выводим подсказку о том что игра выключена
        data[f'{message.chat.id}']['pod_mode'] = ''
        data[f'{message.chat.id}']['game_function_check'] = ''
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        btn_random_number = types.KeyboardButton('🔢Рандомное число🔢')
        btn_random_word = types.KeyboardButton('✏Рандомное слово🗒')
        btn_dice = types.KeyboardButton('🎲Игровые кости🎲')
        btn_basketball = types.KeyboardButton('🏀Баскетбол🏀')
        btn_football = types.KeyboardButton('⚽Футбол⚽')
        btn_bowling = types.KeyboardButton('🎳Боулинг🎳')
        btn_darts = types.KeyboardButton('🎯Дартс🎯')
        btn_slot_machine = types.KeyboardButton('🎰Игровой автомат🎰')
        btn_back = types.KeyboardButton('🔙Назад🔙')
        markup.add(btn_random_number, btn_random_word, btn_dice, btn_basketball, btn_football, btn_bowling,
                   btn_darts, btn_slot_machine, btn_back)
        bot.send_message(message.chat.id, 'Игра "Рандомное число" выключена 🙃', reply_markup=markup)


def random_word(message):
    '''
    функция для выполнения игры рандомное слово
    '''
    global data
    if message.text == '✏Рандомное слово🗒':  # создаём нужные кнопки и отправляем подсказку об использовании
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        btn_choose = types.KeyboardButton('🗒Выбрать слово🗒')
        btn_set_list_of_word = types.KeyboardButton('✏Задать список слов🗃')
        btn_back = types.KeyboardButton('🔙Назад🔙')
        markup.add(btn_choose, btn_set_list_of_word, btn_back)
        bot.send_message(message.chat.id, 'Игра "Рандомное слово" 😝', reply_markup=markup)
        bot.send_message(message.chat.id, 'Задайте список слов и нажмите на кнопку "🗒Выбрать слово🗒", ' +
                         'и я выберу случайное слово из этого списка 😜')
        if len(data[f'{message.chat.id}']['list_for_game_random_word']) != 0:
            words = data[f'{message.chat.id}']['list_for_game_random_word']
            bot.send_message(message.chat.id, 'Сейчас у вас такой список слов: ' +
                             f'{", ".join(words)}')
    elif message.text == '🗒Выбрать слово🗒':  # выбираем и выводим рандомное слово из заданного списка слов
        data[f'{message.chat.id}']['game_function_check'] = ''
        if len(data[f'{message.chat.id}']['list_for_game_random_word']) != 0:
            words = data[f'{message.chat.id}']['list_for_game_random_word']
            bot.send_message(message.chat.id, f'{choice(words)}')

            upd = models.Userinf.update({models.Userinf.game: models.Userinf.game + 1}) \
                .where(models.Userinf.chat_id == message.chat.id)  # обновляем статистику режима в бд
            upd.execute()

            upd = models.Userinf.update({models.Userinf.random_word: models.Userinf.random_word + 1}) \
                .where(models.Userinf.chat_id == message.chat.id)  # обновляем статистику режима в бд
            upd.execute()
        else:
            bot.send_message(message.chat.id, 'Чтобы я выбрал рандомное слово, ' +
                             'вам сначала нужно задать список слов 😉')
    elif message.text == '✏Задать список слов🗃':  # меняем функцию игры на нужную
        data[f'{message.chat.id}']['game_function_check'] = 'Список слов'
        bot.send_message(message.chat.id, 'Напишите слова через пробел для задания списка слов 😃\n' +
                         'Количество слов неограниченно 📗')
        if len(data[f'{message.chat.id}']['list_for_game_random_word']) != 0:
            words = data[f'{message.chat.id}']['list_for_game_random_word']
            bot.send_message(message.chat.id, 'Ваш текущий список слов: ' +
                             f'{", ".join(words)}')
    elif data[f'{message.chat.id}']['game_function_check'] == 'Список слов' and message.text != '✏Задать список слов🗃':
        if message.text != '🔙Назад🔙':  # задаём введённый пользователем список слов
            try:
                data[f'{message.chat.id}']['list_for_game_random_word'] = [word for word in message.text.split()]
                bot.send_message(message.chat.id, 'Список слов задан успешно ✅')
            except BaseException:
                bot.send_message(message.chat.id, 'Неверный формат задания списка слов 🙁')
    if message.text == '🔙Назад🔙':  # возвращаем кнопки режима игр и выводим подсказку о том что игра выключена
        data[f'{message.chat.id}']['pod_mode'] = ''
        data[f'{message.chat.id}']['game_function_check'] = ''
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        btn_random_number = types.KeyboardButton('🔢Рандомное число🔢')
        btn_random_word = types.KeyboardButton('✏Рандомное слово🗒')
        btn_dice = types.KeyboardButton('🎲Игровые кости🎲')
        btn_basketball = types.KeyboardButton('🏀Баскетбол🏀')
        btn_football = types.KeyboardButton('⚽Футбол⚽')
        btn_bowling = types.KeyboardButton('🎳Боулинг🎳')
        btn_darts = types.KeyboardButton('🎯Дартс🎯')
        btn_slot_machine = types.KeyboardButton('🎰Игровой автомат🎰')
        btn_back = types.KeyboardButton('🔙Назад🔙')
        markup.add(btn_random_number, btn_random_word, btn_dice, btn_basketball, btn_football, btn_bowling,
                   btn_darts, btn_slot_machine, btn_back)
        bot.send_message(message.chat.id, 'Игра "Рандомное слово" выключена 🙃', reply_markup=markup)


if __name__ == '__main__':
    bot.polling(none_stop=True, interval=True)