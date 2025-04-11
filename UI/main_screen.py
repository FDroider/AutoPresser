from os.path import exists, join
from os import mkdir, makedirs
from PySide6 import QtWidgets, QtCore, QtGui
from json import dumps, loads

class MainScreen(QtWidgets.QWidget):
    __slots__ = ("tab_widget", "one_key_frame", "hot_key_frame", "group_btn",
                 "key_layout", "chose_script_l", "v_layout")

    def __init__(self, master, starter_script):
        super().__init__(master)

        self.master = master
        self.app = master.master
        self.starter_script_thread = starter_script

        self.custom_key_layout = self.master.create_layout()

        self.dlg_add = AddDialog(master, self.custom_key_layout)
        self.dlg_preset = QtWidgets.QDialog()
        self.dlg_preset.setWindowTitle("Save preset")
        self.dlg_filename = QtWidgets.QTextEdit()
        self.dlg_filename.setPlaceholderText("File name")
        self.dlg_filename.setFixedSize(QtCore.QSize(200, 35))
        self.dlg_btn_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.StandardButton.Ok |
                                                      QtWidgets.QDialogButtonBox.StandardButton.Cancel)
        self.dlg_btn_box.accepted.connect(
            lambda: self.save_preset(self.dlg_filename.toPlainText()) if self.dlg_filename.toPlainText().replace(" ",
                                                                                                                 "") != ""
            else self.master.show_err("ValueError", "Enter file name!"))
        self.dlg_btn_box.rejected.connect(self.dlg_preset.close)
        self.dlg_preset.setLayout(self.master.create_layout("v", widgets=[self.dlg_filename, self.dlg_btn_box]))

        self.tab_widget = QtWidgets.QTabWidget()
        self.tab_widget.setObjectName("QTabWidget")
        self.tab_widget.resize(300, 200)
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("QWidget")
        self.tab_widget.addTab(self.tab, "One key")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("QWidget")
        self.tab_widget.addTab(self.tab_2, "Hot key")

        self.one_key_frame = OneKeyFrame(master)
        self.hot_key_frame = HotKeyFrame(master)

        self.dropdown_btn = QtWidgets.QComboBox()
        self.dropdown_btn.setObjectName("QComboBox")
        self.dropdown_btn.addItems(["Right", "Middle", "Left", "Key", "Custom"])
        self.dropdown_btn.currentIndexChanged.connect(self.change_dropdown_btn)
        self.dropdown_btn.setMaximumSize(QtCore.QSize(100, 30))
        self.dropdown_btn.setToolTip("('Right', 'Middle', 'Left') - mouse button\n"
                                     "'Key' - keyboard button\n"
                                     "'Custom' - for press hot key")

        self.entry = QtWidgets.QTextEdit()
        self.entry.setObjectName("QTextEdit")
        self.entry.setMinimumSize(QtCore.QSize(42, 30))
        self.entry.setVisible(False)
        self.entry.setAlignment(QtGui.Qt.AlignmentFlag.AlignCenter)
        self.entry.textChanged.connect(lambda: self.master.text_change(self.entry))
        self.btn_add = QtWidgets.QPushButton()
        self.btn_add.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.ListAdd))
        self.btn_add.clicked.connect(self.dlg_add.exec)
        self.btn_add.setVisible(False)
        self.btn_remove = QtWidgets.QPushButton()
        self.btn_remove.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.ListRemove))
        self.btn_remove.clicked.connect(self.dlg_add.remove_item)
        self.btn_remove.setVisible(False)

        self.btn_settings = QtWidgets.QPushButton("Settings")
        self.btn_settings.setObjectName("QPushButton")
        self.btn_settings.setIcon(QtGui.QIcon(join(self.app.basedir, "../images/771203.png")))
        self.btn_settings.clicked.connect(self.open_settings)
        self.btn_save = QtWidgets.QPushButton("Save")
        self.btn_save.setObjectName("QPushButton")
        self.btn_save.setIcon(QtGui.QIcon(join(self.app.basedir, "../images/174314.png")))
        self.btn_save.clicked.connect(self.save_settings_script)
        self.btn_save_presets = QtWidgets.QPushButton("Save preset")
        self.btn_save_presets.clicked.connect(self.dlg_preset.exec)
        self.btn_save_presets.setObjectName("QPushButton")
        self.btn_save_presets.setIcon(QtGui.QIcon(join(self.app.basedir, "../images/10057635.png")))
        self.btn_start = QtWidgets.QPushButton("Start script")
        self.btn_start.setObjectName("QPushButton")
        self.btn_start.clicked.connect(self.start_script)

        self.load_config("DataSave/config_script.json")
        if self.dropdown_btn.currentIndex() != 4:
            self._set_keys_visible(False)

        self.dropdown_script = QtWidgets.QComboBox()
        self.dropdown_script.setObjectName("QComboBox")
        self.dropdown_script.addItems(["Presser", "AutoClicker"])
        self.dropdown_script.setCurrentIndex(0)

        self.group_btn = self.master.create_layout(widgets=[self.btn_settings, self.btn_save, self.btn_save_presets])
        self.key_layout = self.master.create_layout(widgets=[self.dropdown_btn, self.entry, self.btn_add, self.btn_remove])
        self.chose_script_l = self.master.create_layout(widgets=[self.btn_start, self.dropdown_script])
        self.v_layout = self.master.add_items_layout(QtWidgets.QVBoxLayout(self),
                                                     widgets=[self.tab_widget],
                                                     layouts=[self.key_layout, self.custom_key_layout,
                                                              self.group_btn, self.chose_script_l])

        self.tab.setLayout(self.one_key_frame.layout())
        self.tab_2.setLayout(self.hot_key_frame.layout())

    def get_options_one_key(self):
        return self.master.settings.get_script_settings()[0]

    def get_options_hot_key(self):
        return self.master.settings.get_script_settings()[1:]

    def open_settings(self):
        self.master.setWindowTitle("Settings")
        self.master.settings.settings_script_frame.update_list_windows()
        self.master.stack_widget.setCurrentIndex(1)

    def change_dropdown_btn(self):
        if self.dropdown_btn.currentIndex() == 3:
            self.entry.setVisible(True)
            self._set_keys_visible(False)
        elif self.dropdown_btn.currentIndex() == 4:
            self.entry.setVisible(False)
            self._set_keys_visible(True)
        else:
            self.entry.setVisible(False)
            try:
                self._set_keys_visible(False)
            except AttributeError:
                pass

    def _set_keys_visible(self, visible):
        self.btn_add.setVisible(visible)
        self.btn_remove.setVisible(visible)
        for i in range(self.custom_key_layout.count()):
            self.custom_key_layout.itemAt(i).widget().setVisible(visible)

    def start_script(self):
        if self.dropdown_btn.currentIndex() == 3:
            if self.entry.toPlainText().lower().replace(" ", "") == "":
                return False
        elif self.dropdown_btn.currentIndex() == 4:
            btns = self.get_buttons()
            for btn in btns:
                if btn.replace(" ", "") == "":
                    return False
        if self.tab_widget.currentIndex() == 0:
            if self.one_key_frame.entry.toPlainText().replace(" ", "") == "":
                return False
        else:
            keys = self.hot_key_frame.get_keys()
            for k in keys:
                if k.replace(" ", "") == "" or k == "None":
                    return False

        w_name = self.master.settings.get_select_window(False)

        self.starter_script = self.starter_script_thread(self, self.tab_widget.currentIndex(),
                                                         self.dropdown_script.currentIndex(),
                                                         w_name)

        self.starter_script.start()
        self.dropdown_script.setDisabled(True)
        self.tab_widget.setDisabled(True)
        self.btn_start.setText("Stop script")
        self.btn_start.clicked.disconnect()
        self.btn_start.clicked.connect(self.stop_script)
        self.app.tray.setIcon(self.app.tray.active_icon)
        return True

    def stop_script(self):
        self.starter_script.stop()
        self.tab_widget.setDisabled(False)
        self.dropdown_script.setDisabled(False)
        self.btn_start.setText("Start script")
        self.btn_start.clicked.disconnect()
        self.btn_start.clicked.connect(self.start_script)
        self.app.tray.setIcon(self.app.tray.default_icon)

    def save_settings_script(self):
        if not exists("DataSave"):
            mkdir("DataSave")
        script_settings = self.master.settings.get_script_settings()
        settings = {"bind_one_key": self.one_key_frame.get_value_entry(),
                    "bind_hot_key": f"{"+".join(self.hot_key_frame.get_keys())}",
                    "button": self.dropdown_btn.currentText(),
                    "button_key": self.entry.toPlainText(),
                    "button_keys": f"{"+".join(self.get_buttons())}",
                    "one_key_duration": script_settings[0],
                    "hot_key_delay": script_settings[1],
                    "hot_key_interval": script_settings[2]}
        try:
            with open("DataSave/config_script.json", "w") as f:
                f.write(dumps(settings))
            self.master.show_info("Success", "Settings saved")
            return True
        except Exception as e:
            self.master.show_err("Exception", str(e))
            return False

    def save_preset(self, filename):
        if not exists("DataSave/Presets"):
            makedirs("DataSave/Presets")
        script_settings = self.master.settings.get_script_settings()
        settings = {"bind_one_key": self.one_key_frame.get_value_entry(),
                    "bind_hot_key": f"{"+".join(self.hot_key_frame.get_keys())}",
                    "button": self.dropdown_btn.currentText(),
                    "button_key": self.entry.toPlainText(),
                    "button_keys": f"{"+".join(self.get_buttons())}",
                    "one_key_dur": script_settings[0],
                    "hot_key_delay": script_settings[1],
                    "hot_key_interval": script_settings[2]}
        try:
            with open(f"DataSave/Presets/{filename}.json", "w") as f:
                f.write(dumps(settings))
            self.master.show_info("Success", "Settings saved")
        except Exception as e:
            self.master.show_err("Exception", str(e))
        self.master.settings.settings_script_frame.update_list_presets()

    def load_preset(self, filename):
        if not exists(f"DataSave/Presets/{filename}.json"):
            self.master.show_err("FileNotFound", f"'{filename}.json' not founded or removed")
            return
        try:
            self.load_config(f"DataSave/Presets/{filename}.json")
        except Exception as e:
            self.master.show_err("Exception", str(e))

    def load_config(self, path: str):
        if not exists(f"{path}"):
            return self.master.show_err("FileNotFound", "Preset was not found")
        with open(f"{path}", "r") as f:
            settings = loads(f.read())
            for i in settings.items():
                i = i[0]
                try:
                    if i[0:4] == "bind":
                        if i[5:] == "one_key":
                            self.one_key_frame.entry.setText(settings[i])
                            self.one_key_frame.entry.setAlignment(QtGui.Qt.AlignmentFlag.AlignCenter)
                        else:
                            self.hot_key_frame.set_keys(settings[i].split("+"))
                    else:
                        if i[0:7] == "one_key":
                            if i[8:] == "duration":
                                self.master.settings.set_script_settings(settings[i])
                            continue
                        elif i[0:7] == "hot_key":
                            match i[8:]:
                                case "delay":
                                    self.master.settings.set_script_settings(delay_hot_key=settings[i])
                                case "interval":
                                    self.master.settings.set_script_settings(interval_hot_key=settings[i])
                            continue
                        else:
                            if i == "button":
                                self.dropdown_btn.setCurrentText(settings[i])
                            elif i == "button_key":
                                self.entry.setText(settings[i])
                                self.entry.setAlignment(QtGui.Qt.AlignmentFlag.AlignCenter)
                            else:
                                self.set_buttons(settings[i].split("+"))
                except Exception as e:
                   self.master.show_err("Exception", str(e))

    def get_buttons(self):
        btns = []
        if self.custom_key_layout.count() == 0:
            return btns
        for i in range(self.custom_key_layout.count()):
            widget = self.custom_key_layout.itemAt(i).widget()
            if widget.windowTitle() == "QTextEdit":
                btns.append(widget.toPlainText())
            elif widget.windowTitle() == "QComboBox":
                btns.append(widget.currentText().lower())
        return btns

    def set_buttons(self, keys: list):
        if self.custom_key_layout.count() != 0:
            for i in range(int(self.custom_key_layout.count())):
                self.dlg_add.remove_item()

        for k in keys:
            if len(k) > 1:
                self.dlg_add.add_dropdown(-1, text=k)
            else:
                self.dlg_add.add_entry(-1, text=k)

