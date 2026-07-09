import win32com.client
import os

def clear_selection():
    shell = win32com.client.Dispatch("Shell.Application")

    for window in shell.Windows():
        try:
            view = window.Document
            items = view.SelectedItems()
            for item in items:
                view.SelectItem(item, 0)
        except:
            pass
    return ""

def get_selected_files():
    shell = win32com.client.Dispatch("Shell.Application")
    paths = []

    for window in shell.Windows():
        try:
            doc = window.Document
            selected = doc.SelectedItems()
            for item in selected:
                paths.append(item.Path)
        except:
            pass
    return paths

####################

def selected_full_path():
    files = get_selected_files()
    if files: return files[0]
    
def selected_full_name():
    file = selected_full_path()
    if file: return os.path.basename(file)

def selected_name():
    name = selected_full_name()
    if name: return os.path.splitext(name)[0]

def selected_extension():
    name = selected_full_name()
    if name: return os.path.splitext(name)[1]

def selected_dir():
    file = selected_full_path()
    if file : return os.path.dirname(os.path.abspath(file))
    
def selected_count():
    return len(get_selected_files())