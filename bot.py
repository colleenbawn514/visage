
from PIL import Image, ImageEnhance
import telebot
import os
import time
import traceback
from keyboa import keyboa_maker
from visage import ApplyMakeup
#from visage import flag

makeup = ApplyMakeup()

#чтение из файла ( для фоток)
def read_file(file_name):
    with open(file_name, 'r') as file:
        return file.read()

#подключение к боту по токену
bot = telebot.TeleBot(read_file('token.ini').strip())
#для фото
user = dict()

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    
    if chat_id not in user:
        bot.send_message(chat_id, 'Ooops')
        return
    
    if call.data == 'lipcstik_r255_g0_b0':
        user[chat_id]['lipstick_color'] = { 'r': 255, 'g': 0 , 'b': 0 }
        user[chat_id]['use_lipstick'] = True    
        
        bot.edit_message_text('Цвет губ: крысный', chat_id, call.message.id)
        choose_liner(chat_id)
    elif call.data == 'lipstick_off':
        user[chat_id]['lipstick_color'] = None
        user[chat_id]['use_lipstick'] = False  
        bot.edit_message_text('Без губной помады', chat_id, call.message.id)
        choose_liner(chat_id)    
    elif call.data == 'liner_on':
        user[chat_id]['use_liner'] = True  
        bot.edit_message_text('Использовать лайнер', chat_id, call.message.id)
        processing(chat_id)
    elif call.data == 'liner_off':
        user[chat_id]['use_liner'] = False  
        bot.edit_message_text('Без лайнера', chat_id, call.message.id)
        processing(chat_id)
    elif call.data == 'add_photo':
        bot.edit_message_text('Фото получено. Отправьте ещё фото', chat_id, call.message.id)
        bot.register_next_step_handler(call.message, handle_docs_photo)
    elif call.data == 'start_makeup':
        bot.clear_step_handler(call.message)
        bot.delete_message(chat_id, call.message.id)
        choose_lipstik(chat_id)
        

#обработка текстовых сообщений
@bot.message_handler(content_types=['text'])
def start(message):
    if message.text == '/start':
        bot.send_message(
            message.from_user.id, 
            'Привет. Это бот для нанесения виртуального макияжа.\n' 
            + 'Напиши /go, чтобы начать обработку.\n' 
            + 'Напиши /help, чтобы узнать полный список команд.'
        )
    elif message.text == '/inst':
        bot.send_message(
            message.from_user.id, 
            'Для нанесения виртуального макияжа необходимо написать /go и отправить фото лица.\n' 
            + 'Лицо должно быть хорошо освещено на фото.\n' 
            + 'Для наилучшего результата на фото должны отсутствовать гримасы, выражение лица должно быть нейтральным.\n' 
            + 'Если лицо на фотографии не обнаружено, бот выдаст сообщение об ошибке.\n'
        )
        bot.send_message(
            message.from_user.id, 
            'Бот обрабатывает фотографии последовательно по 2 за раз. Если ответ на фото не поступил, '
            + 'вы находитесь в очереди на обработку. Необходимо подождать.\n' 
            + 'Если обнаружились проблемы или есть предложения по улучшению, напишите автору в разделе /author.'
        )
    elif message.text == '/help':
        bot.send_message(
            message.from_user.id, 
            '/start - Приветственное сообщение.\n' 
            + '/go - Наложение виртуального макияжа.\n' 
            + '/inst - Инструкция использования, правила для фотографии.\n' 
            + '/author - Связь с автором.'
        )
    elif message.text == '/author':
        bot.send_message(
            message.from_user.id, 
            'Если обнаружились проблемы или есть предложения по улучшению, напишите автору в телеграмм: @Chancellore.'
        )
    elif message.text == '/go':
        user[message.chat.id] = {
            'source_images': [],
            'result_images': [],
            'photo_messages': [],
            'use_lipstick': False,
            'use_liner': False,
            'lipstick_color': None,
        }
        bot.send_message(
            message.from_user.id, 
            'Для нанесении косметики, отправьте фото лица.\n' 
            + 'Лицо должно быть хорошо освещено на фото.\n' 
            + 'Для наилучшего результата на фото должны отсутствовать гримасы, выражение лица должно быть нейтральным.'
        )
        bot.register_next_step_handler(message, handle_docs_photo)
    else:
        bot.send_message(message.from_user.id, 'Напишите /go для начала работы.\n' + 'Напишите /help для получения полного списка команд.')

