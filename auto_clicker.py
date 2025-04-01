from pyautogui import click, press
from pyautogui import PyAutoGUIException
from pynput.keyboard import Listener, KeyCode, HotKey
from PySide6.QtCore import QThread
from time import sleep
from subprocess import check_output, run
from platform import system
try:
    import win32gui
    import win32con
    import win32api
    from pygetwindow import getWindowsWithTitle
except:
    pass

class AutoClicker(QThread):
    def __init__(self, button: str, delay: float):
        super().__init__()
        self.delay = float(delay)
        self.btn_click = button.lower()
        self.running = False
        self.work_program = True

    def start_clicking(self):
        self.running = True

    def stop_clicking(self):
        self.running = False

    def stop(self):
        self.stop_clicking()
        self.work_program = False

    def run(self):
        while self.work_program:
            while self.running:
                try:
                    click(self.btn_click)
                except PyAutoGUIException:
                    press(self.btn_click)
            sleep(self.delay)

class AutoClickerWindowLinux(AutoClicker):
    def __init__(self, button: str, delay: float, window_name: str):
        super().__init__(button, delay)
        self.window_id = check_output(["xdotool", "search", "--name", f"{window_name}"]).split()[0].decode()
        self.check_button()

    def check_button(self):
        if self.btn_click == "left":
            self.btn_click = 1
        elif self.btn_click == "right":
            self.btn_click = 3
        elif self.btn_click == "middle":
            self.btn_click = 2

    def run(self):
        while self.work_program:
            while self.running:
                if self.btn_click in (1, 2, 3):
                    run(["xdotool", "click", "--window", f"{self.window_id}", f"{self.btn_click}"])
                else:
                    run(["xdotool", "key", "--window", f"{self.window_id}", f"{self.btn_click}"])
            sleep(self.delay)

class AutoClickerWindow(AutoClicker):
    def __init__(self, button: str, delay: float, window_name: str):
        super().__init__(button, delay)
        self.window_handel = win32gui.FindWindow(None, window_name[:-4])
        if self.window_handel in (0, "0") or self.window_handel is None:
            self.window_handel = win32gui.FindWindow(None, getWindowsWithTitle(window_name[:-4])[0].title)
        rect = win32gui.GetWindowRect(self.window_handel)
        self.lParam = win32api.MAKELONG(rect[0]+100, rect[1]+100)

    def send_click(self, button_down, button_up, key=None):
        if key is not None:
            win32api.PostMessage(self.window_handel, win32con.WM_KEYDOWN, hex(win32api.VkKeyScan(key)),
                                 self.lParam)
            win32api.PostMessage(self.window_handel, win32con.WM_KEYUP, hex(win32api.VkKeyScan(key)),
                                 self.lParam)
            return
        win32api.PostMessage(self.window_handel, button_down, 1, self.lParam)
        win32api.PostMessage(self.window_handel, button_up, 0, self.lParam)


    def run(self):
        while self.work_program:
            while self.running:
                if self.btn_click == "left":
                    self.send_click(win32con.WM_LBUTTONDOWN, win32con.WM_LBUTTONUP)
                elif self.btn_click == "right":
                    self.send_click(win32con.WM_RBUTTONDOWN, win32con.WM_RBUTTONUP)
                elif self.btn_click == "middle":
                    self.send_click(win32con.WM_MBUTTONDOWN, win32con.WM_MBUTTONUP)
                else:
                    self.send_click(None, None, self.btn_click)
                sleep(0.2)
            sleep(self.delay)

async def start_one_key(start_key, button, *args):
    global app, listener

    delay = 0.0 if args[0] == "" or float(args[0]) < 0.0 else float(args[0])
    w_name = args[1].rstrip() if args[1] else "auto"

    main_system = system().lower()

    if w_name != "auto" and main_system == "windows":
        app = AutoClickerWindow(button, delay, w_name)
    elif w_name != "auto" and main_system == "linux":
        app = AutoClickerWindowLinux(button, delay, w_name)
    else:
        app = AutoClicker(button, delay)
    app.start()

    def on_press(key):
        if key == KeyCode(char=start_key):
            if app.running:
                app.stop_clicking()
            else:
                app.start_clicking()

    with Listener(on_press=on_press) as listener:
        listener.join()


async def start_two_keys(start_key, start_two_key, button, *args):
    global app, listener

    delay = 0.0 if args[0][0] == "" or float(args[0][0]) < 0.0 else float(args[0][0])
    w_name = args[1].rstrip() if args[1] else "auto"

    main_system = system().lower()

    if w_name != "auto" and main_system == "windows":
        app = AutoClickerWindow(button, delay, w_name)
    elif w_name != "auto" and main_system == "linux":
        app = AutoClickerWindowLinux(button, delay, w_name)
    else:
        app = AutoClicker(button, delay)
    app.start()

    def on_active():
        if not app.running:
            app.start_clicking()
        else:
            app.stop_clicking()

    hotkey = HotKey((HotKey.parse(f"<{start_key}>+{start_two_key}")),
                    on_activate=on_active)

    def on_press(f):
        return lambda k: f(listener.canonical(k))

    with Listener(on_press=on_press(hotkey.press)) as listener:
        listener.join()


async def stop():
    app.stop()
    listener.stop()