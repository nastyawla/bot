#!/usr/bin/env python
# coding: utf-8

# In[7]:


pip3 install pytelegrambotapi


# In[ ]:


import telebot
import pytz
import json


# In[ ]:


from os.path import basename

import requests
from bs4 import BeautifulSoup
import random

#парсим данные с киноафиши
def parse():
    url = ['https://www.kinoafisha.info/rating/movies/?page=0' ,
           'https://www.kinoafisha.info/rating/movies/?page=1' ,
           'https://www.kinoafisha.info/rating/movies/?page=2' ,
           'https://www.kinoafisha.info/rating/movies/?page=3' ,
           'https://www.kinoafisha.info/rating/movies/?page=4' ,
           'https://www.kinoafisha.info/rating/movies/?page=5' ,
           'https://www.kinoafisha.info/rating/movies/?page=6' ,
           'https://www.kinoafisha.info/rating/movies/?page=7' ,
           'https://www.kinoafisha.info/rating/movies/?page=8' ,
           'https://www.kinoafisha.info/rating/movies/?page=9']
    k = 0
    pages = 9
    id_films = 1
    film_list = []
    while k <= pages:
        response = requests.get(url[k])
        soup = BeautifulSoup(response.text , 'lxml')
        films = soup.find_all('div' , class_='films_content')

        for i in range(0 , len(films)):
            j = 0
            prod = ''
            film_names = films[i].find('a' , class_='films_name ref')
            ratings = films[i].find('span' , class_='rating_num')
            films_info = films[i].find_all('span' , class_='films_info')
            producers = films[i].find_all('a' , class_='films_info_link')

            for producer in producers:
                prod += producer.get_text()
                if len(producers) > 1 and producer != producers[-1]:
                    prod += ', '

            film_dict = {
                "ID": id_films ,
                "Name": film_names.text ,
                "Ratings": ratings.text ,
                "Genre": films_info[j + 1].text ,
                "Info": films_info[j].text ,
                "Producer": prod
            }
            film_list.append(film_dict)
            id_films += 1

        k += 1
    return film_list
#теперь у нас есть список словарей, содержащих основную инфу о фильмах

#пишем функции для выдачи: рандомного фильма, фильма, опираясь на выбранный жанр, 
#на выбранного режиссера и на режиссер+жанр вместе
def get_random_movie(lst):
    res1 = random.choice(lst)
    num = str(res1["ID"])
    name = res1["Name"]
    ratings = res1["Ratings"]
    genre = res1["Genre"]
    info = res1["Info"]
    producer = res1["Producer"]
    result = ('Название фильма: ' + name + '\n' +
              'Оценка фильма: ' + ratings + '\n' +
              'Жанр: ' + genre + '\n' +
              'Информация о фильме: ' + info + '\n' +
              'Режиссер/ы: ' + producer)
    return num , result


def get_random_movie_of_genre(genre , lst):
    genre_lst = []
    for i in range(0 , len(lst)):
        if lst[i]["Genre"].startswith(genre) or lst[i]["Genre"].endswith(genre):
            genre_lst.append(lst[i])
    num , result = get_random_movie(genre_lst)
    return num , result


def get_random_movie_of_producer(producer , lst):
    producer_lst = []
    for i in range(0 , len(lst)):
        if lst[i]["Producer"].startswith(producer) or lst[i]["Producer"].endswith(producer):
            producer_lst.append(lst[i])
    num , result = get_random_movie(producer_lst)
    return num , result


def get_random_movie_of_genre_and_producer(genre , producer , lst):
    genre_lst = []
    producer_lst = []
    for i in range(0 , len(lst)):
        if lst[i]["Genre"].startswith(genre) or lst[i]["Genre"].endswith(genre):
            genre_lst.append(lst[i])
    if len(genre_lst) != 0:
        for i in range(0 , len(genre_lst)):
            if genre_lst[i]["Producer"].startswith(producer) or genre_lst[i]["Producer"].endswith(producer):
                producer_lst.append(genre_lst[i])
    if len(producer_lst) != 0:
        num , result = get_random_movie(producer_lst)
        return num , result
    if len(genre_lst) != 0 or len(producer_lst) != 0:
        return None, None
#токен для бота
TOKEN = '1407922873:AAGozfimZT4-yds7DyA_2bp7-yQQWW6EZdY'
TIMEZONE = 'Europe/Moscow'
TIMEZONE_COMMON_NAME = 'Moscow'

