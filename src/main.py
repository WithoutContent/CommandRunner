import os
import json
import keyboard
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import webbrowser

global_list = {
    "last_item": "",
    "save": False,

    "root": None,
    "command_dir": "",
    "tree": None,

    "main_page": None,
    "adv_page": None,
    "func_page": None,

    "keybind_menu": None,
    "program_menu": None
}

def add_bool(parent,name,row):
    var = tk.BooleanVar()
    var.trace_add("write",check_save)
    ttk.Checkbutton(parent,text=name,variable=var).grid(row=row,column=0,sticky="nw")
    return var

def add_spin(parent,name,from_,to,row):
    var = tk.IntVar(value=from_)
    var.trace_add("write",check_save)
    ttk.Label(parent,text=name).grid(row=row,column=1,sticky="ne",padx=(40,0))
    ttk.Spinbox(parent,from_=from_,to=to,textvariable=var,width=10).grid(row=row,column=2,sticky="nw")
    return var

def check_state(var,parent):
    state = "normal" if var.get() else "disabled"
    for n in parent.winfo_children():
        if isinstance(n, (ttk.Checkbutton,ttk.Spinbox)):
            n.configure(state=state)

def get_data(file):
    print(f"Getting data from: {file}")
    with open(file,"r",encoding="utf-8") as f:
        return json.load(f)

def write_data(file,w):
    print(f"Writing data: {w}\nTo file: {file}")
    with open(file,"w",encoding="utf-8") as f:
        json.dump(w,f,indent=4)

def check_save(*args):
    global global_list
    if global_list["last_item"]: global_list["save"] = True

def close():
    print("Closing window")
    global global_list
    if global_list["save"]:
        message = messagebox.askyesnocancel(title="Save",message="Do you want to save?")
        if global_list["save"] == True:
            if message == True and global_list["keybind_menu"]:
                global_list["keybind_menu"].save()
            elif message == None:
                return
    if global_list["root"]: global_list["root"].destroy()

def on_press(event):
    global global_list
    m_p = global_list["main_page"]
    root = global_list["root"]
    if not m_p or not root: return
    if m_p.recording:
        if event.name == "esc" or type(root.focus_get()).__name__ != "window":
            m_p.record()
            return
        if not event.name in m_p.typed_keybind:
            m_p.typed_keybind.append(event.name)
            m_p.typed_keybind = [x for x in m_p.typed_keybind if x in keyboard.all_modifiers] + [x for x in m_p.typed_keybind if not x in keyboard.all_modifiers]
            m_p.keybind_var.set("+".join(m_p.typed_keybind).upper())

keyboard.on_press(on_press)

class left_side(ttk.Treeview):
    def __init__(self,p,retrive_data):
        super().__init__(p,show="headings",selectmode="extended",columns=("Name", "Keybind"))
        self.retrive_data = retrive_data

        self.grid(column=0, row=0, padx=(10,0), pady=10, sticky="nsew")

        for n in ["Name","Keybind"]:
            self.column(n,anchor=tk.W,width=80)
            self.heading(n,text=n,anchor="w")

        self.tag_configure('oddrow', background='#E8E8E8')
        self.tag_configure('evenrow', background='#FFFFFF')
    
        self.bind("<ButtonRelease-1>", self.click)

    def insert_data(self):
        try:
            for i,data in enumerate(self.retrive_data()):
                self.insert(
                    parent="",
                    index=i,
                    values=[
                        data["displayName"],
                        data["keybind"].upper(),
                        data["file"]
                    ],
                    tags=("evenrow") if i % 2 == 0 else ("oddrow")
                    )
        except Exception as e:
            print(f"Something went wrong while inserting data to tree: {e}")

    def click(self,*args):
        selection_ = self.selection()
        if not selection_: return
        global global_list
        focus = self.focus()
        tempitem = selection_[0] if len(selection_) == 1 or selection_[0] != focus else selection_[-1]
        if tempitem == global_list["last_item"]: return

        if global_list["save"] and messagebox.askyesno(title="Save",message="Do you want to save?"):
            global_list["keybind_menu"].save()

        global_list["last_item"] = tempitem

        item_values = self.item(global_list["last_item"], "values")
        data = get_data(item_values[2])
        data["file"] = item_values[2]

        if global_list["main_page"]: global_list["main_page"].change_var(data)
        if global_list["adv_page"]: global_list["adv_page"].change_var(data)
        if global_list["func_page"]: global_list["func_page"].change_var(data)

        global_list["save"] = False

    def refresh(self):
        global global_list
        global_list["last_item"] = ""
        for item in self.get_children():
            self.delete(item)
        self.insert_data()

