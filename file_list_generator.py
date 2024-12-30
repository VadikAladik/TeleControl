import os

folder_dir = None

file_icons = {
    'folders': '📁',
    '.jpeg': '🖼️',
    '.jpg': '🖼️',
    '.png': '🖼️',
    '.gif': '🖼️',
    '.bmp': '🖼️',
    '.tiff': '🖼️',
    '.svg': '🖼️',
    '.mp4': '📀',
    '.avi': '📀',
    '.mkv': '📀',
    '.mov': '📀',
    '.flv': '📀',
    '.wmv': '📀',
    '.sys': '⚙️',
    '.ini': '⚙️',
    '.dll': '🧷',
    '.db': '🗂️',
    '.sql': '🗂️',
    '.mdb': '🗂️',
    '.accdb': '🗂️',
    '.rar': '📦',
    '.zip': '📦',
    '.7z': '📦',
    '.tar': '📦',
    '.gz': '📦',
    '.py': '🐍',
    '.lua': '🧬',
    '.sh': '🔧',
    '.bat': '🔧',
    '.txt': '📄',
    '.doc': '📄',
    '.docx': '📄',
    '.odt': '📄',
    '.rtf': '📄',
    '.pdf': '📚',
    '.epub': '📚',
    '.mobi': '📚',
    '.cfg': '📋',
    '.conf': '📋',
    '.exe': '💻',
    '.msi': '💻',
    '.apk': '📱',
    '.ipa': '📱',
    '.mp3': '🎵',
    '.wav': '🎵',
    '.flac': '🎵',
    '.aac': '🎵',
    '.ogg': '🎵',
    '.iso': '💿',
    '.img': '💿',
    '.bin': '💿',
    '.html': '🌐',
    '.htm': '🌐',
    '.css': '🌐',
    '.js': '🌐',
    '.json': '🗂️',
    '.config': '📋'
}


def get_files_list(directory_path):
    items = os.listdir(directory_path)
    return sorted(items,
                  key=lambda item: (not os.path.isdir(os.path.join(directory_path, item)), os.path.splitext(item)[1]))


def generate_files_list(directory_path):
    text = f'📂 Текущая директория: <code>{directory_path}</code>\n'
    try:
        items = get_files_list(directory_path)

        for item in items:
            if item != items[-1]:
                branch_symbol = '┣'
            else:
                branch_symbol = '┗'

            if os.path.isdir(os.path.join(directory_path, item)):
                icon = file_icons['folders']
            else:
                file_name, ext = os.path.splitext(item)
                icon = file_icons.get(ext, '📄')

            text = text + f'{branch_symbol}{icon} <code>{item}</code>\n'

        return text, directory_path

    except Exception as e:
        if 'WinError 5' in str(e):
            print(f'по пути {directory_path} отказ в доступе')
        elif 'WinError 3' in str(e):
            print(f'путь {directory_path} не найден')
