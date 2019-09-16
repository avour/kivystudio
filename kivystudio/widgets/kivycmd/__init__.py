
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.codeinput import CodeInput
from kivy.uix.textinput import TextInput
from kivy.uix.behaviors import FocusBehavior

from kivy.properties import OptionProperty, StringProperty
from kivy.lang import Builder
from kivy.clock import mainthread
from kivy.properties import *
from kivy.compat import PY2
from kivy.utils import platform
from kivy.logger import Logger

from .cmdinput import CmdInput
from .std_in_out import StdInOut

from kivystudio.tools import threaded

import os, sys, subprocess, shlex, re


@threaded
def run_cmd(self, command):
    '''Run the command
    '''
    # this is run inside a thread so take care, avoid gui ops

    # replace $PATH with
    command = os.path.expandvars(command)

    # if command = clear or cls for windows users
    if command == 'clear' or command == 'cls':
        self.clear_output()
        return

    # if command = cd change directory
    if command.startswith('cd ') or command.startswith('export '):
        if command[0] == 'e':
            e_q = command[7:].find('=')
            _exprt = command[7:]
            if e_q:
                os.environ[_exprt[:e_q]] = _exprt[e_q + 1:]
                self.environment = os.environ.copy()
        else:
            command = re.sub('[ ]+', ' ', command)
            if command[3] == os.sep:
                dir_path = command[3:]
            else:
                dir_path = os.path.join(self.current_dir, command[3:])
            dir_path = os.path.abspath(dir_path)
            if os.path.exists(dir_path):
                self.current_dir = dir_path
            else:
                self.log_out('bash: cd: {}: No such file or directory'.format(command[3:]))
                return
        self.command_done()
        return

    try:
        _posix = True
        if sys.platform[0] == 'w':
            _posix = False
        cmd = command
        if PY2 and isinstance(cmd, unicode):
            cmd = command
        if not self.shell:
            cmd = shlex.split(cmd, posix=_posix)
            for i in range(len(cmd)):
                cmd[i] = cmd[i].replace('\x01', ' ')
            map(lambda s: s, cmd)
    except Exception as err:
        Logger.exception(err)
        cmd = ''
        self.add_to_cache(''.join((str(err), ' <', command, ' >\n')))

    if cmd:
        # prev_stdout = sys.stdout
        # sys.stdout = self.stdout
        try:
            # execute command
            popen_obj = popen = subprocess.Popen(
                cmd,
                bufsize=0,
                stdout=subprocess.PIPE,
                stdin=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                preexec_fn=None,
                close_fds=False,
                shell=self.shell,
                cwd=self.current_dir,
                universal_newlines=False,
                startupinfo=None,
                creationflags=0)
            # print(popen_obj.stdout.read(), 'stdout')
            log = popen_obj.stdout.read()
            Logger.info(log)
            self.log_out(log)
            popen_stdout_r = popen.stdout.readline
            popen_stdout_flush = popen.stdout.flush
            txt = popen_stdout_r()
            plat = platform
            while txt:
                # skip flush on android
                if plat[0] != 'a':
                    popen_stdout_flush()

                if isinstance(txt, bytes):
                    txt = txt
                self.add_to_cache(txt)
                txt = popen_stdout_r()
        except (OSError, ValueError) as err:
            self.log_out(str(err))
            self.add_to_cache(''.join(
                    (str(err),
                        ' < ', command, ' >\n')))
            # self.command_status = 'closed'
            # self.dispatch('on_subprocess_done')
        # sys.stdout = prev_stdout
    self.popen_obj = None

