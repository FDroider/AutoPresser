import asyncio
from pyautogui import click, press
from pyautogui import PyAutoGUIException
from pynput.keyboard import Listener, KeyCode, HotKey
from threading import Thread
from time import sleep


class AutoClicker(Thread):
    def __init__(self, button: str, delay: float, interval: float, duration: float):
        super().__init__()
        self.delay = delay
        self.interval = interval
        self.duration = duration
        self.btn_click = button.lower()
        self.running = False
        self.work_program = True

    def start_clicking(self):
        self.running = True

    def stop_clicking(self):
        self.running = False

    def exit(self):
        self.stop_clicking()
        self.work_program = False

    def run(self):
        while self.work_program:
            while self.running:
                try:
                    click(button=self.btn_click, interval=self.interval, duration=self.duration)
                except PyAutoGUIException:
                    press(self.btn_click, interval=self.interval)
                sleep(0.1)
            sleep(self.delay)


async def start_one_key(start_key, stop_key, button, delay=0.5, interval=0.0, duration=0.0):
    global listener, app
    app = AutoClicker(button, delay, interval, duration)
    app.start()

    def on_press(key):
        if key == KeyCode(char=start_key):
            if app.running:
                app.stop_clicking()
            else:
                app.start_clicking()
        elif key == KeyCode(char=stop_key):
            app.exit()
            listener.stop()

    with Listener(on_press=on_press) as listener:
        listener.join()


async def start_two_keys(start_key, start_two_key, stop_key):
    global listener
    app.start()

    def on_active():
        print("Active")

    hotkey = HotKey(HotKey.parse("<shift>+q"), on_activate=on_active)

    def on_press(key):
        if hotkey.press:
                if app.running:
                    app.start_clicking()
                else:
                    app.stop_clicking()
        elif key == KeyCode(char=stop_key):
            app.exit()
            listener.stop()

    with Listener(on_press=on_press) as listener:
        listener.join()


async def stop():
    app.exit()
    listener.stop()


if __name__ == "__main__":
    asyncio.run(start_two_keys(None, None, None))