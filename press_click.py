from time import sleep
from pynput.keyboard import Listener, KeyCode, HotKey
from pyautogui import mouseDown, mouseUp
from pyautogui import keyUp, keyDown
from pyautogui import PyAutoGUIException
from subprocess import run, check_output
from platform import system
try:
    import win32gui
    import win32con
    import win32api
    from pygetwindow import getWindowsWithTitle
except:
    pass

class MouseControl:
    def __init__(self, button: str, duration: float = 0.0):
        self.btn_click = button.lower()
        if self.btn_click in ("shift", "alt", "ctrl"):
            self.btn_click = f"{button.lower()}left"
        self.duration = duration
        self.mouse_pressed = False

    def btn_down(self):
        self.mouse_pressed = True
        try:
            mouseDown(button=self.btn_click)
        except PyAutoGUIException:
            keyDown(self.btn_click)
        if self.duration != 0.0:
            sleep(self.duration)
            self.btn_up()

    def btn_up(self):
        self.mouse_pressed = False
        try:
            mouseUp(button=self.btn_click)
        except PyAutoGUIException:
            keyUp(self.btn_click)

    def start(self):
        if self.mouse_pressed is True:
            self.btn_up()
        else:
            self.btn_down()

    def stop(self):
        self.btn_up()


class MouseControlWindowLinux(MouseControl):
    def __init__(self, button: str, duration: float, window_name: str):
        super().__init__(button, duration)
        self.window_id = check_output(["xdotool", "search", "--name", f"{window_name}"]).split()[0].decode()
        self.check_button()

    def check_button(self):
        if self.btn_click == "left":
            self.btn_click = 1
        elif self.btn_click == "right":
            self.btn_click = 3
        elif self.btn_click == "middle":
            self.btn_click = 2

    def btn_down(self):
        self.mouse_pressed = True
        try:
            if self.btn_click in ("left", "right", "middle"):
                    run(["xdotool", "mousedown", f"--window", f"{self.window_id}", f"{self.btn_click}"])
            else:
                    run(["xdotool", "keydown", f"--window", f"{self.window_id}", f"{self.btn_click}"])
        except FileNotFoundError:
            raise FileNotFoundError("Not found xdotool. Please install it for correct work app")
        if self.duration != 0.0:
            sleep(self.duration)
            self.btn_up()

    def btn_up(self):
        self.mouse_pressed = False
        try:
            if self.btn_click in ("left", "right", "middle"):
                    run(["xdotool", "mouseup", f"--window", f"{self.window_id}", f"{self.btn_click}"])
            else:
                    run(["xdotool", "keyup", f"--window", f"{self.window_id}", f"{self.btn_click}"])
        except FileNotFoundError:
            raise FileNotFoundError("Not found xdotool. Please install it for correct to work app")


class MouseControlWindow(MouseControl):
    def __init__(self, button, duration: float, window_name: str):
        super().__init__(button, duration)
        self.window_handel = win32gui.FindWindow(None, window_name[:-4])
        if self.window_handel in (0, "0") or self.window_handel is None:
            self.window_handle = win32gui.FindWindow(None, getWindowsWithTitle(window_name[:-4])[0].title)
        rect = win32gui.GetWindowRect(self.window_handle)
        self.lParam = win32api.MAKELONG(rect[0] + 100, rect[1] + 100)

    def btn_down(self):
        if self.btn_click == "left":
            win32api.PostMessage(self.window_handel, win32con.WM_LBUTTONDOWN, 1, self.lParam)
        elif self.btn_click == "right":
            win32api.PostMessage(self.window_handel, win32con.WM_RBUTTONDOWN, 1, self.lParam)
        elif self.btn_click == "middle":
            win32api.PostMessage(self.window_handel, win32con.WM_MBUTTONDOWN, 1, self.lParam)
        else:
            win32api.PostMessage(self.window_handel, win32con.WM_KEYDOWN, hex(win32api.VkKeyScan(self.btn_click)),
                                 self.lParam)
        if self.duration != 0.0:
            sleep(self.duration)
            self.btn_up()

    def btn_up(self):
        if self.btn_click == "left":
            win32api.PostMessage(self.window_handel, win32con.WM_LBUTTONUP, 0, self.lParam)
        elif self.btn_click == "right":
            win32api.PostMessage(self.window_handel, win32con.WM_RBUTTONUP, 0, self.lParam)
        elif self.btn_click == "middle":
            win32api.PostMessage(self.window_handel, win32con.WM_MBUTTONUP, 0, self.lParam)
        else:
            win32api.PostMessage(self.window_handel, win32con.WM_KEYUP, hex(win32api.VkKeyScan(self.btn_click)),
                                 self.lParam)


async def start_one_key(start_key, button, *args):
    global app, listener

    duration = 0.0 if args[0] == "" or float(args[0]) < 0.0 else float(args[0])
    w_name = args[1].rstrip() if args[1] else "auto"

    main_system = system().lower()

    if w_name != "auto" and main_system == "windows":
        app = MouseControlWindow(button, duration, w_name)
    elif w_name != "auto" and main_system == "linux":
        app = MouseControlWindowLinux(button, duration, w_name)
    else:
        app = MouseControl(button, duration)

    def on_press(key):
        if key == KeyCode(char=start_key):
            app.start()

    with Listener(on_press=on_press) as listener:
        listener.join()


async def start_two_keys(start_key, start_two_key, button, *args):
    global app, listener

    duration = 0.0 if args[0][0] == "" or float(args[0][0]) < 0.0 else float(args[0][0])
    w_name = args[1] if args[1] else "auto"

    main_system = system().lower()

    if w_name != "auto" and main_system == "windows":
        app = MouseControlWindow(button, duration, w_name)
    elif w_name != "auto" and main_system == "linux":
        app = MouseControlWindowLinux(button, duration, w_name)
    else:
        app = MouseControl(button, duration)

    hotkey = HotKey((HotKey.parse(f"<{start_key}>+{start_two_key}")),
                    on_activate=app.start)

    def on_press(f):
        return lambda k: f(listener.canonical(k))

    with Listener(on_press=on_press(hotkey.press)) as listener:
        listener.join()


async def stop():
    app.stop()
    listener.stop()