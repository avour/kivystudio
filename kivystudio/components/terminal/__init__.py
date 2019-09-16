from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors import ToggleButtonBehavior
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy import properties as prop
from kivy.clock import Clock

from kivy.lang import Builder
from kivystudio.libs.resizablebehavior import ResizableBehavior

from .logger_space import ErrorLogger
from .command_terminal import CommandTerminal


class TerminalSpace(ResizableBehavior, BoxLayout):

    manager = prop.ObjectProperty(None)
    ''' Instance of screen manager used '''

    tab_container = prop.ObjectProperty(None)
    ''' instance of a gridlayout where tha tab lays'''

    state = prop.OptionProperty('open', options=['open', 'close'])

    def __init__(self, **k):
        super(TerminalSpace, self).__init__(**k)
        self.logger = ErrorLogger()
        self.add_widget(self.logger, title='Logs')
        self.terminal = CommandTerminal()
        self.add_widget(self.terminal, title='Terminal')

    def add_widget(self, widget, title=''):
        if len(self.children) > 1:
            tab = TerminalTab()
            tab.text=title
            tab.name=title
            tab.bind(state=self.tab_state)
            self.tab_container.add_widget(tab)
            Clock.schedule_once(lambda dt: setattr(tab, 'state', 'down'))
            screen = Screen(name=title)
            screen.add_widget(widget)
            self.manager.add_widget(screen)
        else:
            super(TerminalSpace, self).add_widget(widget)

    def tab_state(self, tab, state):
        panel = self.manager.get_screen(tab.name).children[0]
        if state=='down':
            self.manager.current = tab.name
            for item in panel.top_pannel_items:
                self.top_pannel.add_widget(item, 2)
        else:
            for item in panel.top_pannel_items:
                if item in self.top_pannel.children:
                    self.top_pannel.remove_widget(item)

 
    def on_state(self, *args):
        if self.state=='open':
            self.height = self.norm_height
        else:
            self.height='48dp'

    def toggle_state(self):
        if self.state=='open':
            self.state='close'
        else:
            self.state='open'

class TerminalTab(ToggleButtonBehavior, Label):

    def on_state(self, *a):
        if self.state=='down':
            self.text = "[u]" + self.text + "[/u]"
            self.color = (.9,.9,.9,1)
        else:
            self.text = self.text.replace('[u]','').replace('[/u]','')
            self.color = (.5,.5,.5,1)


Builder.load_string('''
<TerminalSpace>:
    resizable_up: True
    tab_container: tab_container
    top_pannel: top_pannel
    manager: manager
    orientation: 'vertical'
    pos_hint: {'y': 0, 'center_x': .5}
    size_hint_y: None
    max_norm_height: dp(380)
    norm_height: dp(200)
    height: self.norm_height
    on_height:
        if self.height > self.max_norm_height: height_tog.state='down'
    canvas.before:
        Color:
            rgba: .12,.12,.12,1
        Rectangle:
            size: self.size
            pos: self.pos
        Color:
            rgba: 1,1,1,1
        Line:
            points: [self.x,self.top,self.right,self.top]
            width: dp(1.4)
    BoxLayout:
        size_hint_y: None
        height: '48dp'
        GridLayout:
            id: tab_container
            rows: 1
        BoxLayout:
            id: top_pannel
            size_hint_x: None
            width: self.minimum_width
            IconToggleLabel:
                id: height_tog
                icon_normal: 'fa-angle-up'
                icon_down: 'fa-angle-down'
                icon: self.icon_normal
                icon_size: 30
                size_hint_x: None
                width: '32dp'
                on_state:
                    root.state='open'
                    if self.state=='down': root.height=root.max_norm_height
                    else: root.height=root.norm_height
            IconLabelButton:
                icon: 'fa-close'
                size_hint_x: None
                width: '32dp'
                on_release: root.state='close'
    ScreenManager:
        id: manager

<TerminalTab>:
    allow_no_selection: True
    group: '__terminal_tab__'
    size_hint_x: None
    width: '94dp'
    markup: True

<TopPanelButton@IconLabelButton>:
    icon: 'fa-close'
    size_hint_x: None
    width: '32dp'

''')