class OneKeyFrame(QtWidgets.QFrame):
    __slots__ = ("v_layout", "h_layout")

    def __init__(self, master):
        super().__init__()
        self.lb = QtWidgets.QLabel("Enter activation key")
        self.lb.setAlignment(QtGui.Qt.AlignmentFlag.AlignCenter)
        self.entry = QtWidgets.QTextEdit()
        self.entry.textChanged.connect(lambda: master.text_change(self.entry))
        self.entry.setStyleSheet("""*:focus {border: 1px solid rgba(255, 255, 255, 70);}""")
        self.entry.setAlignment(QtGui.Qt.AlignmentFlag.AlignCenter)
        self.entry.setMinimumSize(QtCore.QSize(42, 30))
        self.v_layout = QtWidgets.QVBoxLayout(self)
        self.h_layout = QtWidgets.QHBoxLayout()
        self.v_layout.addWidget(self.lb)
        self.h_layout.addWidget(self.entry)
        self.v_layout.addLayout(self.h_layout)

    def get_value_entry(self):
        return self.entry.toPlainText()


class HotKeyFrame(QtWidgets.QFrame):
    __slots__ = ("v_layout", "h_layout")

    def __init__(self, master):
        super().__init__()
        self.setVisible(False)
        self.master = master

        self.h_layout = self.master.create_layout()

        self.dlg = AddDialog(master, self.h_layout)

        self.lb = QtWidgets.QLabel("Enter activation keys")
        self.lb.setAlignment(QtGui.Qt.AlignmentFlag.AlignCenter)
        self.btn_add = QtWidgets.QPushButton()
        self.btn_add.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.ListAdd))
        self.btn_add.clicked.connect(self.dlg.exec)
        self.btn_remove = QtWidgets.QPushButton()
        self.btn_remove.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.ListRemove))
        self.btn_remove.clicked.connect(self.dlg.remove_item)
        self.h_btn_layout = self.master.create_layout(widgets=[self.btn_add, self.btn_remove])
        self.v_layout = self.master.create_layout("v", layouts=[self.h_btn_layout, self.h_layout])
        self.setLayout(self.v_layout)

    def get_keys(self):
        keys = []
        if self.h_layout.count() == 0:
            return keys
        for i in range(self.h_layout.count()):
            widget = self.h_layout.itemAt(i).widget()
            if widget.windowTitle() == "QTextEdit":
                keys.append(widget.toPlainText())
            elif widget.windowTitle() == "QComboBox":
                keys.append(widget.currentText().lower())
        return keys

    def set_keys(self, keys: list):
        if self.h_layout.count() != 0:
            for i in range(int(self.h_layout.count())):
                self.dlg.remove_item()

        for k in keys:
            if len(k) > 1:
                self.dlg.add_dropdown(-1, text=k)
            else:
                self.dlg.add_entry(-1, text=k)

