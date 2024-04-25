from flet import (Page, Text, ThemeMode, CrossAxisAlignment,
                  Banner, colors, Icon, icons, FilledTonalButton, app)
from UI import MainScreen
from json import loads


def main(page: Page):
    def check_theme():
        try:
            with open("config.json", "r") as f:
                settings = loads(f.read())
                theme = settings.get("theme_mode")
                if theme == "True":
                    page.theme_mode = ThemeMode.LIGHT
        except FileNotFoundError:
            pass

    def close_banner(e):
        page.banner.open = False
        page.update()

    page.title = "Starter scripts"
    page.window_min_width = 500
    page.window_min_height = 400
    page.window_width = 650
    page.window_height = 450
    page.theme_mode = ThemeMode.DARK
    page.horizontal_alignment = CrossAxisAlignment.CENTER
    page.window_center()

    main_screen = MainScreen()
    page.controls.append(main_screen)

    check_theme()

    page.banner = Banner(bgcolor=colors.AMBER_100,
                         leading=Icon(icons.WARNING_AMBER, color=colors.AMBER, size=40),
                         content=Text("Warning this is application located on stage development! Probably bugs!",
                                      color=colors.BLACK),
                         actions=[FilledTonalButton("Close", on_click=close_banner)])
    page.banner.open = True
    page.update()


if __name__ == "__main__":
    app(target=main)