class main_page(ttk.Frame):
    def __init__(self,p,root):
        super().__init__(p,padding=5)
        self.root = root
        self.pack(fill="both",expand=True)
        self.columnconfigure(1, weight=1)

        ttk.Label(self,text="Name:").grid(row=0,column=0,sticky=tk.W,pady=2)
        self.name_var = tk.StringVar()
        self.name_var.trace_add("write",check_save)
        ttk.Entry(self,textvariable=self.name_var).grid(row=0,column=1,sticky=tk.EW,pady=2,columnspan=2)

        ttk.Label(self,text="File Path:").grid(row=1,column=0,sticky=tk.W,pady=2)
        self.fullPath_var = tk.StringVar()
        ttk.Entry(self,textvariable=self.fullPath_var,state="readonly").grid(row=1,column=1,sticky=tk.EW,pady=2,columnspan=2)

        ttk.Label(self,text="Keybind:").grid(row=2,column=0,sticky=tk.W,pady=2)
        self.keybind_var = tk.StringVar()
        self.keybind_var.trace_add("write",check_save)
        ttk.Entry(self,textvariable=self.keybind_var,state="readonly").grid(row=2,column=1,sticky=tk.EW,pady=2)

        self.recording = False
        self.last_keybind = ""
        self.typed_keybind = []
        self.record_button = ttk.Button(self,text="Record",command=self.record)
        self.record_button.grid(row=2,column=2,sticky=tk.EW,pady=2)
    
        self.disabled_var = tk.BooleanVar()
        self.disabled_var.trace_add("write",check_save)
        ttk.Checkbutton(self,text="Disabled",variable=self.disabled_var).grid(row=3,column=0,sticky=tk.EW,pady=2,columnspan=2)

        ttk.Label(self,text="Command:").grid(row=4,column=0,pady=(10,0))
        self.command_text = tk.Text(self,wrap="none",width=1)
        self.command_text.grid(row=5,column=0,columnspan=3,sticky="nsew")
        self.command_text.bind("<KeyRelease>",check_save)

    def change_var(self,data):
        try:
            self.name_var.set(data["displayName"])
            self.fullPath_var.set(data["file"])
            self.keybind_var.set(data["keybind"].upper())
            self.disabled_var.set(data["disabled"])
            self.command_text.delete(0.0,"end")
            self.command_text.insert(0.0,data["command"])
        except Exception as e:
            print(f"Something went wrong while changing data in main page: {e}")

    def record(self):
        self.recording = not self.recording
        self.root.focus_set()
        if self.recording:
            self.record_button.configure(text="Recording...")
            self.last_keybind = self.keybind_var.get()
            self.keybind_var.set("")
        else:
            self.record_button.configure(text="Record")
            if len(self.typed_keybind) == 0:
                self.keybind_var.set(self.last_keybind)
            else:
                self.keybind_var.set("+".join(self.typed_keybind).upper())
        self.typed_keybind = []

