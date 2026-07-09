import win32gui
import win32process
import psutil

def get_focused_win_hwnd():
    try:
        return win32gui.GetForegroundWindow()
    except:
        pass

#######

def focused_window_hwnd():
    hwnd = get_focused_win_hwnd()
    if hwnd: return hwnd

def focused_window_title():
    hwnd = focused_window_hwnd()
    if hwnd: return win32gui.GetWindowText(hwnd)

def focused_window_class():
    hwnd = focused_window_hwnd()
    if hwnd: return win32gui.GetClassName(hwnd)

def focused_window_pid():
    hwnd = focused_window_hwnd()
    if hwnd:
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        return pid

def focused_window_process_name():
    pid = focused_window_pid()
    if pid: return psutil.Process(pid).name()

def focused_window_process_path():
    pid = focused_window_pid()
    if pid: return psutil.Process(pid).exe()

def focused_window_x():
    hwnd = focused_window_hwnd()
    if hwnd: return win32gui.GetWindowRect(hwnd)[0]

def focused_window_y():
    hwnd = focused_window_hwnd()
    if hwnd: return win32gui.GetWindowRect(hwnd)[1]

def focused_window_w():
    hwnd = focused_window_hwnd()
    if hwnd:
        rect = win32gui.GetWindowRect(hwnd)
        return rect[2]-rect[0]
    
def focused_window_h():
    hwnd = focused_window_hwnd()
    if hwnd:
        rect = win32gui.GetWindowRect(hwnd)
        return rect[3]-rect[1]