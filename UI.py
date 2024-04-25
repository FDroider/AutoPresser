import json.decoder

import flet as ft
import auto_clicker
import press_click
from os.path import isfile, exists
from os import makedirs, listdir
from json import loads, dumps
from asyncio import new_event_loop, run
from win32api import GetKeyboardLayoutName, LoadKeyboardLayout


class MainScreen(ft.UserControl):
    __slots__ = ("settings_page", "settings_script_page", "hot_key_page", "key_page", "loop", "advance_menu", "key_tab",
                 "dropdown_script", "btn_start", "btn_stop" "dlg_error", "dlg_info", "dlg_save", "control_script",
                 "btn_area", "screen_view", "btn_settings", "btn_save_bind", "btn_save_preset", "settings", "text_size")

    def __init__(self):
        super().__init__()

        self.lang_user = int

        self.text_size = 14

        self.settings_page = SettingPage(self)

        self.settings_script_page = SettingScriptPage(self)

        self.key_page = OneKey(self)

        self.hot_key_page = HotKey(self)

        if exists("DataSave/config_scripts.json"):
            with open("DataSave/config_scripts.json", "r") as f:
                settings: dict = loads(f.read())
                self.settings_script_page.entry_dur_press = settings.get("duration_press")
                self.settings_script_page.entry_delay_click = settings.get("delay_click")
                self.settings_script_page.entry_dur_click = settings.get("duration_click")
                self.settings_script_page.entry_inter_click = settings.get("interval_click")
                self.settings_script_page.update()

        self.loop = new_event_loop()

        self.advance_menu = ft.PopupMenuButton(items=[ft.PopupMenuItem(text="Settings", on_click=self.open_settings)])

        self.key_tab = ft.Tabs(selected_index=0, tabs=[ft.Tab(text="One key"), ft.Tab(text="Hot-key")],
                               on_change=self.on_change_tabs)

        self.btn_start = ft.FilledTonalButton(text="Start script", on_click=self.start_script)

        self.btn_stop = ft.FilledTonalButton(text="Stop script", visible=False, on_click=self.stop_script)

        self.dropdown_script = ft.Dropdown(label="Chose script", options=[ft.dropdown.Option("Pressed"),
                                                                          ft.dropdown.Option("Auto-clicker")],
                                           width=150, text_size=self.text_size)

        self.title_dlg_ref = ft.Ref[ft.Text]()
        self.content_dlg_ref = ft.Ref[ft.Text]()
        self.dlg_error = ft.AlertDialog(modal=True, title=ft.Text(ref=self.title_dlg_ref, size=self.text_size + 10),
                                        content=ft.Text(ref=self.content_dlg_ref, size=self.text_size),
                                        actions=[ft.FilledButton("Close", on_click=self.close_dlg_err)])

        self.title_dlg_i_ref = ft.Ref[ft.Text]()
        self.content_dlg_i_ref = ft.Ref[ft.Text]()
        self.dlg_info = ft.AlertDialog(modal=True, title=ft.Text(ref=self.title_dlg_i_ref, size=self.text_size + 10),
                                       content=ft.Text(ref=self.content_dlg_i_ref, size=self.text_size),
                                       actions=[ft.TextButton("Close", on_click=self.close_dlg_info)])

        self.btn_settings = ft.ElevatedButton("Settings", color=ft.colors.WHITE70, bgcolor=ft.colors.BLUE_GREY,
                                              style=ft.ButtonStyle(overlay_color=ft.colors.BLACK12),
                                              icon=ft.icons.SETTINGS_SUGGEST, on_click=self.open_settings_scripts)

        self.btn_save_bind = ft.IconButton(bgcolor=ft.colors.GREEN, icon=ft.icons.SAVE_AS, icon_color=ft.colors.WHITE70,
                                           style=ft.ButtonStyle(overlay_color=ft.colors.BLACK12),
                                           on_click=self.save_bind)

        self.btn_save_preset = ft.ElevatedButton("Save presets", color=ft.colors.BLACK87, bgcolor=ft.colors.BLUE,
                                                 style=ft.ButtonStyle(overlay_color=ft.colors.BLACK12),
                                                 icon=ft.icons.SAVE_ALT_SHARP, on_click=self.show_dlg_save)

        self.filename_ref = ft.Ref[ft.TextField]()
        self.keys_ref = ft.Ref[ft.Dropdown]()
        self.dlg_save = ft.AlertDialog(title=ft.Text("Save settings"),
                                       content=ft.Column(
                                           [ft.TextField(label="Enter name for the save", ref=self.filename_ref),
                                            ft.Dropdown(hint_text="Select keys", options=[ft.dropdown.Option("One key"),
                                                                                          ft.dropdown.Option("Hot-key")
                                                                                          ],
                                                        ref=self.keys_ref, value="One key")], height=120),
                                       actions=[ft.ElevatedButton("Cancel", bgcolor=ft.colors.RED,
                                                                  style=ft.ButtonStyle(overlay_color=ft.colors.BLACK12),
                                                                  on_click=self.close_dlg_save),
                                                ft.ElevatedButton("Save", bgcolor=ft.colors.GREEN,
                                                                  style=ft.ButtonStyle(
                                                                      overlay_color=ft.colors.BLACK12),
                                                                  on_click=self.save_preset)])

        self.control_script = ft.Row([self.btn_start, self.btn_stop, self.dropdown_script],
                                     alignment=ft.MainAxisAlignment.CENTER)

        self.btn_area = ft.Row([self.btn_settings, self.btn_save_bind, self.btn_save_preset],
                               alignment=ft.MainAxisAlignment.CENTER)

        self.screen_view = ft.Row([ft.Column([self.key_tab, self.key_page, self.hot_key_page, self.btn_area,
                                              self.control_script],
                                             horizontal_alignment=ft.CrossAxisAlignment.CENTER)],
                                  alignment=ft.MainAxisAlignment.CENTER)
        self.advance_menu_ref = ft.Ref[ft.Row]()

    def build(self):
        return [self.screen_view,
                ft.Row([self.advance_menu], alignment=ft.alignment.top_left, ref=self.advance_menu_ref),
                self.settings_page, self.settings_script_page]

    def set_lang_key(self, lang):
        self.lang_user = lang

    def get_lang_key(self):
        return self.lang_user

    def on_change_tabs(self, e):
        select_index = self.key_tab.selected_index
        if select_index == 0:
            self.key_page.visible = True
            self.hot_key_page.visible = False
        else:
            self.hot_key_page.visible = True
            self.key_page.visible = False
        self.update()

    def start_script(self, e):
        select = self.key_tab.selected_index

        if self.dropdown_script.value not in ("Pressed", "Auto-clicker"):
            self.show_err_dlg("RuntimeError", "Please chose script for start")
            return

        select_script = self.dropdown_script.value.replace('-', '_')

        if self.key_page.switch_button.value:
            key = self.key_page.press_key.value
            if key.replace(" ", "") == "":
                self.show_err_dlg("ValueError", "Please enter key on which press")
                return

        LoadKeyboardLayout(self.lang_user, 1)

        if select == 0:
            key_start = self.key_page.entry_key.value

            if key_start.replace(" ", "") == "":
                self.show_err_dlg("ValueError", "Please enter activation key")
                return

            if self.key_page.switch_button.value:
                key_press = self.key_page.press_key.value.lower()
            else:
                key_press = self.key_page.dropdown_button.value.lower()

            self.dropdown_script.disabled = True

            self.btn_start.visible = False
            self.btn_stop.visible = True

            self.control_script.update()

            if select_script == "Pressed":
                setting = float(self.settings_script_page.entry_dur_press.value)

                self.loop.run_until_complete(press_click.start_one_key(key_start, None, key_press, setting))

            elif select_script == "Auto_clicker":
                settings = (float(self.settings_script_page.entry_delay_click.value),
                            float(self.settings_script_page.entry_dur_click.value),
                            float(self.settings_script_page.entry_inter_click.value))

                self.loop.run_until_complete(auto_clicker.start_one_key(key_start, None, key_press,
                                                                        settings[0], settings[1], settings[2]))
        else:
            key_first = self.hot_key_page.dropdown_key.value.lower()
            key_second = self.hot_key_page.entry_second_key.value.lower()

            if key_second == "" or key_second == " ":
                self.show_err_dlg("ValueError", "Please enter activation key")
                return

            if self.key_page.switch_button.value:
                key_press = self.hot_key_page.press_key.value.lower()
            else:
                key_press = self.hot_key_page.dropdown_button.value.lower()

            self.dropdown_script.disabled = True

            self.btn_start.visible = False
            self.btn_stop.visible = True

            self.control_script.update()

            if select_script == "Pressed":
                setting = float(self.settings_script_page.entry_dur_press.value)

                self.loop.run_until_complete(press_click.start_two_keys(key_first, key_second, None, key_press,
                                                                        setting))

            elif select_script == "Auto_clicker":
                settings = (float(self.settings_script_page.entry_delay_click.value),
                            float(self.settings_script_page.entry_dur_click.value),
                            float(self.settings_script_page.entry_inter_click.value))

                self.loop.run_until_complete(auto_clicker.start_two_keys(key_first, key_second, None, key_press,
                                                                         settings[0], settings[1], settings[2]))

    def stop_script(self, e):
        self.dropdown_script.disabled = False
        run_script = self.dropdown_script.value.replace('-', '_')

        if run_script == "Pressed":
            run(press_click.stop())
        elif run_script == "Auto_clicker":
            run(auto_clicker.stop())

        self.btn_stop.visible = False
        self.btn_start.visible = True

        self.control_script.update()

    def show_err_dlg(self, title: str, content: str):
        self.title_dlg_ref.current.value = title
        self.content_dlg_ref.current.value = content
        self.page.dialog = self.dlg_error
        self.dlg_error.open = True
        self.page.update()

    def show_dlg_info(self, title: str, content: str):
        self.title_dlg_i_ref.current.value = title
        self.content_dlg_i_ref.current.value = content
        self.page.dialog = self.dlg_info
        self.dlg_info.open = True
        self.page.update()

    def close_dlg_err(self, e):
        self.dlg_error.open = False
        self.page.update()

    def close_dlg_info(self, e):
        self.dlg_info.open = False
        self.page.update()

    def open_settings(self, e):
        self.screen_view.visible = False
        self.advance_menu_ref.current.visible = False
        self.settings_page.visible = True
        self.update()

    def save_bind(self, e):
        if self.settings_script_page.entry_dur_press.value.replace(" ", "") == "":
            self.settings_script_page.entry_dur_press.value = 0.0

        if self.settings_script_page.entry_delay_click.value.replace(" ", "") == "":
            self.settings_script_page.entry_delay_click.value = 0.5

        if self.settings_script_page.entry_dur_click.value.replace(" ", "") == "":
            self.settings_script_page.entry_dur_click.value = 0.0

        if self.settings_script_page.entry_inter_click.value.replace(" ", "") == "":
            self.settings_script_page.entry_inter_click.value = 0.0

        with open("DataSave/config_scripts.json", "w") as f:
            settings = {"duration_press": f"{float(self.settings_script_page.entry_dur_press.value)}",
                        "delay_click": f"{float(self.settings_script_page.entry_delay_click.value)}",
                        "duration_click": f"{float(self.settings_script_page.entry_dur_click.value)}",
                        "interval_click": f"{float(self.settings_script_page.entry_inter_click.value)}"}
            f.write(dumps(settings))

        try:
            if not exists("DataSave"):
                makedirs("DataSave")
            bind_setting = {"bind_key": f"{self.key_page.entry_key.value}",
                            "key_lang": f"{self.get_lang_key()}",
                            "click_mouse": f"{self.key_page.dropdown_button.value}",
                            "key_press": f"{self.key_page.press_key.value}"}
            with open("DataSave/bind_key_one.json", "w") as f:
                f.write(dumps(bind_setting, indent=1))

            bind_setting = {
                "bind_key": f"{self.hot_key_page.dropdown_key.value}+{self.hot_key_page.entry_second_key.value}",
                "key_lang": f"{self.get_lang_key()}",
                "click_mouse": f"{self.hot_key_page.dropdown_button.value}",
                "key_press": f"{self.hot_key_page.press_key.value}"}
            with open("DataSave/bind_two_key.json", "w") as f:
                f.write(dumps(bind_setting, indent=1))

            self.show_dlg_info("Successful", "Your settings saved")
        except Exception as e:
            self.show_err_dlg("Unknown error", str(e))

    def save_preset(self, e):
        if self.filename_ref.current.value.replace(" ", "") == "":
            return

        if self.settings_script_page.entry_dur_press.value.replace(" ", "") == "":
            self.settings_script_page.entry_dur_press.value = 0.0

        if self.settings_script_page.entry_dur_click.value.replace(" ", "") == "":
            self.settings_script_page.entry_dur_click.value = 0.0

        if self.settings_script_page.entry_delay_click.value.replace(" ", "") == "":
            self.settings_script_page.entry_delay_click.value = 0.5

        if self.settings_script_page.entry_inter_click.value.replace(" ", "") == "":
            self.settings_script_page.entry_inter_click.value = 0.0

        select_script = self.keys_ref.current.value.replace(" ", "_")
        if select_script == "One_key":
            bind_settings = {"bind_key": f"{self.key_page.entry_key.value}",
                             "key_lang": f"{self.get_lang_key()}",
                             "click_mouse": f"{self.key_page.dropdown_button.value}",
                             "key_press": f"{self.key_page.press_key.value}",
                             "duration_press": f"{float(self.settings_script_page.entry_dur_press.value)}",
                             "delay_click": f"{float(self.settings_script_page.entry_delay_click.value)}",
                             "duration_click": f"{float(self.settings_script_page.entry_dur_click.value)}",
                             "interval": f"{float(self.settings_script_page.entry_inter_click.value)}"}
        else:
            bind_settings = {"bind_key": f"{self.hot_key_page.dropdown_key.value}+"
                                         f"{self.hot_key_page.entry_second_key.value}",
                             "key_lang": f"{self.get_lang_key()}",
                             "click_mouse": f"{self.hot_key_page.dropdown_button.value}",
                             "key_press": f"{self.hot_key_page.press_key.value}",
                             "duration_press": f"{float(self.settings_script_page.entry_dur_press.value)}",
                             "delay_click": f"{float(self.settings_script_page.entry_delay_click.value)}",
                             "duration_click": f"{float(self.settings_script_page.entry_dur_click.value)}",
                             "interval": f"{float(self.settings_script_page.entry_inter_click.value)}"}
        try:
            if not exists("DataSave/Presets"):
                makedirs("DataSave/Presets")

            with open(f"DataSave/Presets/{self.filename_ref.current.value}_{select_script}.json", "w") as f:
                f.write(dumps(bind_settings, indent=1))

            self.dlg_save.open = False
            self.page.update()

            self.show_dlg_info("Successful", "Your presets saved")
        except Exception as e:
            self.show_err_dlg("Unknown error", str(e))

    def open_settings_scripts(self, e):
        self.screen_view.visible = False
        self.advance_menu_ref.current.visible = False
        self.settings_script_page.visible = True
        self.update()

    def show_dlg_save(self, e):
        self.page.dialog = self.dlg_save
        self.dlg_save.open = True
        self.page.update()

    def close_dlg_save(self, e):
        self.dlg_save.open = False
        self.page.update()


