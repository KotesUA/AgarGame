from functools import partial
import pygame_menu


class ClientMenu:
    MENU_VERTICAL_MARGIN = 25

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.theme = pygame_menu.themes.THEME_SOLARIZED.copy()
        self.theme.title_bar_style = pygame_menu.widgets.MENUBAR_STYLE_ADAPTIVE
        self.theme.widget_selection_effect = pygame_menu.widgets.NoneSelection()

        self.start_menu = pygame_menu.menu.Menu(theme=self.theme,height = self.height,width = self.width,onclose = pygame_menu.events.RESET,title='Start')

        self.update_menu(lambda*args:None)

    def update_menu(self, connect_callback):
        self.start_menu.clear()

        self.start_menu.add.text_input('Nickname: ',default='Cell',maxwidth=14,textinput_id='nick',input_underline='_')
        self.start_menu.add.text_input('Server: ',default='localhost:9999',maxwidth=14,textinput_id='addr', input_underline='_')
        self.start_menu.add.vertical_margin(ClientMenu.MENU_VERTICAL_MARGIN)
        self.start_menu.add.button('Connect',partial(connect_callback,self.start_menu.get_input_data()))
        self.start_menu.add.button('Exit',pygame_menu.events.EXIT)

    def get_menu(self):
        return self.start_menu