#обработка фото
def handle_docs_photo(message):
    chat_id = message.chat.id    
    processing_info_message = None

    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        src = '/home/ekaterina/visage/' + file_info.file_path
        
        processing_info_message = bot.send_message(
            chat_id,
            "Обработка фото..."
        )
        
        with open(src, 'wb') as new_file:
           new_file.write(downloaded_file)
        
        if check_photo(src) is False:
            bot.delete_message(chat_id, processing_info_message.id)
            actions_with_ids = []        
            if len(user[chat_id]['source_images']) > 0:
                actions_with_ids.append({"💅 Сделать красивыми принятые фото": "start_makeup"})
            kb_actions = keyboa_maker(items=actions_with_ids)
            bot.send_message(
                chat_id,
                reply_markup = kb_actions,
                text = 'Не удалось найти лица на этой фотографии, попробуйте другую'
            )
            bot.register_next_step_handler(message, handle_docs_photo)
            return           
        
        kb_actions = keyboa_maker(items=[{"💅 Сделать красиво": "start_makeup"}])
        bot.delete_message(chat_id, processing_info_message.id)
        bot.send_message(
            chat_id,
            reply_markup = kb_actions,
            text = 'Фото получено'
        )
        user[chat_id]['source_images'].append(src)
        user[chat_id]['photo_messages'].append(message)
        
        # reply_img = photo_processing(src)
        # images[str(message.chat.id)].append(reply_img)
        # bot.send_photo(message.chat.id, open(reply_img, 'rb'))
    except Exception as e:
        traceback.print_exc()
        if processing_info_message is not None:
            bot.delete_message(chat_id, processing_info_message.id)
        actions_with_ids = []        
        if len(user[chat_id]['source_images']) > 0:
            actions_with_ids.append({"💅 Сделать красивыми приятные фото": "start_makeup"})
        kb_actions = keyboa_maker(items=actions_with_ids)
        bot.send_message(
            chat_id,
            reply_markup = kb_actions,
            text = 'Не удалось обработать фото, попробуйте другое'
        )
        
    bot.register_next_step_handler(message, handle_docs_photo)

def choose_lipstik(chat_id):
    lipstik_colors_with_ids = [
        {"Красный": "lipcstik_r255_g0_b0"},
        {"Без помады": "lipstick_off"},
    ]
    
    kb_lipstck_colors = keyboa_maker(items=lipstik_colors_with_ids, items_in_row=3)

    bot.send_message(
        chat_id,
        reply_markup = kb_lipstck_colors,
        text = 'Выберете цвет губ:'
    )
    
def choose_liner(chat_id):
    liner_with_ids = [
        {"Да": "liner_on"},
        {"Нет": "liner_off"},
    ]
    
    kb_liner = keyboa_maker(items=liner_with_ids, items_in_row=2)

    bot.send_message(
        chat_id,
        reply_markup = kb_liner,
        text = 'Нужна подводка?'
    )
    
def processing(chat_id):
    bot.send_message(chat_id, 'Обработка фотографиий... Это может занять какое то время')
    
    for i in range(len(user[chat_id]['source_images'])):
        try:
            result_src = photo_processing(user[chat_id]['source_images'][i], user[chat_id])
            print(result_src)
            user[chat_id]['result_images'].append(result_src)
            photo = open(result_src, 'rb')
            bot.send_photo(chat_id, photo)
        except Exception as e:
            traceback.print_exc()
            bot.reply_to(user[chat_id]['photo_messages'][i], 'Не нашли тут лицо')
            
    bot.send_message(chat_id, 'Все фото обработан, вы так прекрасы 🥰. Напишите /go что бы обработать ещё фото')
    clear_content(chat_id)
    
def check_photo(image_path):
    photo = Image.open(image_path)
    #photo = open(image_path, 'rb')
    return makeup.get_face_data(image_path, 'FILE_READ') is not None
    
#обработка фото
def photo_processing(image_path, options):
    result_src = image_path
    
    if options['use_lipstick']:
        result_src = makeup.apply_lipstick(
            result_src,
            options['lipstick_color']['r'],
            options['lipstick_color']['g'],
            options['lipstick_color']['b'],
        )
    if options['use_liner']:
        result_src = makeup.apply_liner(result_src)
    
    return result_src

#очищение папки с фото
def clear_content(chat_id):
    try:
        for img in user[chat_id]['source_images']:
            os.remove(img)
        for img in user[chat_id]['result_images']:
            os.remove(img)
    except Exception as e:
        time.sleep(3)
        clear_content(chat_id)
    del user[chat_id]


#проверка наличия новых сообщений
bot.polling(none_stop=True, interval=2)    
