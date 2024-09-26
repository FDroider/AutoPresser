from os.path import exists
from os import mkdir, makedirs, listdir
from PySide6 import QtWidgets, QtCore, QtGui
from json import dumps, loads


class Settings(QtWidgets.QWidget):
    __slots__ = ("tab_widget", "settings_script_frame", "settings_app_frame",
                 "settings_layout", "btn_layout")

    def __init__(self, master):
        super().__init__()
        self.master = master
        self.master.setWindowTitle("Settings")
        self.tab_view = QtWidgets.QTabWidget()
        self.tab_view.setObjectName("QTabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("QWidget")
        self.tab_view.addTab(self.tab, "Settings script")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("QWidget")
        self.tab_view.addTab(self.tab_2, "Settings app")

        self.btn_back = QtWidgets.QPushButton("Back")
        self.btn_back.setObjectName("QPushButton")
        self.btn_back.clicked.connect(self.back)
        self.btn_save = QtWidgets.QPushButton("Save")
        self.btn_save.setObjectName("QPushButton")
        self.btn_save.clicked.connect(self.save_settings)

        self.settings_script_frame = SettingsScripFrame(self.master)
        self.settings_app_frame = SettingsAppFrame(self.master)

        self.tab.setLayout(self.settings_script_frame.layout())
        self.tab_2.setLayout(self.settings_app_frame.layout())

        self.settings_layout = QtWidgets.QVBoxLayout(self)
        self.btn_layout = QtWidgets.QHBoxLayout()

        self.settings_layout.addWidget(self.tab_view)
        self.btn_layout.addWidget(self.btn_back)
        self.btn_layout.addWidget(self.btn_save)
        self.settings_layout.addLayout(self.btn_layout)

    def back(self):
        self.master.stack_widget.setCurrentIndex(0)

    def save_settings(self):
        settings = {"text_size": self.settings_app_frame.slider.value(),
                    "style": self.settings_app_frame.dropdown_style.currentText()}
        if not exists("DataSave"):
            mkdir("DataSave")
        with open("DataSave/config.json", "w") as f:
            f.write(dumps(settings))
        self.master.show_info("Success", "Settings saved")

    def get_slider_value(self):
        return self.settings_app_frame.slider.value()


class SettingsScripFrame(QtWidgets.QFrame):
    __slots__ = ("h_one_key_l", "h_hot_key_l", "h_presets_l", "v_layout")
    def __init__(self, master):
        super().__init__()
        self.master = master

        self.lb_one_key = QtWidgets.QLabel("Settings for one key option")
        self.duration_one_key = QtWidgets.QTextEdit()
        self.duration_one_key.setAlignment(QtGui.Qt.AlignmentFlag.AlignCenter)
        self.duration_one_key.setPlaceholderText("Duration")
        self.duration_one_key.setToolTip("Duration")
        self.duration_one_key.setMinimumSize(QtCore.QSize(42, 30))
        self.lb_hot_key = QtWidgets.QLabel("Settings for hot key option")
        self.delay_hot_key = QtWidgets.QTextEdit()
        self.delay_hot_key.setAlignment(QtGui.Qt.AlignmentFlag.AlignCenter)
        self.delay_hot_key.setPlaceholderText("Delay")
        self.delay_hot_key.setAlignment(QtGui.Qt.AlignmentFlag.AlignCenter)
        self.delay_hot_key.setToolTip("Delay")
        self.delay_hot_key.setMinimumSize(QtCore.QSize(42, 30))
        self.interval_hot_key = QtWidgets.QTextEdit()
        self.interval_hot_key.setPlaceholderText("Interval")
        self.interval_hot_key.setAlignment(QtGui.Qt.AlignmentFlag.AlignCenter)
        self.interval_hot_key.setToolTip("Interval")
        self.interval_hot_key.setMinimumSize(QtCore.QSize(42, 30))
        self.dropdown_presets = QtWidgets.QComboBox()
        self.dropdown_presets.addItems(self.show_presets())
        self.dropdown_presets.setToolTip("Preset")
        self.btn_select = QtWidgets.QPushButton("Select")
        self.btn_select.clicked.connect(lambda: self.master.main_screen.load_preset(self.dropdown_presets.currentText()))

        self.h_one_key_l = QtWidgets.QHBoxLayout()

        self.h_one_key_l.addWidget(self.duration_one_key)

        self.h_hot_key_l = QtWidgets.QHBoxLayout()

        self.h_hot_key_l.addWidget(self.delay_hot_key)
        self.h_hot_key_l.addWidget(self.interval_hot_key)

        self.h_presets_l = QtWidgets.QHBoxLayout()

        self.h_presets_l.addWidget(self.dropdown_presets)
        self.h_presets_l.addWidget(self.btn_select)

        self.v_layout = QtWidgets.QVBoxLayout(self)

        self.v_layout.addWidget(self.lb_one_key)
        self.v_layout.addLayout(self.h_one_key_l)
        self.v_layout.addWidget(self.lb_hot_key)
        self.v_layout.addLayout(self.h_hot_key_l)
        self.v_layout.addLayout(self.h_presets_l)

    def show_presets(self):
        presets = []
        if not exists("DataSave/Presets"):
            return ("None",)
        for f in listdir("DataSave/Presets"):
            if f.endswith(".json"):
                presets.append(f[:-5])
        if len(presets) < 1:
            return ("None",)
        return presets

    def update_list_presets(self):
        self.dropdown_presets.clear()
        self.dropdown_presets.addItems(self.show_presets())


class SettingsAppFrame(QtWidgets.QFrame):
    __slots__ = ("v_layout",)

    def __init__(self, master):
        super().__init__()
        self.master = master
        self.lb_style = QtWidgets.QLabel("Styles")
        self.lb_style.setAlignment(QtGui.Qt.AlignmentFlag.AlignCenter)
        self.dropdown_style = QtWidgets.QComboBox()
        self.dropdown_style.addItems(self.show_styles())
        self.dropdown_style.setCurrentIndex(1)
        self.dropdown_style.currentIndexChanged.connect(self.changeStyle)
        self.btn_select = QtWidgets.QPushButton("Create style")
        self.btn_select.clicked.connect(self.open_style_dlg)
        self.btn_change = QtWidgets.QPushButton("Change style")
        self.btn_change.clicked.connect(lambda: self.open_style_dlg(self.dropdown_style.currentText())
                                                if self.dropdown_style.currentText()[:3] not in ("New", "Old")
                                                else None)
        self.lb_text_size = QtWidgets.QLabel("Text size")
        self.lb_text_size.setAlignment(QtGui.Qt.AlignmentFlag.AlignCenter)
        self.slider = QtWidgets.QSlider(QtGui.Qt.Orientation.Horizontal)
        self.slider.setValue(self.master.get_text_size())
        self.slider.setMinimum(11)
        self.slider.setMaximum(25)
        self.slider.valueChanged.connect(self.change_size)
        self.slider.setToolTip(f"{self.slider.value()}px")

        self.v_layout = QtWidgets.QVBoxLayout(self)
        self.h_layout = QtWidgets.QHBoxLayout()

        self.v_layout.addWidget(self.lb_style)
        self.h_layout.addWidget(self.dropdown_style)
        self.h_layout.addWidget(self.btn_select)
        self.v_layout.addLayout(self.h_layout)
        self.v_layout.addWidget(self.btn_change)
        self.v_layout.addWidget(self.lb_text_size)
        self.v_layout.addWidget(self.slider)

    def change_size(self):
        self.lb_text_size.setStyleSheet("""QLabel {font-size: %spx;}""" % self.slider.value())
        self.slider.setToolTip(f"{self.slider.value()}px")
        self.master.set_text_size(self.slider.value())

    def show_styles(self):
        styles = ["Old version", "New version"]
        if not exists("DataSave/Styles"):
            return styles
        for f in listdir("DataSave/Styles"):
            if f.endswith(".json"):
                styles.append(f[:-5])
        return styles

    def update_styles(self):
        currentText = self.dropdown_style.currentText()
        self.dropdown_style.currentIndexChanged.disconnect()
        self.dropdown_style.clear()
        styles = self.show_styles()
        self.dropdown_style.addItems(styles)
        self.dropdown_style.currentIndexChanged.connect(self.changeStyle)
        if currentText not in styles:
            self.dropdown_style.setCurrentIndex(1)
        else:
            self.dropdown_style.setCurrentText(currentText)

    def changeStyle(self):
        if self.dropdown_style.currentIndex() == 0:
            self.master.setStyleApp("Old")
        elif self.dropdown_style.currentIndex() == 1:
            self.master.setStyleApp("New")
        else:
            try:
                self.master.setStyleApp(self.dropdown_style.currentText())
            except FileNotFoundError:
                self.update_styles()

    def open_style_dlg(self, style_name: str = None):
        if style_name and not exists(f"DataSave/Styles/{style_name}.json"):
            self.master.show_err("FileNotFound", f"File {style_name}.json not found")
            self.update_styles()
            return
        dlg = SettingsColor(self.slider.value(), self, style_name)
        dlg.exec()


class SettingsColor(QtWidgets.QDialog):
    __slots__ = ("h_layout_window", "h_layout_button", "h_layout_text", "h_layout_dropdown", "h_layout_tab", "v_layout")
    def __init__(self, text_size, master, style_name):
        super().__init__()
        self.size_var = master.master.get_text_size()
        self.resize(self.size_var * 20, self.size_var * 15.4)
        self.colors = {}
        self.app = QtWidgets.QApplication.instance()
        self.master = master
        self.dlg_color = QtWidgets.QColorDialog()
        self.setWindowTitle("Create style")
        self.style_name = QtWidgets.QTextEdit()
        self.style_name.setMaximumSize(QtCore.QSize(text_size * 20, int((text_size / 2) * 5)))
        self.style_name.setStyleSheet("""* {font-size: %spx;
                                            border: 1.8px solid black;
                                            border-radius: 5px;}
                                         *:focus {border: 1px solid rgba(255, 255, 255, 70);}""" % text_size)
        self.style_name.setPlaceholderText("Name style")
        self.style_name.setAlignment(QtGui.Qt.AlignmentFlag.AlignCenter)
        self.style_name.setMinimumSize(QtCore.QSize(50, 35))

        if style_name:
            with open(f"DataSave/Styles/{style_name}.json", "r") as f:
                self.colors = loads(f.read())
            self._update_stylesheet()
            self.style_name.setText(style_name)
            self.style_name.setAlignment(QtGui.Qt.AlignmentFlag.AlignCenter)

        self.lb_window = QtWidgets.QLabel("Window")
        self.btn_window = QtWidgets.QPushButton(text="Select color")
        self.btn_window.clicked.connect(lambda: self._stylesheet_select(self.dlg_color.getColor(),
                                                                "QMainWindow",
                                                                 ("background-color",)))

        self.lb_button = QtWidgets.QLabel("Button")
        self.btn_button = QtWidgets.QPushButton(text="Select color")
        self.btn_button.clicked.connect(lambda: self._stylesheet_select(self.dlg_color.getColor(),
                                                                        "QPushButton",
                                                                 ("background-color",)))
        self.frame_button_extra = ExtraButtonOption(self)
        self.frame_button_extra.setHidden(True)
        self.btn_button_extra = QtWidgets.QPushButton(text="Extra options")
        self.btn_button_extra.clicked.connect(lambda: self._open_extra(self.frame_button_extra))

        self.lb_text = QtWidgets.QLabel("Text")
        self.btn_text = QtWidgets.QPushButton(text="Select color")
        self.btn_text.clicked.connect(lambda: self._stylesheet_select(self.dlg_color.getColor(),
                                                             "QLabel",
                                                               ("color",)))

        self.lb_dropdown = QtWidgets.QLabel("Dropdown")
        self.btn_dropdown = QtWidgets.QPushButton(text="Select color")
        self.btn_dropdown.clicked.connect(lambda: self._stylesheet_select(self.dlg_color.getColor(),
                                                                 "QComboBox",
                                                                   ("background-color",)))
        self.frame_dropdown_extra = ExtraDropdownOption(self)
        self.frame_dropdown_extra.setHidden(True)
        self.btn_dropdown_extra = QtWidgets.QPushButton(text="Extra options")
        self.btn_dropdown_extra.clicked.connect(lambda: self._open_extra(self.frame_dropdown_extra))

        self.lb_tab = QtWidgets.QLabel("Tab")
        self.btn_tab = QtWidgets.QPushButton(text="Select color")
        self.btn_tab.clicked.connect(lambda: self._stylesheet_select(self.dlg_color.getColor(),
                                                            "QTabWidget::pane",
                                                              ("background-color",)))
        self.frame_tab_extra = ExtraTabOption(self)
        self.frame_tab_extra.setHidden(True)
        self.btn_tab_extra = QtWidgets.QPushButton(text="Extra options")
        self.btn_tab_extra.clicked.connect(lambda: self._open_extra(self.frame_tab_extra))

        self.btnBox = QtWidgets.QDialogButtonBox((QtWidgets.QDialogButtonBox.StandardButton.Ok |
                                                  QtWidgets.QDialogButtonBox.StandardButton.Cancel))
        self.btnBox.accepted.connect(self.accept)
        self.btnBox.rejected.connect(self.reject)

        self.h_layout_window = QtWidgets.QHBoxLayout()
        self.h_layout_button = QtWidgets.QHBoxLayout()
        self.h_layout_text = QtWidgets.QHBoxLayout()
        self.h_layout_dropdown = QtWidgets.QHBoxLayout()
        self.h_layout_tab = QtWidgets.QHBoxLayout()

        self.h_layout_window.addWidget(self.lb_window)
        self.h_layout_window.addWidget(self.btn_window)
        self.h_layout_button.addWidget(self.lb_button)
        self.h_layout_button.addWidget(self.btn_button)
        self.h_layout_text.addWidget(self.lb_text)
        self.h_layout_text.addWidget(self.btn_text)
        self.h_layout_dropdown.addWidget(self.lb_dropdown)
        self.h_layout_dropdown.addWidget(self.btn_dropdown)
        self.h_layout_tab.addWidget(self.lb_tab)
        self.h_layout_tab.addWidget(self.btn_tab)

        self.v_layout = QtWidgets.QVBoxLayout(self)
        self.v_layout.addWidget(self.style_name)
        self.v_layout.addLayout(self.h_layout_window)
        self.v_layout.addLayout(self.h_layout_button)
        self.v_layout.addWidget(self.btn_button_extra)
        self.v_layout.addWidget(self.frame_button_extra)
        self.v_layout.addLayout(self.h_layout_text)
        self.v_layout.addLayout(self.h_layout_dropdown)
        self.v_layout.addWidget(self.btn_dropdown_extra)
        self.v_layout.addWidget(self.frame_dropdown_extra)
        self.v_layout.addLayout(self.h_layout_tab)
        self.v_layout.addWidget(self.btn_tab_extra)
        self.v_layout.addWidget(self.frame_tab_extra)
        self.v_layout.addWidget(self.btnBox)

    def _parent_select(self):
        pass

    def _stylesheet_select(self, color=None, obj_name: str = None, options: tuple = None):
        for i in options:
            if self.colors.get(obj_name):
                self.colors.get(obj_name).update({i: f"{color.name()}"})
            else:
                self.colors.update({obj_name: {i: f"{color.name()}"}})
        self._update_stylesheet()

    def _update_stylesheet(self):
        styles = []
        for k, v in self.colors.items():
            styles.append(f"{k} {v}".replace(",", ";").replace("'", ""))
            for i in range(len(styles)):
                if styles[i][:len(k)] == k:
                    styles[i] = f"{k} {v}".replace(",", ";").replace("'", "")

        self.setStyleSheet("""\n""".join(styles))
        self.update()

    def accept(self):
        if self.style_name.toPlainText().replace(" ", "") == "":
            self.master.master.show_err("ValueError", "Enter name for style!")
            return

        if not exists("DataSave/Styles"):
            makedirs("DataSave/Styles")
        with open(f"DataSave/Styles/{self.style_name.toPlainText()}.json", "w") as f:
            f.write(dumps(self.colors))

        self.master.update_styles()
        self.close()

    def _open_extra(self, frame: QtWidgets.QFrame):
        if frame.isHidden():
            frame.setHidden(False)
            if frame == self.frame_tab_extra:
                self.resize(self.size_var * 20, self.size_var * 42.4)
            else:
                self.resize(self.size_var * 20, self.size_var * 35.4)
        else:
            frame.setHidden(True)
            self.resize(self.size_var * 20, self.size_var * 15.4)


class ExtraButtonOption(QtWidgets.QFrame):
    __slots__ = ("h_layout_button_text", "h_layout_button_hover", "h_layout_button_disabled", "v_layout")
    def __init__(self, master):
        super().__init__()
        self.lb_button_text = QtWidgets.QLabel("Button text")
        self.btn_button_text = QtWidgets.QPushButton(text="Select color")
        self.btn_button_text.clicked.connect(lambda: master._stylesheet_select(master.dlg_color.getColor(),
                                                                               "QPushButton",
                                                                               ("color",)))

        self.lb_button_hover = QtWidgets.QLabel("Button hover")
        self.btn_button_hover = QtWidgets.QPushButton("Select color")
        self.btn_button_hover.clicked.connect(lambda: master._stylesheet_select(master.dlg_color.getColor(),
                                                                                "QPushButton::hover",
                                                                                ("background-color",)))

        self.lb_button_disabled = QtWidgets.QLabel("Button disabled")
        self.btn_button_disabled = QtWidgets.QPushButton("Select color")
        self.btn_button_disabled.clicked.connect(lambda: master._stylesheet_select(master.dlg_color.getColor(),
                                                                                   "QPushButton::disabled",
                                                                                   ("background-color",)))

        self.h_layout_button_text = QtWidgets.QHBoxLayout()
        self.h_layout_button_hover = QtWidgets.QHBoxLayout()
        self.h_layout_button_disabled = QtWidgets.QHBoxLayout()

        self.h_layout_button_text.addWidget(self.lb_button_text)
        self.h_layout_button_text.addWidget(self.btn_button_text)
        self.h_layout_button_hover.addWidget(self.lb_button_hover)
        self.h_layout_button_hover.addWidget(self.btn_button_hover)
        self.h_layout_button_disabled.addWidget(self.lb_button_disabled)
        self.h_layout_button_disabled.addWidget(self.btn_button_disabled)

        self.v_layout = QtWidgets.QVBoxLayout(self)
        self.v_layout.addLayout(self.h_layout_button_text)
        self.v_layout.addLayout(self.h_layout_button_hover)
        self.v_layout.addLayout(self.h_layout_button_disabled)


class ExtraDropdownOption(QtWidgets.QFrame):
    __slots__ = ("h_layout_dropdown_text", "h_layout_dropdown_hover", "h_layout_dropdown_disabled", "v_layout")
    def __init__(self, master):
        super().__init__()
        self.lb_dropdown_text = QtWidgets.QLabel("Dropdown text")
        self.btn_dropdown_text = QtWidgets.QPushButton(text="Select color")
        self.btn_dropdown_text.clicked.connect(lambda: master._stylesheet_select(master.dlg_color.getColor(),
                                                                                 "QComboBox",
                                                                                 ("color",)))

        self.lb_dropdown_hover = QtWidgets.QLabel("Dropdown hover")
        self.btn_dropdown_hover = QtWidgets.QPushButton("Select color")
        self.btn_dropdown_hover.clicked.connect(lambda: master._stylesheet_select(master.dlg_color.getColor(),
                                                                                  "QComboBox::hover",
                                                                                  ("background-color",)))

        self.lb_dropdown_disabled = QtWidgets.QLabel("Dropdown disabled")
        self.btn_dropdown_disabled = QtWidgets.QPushButton("Select color")
        self.btn_dropdown_disabled.clicked.connect(lambda: master._stylesheet_select(master.dlg_color.getColor(),
                                                                                     "QComboBox::disabled",
                                                                                     ("background-color",)))

        self.h_layout_dropdown_text = QtWidgets.QHBoxLayout()
        self.h_layout_dropdown_hover = QtWidgets.QHBoxLayout()
        self.h_layout_dropdown_disabled = QtWidgets.QHBoxLayout()

        self.h_layout_dropdown_text.addWidget(self.lb_dropdown_text)
        self.h_layout_dropdown_text.addWidget(self.btn_dropdown_text)
        self.h_layout_dropdown_hover.addWidget(self.lb_dropdown_hover)
        self.h_layout_dropdown_hover.addWidget(self.btn_dropdown_hover)
        self.h_layout_dropdown_disabled.addWidget(self.lb_dropdown_disabled)
        self.h_layout_dropdown_disabled.addWidget(self.btn_dropdown_disabled)

        self.v_layout = QtWidgets.QVBoxLayout(self)
        self.v_layout.addLayout(self.h_layout_dropdown_text)
        self.v_layout.addLayout(self.h_layout_dropdown_hover)
        self.v_layout.addLayout(self.h_layout_dropdown_disabled)

class ExtraTabOption(QtWidgets.QFrame):
    __slots__ = ("h_layout_tab_bar", "h_layout_tab_bar_text", "h_layout_tab_bar_hover", "h_layout_tab_bar_selected",
                 "h_layout_tab_bar_disabled", "v_layout")
    def __init__(self, master):
        super().__init__()
        self.lb_tab_bar = QtWidgets.QLabel("Tab bar")
        self.btn_tab_bar = QtWidgets.QPushButton(text="Select color")
        self.btn_tab_bar.clicked.connect(lambda: master._stylesheet_select(master.dlg_color.getColor(),
                                                                           "QTabBar::tab",
                                                                           ("background-color",)))

        self.lb_tab_bar_text = QtWidgets.QLabel("Tab bar text")
        self.btn_tab_bar_text = QtWidgets.QPushButton(text="Select color")
        self.btn_tab_bar_text.clicked.connect(lambda: master._stylesheet_select(master.dlg_color.getColor(),
                                                                                "QTabBar::tab",
                                                                                ("color",)))

        self.lb_tab_bar_hover = QtWidgets.QLabel("Tab bar hover")
        self.btn_tab_bar_hover = QtWidgets.QPushButton("Select color")
        self.btn_tab_bar_hover.clicked.connect(lambda: master._stylesheet_select(master.dlg_color.getColor(),
                                                                                 "QTabBar::tab:hover",
                                                                                 ("background-color",)))

        self.lb_tab_bar_selected = QtWidgets.QLabel("Tab bar selected")
        self.btn_tab_bar_selected = QtWidgets.QPushButton("Select color")
        self.btn_tab_bar_selected.clicked.connect(lambda: master._stylesheet_select(master.dlg_color.getColor(),
                                                                                    "QTabBar::tab:selected",
                                                                                    ("background-color",)))

        self.lb_tab_bar_disabled = QtWidgets.QLabel("Tab bar disabled")
        self.btn_tab_bar_disabled = QtWidgets.QPushButton("Select color")
        self.btn_tab_bar_disabled.clicked.connect(lambda: master._stylesheet_select(master.dlg_color.getColor(),
                                                                                    "QTabBar::tab:disabled",
                                                                                    ("background-color",)))
        self.lb_tab_disabled = QtWidgets.QLabel("Tab disabled")
        self.btn_tab_disabled = QtWidgets.QPushButton("Select color")
        self.btn_tab_disabled.clicked.connect(lambda: master._stylesheet_select(master.dlg_color.getColor(),
                                                                                "QTabWidget::pane:disabled",
                                                                                ("background-color",)))

        self.h_layout_tab_bar = QtWidgets.QHBoxLayout()
        self.h_layout_tab_bar_text = QtWidgets.QHBoxLayout()
        self.h_layout_tab_bar_hover = QtWidgets.QHBoxLayout()
        self.h_layout_tab_bar_selected = QtWidgets.QHBoxLayout()
        self.h_layout_tab_bar_disabled = QtWidgets.QHBoxLayout()
        self.h_layout_tab_disabled = QtWidgets.QHBoxLayout()

        self.h_layout_tab_bar.addWidget(self.lb_tab_bar)
        self.h_layout_tab_bar.addWidget(self.btn_tab_bar)
        self.h_layout_tab_bar_text.addWidget(self.lb_tab_bar_text)
        self.h_layout_tab_bar_text.addWidget(self.btn_tab_bar_text)
        self.h_layout_tab_bar_hover.addWidget(self.lb_tab_bar_hover)
        self.h_layout_tab_bar_hover.addWidget(self.btn_tab_bar_hover)
        self.h_layout_tab_bar_selected.addWidget(self.lb_tab_bar_selected)
        self.h_layout_tab_bar_selected.addWidget(self.btn_tab_bar_selected)
        self.h_layout_tab_bar_disabled.addWidget(self.lb_tab_bar_disabled)
        self.h_layout_tab_bar_disabled.addWidget(self.btn_tab_bar_disabled)
        self.h_layout_tab_disabled.addWidget(self.lb_tab_disabled)
        self.h_layout_tab_disabled.addWidget(self.btn_tab_disabled)

        self.v_layout = QtWidgets.QVBoxLayout(self)
        self.v_layout.addLayout(self.h_layout_tab_bar)
        self.v_layout.addLayout(self.h_layout_tab_bar_text)
        self.v_layout.addLayout(self.h_layout_tab_bar_hover)
        self.v_layout.addLayout(self.h_layout_tab_bar_selected)
        self.v_layout.addLayout(self.h_layout_tab_bar_disabled)
        self.v_layout.addLayout(self.h_layout_tab_disabled)