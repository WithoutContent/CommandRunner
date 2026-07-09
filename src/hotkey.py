from tkinter import simpledialog
import keyboard
import subprocess
import pythoncom

import functions.input as m_i
import functions.path as m_p
import functions.system as m_s
import functions.window as m_w

def set_hotkeys(data_list):
    print("Setting up the hotkeys")
    data_list = data_list or []
    for data in data_list:
        try:
            if data["keybind"] and not data["disabled"]:
                keybind = data["keybind"].lower()
                command = data["command"].replace("\n","")

                """Advanced settings"""

                shell = False
                suppress = False
                console = False
                trigger_on_release = False
                key_timeout = 1

                advanced = data.get("advanced")
                if advanced and advanced.get("enable", False):
                    shell = advanced.get("shell", False)
                    suppress = advanced.get("suppress", False)
                    console = advanced.get("console", False)
                    trigger_on_release = advanced.get("trigger_on_release", False)
                    key_timeout = advanced.get("key_timeout", 1)

                if console:
                    shell = True
                    command = ["start","cmd","/c",f"{command} && pause"] 

                """Functions"""

                functions = data.get("functions")
                if functions and functions.get("enable", False):
                    mouse = functions.get("mouse",False)
                    clipboard = functions.get("clipboard",False)
                    path = functions.get("path",False)
                    system = functions.get("system",False)
                    window = functions.get("window",False)
                    input_ = functions.get("input",False)

                    args = {}
                    if mouse:
                        args['mouse(\"x\")'] = m_i.mouse_x
                        args['mouse(\"y\")'] = m_i.mouse_y
                    if clipboard:
                        args["board()"] = m_i.get_clipboard
                    if path:
                        args["clear()"] = m_p.clear_selection
                        args["path()"] = m_p.selected_full_path
                        args["full_name()"] = m_p.selected_full_name
                        args["name()"] = m_p.selected_name
                        args["extension()"] = m_p.selected_extension
                        args["dir()"] = m_p.selected_dir
                        args["count()"] = m_p.selected_count
                    if system:
                        args["s_username()"] = m_s.system_username
                        args["s_hostname()"] = m_s.system_hostname
                        args["s_version()"] = m_s.system_version
                        args["cpu_usage()"] = m_s.cpu_usage
                        args["ram_usage()"] = m_s.ram_usage
                        args["timestamp()"] = m_s.timestamp
                        args["date_time()"] = m_s.date_time
                    if window:
                        args["focus_hwnd()"] = m_w.focused_window_hwnd
                        args["focus_title()"] = m_w.focused_window_title
                        args["focus_class()"] = m_w.focused_window_class
                        args["focus_pid()"] = m_w.focused_window_pid
                        args["focus_process_name()"] = m_w.focused_window_process_name
                        args["focus_process_path()"] = m_w.focused_window_process_path
                        args["focus_x()"] = m_w.focused_window_x
                        args["focus_y()"] = m_w.focused_window_y
                        args["focus_w()"] = m_w.focused_window_w
                        args["focus_h()"] = m_w.focused_window_h

                    keyboard.add_hotkey(keybind,run_command_with_funcs,args=[command,shell,args,input_],suppress=suppress,timeout=key_timeout,trigger_on_release=trigger_on_release)
                else:
                    keyboard.add_hotkey(keybind,run_command,args=[command,shell],suppress=suppress,timeout=key_timeout,trigger_on_release=trigger_on_release)
                print(f"Added a new hotkey!\nKeybind: {keybind}\nCommand: {command}")
        except Exception as e:
            print(f"Error while setting a hotkey: {e}")   

def run_command(command,shell):
    print("Trying to execute a command")
    try:
        result = subprocess.run(command, shell=shell, capture_output=True, text=True)
        print(f"Command executed: {command}")
        print(f"Command Output: {result.stdout}")
    except Exception as e:
        print(f"Something went wrong while trying to run a hotkey: {e}")

def run_command_with_funcs(command,shell,args,input_):
    print("Trying to execute a command with functions")
    pythoncom.CoInitialize()
    try:
        is_list = isinstance(command,list)
        last_c = command
        if is_list:
            command = command.copy()
            last_c = last_c[-1]

        """Input"""

        if input_:
            while True:
                i_start = last_c.find('input(\"')
                if i_start == -1: break
                i_end = last_c[i_start+7:].find('\")')
                if i_end == -1: break
                prompt = last_c[i_start+7:i_end+i_start+7]

                user_input = simpledialog.askstring("", prompt)
                if user_input is None: return

                last_c = f"{last_c[0:i_start]}{user_input}{last_c[i_start+i_end+9:]}"

        """var"""

        for key,value in args.items():
            if last_c.find(key) != -1:
                v = value() or ""
                if not isinstance(v, str):
                    v = str(v)
                last_c = last_c.replace(key,v)

        """result"""

        if is_list:
            command[-1] = last_c
        else:
            command = last_c

        result = subprocess.run(command, shell=shell, capture_output=True, text=True)
        print(f"Command executed: {command}")
        print(f"Command Output: {result.stdout}")
    except Exception as e:
        pythoncom.CoUninitialize()
        print(f"Something went wrong while trying to run a hotkey (With functions): {e}")

def unhook_hotkeys():
    print("Unhooking all hotkeys...")
    keyboard.unhook_all_hotkeys()