film_list = parse()
P_TIMEZONE = pytz.timezone(TIMEZONE)
genre = ''
producer = ''
#создаем бота
bot = telebot.TeleBot(TOKEN)
@bot.message_handler(commands=['start'])
def start_command(message):
    bot.send_message(
        message.chat.id ,
        'Приветствую тебя.\n' +
        'Этот бот поможет выбрать фильмы из списка 1000 фильмов.\n' +
        'Вам нужно выбрать жанр.\n' +
        'Для этого нажмите /genre.\n' +
        'Затем можно выбрать фильм по имени режиссера\n' +
        'Для получения информации о работе бота нажмите /help.'
    )
@bot.message_handler(commands=['help'])
def help_command(message):
    bot.send_message(
        message.chat.id ,
        '1) Для выбора жанров нажмите /genre.\n' +
        '2) Дальше вам предложат на выбор несколько жанров, нажмите на интересующий вас.\n' +
        '3) Дальше вам предложат на выбор несколько режиссеров, нажмите на интересующего вас.\n' +
        '4) Вам придет сообщение с названием и картинкой фильма, также укажется некоторая информация о фильме '
    )

#кнопки, которые будут показываться пользователю для выбора жанра
@bot.message_handler(commands=['genre'])
def genre_command(message):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(
        telebot.types.InlineKeyboardButton('Драма' , callback_data='genre_btn1'))
    keyboard.row(
        telebot.types.InlineKeyboardButton('Триллер' , callback_data='genre_btn2'))
    keyboard.row(
        telebot.types.InlineKeyboardButton('Комедия' , callback_data='genre_btn3'))
    keyboard.row(
        telebot.types.InlineKeyboardButton('Семейное' , callback_data='genre_btn4'))
    keyboard.row(
        telebot.types.InlineKeyboardButton('Приключения' , callback_data='genre_btn5'))
    keyboard.row(
        telebot.types.InlineKeyboardButton('Анимация' , callback_data='genre_btn6'))
    keyboard.row(
        telebot.types.InlineKeyboardButton('Любой жанр' , callback_data='genre_btn7'))
    bot.send_message(
        message.chat.id ,
        'Выберите жанр:\n' ,
        reply_markup=keyboard
    )


@bot.callback_query_handler(func=lambda call: True)
def iq_callback(query):
    data = query.data
    if data.startswith('genre_btn'):
        bot.answer_callback_query(query.id)
        get_genre_callback(query)
    if data.startswith('producer_btn'):
        bot.answer_callback_query(query.id)
        get_producer_callback(query)


def get_genre_callback(query):
    bot.answer_callback_query(query.id)
    send_genre_result(query.message , query.data[9:])

# после того как жанр был выбран, делаем то же самое для режиссеров
def send_genre_result(message , ex_code):
    global genre
    bot.send_chat_action(message.chat.id , 'typing')
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(
        telebot.types.InlineKeyboardButton('Кристофер Нолан' , callback_data='producer_btn1'))
    keyboard.row(
        telebot.types.InlineKeyboardButton('Гай Ричи' , callback_data='producer_btn2'))
    keyboard.row(
        telebot.types.InlineKeyboardButton('Джеймс Кэмерон' , callback_data='producer_btn3'))
    keyboard.row(
        telebot.types.InlineKeyboardButton('Люк Бессон' , callback_data='producer_btn4'))
    keyboard.row(
        telebot.types.InlineKeyboardButton('Любой режиссер' , callback_data='producer_btn5'))
    if ex_code == '1':
        genre = 'драма'
        bot.send_message(
            message.chat.id ,
            'Вы выбрали Драму\n' +
            'Выберите Режиссера:\n' ,
            reply_markup=keyboard
        )
    if ex_code == '2':
        genre = 'триллер'
        bot.send_message(
            message.chat.id ,
            'Вы выбрали Триллер\n' +
            'Выберите Режиссера:\n' ,
            reply_markup=keyboard
        )
    if ex_code == '3':
        genre = 'комедия'
        bot.send_message(
            message.chat.id ,
            'Вы выбрали Комедию\n' +
            'Выберите Режиссера:\n' ,
            reply_markup=keyboard
        )
    if ex_code == '4':
        genre = 'семейный'
        bot.send_message(
            message.chat.id ,
            'Вы выбрали Семейное\n' +
            'Выберите Режиссера:\n' ,
            reply_markup=keyboard
        )
    if ex_code == '5':
        genre = 'приключения'
        bot.send_message(
            message.chat.id ,
            'Вы выбрали Приключение\n' +
            'Выберите Режиссера:\n' ,
            reply_markup=keyboard
        )
    if ex_code == '6':
        genre = 'анимация'
        bot.send_message(
            message.chat.id ,
            'Вы выбрали Анимацию\n' +
            'Выберите Режиссера:\n' ,
            reply_markup=keyboard
        )
    if ex_code == '7':
        bot.send_message(
            message.chat.id ,
            'Вы выбрали Любой жанр\n' +
            'Выберите Режиссера:\n' ,
            reply_markup=keyboard
        )


