import threading
import tkinter

from tkinter import filedialog

from scripts import utils, checking, manage_account
from scripts.types import StartEvent

import style


root = tkinter.Tk()
root.title('Soft 1.0')
root.geometry('1080x540')
root.minsize(1080, 540)


FILES_PATH = {}

TXTVAR_1 = tkinter.StringVar(root, value='Action')
TXTVAR_2 = tkinter.StringVar(root, value='Time')

BOOLVAR_1 = tkinter.BooleanVar(root)
BOOLVAR_2 = tkinter.BooleanVar(root)
BOOLVAR_3 = tkinter.BooleanVar(root)
BOOLVAR_4 = tkinter.BooleanVar(root)

FILE_TYPES = (
    ('Text Files', '*.txt'),
)

logger = utils.LogVar(root)


def focus_in(event: tkinter.Event, string: str) -> None:

    if event.widget.get() == string:
        event.widget.delete(0, tkinter.END)


def focus_out(event: tkinter.Event, string: str) -> None:

    if event.widget.get() == '':
        event.widget.insert(0, string)


class MainApp(tkinter.Frame):

    def __init__(self, master: tkinter.Tk) -> None:
        super().__init__(master)

        self._create_toplevel()
        self._create_log_label()


    def _create_toplevel(self) -> None:
        toplevel = tkinter.Frame(root, style.TOPLEVEL)
        toplevel.pack(side=tkinter.TOP, fill=tkinter.X)

        level_1 = tkinter.Frame(root, style.LEVEL_1)
        level_1.pack(side=tkinter.TOP, fill=tkinter.X)


        self.button_1 = tkinter.Button(toplevel, style.INNER_BUTTON_MANAGE, text='Account',
                                       command=lambda: self.load_file('account'))
        self.button_1.pack(padx=14, side=tkinter.LEFT)

        self.button_2 = tkinter.Button(toplevel, style.INNER_BUTTON_MANAGE, text='Proxy',
                                       command=lambda: self.load_file('proxy'))
        self.button_2.pack(padx=14, side=tkinter.LEFT)

        self.button_3 = tkinter.Button(toplevel, style.INNER_BUTTON_MANAGE, text='Link',
                                       command=lambda: self.load_file('link'))
        self.button_3.pack(padx=14, side=tkinter.LEFT)


        self.entry_1 = tkinter.Entry(toplevel, style.INNER_ENTRY, textvariable=TXTVAR_1)
        self.entry_1.bind('<FocusIn>', lambda event: focus_in(event, 'action'))
        self.entry_1.bind('<FocusOut>', lambda event: focus_out(event, 'action'))
        self.entry_1.pack(padx=20, side=tkinter.LEFT)

        self.entry_2 = tkinter.Entry(toplevel, style.INNER_ENTRY, textvariable=TXTVAR_2)
        self.entry_2.bind('<FocusIn>', lambda event: focus_in(event, 'time'))
        self.entry_2.bind('<FocusOut>', lambda event: focus_out(event, 'time'))
        self.entry_2.pack(padx=20, side=tkinter.LEFT)


        self.checkbox_4 = tkinter.Checkbutton(toplevel, style.INNER_CHECKBOX, text='Check account',
                                              variable=BOOLVAR_4)
        self.checkbox_4.pack(padx=15, side=tkinter.RIGHT)

        self.checkbox_3 = tkinter.Checkbutton(toplevel, style.INNER_CHECKBOX, text='Repost',
                                              variable=BOOLVAR_3)
        self.checkbox_3.pack(padx=15, side=tkinter.RIGHT)

        self.checkbox_2 = tkinter.Checkbutton(toplevel, style.INNER_CHECKBOX, text='Like',
                                              variable=BOOLVAR_2)
        self.checkbox_2.pack(padx=15, side=tkinter.RIGHT)

        self.checkbox_1 = tkinter.Checkbutton(toplevel, style.INNER_CHECKBOX, text='Sub',
                                              variable=BOOLVAR_1)
        self.checkbox_1.pack(padx=15, side=tkinter.RIGHT)


        self.button_start = tkinter.Button(level_1, style.INNER_BUTTON_START, text='Start',
                                           command=self.start_script)
        self.button_start.pack(side=tkinter.LEFT)


    def _create_log_label(self) -> None:
        field = tkinter.Frame(root, style.LOG_FIELD)
        field.pack(side=tkinter.TOP, fill=tkinter.BOTH)

        inner_field = tkinter.Frame(field, style.INNER_LOG_FIELD)
        inner_field.pack(side=tkinter.TOP, fill=tkinter.BOTH)

        label = tkinter.Listbox(inner_field, style.LOG_LABEL, listvariable=logger)
        label.pack(side=tkinter.TOP, fill=tkinter.BOTH)


    def load_file(self, name: str) -> None:
        file_path = filedialog.askopenfilename(title='Select a text file.',
                                               filetypes=FILE_TYPES)

        if file_path:
            FILES_PATH.update({name: file_path})
            logger.update(f'File for {name} set.')


    def start_script(self) -> None:
        subscription, like, repost = BOOLVAR_1.get(), BOOLVAR_2.get(), BOOLVAR_3.get()
        check_account = BOOLVAR_4.get()

        action, time = TXTVAR_1.get(), TXTVAR_2.get()


        if not FILES_PATH.get('account'):
            return logger.update('Add required accounts file!')

        if not FILES_PATH.get('link') and any((subscription, repost, like)):
            return logger.update('Add a file with links!')

        if not all((action.isdigit(), time.isdigit())):
            return logger.update('Enter a numeric value into the action and time fields!')

        if not any((subscription, repost, like, check_account)):
            return logger.update('Select at least one checkbox!')

        if utils.check_internet() is False:
            return logger.update('No internet connection!')


        self.button_start.config(state=tkinter.DISABLED)
        self.button_1.config(state=tkinter.DISABLED)
        self.button_2.config(state=tkinter.DISABLED)
        self.button_3.config(state=tkinter.DISABLED)

        self.entry_1.config(state=tkinter.DISABLED)
        self.entry_2.config(state=tkinter.DISABLED)

        self.checkbox_1.config(state=tkinter.DISABLED)
        self.checkbox_2.config(state=tkinter.DISABLED)
        self.checkbox_3.config(state=tkinter.DISABLED)
        self.checkbox_4.config(state=tkinter.DISABLED)


        event = StartEvent(files_path=FILES_PATH,
                           action=int(time),
                           time=int(action),
                           logger=logger,
                           subscription=subscription,
                           repost=repost,
                           like=like)

        if check_account is False:
            threading.Thread(target=manage_account, args=(self, event)).start()
        else:
            threading.Thread(target=checking, args=(self, event)).start()


if __name__ == '__main__':
    app = MainApp(root)
    app.mainloop()
