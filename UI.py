import flet as ft

import auto_clicker
import press_click

# from re import findall
from asyncio import new_event_loop
from asyncio import run
from json import dumps, loads
from os import makedirs, listdir
from os.path import isfile, exists

from win32api import GetKeyboardLayoutName, LoadKeyboardLayout


class MainScreen(ft.UserControl):
    lang_user = int
    __slots__ = ("settings_page", "key_page", "loop", "advance_menu", "key_tab", "dropdown_script", "btn_start",
                 "btn_stop" "dlg_error", "dlg_info", "control_script", "screen_view")

    def __init__(self):
        super().__init__()

        self.text_size = 14

        self.settings_page = SettingPage(self)

        self.settings_script_page = SettingScriptPage(self)

        self.key_page = OneKey(self)

        # self.hot_key_page = HotKey(self.text_size)

        self.loop = new_event_loop()

        self.advance_menu = ft.PopupMenuButton(items=[ft.PopupMenuItem(text="Settings", on_click=self.open_settings)])

        self.key_tab = ft.Tabs(selected_index=0, tabs=[ft.Tab(text="One key"), ft.Tab(text="Hot-key", visible=False)])

        self.btn_start = ft.FilledTonalButton(text="Start script", on_click=self.start_script)

        self.btn_stop = ft.FilledTonalButton(text="Stop script", visible=False, on_click=self.stop_script)

        self.dropdown_script = ft.Dropdown(label="Chose script", options=(ft.dropdown.Option("Pressed"),
                                                                          ft.dropdown.Option("Auto-clicker")),
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

        self.control_script = ft.Row([self.btn_start, self.btn_stop, self.dropdown_script],
                                     alignment=ft.MainAxisAlignment.CENTER)

        # self.screen_view = ft.Container(content=ft.Row([
        #                            ft.Column([self.key_tab, self.key_page, self.hot_key_page, self.control_script],
        #                                      horizontal_alignment=ft.CrossAxisAlignment.CENTER)],
        #                             alignment=ft.MainAxisAlignment.CENTER), alignment=ft.alignment.center, margin=200)

        self.screen_view = ft.Row([ft.Column([self.key_tab, self.key_page, self.control_script],
                                             horizontal_alignment=ft.CrossAxisAlignment.CENTER)],
                                  alignment=ft.MainAxisAlignment.CENTER)
        self.advance_menu_ref = ft.Ref[ft.Row]()

    def build(self):
        return [self.screen_view,
                ft.Row([self.advance_menu], alignment=ft.alignment.top_left, ref=self.advance_menu_ref),
                self.settings_page, self.settings_script_page]

    def start_script(self, e):
        select = self.key_tab.tabs[self.key_tab.selected_index].text.replace(" ", "_").replace("-", "_")

        if self.dropdown_script.value not in ("Pressed", "Auto-clicker"):
            self.show_err_dlg("RuntimeError", "Please chose script for start")
            return

        select_script = self.dropdown_script.value.replace('-', '_')

        if self.key_page.switch_button.value:
            key = self.key_page.press_key.value
            if key == "" or key == "":
                self.show_err_dlg("ValueError", "Please enter key on which press")
                return

        LoadKeyboardLayout(MainScreen.lang_user, 1)

        if select == "One_key":
            key_start = str(self.key_page.entry_key.value)

            if key_start == "" or key_start == " ":
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
                setting = str(self.settings_script_page.entry_dur_press.value).replace(" ", "")

                if setting == "":
                    self.loop.run_until_complete(press_click.start_one_key(key_start, None, key_press))
                else:
                    self.loop.run_until_complete(press_click.start_one_key(key_start, None, key_press,
                                                                           float(
                                                                               self.settings_script_page.entry_dur_press.value)))
            elif select_script == "Auto_clicker":
                settings = (str(self.settings_script_page.entry_delay_click.value).replace(" ", ""),
                          str(self.settings_script_page.entry_dur_click.value).replace(" ", ""),
                          str(self.settings_script_page.entry_inter_click.value).replace(" ", ""))

                if settings[0] != "" and settings[1] != "" and settings[2] != "":
                    self.loop.run_until_complete(auto_clicker.start_one_key(key_start, None, key_press,
                                                                            float(settings[0]), float(settings[1]),
                                                                            float(settings[2])))
                elif settings[0] != "" and settings[1] != "":
                    self.loop.run_until_complete(auto_clicker.start_one_key(key_start, None, key_press,
                                                                            float(settings[0]), float(settings[1])))
                elif settings[0] != "" and settings[2] != "":
                    self.loop.run_until_complete(auto_clicker.start_one_key(key_start, None, key_press,
                                                                            float(settings[0]),
                                                                            interval=float(settings[2])))
                elif settings[1] != "" and settings[2] != "":
                    self.loop.run_until_complete(auto_clicker.start_one_key(key_start, None, key_press,
                                                                            duration=float(settings[1]),
                                                                            interval=float(settings[2])))
                elif settings[0] != "":
                    self.loop.run_until_complete(auto_clicker.start_one_key(key_start, None, key_press,
                                                                            float(settings[0])))
                elif settings[1] != "":
                    self.loop.run_until_complete(auto_clicker.start_one_key(key_start, None, key_press,
                                                                            duration=float(settings[1])))
                elif settings[2] != "":
                    self.loop.run_until_complete(auto_clicker.start_one_key(key_start, None, key_press,
                                                                            interval=float(settings[2])))
                else:
                    self.loop.run_until_complete(auto_clicker.start_one_key(key_start, None, key_press))
                del select

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

    def open_settings(self, e):
        self.screen_view.visible = False
        self.advance_menu_ref.current.visible = False
        self.settings_page.visible = True
        self.update()


class OneKey(ft.UserControl):
    __slots__ = ("lb", "entry_key", "dropdown_button", "switch_button", "press_key", "main_page", "btn_save_bind",
                 "change_frame", "screen_view")

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

        self.btn_settings = ft.ElevatedButton("Settings", color=ft.colors.WHITE70, bgcolor=ft.colors.BLUE_GREY,
                                              style=ft.ButtonStyle(overlay_color=ft.colors.BLACK12),
                                              icon=ft.icons.SETTINGS_SUGGEST, on_click=self.open_settings_scripts)

        self.btn_save_bind = ft.IconButton(bgcolor=ft.colors.GREEN, icon=ft.icons.SAVE_AS,
                                           style=ft.ButtonStyle(overlay_color=ft.colors.BLACK12),
                                           on_click=self.save_bind)

        self.btn_save_preset = ft.ElevatedButton("Save presets", color=ft.colors.BLACK87, bgcolor=ft.colors.BLUE,
                                                 style=ft.ButtonStyle(overlay_color=ft.colors.BLACK12),
                                                 icon=ft.icons.SAVE_ALT_SHARP, on_click=self.show_dlg_save)

        if isfile("DataSave/bind_key_one.json"):
            with open("DataSave/bind_key_one.json", "r") as f:
                settings: dict = loads(f.read())
                self.entry_key.value = settings.get("bind_key")
                MainScreen.lang_user = settings.get("key_lang")
                self.dropdown_button.value = settings.get("click_mouse")
                self.press_key.value = settings.get("key_press")
                self.main_page.settings_script_page.entry_dur_press.value = settings.get("duration_press")
                self.main_page.settings_script_page.entry_delay_click.value = settings.get("delay_click")
                self.main_page.settings_script_page.entry_dur_click.value = settings.get("duration_click")
                self.main_page.settings_script_page.entry_inter_click.value = settings.get("interval")

        self.filename_ref = ft.Ref[ft.TextField]()
        self.dlg_save = ft.AlertDialog(title=ft.Text("Save settings"),
                                       content=ft.TextField(label="Enter name for the save", ref=self.filename_ref),
                                       actions=[ft.ElevatedButton("Cancel", bgcolor=ft.colors.RED,
                                                                  style=ft.ButtonStyle(overlay_color=ft.colors.BLACK12),
                                                                  on_click=self.close_dlg_save),
                                                ft.ElevatedButton("Save", bgcolor=ft.colors.GREEN,
                                                                  style=ft.ButtonStyle(
                                                                      overlay_color=ft.colors.BLACK12),
                                                                  on_click=self.save_preset)])

        self.change_frame = ft.Row([self.switch_button, ft.Column([self.dropdown_button, self.press_key])])

        self.screen_view = ft.Row(
            [ft.Column([self.lb, self.entry_key, self.change_frame,
                        ft.Row([self.btn_settings, self.btn_save_bind, self.btn_save_preset])],
                       horizontal_alignment=ft.CrossAxisAlignment.CENTER)],
            alignment=ft.MainAxisAlignment.CENTER)

    def build(self):
        return self.screen_view

    def change_enter_key(self, e):
        MainScreen.lang_user = GetKeyboardLayoutName()
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

    def save_bind(self, e):
        bind_setting = {"bind_key": f"{self.entry_key.value}",
                        "key_lang": f"{MainScreen.lang_user}",
                        "click_mouse": f"{self.dropdown_button.value}",
                        "key_press": f"{self.press_key.value}",
                        "duration_press": f"{float(self.main_page.settings_script_page.entry_dur_press.value)}",
                        "delay_click": f"{float(self.main_page.settings_script_page.entry_delay_click.value)}",
                        "duration_click": f"{float(self.main_page.settings_script_page.entry_dur_click.value)}",
                        "interval": f"{float(self.main_page.settings_script_page.entry_inter_click.value)}"}

        try:
            if not exists("DataSave"):
                makedirs("DataSave")

            with open("DataSave/bind_key_one.json", "w") as f:
                f.write(dumps(bind_setting, indent=1))

            self.main_page.show_dlg_info("Successful", "Your settings saved")
        except Exception as e:
            self.main_page.show_err_dlg("Unknown error", str(e))

    def save_preset(self, e):
        if self.filename_ref.current.value.replace(" ", "") == "":
            return

        if self.main_page.settings_script_page.entry_dur_press.value.replace(" ", "") == "":
            self.main_page.settings_script_page.entry_dur_press.value = "0.0"

        if self.main_page.settings_script_page.entry_dur_click.value.replace(" ", "") == "":
            self.main_page.settings_script_page.entry_dur_click.value = "0.0"

        if self.main_page.settings_script_page.entry_delay_click.value.replace(" ", "") == "":
            self.main_page.settings_script_page.entry_delay_click.value = "0.0"

        if self.main_page.settings_script_page.entry_inter_click.value.replace(" ", "") == "":
            self.main_page.settings_script_page.entry_inter_click.value = "0.0"

        bind_settings = {"bind_key": f"{self.entry_key.value}",
                         "key_lang": f"{MainScreen.lang_user}",
                         "click_mouse": f"{self.dropdown_button.value}",
                         "key_press": f"{self.press_key.value}",
                         "duration_press": f"{float(self.main_page.settings_script_page.entry_dur_press.value)}",
                         "delay_click": f"{float(self.main_page.settings_script_page.entry_delay_click.value)}",
                         "duration_click": f"{float(self.main_page.settings_script_page.entry_dur_click.value)}",
                         "interval": f"{float(self.main_page.settings_script_page.entry_inter_click.value)}"}
        try:
            if not exists("DataSave/Presets"):
                makedirs("DataSave/Presets")

            with open(f"DataSave/Presets/{self.filename_ref.current.value}.json", "w") as f:
                f.write(dumps(bind_settings, indent=1))

            self.dlg_save.open = False
            self.page.update()

            self.main_page.show_dlg_info("Successful", "Your presets saved")
        except Exception as e:
            self.main_page.show_err_dlg("Unknown error", str(e))

    def open_settings_scripts(self, e):
        self.main_page.screen_view.visible = False
        self.main_page.advance_menu_ref.current.visible = False
        self.main_page.settings_script_page.visible = True
        self.main_page.update()

    def show_dlg_save(self, e):
        self.page.dialog = self.dlg_save
        self.dlg_save.open = True
        self.page.update()

    def close_dlg_save(self, e):
        self.dlg_save.open = False
        self.page.update()


class SettingScriptPage(ft.UserControl):
    __slots__ = ("tabs", "entry_dur_press", "entry_delay_click", "entry_dur_click", "entry_inter_click",
                 "area")

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

        self.btn_presets = ft.TextButton("Presets", on_click=self.show_presets)

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
        select = self.tabs.tabs[self.tabs.selected_index].text
        if select == "Pressed":
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
                        self.view_preset.controls.append(ft.TextButton(text=str(f[:-5]), on_click=self.get_preset))

            if len(self.view_preset.controls) < 1:
                self.view_preset.controls.append(ft.Text("No saves!", text_align=ft.TextAlign.CENTER))

        self.update()

    def get_preset(self, e):
        filename = e.control.text
        if not exists(f"DataSave/Presets/{filename}.json"):
            self.main_page.show_err_dlg("FileNotFound", "File does not exist")
            return

        with open(f"DataSave/Presets/{filename}.json", "r") as f:
            settings: dict = loads(f.read())
            self.main_page.key_page.entry_key.value = settings.get("bind_key")
            MainScreen.lang_user = settings.get("key_lang")
            self.main_page.key_page.dropdown_button.value = settings.get("click_mouse")
            self.main_page.key_page.press_key.value = settings.get("key_press")
            self.entry_dur_press.value = settings.get("duration_press")
            self.entry_delay_click.value = settings.get("delay_click")
            self.entry_dur_click.value = settings.get("duration_click")
            self.entry_inter_click.value = settings.get("interval")
        self.update()
        self.main_page.key_page.update()
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
            with open("DataSave/config.json", "r") as f:
                settings: dict = loads(f.read())
                self.dropdown_lang.value = settings.get("language")
                self.main_page.text_size = float(settings.get("text_size"))
                self.slider_size.value = float(settings.get("text_size"))
                self.switch_theme.value = settings.get("theme_mode")

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

    def change_text_size(self, e):
        self.main_page.text_size = self.slider_size.value
        self.lb_slider.size = self.slider_size.value
        self.main_page.dropdown_script.text_size = self.slider_size.value
        self.main_page.key_page.lb.size = self.slider_size.value
        self.main_page.key_page.entry_key.width = self.slider_size.value * 3
        self.main_page.key_page.entry_key.height = self.slider_size.value * 5
        self.main_page.key_page.entry_key.text_size = self.slider_size.value
        self.main_page.key_page.press_key.width = self.slider_size.value * 3
        self.main_page.key_page.press_key.height = self.slider_size.value * 5
        self.main_page.key_page.press_key.text_size = self.slider_size.value
        self.main_page.key_page.dropdown_button.text_size = self.slider_size.value
        self.main_page.title_dlg_ref.current.size = self.slider_size.value
        self.main_page.content_dlg_ref.current.size = self.slider_size.value
        self.main_page.settings_script_page.entry_dur_press.width = self.slider_size.value * 6
        self.main_page.settings_script_page.entry_dur_press.height = self.slider_size.value * 5
        self.main_page.settings_script_page.entry_dur_press.text_size = self.slider_size.value
        self.main_page.settings_script_page.entry_delay_click.width = self.slider_size.value * 5
        self.main_page.settings_script_page.entry_delay_click.height = self.slider_size.value * 5
        self.main_page.settings_script_page.entry_delay_click.text_size = self.slider_size.value
        self.main_page.settings_script_page.entry_dur_click.width = self.slider_size.value * 6
        self.main_page.settings_script_page.entry_dur_click.height = self.slider_size.value * 5
        self.main_page.settings_script_page.entry_dur_click.text_size = self.slider_size.value
        self.main_page.settings_script_page.entry_inter_click.width = self.slider_size.value * 5
        self.main_page.settings_script_page.entry_inter_click.height = self.slider_size.value * 5
        self.main_page.settings_script_page.entry_inter_click.text_size = self.slider_size.value

        self.update()
        self.main_page.update()
        self.main_page.key_page.update()
        self.main_page.settings_script_page.update()

    def save_settings(self, e):
        self.main_page.text_size = self.slider_size.value
        settings = {"theme_mode": f"{self.switch_theme.value}",
                    "language": f"{self.dropdown_lang.value}",
                    "text_size": f"{self.main_page.text_size}"}
        try:
            if not exists("DataSave"):
                makedirs("DataSave")

            with open("DataSave/config.json", "w+") as f:
                f.write(dumps(settings, indent=1))

            self.main_page.show_dlg_info("Successful", "Your settings saved")
        except Exception as e:
            self.main_page.show_err_dlg("Unknown error", str(e))