def get_producer_callback(query):
    bot.answer_callback_query(query.id)
    send_producer_result(query.message , query.data[12:])


def send_producer_result(message , ex_code):
    global genre
    bot.send_chat_action(message.chat.id , 'typing')
    if ex_code == '1':
        producer = 'Кристофер Нолан'
        if genre != '':
            num , film = get_random_movie_of_genre_and_producer(genre , producer , film_list)
        else:
            num , film = get_random_movie_of_producer(producer , film_list)
        if film != None:
            num = 'images/' + str(num) + '.jpeg'
            #img = open(num , 'rb')
            #bot.send_photo(message.chat.id , img)
            bot.send_message(
                message.chat.id ,
                'Вы выбрали Кристофера Нолана\n\n' +
                'Вы получили фильм: \n' +
                film
            )
        else:
            bot.send_message(
                message.chat.id ,
                'Увы! Такого фильма не нашлось, попробуйте еще раз'
            )
    if ex_code == '2':
        producer = 'Гай Ричи'
        if genre != '':
            num , film = get_random_movie_of_genre_and_producer(genre , producer , film_list)
        else:
            num , film = get_random_movie_of_producer(producer , film_list)
        if film != None:
            num = 'images/' + str(num) + '.jpeg'
            #img = open(num , 'rb')
            #bot.send_photo(message.chat.id , img)
            bot.send_message(
                message.chat.id ,
                'Вы выбрали Гая Ричи\n\n' +
                'Вы получили фильм: \n' +
                film
            )
        else:
            bot.send_message(
                message.chat.id ,
                'Увы! Такого фильма не нашлось, попробуйте еще раз'
            )
    if ex_code == '3':
        producer = 'Джеймс Кэмерон'
        if genre != '':
            num , film = get_random_movie_of_genre_and_producer(genre , producer , film_list)
        else:
            num , film = get_random_movie_of_producer(producer , film_list)
        if film != None:
            num = 'images/' + str(num) + '.jpeg'
            #img = open(num , 'rb')
            #bot.send_photo(message.chat.id , img)
            bot.send_message(
                message.chat.id ,
                'Вы выбрали Джейса Кэмерона\n\n' +
                'Вы получили фильм: \n' +
                film
            )
        else:
            bot.send_message(
                message.chat.id ,
                'Увы! Такого фильма не нашлось, попробуйте еще раз'
            )
    if ex_code == '4':
        producer = 'Люк Бессон'
        if genre != '':
            num , film = get_random_movie_of_genre_and_producer(genre , producer , film_list)
        else:
            num , film = get_random_movie_of_producer(producer , film_list)
        if film != None:
            num = 'images/' + str(num) + '.jpeg'
            #img = open(num , 'rb')
            #bot.send_photo(message.chat.id , img)
            bot.send_message(
                message.chat.id ,
                'Вы выбрали Люка Бессона\n\n' +
                'Вы получили фильм: \n' +
                film
            )
        else:
            bot.send_message(
                message.chat.id ,
                'Увы! Такого фильма не нашлось, попробуйте еще раз'
            )
    if ex_code == '5':
        if genre != '':
            num , film = get_random_movie_of_genre(genre, film_list)
        else:
            num , film = get_random_movie(film_list)
        if film != None:
            num = 'images/' + str(num) + '.jpeg'
            #img = open(num , 'rb')
            #bot.send_photo(message.chat.id , img)
            bot.send_message(
                message.chat.id ,
                'Вы выбрали Любой режиссер\n\n' +
                'Вы получили фильм: \n' +
                film
            )
        else:
            bot.send_message(
                message.chat.id ,
                'Увы! Такого фильма не нашлось, попробуйте еще раз'
            )


bot.polling(none_stop=True)


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[10]:





# In[12]:





# In[21]:





# In[ ]:





# In[28]:





# In[31]:





# In[32]:





# In[34]:





# In[37]:





# In[ ]:




