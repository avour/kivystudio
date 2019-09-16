
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy.uix.behaviors import ToggleButtonBehavior, ButtonBehavior

from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import ListProperty, BooleanProperty

from kivystudio.behaviors import HoverBehavior
from . import dropmenu

__all__ = ('TopMenu',)


class TopMenu(GridLayout):
    drop_on_hover = BooleanProperty(False)

    def __init__(self, **kwargs):
        super(TopMenu, self).__init__(**kwargs)

    def drop(self, btn, hover):
        if hover and not self.dropdown.parent:
            self.dropdown.drop_list=btn.drop_list
            self.dropdown.open(btn)
        else:
            Clock.schedule_once(self.decide_drop)
    
    def decide_drop(self, dt):
        if not self.dropdown.hover:
            self.dropdown.dismiss()

    def drop_menu(self, menu_name, index):
        if not hasattr(self, menu_name):
            setattr(self, menu_name, getattr(dropmenu, menu_name)())
        
        menu = getattr(self, menu_name)
        if menu.parent:
            menu.parent.remove_widget(menu)
        menu.open(self.children[index])


class TopMenuItem(HoverBehavior, ButtonBehavior, Label):

    def on_hover(self, *args):
        if self.hover:
            self.text = "[u]" + self.text + "[/u]"
            self.color = (.1,.1,.1,1)
                
        else:
            self.text = self.text.replace('[u]','').replace('[/u]','')
            self.color = (0,0,0,1)
            


Builder.load_string('''

<TopMenu>:
    size_hint_y: None
    height: '24dp'
    rows: 1
    canvas.before:
        Color:
            rgba: .85,.85,.85,1
        Rectangle:
            size: self.size
            pos: self.pos
    TopMenuItem:
        text: 'File'
        on_release:
            root.drop_on_hover=False;
            root.drop_menu('FileTopMenu', 4)

    TopMenuItem:
        text: 'Edit'
        on_release:
            root.drop_on_hover=False;
            root.drop_menu('EditTopMenu', 3)

    TopMenuItem:
        text: 'View'
        on_release:
            root.drop_on_hover=False;
            root.drop_menu('FileTopMenu', 2)

    TopMenuItem:
        text: 'Selection'
        on_release:
            root.drop_on_hover=False;
            root.drop_menu('FileTopMenu', 1)

    TopMenuItem:
        text: 'Help'
        on_release:
            root.drop_on_hover=False;
            root.drop_menu('FileTopMenu', 0)

<TopMenuItem>:
    size_hint_x: None
    width: '60dp'
    markup: True
    color: (0,0,0,1)



''')
