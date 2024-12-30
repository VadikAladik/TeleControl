import psutil
import os


def get_drives():
    partitions = psutil.disk_partitions()
    drives = []
    for partition in partitions:
        drives.append(partition.device)
    return drives


def get_memory_info():
    memory_info = psutil.virtual_memory()
    total_memory = memory_info.total / (1024 ** 2)
    used_memory = memory_info.used / (1024 ** 2)
    free_memory = memory_info.available / (1024 ** 2)

    process = psutil.Process(os.getpid())
    program_memory = process.memory_info().rss / (1024 ** 2)

    return total_memory, used_memory, free_memory, program_memory