class adv_page(ttk.Frame):
    def __init__(self,p):
        super().__init__(p,padding=5)
        self.pack(fill="both",expand=True)
        self.columnconfigure(1, weight=1)

        self.adv_var = tk.BooleanVar()
        self.adv_var.trace_add("write",check_save)
        ttk.Checkbutton(self,text="Advanced Settings",variable=self.adv_var,command=lambda: check_state(self.adv_var,self.adv_labelframe)).grid(row=0,column=0,pady=5)

        self.adv_labelframe = ttk.LabelFrame(self,text="Settings",padding=5)
        self.adv_labelframe.grid(row=1,column=0,columnspan=2,sticky="nsew")

        self.console_var = add_bool(self.adv_labelframe,"Console",0)
        self.shell_var = add_bool(self.adv_labelframe,"Shell",1)
        self.suppress_var = add_bool(self.adv_labelframe,"Suppress",2)
        self.trigger_on_release = add_bool(self.adv_labelframe,"Trigger on release",3)

        self.keyT_var = add_spin(self.adv_labelframe,"Key timeout (s):",1,10,0)

    def change_var(self,data):
        try:
            adv = data["advanced"]

            self.adv_var.set(adv["enable"])
            self.console_var.set(adv["console"])
            self.suppress_var.set(adv["suppress"])
            self.shell_var.set(adv["shell"])
            self.trigger_on_release.set(adv["trigger_on_release"])
            self.keyT_var.set(adv["key_timeout"])

            check_state(self.adv_var,self.adv_labelframe)
        except Exception as e:
            print(f"Something went wrong while changing data in advanced page: {e}")

class func_page(ttk.Frame):
    def __init__(self,p):
        super().__init__(p,padding=5)
        self.pack(fill="both",expand=True)
        self.columnconfigure(1, weight=1)

        self.func_var = tk.BooleanVar()
        self.func_var.trace_add("write",check_save)
        ttk.Checkbutton(self,text="Custom Functions",variable=self.func_var,command=lambda: check_state(self.func_var,self.func_labelframe)).grid(row=0,column=0,pady=5)

        self.func_labelframe = ttk.LabelFrame(self,text="Functions",padding=5)
        self.func_labelframe.grid(row=1,column=0,columnspan=2,sticky="nsew")

        self.mouse_var = add_bool(self.func_labelframe,"Mouse",0)
        self.clipboard_var = add_bool(self.func_labelframe,"Clipboard",1)
        self.path_var = add_bool(self.func_labelframe,"Path",2)
        self.system_var = add_bool(self.func_labelframe,"System",3)
        self.window_var = add_bool(self.func_labelframe,"Window",4)
        self.input_var = add_bool(self.func_labelframe,"Input",5)

    def change_var(self,data):
        try:
            func = data["functions"]

            self.func_var.set(func["enable"])
            self.mouse_var.set(func["mouse"])
            self.clipboard_var.set(func["clipboard"])
            self.path_var.set(func["path"])
            self.system_var.set(func["system"])
            self.window_var.set(func["window"])
            self.input_var.set(func["input"])

            check_state(self.func_var,self.func_labelframe)
        except Exception as e:
            print(f"Something went wrong while changing data in functions page: {e}")

class toplevel(tk.Toplevel):
    def __init__(self):
        super().__init__()

        self.title("Naming new file")

        padding = {"padx":5,"pady":5}
        ttk.Label(self,text="Enter name:").pack(**padding)
        self.enter_var = tk.StringVar()
        ttk.Entry(self,textvariable=self.enter_var,width=30).pack(padx=5)
        ttk.Button(self,text="Continue",command=self.button).pack(**padding)

    def button(self):
        global global_list
        cd = global_list["command_dir"]
        if not cd or not global_list["tree"]: return

        name = self.enter_var.get() or "New Command"
        self.destroy()

        if os.path.exists(f"{cd}\\{name}.json"):
            messagebox.showerror(title="File already exists",message="You cannot make a file with the same name as another file")
            return
        
        data = {
            "displayName": name,
            "command": "",
            "keybind": "",
            "disabled": False,
            "advanced": {
                "enable": False,
                "console": False,
                "shell": False,
                "suppress": False,
                "trigger_on_release": False,
                "key_timeout": 1
            },
            "functions": {
                "enable": False,
                "mouse": False,
                "clipboard": False,
                "path": False,
                "system": False,
                "window": False,
                "input": False
            }
        }

        write_data(f"{cd}\\{name}.json",data)
        print("New command has been created")
        global_list["tree"].refresh()