class KivyCmd(ScrollView):

    command_status=''
    textcache=[]

    foreground_color = ListProperty((1, 1, 1, 1))
    '''This defines the color of the text in the console
    :data:`foreground_color` is an :class:`~kivy.properties.ListProperty`,
    Default to '(1, 1, 1, 1)'
    '''

    background_color = ListProperty((0, 0, 0, 1))
    '''This defines the color of the text in the console
    :data:`foreground_color` is an :class:`~kivy.properties.ListProperty`,
    Default to '(0, 0, 0, 1)'
    '''

    cached_history = NumericProperty(200)
    '''Indicates the No. of lines to cache. Defaults to 200
    :data:`cached_history` is an :class:`~kivy.properties.NumericProperty`,
    Default to '200'
    '''

    cached_commands = NumericProperty(90)
    '''Indicates the no of commands to cache. Defaults to 90
    :data:`cached_commands` is a :class:`~kivy.properties.NumericProperty`,
    Default to '90'
    '''

    environment = DictProperty(os.environ.copy())
    '''Indicates the environment the commands are run in. Set your PATH or
    other environment variables here. like so::
        kivy_console.environment['PATH']='path'

    environment is :class:`~kivy.properties.DictProperty`, defaults to
    the environment for the process running Kivy console
    '''

    textcache = ListProperty(['', ])
    '''Indicates the cache of the commands and their output

    :data:`textcache` is a :class:`~kivy.properties.ListProperty`,
    Default to ''
    '''

    shell = BooleanProperty(False)
    '''Indicates the whether system shell is used to run the commands

    :data:`shell` is a :class:`~kivy.properties.BooleanProperty`,
    Default to 'False'

    WARNING: Shell = True is a security risk and therefore = False by default,
    As a result with shell = False some shell specific commands and
    redirections
    like 'ls |grep lte' or dir >output.txt will not work.
    If for some reason you need to run such commands, try running the platform
    shell first
    eg:  /bin/sh ...etc on nix platforms and cmd.exe on windows.
    As the ability to interact with the running command is built in,
    you should be able to interact with the native shell.

    Shell = True, should be set only if absolutely necessary.
    '''

    current_dir = StringProperty(os.path.expanduser('~'))

    _current_instance = None

    def __init__(self, **k):
        KivyCmd._current_instance = self
        super(KivyCmd,self).__init__(**k)
        self.stdout = StdInOut(self, 'stdout')
        self.stdin = StdInOut(self, 'stdin')

        cmd_input = CmdContent(cmd_type='input')
        self.cmd_container.add_widget(cmd_input)
        cmd_input.context.focus = True
        self.current_input = cmd_input

    @mainthread
    def log_out(self, msg):
        output = CmdContent(cmd_type='output')
        self.cmd_container.add_widget(output)
        @mainthread
        def set_text():
            output.context.text = msg
            self.command_done()
            self.scroll_y = 0
        set_text()

    def on_enter(self):
        cmdinput = CmdInput._current_instance
        cmd = cmdinput.get_command()
        run_cmd(self, cmd)

    def add_to_cache(self, _string):
        self.textcache.append(_string)

    @mainthread
    def command_done(self):
        self.current_input.context.readonly = True
        cmd_input = CmdContent(cmd_type='input')
        self.cmd_container.add_widget(cmd_input)
        cmd_input.context.focus = True
        self.current_input = cmd_input
    
    def clear_output(self):
        self.cmd_container.clear_widgets()
        self.command_done()

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            super(KivyCmd,self).on_touch_down(touch)
            FocusBehavior.ignored_touch.append(touch)
            self.current_input.context.focus = True
            return True

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            super(KivyCmd,self).on_touch_up(touch)
            FocusBehavior.ignored_touch.append(touch)
            self.current_input.context.focus = True
            return True

class CmdContent(GridLayout):
    
    cmd_type = OptionProperty('input', options=['input', 'output',])
    context = None

    def __init__(self, **kwargs):
        super(CmdContent,self).__init__(**kwargs)
        getattr(self, 'show_{}'.format(self.cmd_type))()
        
    def on_cmd_type(self, *a):
        self.clear_widgets()
        getattr(self, 'show_{}'.format(self.cmd_type))()

    def show_input(self):
        self.context = CmdInput(console=KivyCmd._current_instance)
        self.add_widget(self.context)

    @mainthread
    def show_output(self):
        self.context = CmdOutput()
        self.add_widget(self.context)


class CmdOutput(TextInput):
    pass

Builder.load_string('''
<KivyCmd>:
    cmd_container: cmd_container
    GridLayout:
        id: cmd_container
        size_hint_y: None
        height: self.minimum_height
        cols: 1

<CmdContent>:
    size_hint_y: None
    height: self.minimum_height
    cols: 1

<CmdOutput>
    size_hint_y: None
    height: self.minimum_height
    readonly: True
    foreground_color: (.6,.6,.6,1)
    background_color: (0,0,0,1)
    cursor_color: 0,0,0,0
    # font_size: root.font_size

<CmdInput>
    size_hint_y: None
    height: self.minimum_height
    multiline: True
    foreground_color: (1,1,1,1)
    background_color: (0,0,0,1)
    # font_size: root.font_size
    on_touch_up:
        self.collide_point(*args[1].pos)\\
        and root._move_cursor_to_end(self)
''')
