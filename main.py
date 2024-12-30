import configparser
import telebot
import hashlib
from functools import partial

from keyboards import *
from system_info import *
from file_list_generator import *
from step_handlers import *

user_states = {}
version = '0.0.1'
current_path = None


def save_config():
    with open('config.cfg', 'w') as f:
        config.write(f)


def text_to_hash(text):
    memory_hash = hashlib.sha256(text.encode())
    hashed_password = memory_hash.hexdigest()
    return hashed_password


config = configparser.ConfigParser()
config.read('config.cfg')

if config['DEFAULT']['token']:
    print('CONFIG: токен бота найден')
else:
    print('CONFIG: токен бота не найден. Введите токен')
    config['DEFAULT']['token'] = input()
    save_config()

if config['DEFAULT']['admin_id']:
    print('CONFIG: admin id найден')
else:
    print('CONFIG: admin id не найден')
    if config['DEFAULT']['bot_password']:
        print('CONFIG: пароль бота найден')
    else:
        print('CONFIG: пароль бота не найден. Введите новый пароль')
        config['DEFAULT']['bot_password'] = text_to_hash(input())
        print('Новый пароль установлен')
        save_config()

bot = telebot.TeleBot(config['DEFAULT']['token'])


@bot.message_handler(commands=['start'])
def start(message):
    print(f'@{message.from_user.username}({message.from_user.id}) ввел команду: {message.text}')
    if config['DEFAULT']['admin_id']:
        if str(message.from_user.id) == config['DEFAULT']['admin_id']:
            print(f'@{message.from_user.username}({message.from_user.id}) вызвал меню')
            user_states[message.chat.id] = 'main_menu'

            kb = create_main_menu()

            bot.send_message(message.chat.id, text='Пожалуйста, выберите действие:', reply_markup=kb)
        else:
            print(f'@{message.from_user.username}({message.from_user.id}) не является админом')
    else:
        inputted_password = bot.send_message(message.chat.id, text='Введите пароль')
        bot.register_next_step_handler(inputted_password,
                                       lambda msg: verify_password(msg, inputted_password.message_id))


def verify_password(message, password_prompt_id):
    print(
        f'@{message.from_user.username}({message.from_user.id}) '
        f'{"ввел верный пароль" if text_to_hash(message.text) == config["DEFAULT"]["bot_password"] else
        f"попытался ввести пароль: {message.text}"}')

    inputted_password = text_to_hash(message.text)
    bot.delete_message(message.chat.id, password_prompt_id)
    if inputted_password == config['DEFAULT']['bot_password']:
        bot.delete_message(message.chat.id, message.message_id)
        bot.send_message(message.chat.id, text='Пароль верный ✅\n'
                                               'Напишите /start')
        config['DEFAULT']['admin_id'] = str(message.chat.id)
        save_config()
        print('Новый admin id установлен')

    else:
        bot.send_message(message.chat.id, text='Пароль неверный ❌')


@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    user_id = call.message.chat.id
    action, param = call.data.split('--')
    print(f'Нажата кнопка "{param}" в группе "{action}"')

    if action == 'menu':
        if param == 'explorer':
            user_states[user_id] = 'explorer'

            kb = select_disk()

            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                  text=f'Выберите диск для открытия:', reply_markup=kb)


        elif param == 'info':
            user_states[user_id] = 'info'

            kb = create_back_button()

            total_memory, used_memory, free_memory, program_memory = get_memory_info()

            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                  text=f'Made by <a href="https://github.com/VadikAladik">VadikAladik</a>\n'
                                       f'Версия бота: <code>{version}</code>\n\n'
                                       f'<b>ОЗУ:</b>\n'
                                       f'    Всего озу: <code>{total_memory:.1f} MB</code>\n'
                                       f'    Использовано озу: <code>{used_memory:.1f} MB</code>\n'
                                       f'    Свободно озу: <code>{free_memory:.1f} MB</code>\n'
                                       f'    Используется ботом: <code>{program_memory:.1f} MB</code>',
                                  parse_mode='HTML', disable_web_page_preview=True, reply_markup=kb)

        elif param == 'execute':
            user_states[user_id] = 'execute'

            kb = cancel_button()

            input_command = bot.send_message(chat_id=call.message.chat.id,
                                             text='Введите команду которая будет выполнена на компьютере\n'
                                                  '<i>Команда выполняется скрытно т.е. на компьютере не будет видно вызов консоли</i>',
                                             parse_mode='HTML')
            bot.register_next_step_handler(input_command, run_command)

        elif param == 'back':
            user_states[user_id] = 'main_menu'

            kb = create_main_menu()

            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                  text='Пожалуйста, выберите действие:', reply_markup=kb)

        elif param == 'cancel':
            user_states[user_id] = 'cancelled'

            bot.send_message(call.message.chat.id, text='❌ Ввод отменен')
            bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)

            user_states.pop(user_id, None)
            bot.clear_step_handler_by_chat_id(chat_id=user_id)

    if action == 'disks':

        if param == 'back':
            kb = select_disk()

            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                  text=f'Выберите диск для открытия:', reply_markup=kb)

        else:
            disk_name = param.split('_')
            print(f'Выбран диск {disk_name[1]}')

            kb = explorer_buttons(disk_name[1], enable_back_button=False)

            files_list = generate_files_list(disk_name[1], )

            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                  text=files_list, reply_markup=kb, parse_mode='HTML')

    if action == 'folders':
        if param.startswith('open|'):
            message_to_edit = call.message

            kb = cancel_button()

            subaction, dir_path = param.split('|')
            input_path = bot.send_message(chat_id=call.message.chat.id, text='Введите имя папки', reply_markup=kb)
            bot.register_next_step_handler(input_path,
                                           partial(folder_opener, current_path=dir_path, message_to_delete=input_path,
                                                   message_to_edit=message_to_edit))

        elif param.startswith('back|'):
            message_to_edit = call.message

            param_trash = param.split('|')
            parts_of_dir = param_trash[1].split('\\')
            good_dir = '\\'.join(parts_of_dir[:-1])
            if not good_dir.endswith('\\'):
                good_dir = good_dir + '\\'
            print(f'Возвращаюсь назад - {good_dir}')
            folder_opener(current_path=good_dir, message_to_edit=message_to_edit)

        elif param.startswith('createfolder|'):
            kb = cancel_button()
            param_trash = param.split('|')
            input_folder_name = bot.send_message(chat_id=call.message.chat.id, text='Введите имя папки',
                                                 reply_markup=kb)
            bot.register_next_step_handler(input_folder_name,
                                           partial(createfolder, path=param_trash[1], msg_to_delete=input_folder_name))

        elif param.startswith('upload|'):
            param_trash = param.split('|')
            kb = cancel_button()
            input_file = bot.send_message(chat_id=call.message.chat.id,
                                          text=f'Отправьте файл который нужно загрузить по пути {param_trash[1]}',
                                          reply_markup=kb)
            bot.register_next_step_handler(input_file,
                                           partial(upload_file, current_path=param_trash[1], msg_to_delete=input_file))

        elif param.startswith('delete|'):
            param_trash = param.split('|')
            kb = cancel_button()
            input_file_to_delete = bot.send_message(chat_id=call.message.chat.id,
                                                    text=f'Отправьте имя файла который нужно удалить по пути {param_trash[1]}',
                                                    reply_markup=kb)
            bot.register_next_step_handler(input_file_to_delete, partial(delete_file, current_path=param_trash[1],
                                                                         msg_to_delete=input_file_to_delete))


if __name__ == '__main__':
    bot.infinity_polling(timeout=10, long_polling_timeout=5, skip_pending=True)