class OneKey(ft.UserControl):
    __slots__ = ("lb", "entry_key", "dropdown_button", "switch_button", "press_key", "main_page", "btn_save_bind",
                 "change_frame", "screen_view", "settings")

    def __init__(self, master):
        super().__init__()
        self.visible = True

        self.main_page = master

        self.lb = ft.Text(value="Enter activation key", size=self.main_page.text_size)
        self.entry_key = ft.TextField(width=self.main_page.text_size * 3, height=self.main_page.text_size * 5,
                                      text_size=self.main_page.text_size, text_align=ft.TextAlign.CENTER,
                                      on_change=self.change_enter_key)

        self.dropdown_button = ft.Dropdown(label="Chose button mouse", options=[ft.dropdown.Option("Right"),
                                                                                ft.dropdown.Option("Middle"),
                                                                                ft.dropdown.Option("Left")],
                                           width=150, value="Right", text_size=master.text_size)
        self.switch_button = ft.Switch(label="Key mode", value=False, on_change=self.change_mode)
        self.press_key = ft.TextField(width=self.main_page.text_size * 3, height=self.main_page.text_size * 4.8,
                                      text_size=self.main_page.text_size, text_align=ft.TextAlign.CENTER,
                                      visible=False)

        # Змінити алгоритм збереження бінду
        if isfile("DataSave/bind_key_one.json"):
            with open("DataSave/bind_key_one.json", "r") as f:
                settings: dict = loads(f.read())
                self.entry_key.value = settings.get("bind_key")
                self.main_page.set_lang_key(settings.get("key_lang"))
                self.dropdown_button.value = settings.get("click_mouse")
                self.press_key.value = settings.get("key_press")

        self.change_frame = ft.Row([self.switch_button, ft.Column([self.dropdown_button, self.press_key])])

        self.screen_view = ft.Row(
            [ft.Column([self.lb, self.entry_key, self.change_frame],
                       horizontal_alignment=ft.CrossAxisAlignment.CENTER)],
            alignment=ft.MainAxisAlignment.CENTER)

    def build(self):
        return self.screen_view

    def change_enter_key(self, e):
        self.main_page.set_lang_key(GetKeyboardLayoutName())
        if len(self.entry_key.value) > 1:
            self.entry_key.value = self.entry_key.value[0]
        self.entry_key.update()

    def change_press_key(self, e):
        if len(self.press_key.value) > 1:
            self.press_key.value = self.press_key.value[0]
        self.press_key.update()

    def change_mode(self, e):
        if self.switch_button.value:
            self.press_key.visible = True
            self.dropdown_button.visible = False
        else:
            self.press_key.visible = False
            self.dropdown_button.visible = True

        self.update()