class AddDialog(QtWidgets.QDialog):
    def __init__(self, master, layout, index = -1, text: tuple = ("Ctrl", "False")):
        super().__init__()
        self.master = master

        self.main_layout = layout

        self.btn_add_entry = QtWidgets.QPushButton("Add key")
        self.btn_add_entry.clicked.connect(lambda: self.add_entry(index, text[1]))
        self.btn_add_dropdown = QtWidgets.QPushButton("Add auxiliary button")
        self.btn_add_dropdown.clicked.connect(lambda: self.add_dropdown(index, text[0]))
        self.btn_close = QtWidgets.QPushButton("Close")
        self.btn_close.clicked.connect(self.close)

        self.h_layout = self.master.create_layout(widgets=[self.btn_add_entry, self.btn_add_dropdown])
        self.v_layout = self.master.create_layout("v", layouts=[self.h_layout])
        self.v_layout.addWidget(self.btn_close)
        self.setLayout(self.v_layout)

    def add_entry(self, index, text):
        entry = QtWidgets.QTextEdit()
        entry.setWindowTitle("QTextEdit")
        entry.textChanged.connect(lambda: self.master.text_change(entry))
        entry.setStyleSheet("""*:focus {border: 1px solid rgba(255, 255, 255, 70);}""")
        if text != "False":
            entry.setText(text)
        entry.setAlignment(QtGui.Qt.AlignmentFlag.AlignCenter)
        entry.setMaximumSize(QtCore.QSize(48, 35))
        self.main_layout.insertWidget(index, entry)

    def add_dropdown(self, index, text):
        dropdown = QtWidgets.QComboBox()
        dropdown.addItems(["Ctrl", "Alt", "Shift"])
        dropdown.setWindowTitle("QComboBox")
        dropdown.setCurrentText(text.capitalize())
        self.main_layout.insertWidget(index, dropdown)

    def remove_item(self):
        if self.main_layout.count() != 0:
            self.main_layout.takeAt(self.main_layout.count()-1).widget().deleteLater()