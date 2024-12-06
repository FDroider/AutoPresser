from time import sleep
from pynput.keyboard import Listener, KeyCode, HotKey
from pyautogui import mouseDown, mouseUp
from pyautogui import keyUp, keyDown
from pyautogui import PyAutoGUIException

class MouseControl:
    def __init__(self, button: str, duration: float = 0.0):
        super().__init__()
        self.btn_click = button.lower()
        if button.lower() in ("shift", "alt", "ctrl"):
            self.btn_click = f"{button.lower()}left"
        self.duration = duration
        self.mouse_pressed = False

    def start_mouse_down(self):
        self.mouse_pressed = True
        try:
            mouseDown(button=self.btn_click)
        except PyAutoGUIException:
            keyDown(self.btn_click)
        if self.duration != 0.0:
            sleep(self.duration)
            try:
                mouseUp(self.btn_click)
            except PyAutoGUIException:
                keyUp(self.btn_click)
            self.mouse_pressed = False

    def stop_mouse_down(self):
        self.mouse_pressed = False
        try:
            mouseUp(button=self.btn_click)
        except PyAutoGUIException:
            keyUp(self.btn_click)

    def start(self):
        if self.mouse_pressed is True:
            self.stop_mouse_down()
        else:
            self.start_mouse_down()


async def start_one_key(start_key, button, *args):
    global app, listener

    duration = 0.0 if args[0] == "" or float(args[0]) < 0.0 else float(args[0])

    app = MouseControl(button, duration)

    def on_press(key):
        if key == KeyCode(char=start_key):
            app.start()

    with Listener(on_press=on_press) as listener:
        listener.join()


async def start_two_keys(start_key, start_two_key, button, *args):
    global app, listener

    duration = 0.0 if args[0][0] == "" or float(args[0][0]) < 0.0 else float(args[0][0])

    app = MouseControl(button, duration)

    hotkey = HotKey((HotKey.parse(f"<{start_key}>+{start_two_key}")),
                    on_activate=app.start)

    def on_press(f):
        return lambda k: f(listener.canonical(k))

    with Listener(on_press=on_press(hotkey.press), on_release=on_press(hotkey.release)) as listener:
        listener.join()


async def stop():
    app.stop_mouse_down()
    listener.stop()