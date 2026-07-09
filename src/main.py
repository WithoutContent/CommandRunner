import sys
import os
import json
import win32event
import win32api
import winerror

import hotkey
import gui

if getattr(sys, 'frozen', False):
    MAIN_DIR = os.path.dirname(sys.executable)
else:
    MAIN_DIR = os.path.dirname(os.path.abspath(__file__))

COMMAND_DIR = os.path.join(MAIN_DIR,"commands")

def enable_console():
    import ctypes
    kernel32 = ctypes.windll.kernel32
    
    if not kernel32.GetConsoleWindow():
        kernel32.AllocConsole()

    sys.stdout = open("CONOUT$", "w", encoding="utf-8")
    sys.stderr = open("CONOUT$", "w", encoding="utf-8")
    ctypes.windll.kernel32.SetConsoleTitleW("Super cool console")

    print("Started program with console.")

def retrive_data():
    data_list = []
    try:
        for file in os.listdir(COMMAND_DIR):
            file = os.path.join(COMMAND_DIR,file)
            if file.lower().endswith(".json"):
                try:
                    with open(file,"r",encoding="utf-8") as f:
                        data = json.load(f)
                        data["file"] = file
                        data_list.append(data)
                        print(f"Retrived data: {data}")
                except json.JSONDecodeError as e:
                    print(f"Invalid JSON format: {e}")
                except Exception as e:
                    print(f"Error reading file: {e}")
    except FileNotFoundError as e:
        print(f"Error commands folder doesnt exist: {e}")
        print("Creating commands folder...")
        try:
            os.mkdir(COMMAND_DIR)
            print(f"Directory '{COMMAND_DIR}' created successfully.")
            data_list = retrive_data()
        except FileExistsError:
            print(f"Directory '{COMMAND_DIR}' already exists.")
        except PermissionError:
            print(f"Permission denied: Unable to create '{COMMAND_DIR}'.")
        except Exception as e:
            print(f"An error occurred: {e}")
    except Exception as e:
        print(f"Something went wrong while loading commands folder: {e}")

    return data_list

def reset_hotkeys():
    print("Reseting hotkeys...")
    hotkey.unhook_hotkeys()
    hotkey.set_hotkeys(retrive_data())
    print("Hoykeys has been reset")

def terminate(): 
    print("Terminating whole process...")
    hotkey.unhook_hotkeys()
    sys.exit()

if __name__ == "__main__":
    mutex = win32event.CreateMutex(None, False, "CommandRunner")

    if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
        event = win32event.OpenEvent(win32event.EVENT_MODIFY_STATE, False, "CommandRunnerEvent")
        win32event.SetEvent(event)
        sys.exit()

    event = win32event.CreateEvent(None, False, False, "CommandRunnerEvent")

    retrived_data = retrive_data()
    hotkey.set_hotkeys(retrived_data)

    args = sys.argv[1:]
    if "--console" in args:
        enable_console()
    if "--gui" in args:
        try:
            gui.create_window(COMMAND_DIR,retrive_data,reset_hotkeys,terminate)
        except Exception as e:
            print(f"Something went wrong while starting gui: {e}")

    print(sys.argv)
    print(f"Retrived data: {retrived_data}")

    while True:
        win32event.WaitForSingleObject(event, win32event.INFINITE)
        print("Detected a signal from another process!")
        try:
            gui.create_window(COMMAND_DIR,retrive_data,reset_hotkeys,terminate)
        except Exception as e:
            print(f"Something went wrong while starting gui: {e}")