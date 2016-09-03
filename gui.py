#! /usr/bin/env python
# -*- coding: utf-8 -*- 
"""
@time = 9/2/2016 1:35 PM
@author = Rongcheng
"""
from Tkinter import *
import tkFileDialog, tkMessageBox
import numpy as np
from handler import *


class GUI:

    def __init__(self):
        self.display_pos = 0
        self.global_pos = 0
        self.deleted = 0
        self.image_tuples = []
        self.positive_image_names = set()
        self.negative_image_names = set()
        self._next_image = None
        self.handler = Handler(resize=(200, 190))
        self.root = Tk()
        self.root.title("Image Label Tool")
        self.init_ui()
        self._center(self.root)
        self.root.minsize(750, 550)
        self.root.mainloop()



    def _center(self, toplevel):
        toplevel.update_idletasks()
        w = toplevel.winfo_screenwidth()
        h = toplevel.winfo_screenheight()
        size = tuple(int(_) for _ in toplevel.geometry().split('+')[0].split('x'))
        x = w/2 - size[0]/2
        y = h/2 - size[1]/2
        toplevel.geometry("%dx%d+%d+%d" % (size + (x, y)))

    def init_ui(self):
        # frame init
        self.main_frame = Frame(self.root)
        self.main_frame.pack(fill=X)
        self.config_frame = Frame(self.main_frame, width=400, height=100)
        self.config_frame.pack(side=TOP, fill=X)

        # config init
        self.label_folder = Label(self.config_frame, text="Folder: ")
        self.entry_folder = Entry(self.config_frame, width=50, bd=2)
        self.btn_confirm = Button(self.config_frame, text="confirm", bd=2, width=15, relief=RAISED)
        self.btn_browser = Button(self.config_frame, text="browse...", bd=2, width=15)
        self.btn_delete = Button(self.config_frame, text="delete negative", bd=2, width=15)
        self.btn_delete_unreadable = Button(self.config_frame, text="delete unreadable", bd=2, width=15)
        self.label_status = Label(self.config_frame, text="", bd=2, width=50)

        self.label_folder.grid(row=0, column=0, sticky=E)
        self.entry_folder.grid(row=0, column=1, columnspan=3)
        self.btn_confirm.grid(row=0, column=4)
        self.btn_browser.grid(row=0, column=5)
        self.label_status.grid(row=1, column=0, columnspan=4, sticky=W)
        self.btn_delete.grid(row=1, column=4)
        self.btn_delete_unreadable.grid(row=1, column=5)

        self.btn_confirm.bind('<Button-1>', self.button_event)
        self.btn_browser.bind('<Button-1>', self.button_event)
        self.btn_delete.bind('<Button-1>', self.button_event)
        self.btn_delete_unreadable.bind('<Button-1>', self.button_event)
        self.root.bind('<Up>', self.keyboard_event)
        self.root.bind('<Down>', self.keyboard_event)
        self.root.bind('<Left>', self.keyboard_event)
        self.root.bind('<Right>', self.keyboard_event)

        self.canvas = Canvas(self.main_frame, width=750, height=500)
        self.canvas.pack(side=TOP, fill=BOTH)
        border_init_pos = np.array([8, 8, 234, 214])
        text_init_pos = np.array([125, 235])
        image_init_pos = np.array([20, 15])

        self.border_list = []
        self.title_list = []
        self.display_list = []
        for m in range(2):
            for n in range(3):
                border_pos = border_init_pos + np.array([250*n, 250*m, 250*n, 250*m])
                self.border_list.append(self.canvas.create_rectangle(*border_pos, fill="grey"))
                text_pos = text_init_pos + np.array([250*n, 250*m])
                self.title_list.append(self.canvas.create_text(*text_pos, text="title", anchor="center"))
                image_pos = image_init_pos + np.array([250*n, 250*m])
                self.display_list.append(self.canvas.create_image(*image_pos, image=PhotoImage(), anchor="nw"))

    def _default_display(self, ind):
        self.canvas.itemconfig(self.title_list[ind], text="title")
        self.canvas.itemconfig(self.border_list[ind], fill="grey")
        self.canvas.itemconfig(self.display_list[ind], image=PhotoImage())

    def update_status(self):
        status = "total:{}, positive:{}, negative:{}, unreadable:{}, deleted:{}".format(len(self.handler.file_list), len(self.positive_image_names), len(self.negative_image_names), len(self.handler.unreadable), self.deleted)
        self.label_status.config(text=status)

    def replace_images(self, image_tuples):
        for m in range(2):
            for n in range(3):
                ind = m*3 + n
                if ind >= len(image_tuples):
                    self._default_display(ind)
                    continue
                title, image = image_tuples[ind]
                self.canvas.itemconfig(self.title_list[ind], text=title)
                self.canvas.itemconfig(self.display_list[ind], image=image)
                self.walk_through(title, ind)
        self.canvas.itemconfig(self.border_list[0], fill="blue")


    def button_event(self, event):
        if event.widget == self.btn_confirm:
            path = self.entry_folder.get()
            self.image_tuples = []
            self.deleted = 0
            self.handler.explore_folder(path)
            self._next_image = self.handler.image_gtr().next
            self.image_tuples.extend(self._next_n_image_tuples(6))
            self.replace_images(self.image_tuples[-6:])
            self.btn_confirm.tkraise()
        elif event.widget == self.btn_browser:
            folder = tkFileDialog.askdirectory(parent=self.root) # initialdir="D:/kaggle/leaf/data/images")
            self.entry_folder.delete(0, END)
            self.entry_folder.insert(0, folder)
        elif event.widget == self.btn_delete:
            count = self.handler.delete()
            self.deleted += count
            self.negative_image_names=set()
        elif event.widget == self.btn_delete_unreadable:
            count = self.handler.delete_unreadable()
            self.deleted += count
        self.update_status()

    def _next_n_image_tuples(self, n):
        image_tuples = []
        try:
            for i in range(n):
                image_tuples.append(self._next_image())
        except StopIteration:
            pass
        return image_tuples


    def move_next(self):
        if self.display_pos == 5:
            if self.global_pos == len(self.image_tuples) - 1:
                i_tuples = self._next_n_image_tuples(6)
                self.replace_images(i_tuples)
                self.image_tuples.extend(i_tuples)
                self.display_pos = 0
                self.global_pos += 1
            else:
                i_tuples = self.image_tuples[self.global_pos + 1:self.global_pos + 7]
                extra_n = 6 - len(i_tuples)
                if extra_n > 0:
                    extra_tuple = self._next_n_image_tuples(extra_n)
                    i_tuples.extend(extra_tuple)
                    self.image_tuples.extend(extra_tuple)
                self.replace_images(i_tuples)
                self.global_pos += 1
                self.display_pos = 0
        else:
            if self.global_pos >= len(self.image_tuples): # reach the end
                tkMessageBox.showinfo("Finished!")
                self.display_pos += 1
            else:
                self.display_pos += 1
                self.global_pos += 1
        if self.display_pos < 6:
            self._move_to(self.display_pos)

    def _move_to(self, ind):
        self.canvas.itemconfig(self.border_list[ind], fill="blue")

    def move_back(self):
        if self.display_pos == 0:
            if self.global_pos == 0:
                tkMessageBox.showinfo("info", "Reach begining!")
                self._move_to(0)
                return
            self.global_pos -= 6
            self.replace_images(self.image_tuples[self.global_pos:self.global_pos+6])
            self._move_to(0)
        else:
            self.walk_through(self.image_tuples[self.global_pos][0], self.display_pos)
            self.display_pos -= 1
            self.global_pos -= 1
            self._move_to(self.display_pos)

    def change_display_status(self, status, ind=None):
        if ind is None:
            ind = self.display_pos
        if status == "positive":
            self.canvas.itemconfig(self.border_list[ind], fill="green")
        elif status == "negative":
            self.canvas.itemconfig(self.border_list[ind], fill = "red")
        else:
            self.canvas.itemconfig(self.border_list[ind], fill="grey")

    def walk_through(self, file_name, ind=None):
        if ind is None:
            ind = self.display_pos
        status = ""
        if file_name in self.positive_image_names:
            status = "positive"
        elif file_name in self.negative_image_names:
            status = "negative"
        self.change_display_status(status, ind)

    def keyboard_event(self, event):
        # print "hit a direction"
        try:
            current = self.image_tuples[self.global_pos]
        except IndexError:
            tkMessageBox.showwarning('warning', "No Images!")
            return
        title = current[0]
        if event.keysym == "Up":
            self.change_display_status("positive")
            self.handler.update(title, True)
            self.positive_image_names.add(title)
            if title in self.negative_image_names:
                self.negative_image_names.remove(title)
            self.move_next()
        elif event.keysym == "Down":
            self.change_display_status("negative")
            self.handler.update(title, False)
            self.negative_image_names.add(title)
            if title in self.positive_image_names:
                self.positive_image_names.remove(title)
            self.move_next()
        elif event.keysym == "Right":
            self.walk_through(title)
            self.move_next()
        elif event.keysym == "Left":
            self.walk_through(title)
            self.move_back()
        self.update_status()

if __name__ == "__main__":
    tool = GUI()