class HotKey(ft.UserControl):
    __slots__ = ("lb", "entry_second_key", "dropdown_key", "dropdown_button", "switch_button", "press_key", "main_page",
                 "btn_save_bind", "change_frame", "screen_view", "settings")

    def __init__(self, master):
        super().__init__(master)
        self.visible = False

        self.main_page = master

        self.lb = ft.Text(value="Enter activation key", size=self.main_page.text_size)
        self.dropdown_key = ft.Dropdown(value="Chose first key", options=[ft.dropdown.Option("Ctrl"),
                                                                          ft.dropdown.Option("Alt"),
                                                                          ft.dropdown.Option("Shift")],
                                        width=150, text_size=self.main_page.text_size)
        self.entry_second_key = ft.TextField(width=self.main_page.text_size * 3, height=self.main_page.text_size * 5,
                                             text_size=self.main_page.text_size, text_align=ft.TextAlign.CENTER,
                                             on_change=self.change_enter_key)

        self.dropdown_button = ft.Dropdown(label="Chose button mouse", options=[ft.dropdown.Option("Right"),
                                                                                ft.dropdown.Option("Middle"),
                                                                                ft.dropdown.Option("Left")],
                                           width=150, value="Right", text_size=master.text_size)
        self.switch_button = ft.Switch(label="Key mode", value=False, on_change=self.change_mode)
        self.press_key = ft.TextField(width=self.main_page.text_size * 3, height=self.main_page.text_size * 4.8,
                                      text_size=self.main_page.text_size, text_align=ft.TextAlign.CENTER,
                                      visible=False)

        # Змінити алгоритм збереження бінду
        if isfile("DataSave/bind_two_key.json"):
            with open("DataSave/bind_two_key.json", "r") as f:
                settings: dict = loads(f.read())
                self.dropdown_key.value = settings.get("bind_key")[:-2]
                self.entry_second_key.value = settings.get("bind_key")[-1]
                self.main_page.set_lang_key(settings.get("key_lang"))
                self.dropdown_button.value = settings.get("click_mouse")
                self.press_key.value = settings.get("key_press")

        self.change_frame = ft.Row([self.switch_button, ft.Column([self.dropdown_button, self.press_key])])

        self.screen_view = ft.Row(
            [ft.Column([self.lb, ft.Row([self.dropdown_key, self.entry_second_key],
                                        alignment=ft.MainAxisAlignment.CENTER), self.change_frame],
                       horizontal_alignment=ft.CrossAxisAlignment.CENTER)],
            alignment=ft.MainAxisAlignment.CENTER)

    def build(self):
        return self.screen_view

    def change_enter_key(self, e):
        self.main_page.set_lang_key(GetKeyboardLayoutName())
        if len(self.entry_second_key.value) > 1:
            self.entry_second_key.value = self.entry_second_key.value[0]
        self.entry_second_key.update()

    def change_mode(self, e):
        if self.switch_button.value:
            self.press_key.visible = True
            self.dropdown_button.visible = False
        else:
            self.press_key.visible = False
            self.dropdown_button.visible = True

        self.update()


