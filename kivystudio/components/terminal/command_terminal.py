

from kivystudio.widgets.kivycmd import KivyCmd

from kivy import properties as prop
from kivy.lang import Builder
from kivy.factory import Factory

MAX_LOG_LINES = 260


class CommandTerminal(KivyCmd):
    
    text = prop.StringProperty()
    ''' property where the logs are stored '''

    top_pannel_items = prop.ListProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        clearbtn = Factory.TopPanelButton(icon='fa-trash-o')
        self.top_pannel_items.append(clearbtn)

