import global_vars as Globals
import main_functions_lib as FUNC
import tkinter as tk
from os import path as OSpath
from tkinter import filedialog
from tkinter import scrolledtext
import tkinter.font as TKfont

class APP(tk.Tk):
    def __init__(self):
        super().__init__()
        self.geometry(str(Globals.app_width) + "x" + str(Globals.app_height))
        self.title(Globals.app_title)
        self.resizable(0,0)                                                 # makes the app window unresizable

        # Buttons for files choosing
        self.buttons = {}
        for i in range(2):
            self.buttons['btn'+str(i)] = tk.Button(self, padx=10, pady=3, height=1, width=33)
            self.buttons['btn'+str(i)].grid(column=0, row=i, columnspan=2, padx=7, pady=15-(i*15), sticky=tk.E)
        self.buttons['btn0']['text']    = 'Выбрать список названий с Type ID'
        self.buttons['btn1']['text']    = 'Выбрать список OEM-номеров с Type ID'
        self.buttons['btn0']['command'] = self.btn0_clicked
        self.buttons['btn1']['command'] = self.btn1_clicked

        # Labels for files choosing
        self.labels = {}
        for i in range(2):
            self.labels['lbl'+str(i)] = {'num'      : i,
                                         'obj'      : tk.Label(self,
                                                               padx=12,
                                                               pady=5,
                                                               width=47,
                                                               text='Не выбрано',
                                                               foreground=Globals.COLORS['red'],
                                                               anchor='w',
                                                               relief=tk.GROOVE)}
            self.labels['lbl'+str(i)]['obj'].grid(column=2, row=i, columnspan=2, padx=15, sticky=tk.W)

        # Hint text (label) for client's feed
        text = ''
        for i in range(129):
            text += '-'
        text += """
↓ Вставьте в поле ниже список наименований из фида клиента. Желательно удалить все лишние строки снизу. ↓"""
        self.labels['feed_hint'] = {}
        self.labels['feed_hint']['obj'] = tk.Label(self, text=text, justify=tk.LEFT, anchor='w')
        self.labels['feed_hint']['obj'].grid(column=0, row=2, columnspan=4, padx=5, pady=5, sticky=tk.W)

        # Text field for client's feed
        self.clients_feed_list = scrolledtext.ScrolledText(self, width=80, height=24)
        self.clients_feed_list.grid(column=0, row=3, columnspan=4, padx=5, pady=7)

        # Start main processing button
        self.buttons['MAIN_START'] = tk.Button(self,
                                               font=TKfont.Font(family='Arial', size=13),
                                               command=self.MAIN_START_clicked,
                                               padx=10,
                                               pady=3,
                                               height=5)
        self.buttons['MAIN_START'].grid(column=3, row=4, padx=10, pady=5, sticky=tk.E)

        # Button & label for client's feed strings counter
        self.buttons['count_feed'] = tk.Button(self,
                                               text="Посчитать строки",
                                               command=self.count_feed_clicked,
                                               padx=10,
                                               pady=3,
                                               height=2)
        self.buttons['count_feed'].grid(column=0, row=4, padx=10, pady=10, sticky=tk.N)

        self.labels['feed_counter'] = {}
        self.labels['feed_counter']['obj'] = tk.Label(self,
                                                      padx=12,
                                                      pady=12,
                                                      width=25,
                                                      relief=tk.GROOVE)
        self.labels['feed_counter']['obj'].grid(column=1, row=4, columnspan=2, padx=10, pady=10, sticky=tk.NW)

        # Init settings
        init_checkbox = self.init_settings()

        # 'Copy to clipboard' checkbox
        self.checkboxes = {}
        self.checkboxes['clipboard'] = {'var' : tk.BooleanVar(value=init_checkbox)}
        self.checkboxes['clipboard']['obj'] = tk.Checkbutton(self,
                                                             text='Скопировать результат в буфер обмена',
                                                             variable=self.checkboxes['clipboard']['var'],
                                                             onvalue=True,
                                                             offvalue=False)
        self.checkboxes['clipboard']['obj'].grid(column=1, row=5, columnspan=3, padx=10, sticky=tk.E)

        self.count_feed_clicked()
    def save_settings(self):
        clipboard_setting = str(int(self.checkboxes['clipboard']['var'].get()))
        data = [clipboard_setting + '\n']
        for i in range(2):
            data.append(self.files[i]+'\n')
        FUNC.write_to_the_file(data, 'settings')
    def init_settings(self):
        self.files         = ['', '']                                       # only the path to each file
        self.IDlists       = [{'obj' : '', 'count' : 0, 'ready' : False},
                              {'obj' : '', 'count' : 0, 'ready' : False}]   # ID lists as a reference to check
        self.FEED_original  = {'obj' : '', 'count' : 0, 'ready' : False}    # client's feed names list

        if OSpath.isfile('settings'):
            data = FUNC.read_file('settings')
            for i in range(2):
                file_path = data[i+1][:-1]      # without '\n'
                if OSpath.isfile(file_path):
                    self.files[i] = file_path
                    self.file_choose_clicked(i)
            return bool(int(data[0][:-1]))
        return True
    def btn0_clicked(self):
        self.files[0] = filedialog.askopenfilename(initialdir= OSpath.dirname(__file__))
        self.file_choose_clicked(0)
    def btn1_clicked(self):
        self.files[1] = filedialog.askopenfilename(initialdir= OSpath.dirname(__file__))
        self.file_choose_clicked(1)
    def file_choose_clicked(self, num):
        if self.files[num]:
            text = OSpath.basename(self.files[num])[:40]
            if self.files[num][-4:] in (".csv", ".txt"):
                color = Globals.COLORS['green']
                self.IDlists[num]['obj']   = FUNC.prepare_ID_list(self.files[num])
                self.IDlists[num]['count'] = len(self.IDlists[num]['obj'])
                self.IDlists[num]['ready'] = True           # it means "ready to start main processing"
                text = ''.join(['[',
                                str(self.IDlists[num]['count']),
                                ' ',
                                FUNC.plural_word_endings(self.IDlists[num]['count']),
                                '] ',
                                text])
            else:
                color = Globals.COLORS['red']
                self.IDlists[num]['ready'] = False
            self.labels['lbl'+str(num)]['obj'].config(foreground=color, text=text)
        self.check_main_start_state()
    def count_feed_clicked(self):
        TEMP = self.clients_feed_list.get("1.0", tk.END)
        TEMP = list(TEMP.split("\n"))
        self.FEED_original['obj']   = FUNC.prepare_FEED_original(TEMP)

        counter = 0
        for i in range(len(self.FEED_original['obj'])):
            if self.FEED_original['obj'][i]:
                counter += 1
        self.FEED_original['count'] = counter

        self.FEED_original['ready'] = bool(counter)

        text = str(self.FEED_original['count']) + ' ' + FUNC.plural_word_endings(self.FEED_original['count'])
        color = ('red', 'green')[self.FEED_original['ready']]
        self.labels['feed_counter']['obj'].config(text       = text,
                                                  foreground = Globals.COLORS[color])
        self.check_main_start_state()
    def check_main_start_state(self):
        if self.ready_for_MAIN_START_condition():
            self.buttons['MAIN_START']["state"] = "normal"
            self.buttons['MAIN_START']["text"] = "ЗАПУСТИТЬ\n»»»"
        else:
            self.buttons['MAIN_START']["state"] = "disabled"
            self.buttons['MAIN_START']["text"] = "ЗАПУСТИТЬ\nxxx"
    def ready_for_MAIN_START_condition(self):
        return self.FEED_original['ready'] and (self.IDlists[0]['ready'] or self.IDlists[1]['ready'])
    def MAIN_START_clicked(self):
        self.count_feed_clicked()
        if self.ready_for_MAIN_START_condition():
            self.save_settings()
            FINAL_ID_list = []
            FINAL_IDs_counter = [-1, -1]        # the list for both files; '-1' means this file wasn't processed

            for i in range(2):                  # launch the main cycle separately for both ID lists
                if self.IDlists[i]['ready']:
                    LOCAL_ID_list = []
                    IDs_counter = 0
                    FEEDorig = self.FEED_original['obj']

                    for index in range(len(FEEDorig)):
                        num, ID = FUNC.MAIN_CYCLE(FEEDorig[index], self.IDlists[i]['obj'])
                        IDs_counter += num
                        LOCAL_ID_list.append(ID)

                        percent = 100*(index+1)/len(FEEDorig)
                        percent = "{0:.1f} %".format(percent)
                        print(percent, end="\r")
                    print()

                    FINAL_IDs_counter[i] = IDs_counter
                    if FINAL_ID_list:
                        for index in range(len(FINAL_ID_list)):
                            if not FINAL_ID_list[index]:
                                FINAL_ID_list[index] = LOCAL_ID_list[index]
                    else:
                        FINAL_ID_list = LOCAL_ID_list

            FUNC.write_to_the_file(FINAL_ID_list, Globals.FILES['result'])