class keybind_menu(tk.Menu):
    def __init__(self,p,reset_hotkeys):
        super().__init__(p,tearoff=False)
        self.reset_hotkeys = reset_hotkeys

        self.add_command(label="New keybind",command=self.new)
        self.add_separator()
        self.add_command(label="Open",command=self.open)
        self.add_separator()
        self.add_command(label="Save",command=self.save)
        self.add_command(label="Save as",command=self.save_as)
        self.add_separator()
        global global_list
        if global_list["tree"]: self.add_command(label="Refresh table",command=global_list["tree"].refresh)
        self.add_separator()
        self.add_command(label="Delete",command=self.delete)

    def new(self):
        print("New command creation")
        toplevel()
    
    def open(self):
        print("Opening command")
        global global_list
        cd = global_list["command_dir"]
        if not cd or not global_list["tree"]: return

        file_path = filedialog.askopenfilename(
            defaultextension=".json",
            filetypes=[
                ("Json files", "*.json")
            ]
        )
        if not file_path: return
        file_name_s = os.path.splitext(os.path.basename(file_path))[0]
        add = ""

        if os.path.exists(f"{cd}\\{file_name_s}.json"):
            i = 1
            while os.path.exists(f"{cd}\\{file_name_s}{i}.json"):
                i += 1
            file_name_s += str(i)
            add = f" {i}"

        data = get_data(file_path)
        data["displayName"] += add
        write_data(f"{cd}\\{file_name_s}.json",data)
        global_list["tree"].refresh()
        self.reset_hotkeys()

    def update_data(self,data):
        global global_list
        m_p = global_list["main_page"]
        a_p = global_list["adv_page"]
        f_p = global_list["func_page"]
        if not m_p or not a_p or not f_p: return
        data["displayName"] = m_p.name_var.get()
        data["keybind"] = m_p.keybind_var.get()
        data["command"] = m_p.command_text.get(1.0,tk.END)
        data["disabled"] = m_p.disabled_var.get()

        data["advanced"]["enable"] = a_p.adv_var.get()
        data["advanced"]["console"] = a_p.console_var.get()
        data["advanced"]["shell"] = a_p.shell_var.get()
        data["advanced"]["suppress"] = a_p.suppress_var.get()
        data["advanced"]["trigger_on_release"] = a_p.trigger_on_release.get()
        data["advanced"]["key_timeout"] = a_p.keyT_var.get()

        data["functions"]["enable"] = f_p.func_var.get()
        data["functions"]["mouse"] = f_p.mouse_var.get()
        data["functions"]["clipboard"] = f_p.clipboard_var.get()
        data["functions"]["path"] = f_p.path_var.get()
        data["functions"]["system"] = f_p.system_var.get()
        data["functions"]["window"] = f_p.window_var.get()
        data["functions"]["input"] = f_p.input_var.get()
        return data

    def save(self):
        print("Saving command")
        global global_list
        if not global_list["last_item"] or not global_list["tree"]: return
        item_values = global_list["tree"].item(global_list["last_item"],"values")
        file = item_values[2]

        data = self.update_data(get_data(file))
        write_data(file,data)
        global_list["save"] = False
        self.reset_hotkeys()

    def save_as(self):
        print("Saving command as")
        global global_list
        if not global_list["last_item"] or not global_list["tree"]: return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[
                ("Json files", "*.json"),
                ("All files", "*.*")
            ]
        )
        if not file_path: return
        item_values = global_list["tree"].item(global_list["last_item"],"values")
        file = item_values[2]

        data = self.update_data(get_data(file))
        write_data(file_path,data)
        global_list["save"] = False

    def delete(self):
        print("Deleting command")
        if not messagebox.askyesno(title="Keybind deletion",message="Are you sure you want to delete this keybind PERMAMENTLY?"): return
        global global_list
        if not global_list["last_item"] or not global_list["tree"]: return
        selection_ = global_list["tree"].selection()
        for n in selection_:
            item_values = global_list["tree"].item(n,"values")
            file = item_values[2]
            os.remove(file)
        global_list["last_item"] = ""
        global_list["tree"].refresh()
        global_list["save"] = False
        self.reset_hotkeys()

