from kivy.uix.textinput import TextInput
from kivy.properties import StringProperty
from kivy.clock import Clock
import os

class CmdInput(TextInput):

    _current_instance = None

    console = None

    def __init__(self, console=None,**k):
        CmdInput._current_instance = self
        super(CmdInput,self).__init__(**k)
        self.console=console
        
        self.set_hostname()
        self.text = self.get_display_path()

    def get_command(self,*a):
        command = self.text[len(self.get_display_path()):]
        return command

    def set_hostname(self):
        if hasattr(os, 'uname'):
            self._hostname = os.uname()[1]
        else:
            self._hostname = os.environ.get('COMPUTERNAME', 'unknown')

        self._username = os.environ.get('USER', '')
        if not self._username:
            self._username = os.environ.get('USERNAME', 'unknown')

    def get_display_path(self, *args):
        # username = '[color=#ff6600][b]'+self._username+'@'+self._hostname+'[/b][/color]'
        # curpath =  '[color=#2266ff][b] '+self.current_path+ '[/b][/color]'
        username = self._username+'@'+self._hostname+':'
        curpath =  self.console.current_dir
        path = "[%s %s]$    " % (
            username,
            curpath)
        return path

    def keyboard_on_key_down(self, keyboard, keycode, text, modifiers):
        # print(keyboard,keycode,text,modifiers)
        if keycode[1]=='backspace':
            if len(self.text) == len(self.get_display_path()):
                return True
        if keycode[1]=='enter':
            self.console.on_enter()
            return True

        return super(CmdInput,self).keyboard_on_key_down(keyboard,keycode,text,modifiers)

    def _move_cursor_to_end(self, instance):
        '''Moves the command input cursor to the end'''
        def mte(*l):
            instance.cursor = instance.get_cursor_from_index(len_prompt)
        len_prompt = len(self.get_display_path())
        if instance.cursor[0] < len_prompt:
            Clock.schedule_once(mte, -1)

