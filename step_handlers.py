import telebot
import configparser
import os
import subprocess

from keyboards import explorer_buttons
from file_list_generator import generate_files_list

config = configparser.ConfigParser()
config.read('config.cfg')

bot = telebot.TeleBot(config['DEFAULT']['token'])


def folder_opener(message=None, current_path=None, message_to_delete=None, message_to_edit=None):
    try:
        if message:
            if current_path.endswith('\\'):
                next_path = current_path + message.text
            else:
                next_path = current_path + '\\' + message.text
            bot.delete_message(chat_id=message.chat.id, message_id=message.id)
            print(f'Открываю {next_path}')
            if message_to_delete:
                bot.delete_message(chat_id=message.chat.id, message_id=message_to_delete.id)

            kb = explorer_buttons(next_path)
            data_from_generator = generate_files_list(next_path)


        else:
            kb = explorer_buttons(current_path)
            data_from_generator = generate_files_list(current_path)

        bot.edit_message_text(chat_id=message_to_edit.chat.id, message_id=message_to_edit.id,
                              text=data_from_generator[0], reply_markup=kb, parse_mode='HTML')

    except Exception as e:
        bot.send_message(chat_id=message_to_edit.chat.id, text=f'❌ Ошибка при открытии папки: {e}\n'
                                                               f'Вероятнее всего отказ в доступе/папка не существует')


def createfolder(message, path=None, msg_to_delete=None):
    print(f'Создаю папку "{message.text}" по пути {path}')
    if path.endswith('\\'):
        path = path + message.text
    else:
        path = path + '\\' + message.text

    try:
        os.mkdir(path)
        print('Успех')
        bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        if msg_to_delete:
            bot.delete_message(chat_id=msg_to_delete.chat.id, message_id=msg_to_delete.message_id)
    except Exception as e:
        print(f'Произошла ошибка {e}')
        bot.send_message(chat_id=message.chat.id, text=f'Произошла ошибка {e}')


def upload_file(message, current_path=None, msg_to_delete=None):
    if message.content_type == 'document':
        file_size = message.document.file_size
        if file_size > 20 * 1024 ** 2:
            print('Файл превышает допустимый размер в 20мб')
            bot.send_message(message.chat.id, text='❌ Файл превышает допустимый размер в 20мб')
        else:
            if current_path.endswith('\\'):
                path = os.path.join(current_path, message.document.file_name)
            else:
                path = os.path.join(current_path, message.document.file_name)
            downloaded_file = bot.download_file(bot.get_file(message.document.file_id).file_path)

            with open(path, 'wb') as f:
                f.write(downloaded_file)
            bot.delete_message(chat_id=message.chat.id, message_id=message.id)
            bot.delete_message(chat_id=msg_to_delete.chat.id, message_id=msg_to_delete.id)
            print(f'Файл "{message.document.file_name}" получен и сохранен в "{current_path}"')
            bot.send_message(message.chat.id,
                             text=f'✅ Файл "{message.document.file_name}" получен и сохранен в "{current_path}"')
    else:
        print('это не файл...')
        bot.send_message(message.chat.id, text=f'Это не файл...')


def delete_file(message, current_path=None, msg_to_delete=None):
    path = os.path.join(current_path, message.text)
    print(path)
    try:
        os.remove(path)
        print(f'файл "{message.text}" по пути "{current_path}" успешно удален')
    except FileNotFoundError:
        print(f'Файл "{message.text}" по пути "{current_path}" не найден')
        bot.send_message(chat_id=message.chat.id, text=f'Файл "{message.text}" по пути "{current_path}" не найден')
    except PermissionError:
        print(f'Недостаточно прав для удаления файла "{message.text}" по пути "{current_path}"')
        bot.send_message(chat_id=message.chat.id,
                         text=f'Недостаточно прав для удаления файла "{message.text}" по пути "{current_path}"')
    except Exception as e:
        print(f'Произошла ошибка: {e}')
    bot.delete_message(chat_id=message.chat.id, message_id=message.id)
    bot.delete_message(chat_id=msg_to_delete.chat.id, message_id=msg_to_delete.id)


def run_command(command):
    print(1)
    try:
        result = subprocess.run(command.text, shell=True, text=True, capture_output=True, timeout=10)
        print(2)
        if result.returncode == 0:
            messages = telebot.util.smart_split(text=result.stdout, chars_per_string=4096)
        else:
            messages = telebot.util.smart_split(text=result.stderr, chars_per_string=4096)
        print(result.returncode)
        for msg in messages:
            bot.send_message(chat_id=command.chat.id, text=f'```shell\n{msg}\n```', parse_mode='MarkdownV2')

    except subprocess.TimeoutExpired:
        print('Время ожидания команды истекло')
        bot.send_message(chat_id=command.chat.id, text="Время ожидания команды истекло")
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        bot.send_message(chat_id=command.chat.id, text=f'Произошла ошибка {e}')