class SettingScriptPage(ft.UserControl):
    __slots__ = ("tabs", "entry_dur_press", "entry_delay_click", "entry_dur_click", "entry_inter_click",
                 "area", "area_back", "view_preset")

    def __init__(self, master):
        super().__init__()
        self.visible = False

        self.main_page = master

        self.tabs = ft.Tabs(selected_index=0, tabs=[ft.Tab(text="Pressed"), ft.Tab(text="Auto-clicker")],
                            on_change=self.change_tab)

        self.entry_dur_press = ft.TextField(label="Duration", width=self.main_page.text_size * 5,
                                            height=self.main_page.text_size * 5, text_size=self.main_page.text_size,
                                            value="0.0")

        self.entry_delay_click = ft.TextField(label="Delay", width=self.main_page.text_size * 5,
                                              height=self.main_page.text_size * 5, text_size=self.main_page.text_size,
                                              visible=False, value="0.5")
        self.entry_dur_click = ft.TextField(label="Duration", width=self.main_page.text_size * 5,
                                            height=self.main_page.text_size * 5, text_size=self.main_page.text_size,
                                            visible=False, value="0.0")
        self.entry_inter_click = ft.TextField(label="Interval", width=self.main_page.text_size * 5,
                                              height=self.main_page.text_size * 5, text_size=self.main_page.text_size,
                                              visible=False, value="0.0")

        self.btn_presets = ft.TextButton("Open presets", on_click=self.show_presets)

        self.view_preset = ft.ListView(spacing=10, height=100, width=300, visible=False)

        self.btn_back = ft.IconButton(icon=ft.icons.ARROW_BACK, on_click=self.back)

        self.area_back = ft.Row([self.btn_back], alignment=ft.MainAxisAlignment.CENTER)

        self.area = ft.Row([ft.Column([self.tabs, self.entry_dur_press,
                                       ft.Row([self.entry_delay_click, self.entry_dur_click, self.entry_inter_click],
                                              alignment=ft.MainAxisAlignment.CENTER), self.btn_presets,
                                       self.view_preset],
                                      horizontal_alignment=ft.CrossAxisAlignment.CENTER)],
                           alignment=ft.MainAxisAlignment.CENTER)

        self.back_area_ref = ft.Ref[ft.Row]()
        self.screen_view = [ft.Row([self.area_back], alignment=ft.alignment.top_left), self.area]

    def build(self):
        return self.screen_view

    def change_tab(self, e):
        select = self.tabs.selected_index
        if select == 0:
            self.entry_dur_click.visible = False
            self.entry_inter_click.visible = False
            self.entry_delay_click.visible = False
            self.entry_dur_press.visible = True
        else:
            self.entry_dur_press.visible = False
            self.entry_dur_click.visible = True
            self.entry_inter_click.visible = True
            self.entry_delay_click.visible = True
        self.update()

    def show_presets(self, e):
        if self.view_preset.visible:
            self.view_preset.visible = False
            self.btn_presets.text = "Open presets"
            self.view_preset.controls.clear()
        else:
            self.view_preset.visible = True
            self.btn_presets.text = "Close presets"

            if exists("DataSave/Presets"):
                for f in listdir("DataSave/Presets"):
                    if f.endswith(".json"):
                        self.view_preset.controls.append(ft.TextButton(text=f[:-5], on_click=self.get_preset))

            if len(self.view_preset.controls) < 1:
                self.view_preset.controls.append(ft.Text("No saves!", text_align=ft.TextAlign.CENTER))

        self.update()

    def get_preset(self, e):
        filename = e.control.text
        if not exists(f"DataSave/Presets/{filename}.json"):
            self.main_page.show_err_dlg("FileNotFound", "File does not exist")
            return

        if filename[-7:] == "One_key":
            with open(f"DataSave/Presets/{filename}.json", "r") as f:
                settings: dict = loads(f.read())
                self.main_page.key_page.entry_key.value = settings.get("bind_key")
                self.main_page.set_lang_key(settings.get("key_lang"))
                self.main_page.key_page.dropdown_button.value = settings.get("click_mouse")
                self.main_page.key_page.press_key.value = settings.get("key_press")
                self.entry_dur_press.value = settings.get("duration_press")
                self.entry_delay_click.value = settings.get("delay_click")
                self.entry_dur_click.value = settings.get("duration_click")
                self.entry_inter_click.value = settings.get("interval")
        else:
            with open(f"DataSave/Presets/{filename}.json", "r") as f:
                settings: dict = loads(f.read())
                self.main_page.hot_key_page.dropdown_key.value = settings.get("bind_key")[:-2]
                self.main_page.hot_key_page.entry_second_key.value = settings.get("bind_key")[-1]
                self.main_page.set_lang_key(settings.get("key_lang"))
                self.main_page.hot_key_page.dropdown_button.value = settings.get("click_mouse")
                self.main_page.hot_key_page.press_key.value = settings.get("key_press")
                self.entry_dur_press.value = settings.get("duration_press")
                self.entry_delay_click.value = settings.get("delay_click")
                self.entry_dur_click.value = settings.get("duration_click")
                self.entry_inter_click.value = settings.get("interval")
        self.update()
        self.main_page.key_page.update()
        self.main_page.hot_key_page.update()
        self.main_page.update()

    def back(self, e):
        self.main_page.screen_view.visible = True
        self.main_page.advance_menu_ref.current.visible = True
        self.visible = False
        self.main_page.update()


