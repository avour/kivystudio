import os
from kivy.logger import Logger

from kivystudio.tools import threaded

class StdInOut(object):
    ''' class for writing to/reading from this console'''

    def __init__(self, obj, mode='stdout'):
        self.obj = obj
        self.mode = mode
        self.stdin_pipe, self.stdout_pipe = os.pipe()
        self.read_from_in_pipe()
        self.textcache = None

    def update_cache(self, text_line, *l):
        '''Update the output text area
        '''
        self.obj.textcache.append(text_line)

    @threaded
    def read_from_in_pipe(self, *l):
        '''Read the output from the command
        '''
        txt = '\n'
        txt_line = ''
        try:
            while txt != '':
                Logger.error('sdsd')
                txt = os.read(self.stdin_pipe, 1)
                txt_line += txt
                if txt == '\n':
                    if self.mode == 'stdin':
                        # run command
                        self.write(txt_line)
                    else:
                        Clock.schedule_once(
                            partial(self.update_cache, txt_line), 0)
                        self.flush()
                    txt_line = ''
        except OSError as e:
            Logger.exception(e)

    def close(self):
        '''Close the pipes
        '''
        os.close(self.stdin_pipe)
        os.close(self.stdout_pipe)

    def __del__(self):
        self.close()

    def fileno(self):
        return self.stdout_pipe

    def write(self, s):
        '''Write a command to the pipe
        '''
        if isinstance(s, bytes):
            s = s.decode(get_fs_encoding())
        Logger.debug('write called with command:' + s)
        if self.mode == 'stdout':
            self.obj.add_to_cache(s)
            self.flush()
        else:
            # process.stdout.write ...run command
            if self.mode == 'stdin':
                log = ''.join((
                    self.obj.prompt(), s))
                self.obj.log_out(log)
                # self.obj.txtinput_command_line.text = ''.join((
                #     self.obj.prompt(), s))
                # self.obj.on_enter()

    def read(self, no_of_bytes=0):
        if self.mode == 'stdin':
            # stdin.read
            Logger.exception('KivyConsole: can not read from a stdin pipe')
            return
        # process.stdout/in.read
        txtc = self.textcache
        if no_of_bytes == 0:
            # return all data
            if txtc is None:
                self.flush()
            while self.obj.command_status != 'closed':
                pass
            txtc = self.textcache
            return txtc
        try:
            self.textcache = txtc[no_of_bytes:]
        except IndexError:
            self.textcache = txtc
        return txtc[:no_of_bytes]

    def readline(self):
        if self.mode == 'stdin':
            # stdin.readline
            Logger.exception('KivyConsole: can not read from a stdin pipe')
            return
        else:
            # process.stdout.readline
            if self.textcache is None:
                self.flush()
            txt = self.textcache
            x = txt.find('\n')
            if x < 0:
                Logger.Debug('console_shell: no more data')
                return
            self.textcache = txt[x:]
            # ##self. write to ...
            return txt[:x]

    def flush(self):
        self.textcache = ''.join(self.obj.textcache)
        return
