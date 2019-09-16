
import os
from os.path import dirname, join, exists, expanduser
from kivy import platform
from kivy.lang import Builder
from kivy.core.window import Window

def set_auto_mouse_position(widget):
    ''' functions trys to position widget
    automaticaly on the mouse pos'''

    if Window.mouse_pos[0]+widget.width > Window.width:
        widget.x = Window.mouse_pos[0]

    else:
        widget.x = Window.mouse_pos[0]
    
    if (Window.mouse_pos[1]+widget.height > Window.height):
        widget.top = Window.mouse_pos[1]-16
    else:
        widget.top = Window.mouse_pos[1]-16

def load_kv(filepath, file):
	''' load a kivy file from the current
		directory of the file calling this func
		where filepath is __file__ and file is a kv file''' 
	filepath = dirname(filepath)
	Builder.load_file(join(filepath, file))


def get_user_data_dir(name):
    # Determine and return the user_data_dir.
    data_dir = ""
    if platform == 'ios':
        raise NotImplemented()
    elif platform == 'android':
        raise NotImplemented()
    elif platform == 'win':
        data_dir = os.path.join(os.environ['APPDATA'], name)
    elif platform == 'macosx':
        data_dir = '~/Library/Application Support/{}'.format(name)
        data_dir = expanduser(data_dir)
    else:  # _platform == 'linux' or anything else...:
        data_dir = os.environ.get('XDG_CONFIG_HOME', '~/.config')
        data_dir = expanduser(join(data_dir, name))
    if not exists(data_dir):
        os.mkdir(data_dir)
    return data_dir


def threaded(func, *args, **kwargs):
	'decorator that run fuc in a thread'
	from threading import Thread
	def caller(*args, **kwargs):
		Thread(target=func, args=args,
				kwargs=kwargs, daemon=True).start()
	return caller
