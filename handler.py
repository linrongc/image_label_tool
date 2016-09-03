#! /usr/bin/env python
# -*- coding: utf-8 -*- 
"""
@time = 9/2/2016 1:35 PM
@author = Rongcheng
"""
from Tkinter import *
from PIL import Image, ImageTk
import os


class Handler:

    def __init__(self, resize=None):
        self.sel_map = {}
        self.unreadable = []
        self.resize = resize
        self.file_list = []
        self.folder = None
        self.counter = 0

    def explore_folder(self, folder):
        self.folder = folder
        self.sel_map = {}
        self.unreadable = []
        self.file_list = os.listdir(folder)

    def image_gtr(self):
        for file_name in self.file_list:
            path = os.path.join(self.folder, file_name)
            try:
                img = Image.open(path)
            except IOError:
                self.unreadable.append(file_name)
                print file_name
                continue
            if self.resize is not None:
                img = img.resize(self.resize)

            yield file_name, ImageTk.PhotoImage(image=img)
            self.counter += 1

    def update(self, file_name, select):
        self.sel_map[file_name] = select

    def delete(self):
        count = 0
        for file_name, decision in self.sel_map.iteritems():
            if not decision:
                path = os.path.join(self.folder, file_name)
                if os.path.exists(path):
                    os.remove(path)
                    count += 1
        return count

    def delete_unreadable(self):
        count = 0
        for file_name in self.unreadable:
            path = os.path.join(self.folder, file_name)
            if os.path.exists(path):
                os.remove(path)
                count += 1
        self.unreadable = []
        return count

    def dump_label_map(self, path):
        with open(path, "w") as f:
            name_labels = [(key, value) for key, value in self.sel_map.iteritems()]
            name_labels.sort()
            for file_name, select in name_labels:
                label = '1' if select else '0'
                f.write(file_name + "," + label + "\n")


if __name__ == "__main__":
    handler = Handler(resize=(200, 180))
    handler.explore_folder(r"D:/kaggle/leaf/data/images/")
    root = Tk()
    _, image = handler.image_gtr().next()
    canvas = Canvas(root)
    canvas.create_image((0,0), image=image, anchor="nw")
    canvas.pack()
    root.mainloop()