class program_menu(tk.Menu):
    def __init__(self,p,reset_hotkeys,terminate):
        super().__init__(p,tearoff=False)

        global global_list
        self.add_command(label="Open command folder",command=lambda: os.startfile(global_list["command_dir"]))
        self.add_separator()
        self.add_command(label="Close",command=close)
        self.add_command(label="Restart hoykeys",command=reset_hotkeys)
        self.add_command(label="Terminate",command=terminate)

class help_menu(tk.Menu):
    def __init__(self,p):
        super().__init__(p,tearoff=False)

        self.add_command(label="Github",command=lambda: webbrowser.open("https://github.com/WithoutContent/CommandRunner"))
        self.add_command(label="Custom functions documentation",command=lambda: webbrowser.open("https://github.com/WithoutContent/CommandRunner#custom-functions"))
        self.add_command(label="Advanced settings documentation",command=lambda: webbrowser.open("https://github.com/WithoutContent/CommandRunner#advanced-settings"))

class window(tk.Tk):
    def __init__(self):
        super().__init__()

        self.geometry("600x250")

        try:
            self.iconbitmap("icon.ico")
        except Exception as e:
            print(f"Something went wrong while trying to set gui's icon: {e}")

        self.title("Command Runner")

        self.columnconfigure(0,weight=1)
        self.columnconfigure(2,weight=4)
        self.rowconfigure(0,weight=1)

        self.protocol("WM_DELETE_WINDOW", close)

def create_window(COMMAND_DIR,retrive_data,reset_hotkeys,terminate):
    print("Creating new window")
    global global_list
    global_list = {
        "last_item": "",
        "save": False,

        "root": None,
        "command_dir": "",
        "tree": None,

        "main_page": None,
        "adv_page": None,
        "func_page": None,

        "keybind_menu": None,
        "program_menu": None
    }

    root = window()
    global_list["root"] = root
    global_list["command_dir"] = COMMAND_DIR

    tree = left_side(root,retrive_data)
    tree.insert_data()
    global_list["tree"] = tree

    scrollbar = ttk.Scrollbar(root,orient="vertical",command=tree.yview)
    scrollbar.grid(column=1, row=0, padx=(0, 10), pady=10, sticky="ns")
    tree.configure(yscrollcommand=scrollbar.set)

    notebook = ttk.Notebook(root)
    notebook.grid(column=2, row=0, pady=10, padx=10, sticky="nsew", columnspan=3)

    m_p = main_page(notebook,root)
    a_p = adv_page(notebook)
    f_p = func_page(notebook)

    global_list["main_page"] = m_p
    global_list["adv_page"] = a_p
    global_list["func_page"] = f_p

    notebook.add(m_p, text="Main")
    notebook.add(a_p, text="Advanced")
    notebook.add(f_p, text="Functions")

    toolbar = tk.Menu(root)
    root.config(menu=toolbar)

    keybind_m = keybind_menu(toolbar,reset_hotkeys)
    global_list["keybind_menu"] = keybind_m
    program_m = program_menu(toolbar,reset_hotkeys,terminate)
    global_list["program_menu"] = program_m

    toolbar.add_cascade(label="Keybind",menu=keybind_m)
    toolbar.add_cascade(label="Program",menu=program_m)
    toolbar.add_cascade(label="Help",menu=help_menu(toolbar))

    sizegrip = ttk.Sizegrip(root)
    sizegrip.place(relx=1.0, rely=1.0, anchor=tk.CENTER, x=-10, y=-10)
    sizegrip.lift()

    root.mainloop()