class SettingPage(ft.UserControl):
    __slots__ = ("btn_back", "switch_theme", "dropdown_lang", "lb_slider", "slider_size", "screen_view", "main_page",
                 "btn_back", "btn_save", "btn_cancel", "settings")

    def __init__(self, naster):
        super().__init__()
        self.visible = False

        self.main_page = naster

        self.btn_back = ft.IconButton(icon=ft.icons.ARROW_BACK, on_click=self.back)
        self.switch_theme = ft.Switch(label="Theme mode", value=False, thumb_icon=ft.icons.SUNNY,
                                      thumb_color={ft.MaterialState.SELECTED: ft.colors.BLACK26,
                                                   ft.MaterialState.DEFAULT: ft.colors.WHITE10},
                                      on_change=self.change_theme)

        self.dropdown_lang = ft.Dropdown(label="Language", options=[ft.dropdown.Option(text="English"),
                                                                    ft.dropdown.Option(text="Russian"),
                                                                    ft.dropdown.Option(text="Ukrainian")],
                                         disabled=True, width=200, value="English", text_size=self.main_page.text_size)

        self.lb_slider = ft.Text("For change size text", size=self.main_page.text_size)
        self.slider_size = ft.Slider(min=12, max=20, divisions=8, label="{value}px",
                                     on_change=self.change_text_size, value=self.main_page.text_size)

        self.btn_save = ft.ElevatedButton("Save settings", color=ft.colors.BLACK, bgcolor=ft.colors.GREEN,
                                          style=ft.ButtonStyle(overlay_color=ft.colors.BLACK12),
                                          on_click=self.save_settings)
        self.btn_cancel = ft.ElevatedButton("Cancel", color=ft.colors.BLACK, bgcolor=ft.colors.RED,
                                            style=ft.ButtonStyle(overlay_color=ft.colors.BLACK12),
                                            on_click=self.back)

        if isfile("DataSave/config.json"):
            try:
                with open("DataSave/config.json", "r") as f:
                    settings: dict = loads(f.read())
                    self.dropdown_lang.value = settings.get("language")
                    self.main_page.text_size = float(settings.get("text_size"))
                    self.slider_size.value = float(settings.get("text_size"))
                    self.switch_theme.value = settings.get("theme_mode")
            except json.decoder.JSONDecodeError:
                pass

        self.settings = ft.Column([
            ft.Row([self.switch_theme, self.dropdown_lang], alignment=ft.MainAxisAlignment.CENTER,
                   vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ft.Column([self.lb_slider, self.slider_size, ], horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                      width=300),
            ft.Row([self.btn_cancel, self.btn_save], alignment=ft.MainAxisAlignment.CENTER)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER)

        self.screen_view = [ft.Container(content=self.btn_back, alignment=ft.alignment.top_left,
                                         padding=ft.padding.symmetric(horizontal=-8)), self.settings]

    def build(self):
        return self.screen_view

    def back(self, e):
        if exists("DataSave/config.json"):
            with open("DataSave/config.json", "r") as f:
                settings: dict = loads(f.read())
                self.dropdown_lang.value = settings.get("language")
                self.main_page.text_size = float(settings.get("text_size"))
                self.slider_size.value = float(settings.get("text_size"))
                self.switch_theme.value = settings.get("theme_mode")
        else:
            self.slider_size.value = 14
            self.main_page.text_size = 14
            self.slider_size.value = 14
            self.switch_theme.value = False

        self.change_theme(None)

        self.main_page.screen_view.visible = True
        self.main_page.advance_menu_ref.current.visible = True
        self.visible = False

        self.change_text_size(None)

    def change_theme(self, e):
        if self.switch_theme.value:
            self.page.theme_mode = ft.ThemeMode.LIGHT
        else:
            self.page.theme_mode = ft.ThemeMode.DARK
        self.page.update()

    def _enter_change(self, control):
        if control.__class__ in (ft.Row, ft.Column):
            for c in control.controls:
                self._enter_change(c)
        elif control.__class__ in (SettingPage, SettingScriptPage, OneKey, HotKey):
            for c in control.controls:
                self._enter_change(c)
        if control.__class__ == ft.Text:
            control.size = self.slider_size.value
        elif control.__class__ == ft.Dropdown:
            control.text_size = self.slider_size.value
        elif control.__class__ == ft.TextField:
            control.width = self.slider_size.value * 3
            control.height = self.slider_size.value * 5
            control.text_size = self.slider_size.value
        elif control.__class__ == ft.Ref:
            if control.__class__ == ft.Text:
                control.size = self.slider_size.value

    def change_text_size(self, e):
        self.main_page.text_size = self.slider_size.value

        for control in self.main_page.controls:
            if control.__class__ in (ft.Row, ft.Column):
                for c in  control.controls:
                    self._enter_change(c)
            elif control.__class__ == ft.Container:
                for c in control.content:
                    self._enter_change(c)
            else:
                self._enter_change(control)

        self.update()
        self.main_page.update()
        self.main_page.key_page.update()
        self.main_page.hot_key_page.update()
        self.main_page.settings_script_page.update()

    def save_settings(self, e):
        self.main_page.text_size = self.slider_size.value
        try:
            if not exists("DataSave"):
                makedirs("DataSave")

            with open("DataSave/config.json", "w+") as f:
                settings = {"theme_mode": f"{self.switch_theme.value}",
                            "language": f"{self.dropdown_lang.value}",
                            "text_size": f"{self.main_page.text_size}"}
                f.write(dumps(settings, indent=1))

            self.main_page.show_dlg_info("Successful", "Your settings saved")
        except Exception as e:
            self.main_page.show_err_dlg("Unknown error", str(e))
