import getpass
import socket
import platform
import psutil
import time
from datetime import datetime

def system_username():
    return getpass.getuser()

def system_hostname():
    return socket.gethostname()

def system_version():
    return platform.version()

def cpu_usage():
    return psutil.cpu_percent(interval=1)

def ram_usage():
    ram = psutil.virtual_memory()
    return ram.percent

def timestamp():
    return time.time()

def date_time():
    return datetime.now()