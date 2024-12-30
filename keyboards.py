from telebot.types import InlineKeyboardMarkup as K, InlineKeyboardButton as B

from system_info import *


def create_main_menu():
    kb = K()
    kb.row(B(text='📁 Проводник', callback_data='menu--explorer'))
    kb.row(B(text='📊 Информация', callback_data='menu--info'),
           B(text='🚀 Выполнить команду', callback_data='menu--execute'))
    return kb


def create_back_button():
    kb = K()
    kb.row(B(text='⬅️ Назад', callback_data='menu--back'))
    return kb


def select_disk():
    drives = get_drives()
    kb = K()
    for drive in drives:
        kb.row(B(text=f'Диск {drive.strip(':\\')}', callback_data=f'disks--drive_{drive}'))

    kb.row(B(text='⬅️ Назад', callback_data='menu--back'))
    return kb


def explorer_buttons(directory_path='', enable_back_button=True):
    kb = K()
    if enable_back_button and (not directory_path.endswith(':\\') or not directory_path.endswith(':\\')):
        kb.row(B(text='🔙 Вернуться на 1 папку назад', callback_data=f'folders--back|{directory_path}'))
    kb.row(B(text='📂 Открыть папку', callback_data=f'folders--open|{directory_path}'),
           B(text='📁 Создать папку', callback_data=f'folders--createfolder|{directory_path}'))
    kb.row(B(text='📥 Загрузить', callback_data=f'folders--upload|{directory_path}'),
           B(text='🗑️ Удалить', callback_data=f'folders--delete|{directory_path}'))
    kb.row(B(text='⬅️ Назад', callback_data='disks--back'))
    return kb


def cancel_button():
    kb = K()
    kb.add(B(text='❌ Отмена', callback_data='menu--cancel'))
    return kb
