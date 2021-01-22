#!/usr/bin/env python3

from tkinter import *
from tkinter import filedialog
import math
import re


class TocEditor:

    def __init__(self):
        self.root = Tk()
        self.root.title('TocEditor v. 0.2')

        self.scroll_y = Scrollbar(self.root)
        self.scroll_y.pack(side=RIGHT, fill=Y)
        self.text = Text(self.root)
        self.text.pack(side=LEFT, expand=True, fill=BOTH)
        self.text.configure(font=("Times", 16, "normal"))
        self.scroll_y.config(command=self.text.yview)
        self.text.config(yscrollcommand=self.scroll_y.set)

        # Taustaväri ja fontti muutettu, mutta voi myös käyttää oletusta
        # , jolloin näitä ei tarvita.
        self.text.configure(background="white", foreground="black")

        self.menubar = Menu(self.root)

        # Open/Close/Save file
        self.filemenu = Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label="Open (Ctrl+o)", command=lambda: self.open())
        self.filemenu.add_command(label="Save (Ctrl+s)", command=lambda: self.save())
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Exit", command=lambda: self.exit_quit())

        self.editmenu = Menu(self.menubar, tearoff=0)
        self.editmenu.add_command(label="new level1 heading (Ctrl+1)", command=lambda: self.new_heading(1))
        self.editmenu.add_command(label="new level2 heading (Ctrl+2)", command=lambda: self.new_heading(2))
        self.editmenu.add_command(label="new level3 heading (Ctrl+3)", command=lambda: self.new_heading(3))
        self.editmenu.add_command(label="new level4 heading (Ctrl+4)", command=lambda: self.new_heading(4))
        self.editmenu.add_command(label="new level5 heading (Ctrl+5)", command=lambda: self.new_heading(5))
        self.editmenu.add_command(label="new level6 heading (Ctrl+6)", command=lambda: self.new_heading(6))
        self.editmenu.add_separator()
        self.editmenu.add_command(label="TreeView (Alt+t)", command=lambda: self.tree_view(''))
        self.editmenu.add_command(label="Headinglevel up (Alt+u)", command=lambda: self.heading_up_or_down('u'))
        self.editmenu.add_command(label="Headinglevel down (Alt+d)", command=lambda: self.heading_up_or_down('d'))
        self.editmenu.add_separator()
        self.editmenu.add_command(label="Cut (Ctrl+x)")
        self.editmenu.add_command(label="Copy (Ctrl+c)")
        self.editmenu.add_command(label="Paste (Ctrl+v)")

        self.menubar.add_cascade(label="File", menu=self.filemenu)

        self.menubar.add_cascade(label="Edit", menu=self.editmenu)

        self.root.config(menu=self.menubar)

        self.text.focus()

        self.root.bind('<Control-Key-1>', self.new_heading)
        self.root.bind('<Control-Key-2>', self.new_heading)
        self.root.bind('<Control-Key-3>', self.new_heading)
        self.root.bind('<Control-Key-4>', self.new_heading)
        self.root.bind('<Control-Key-5>', self.new_heading)
        self.root.bind('<Control-Key-6>', self.new_heading)

        self.root.bind('<Control-s>', self.save)
        self.root.bind('<Control-o>', self.open)

        self.root.bind('<Alt-Key-t>', self.tree_view)
        self.root.bind('<Alt-Key-u>', self.heading_up_or_down)
        self.root.bind('<Alt-Key-d>', self.heading_up_or_down)

        self.root.mainloop()

    def new_heading(self, level):
        try:
            heading_level = int(level.keysym)
        except Exception as e:
            heading_level = int(level)
        cursor_at = self.text.index(INSERT)
        line_start = float(self.text.index(cursor_at + 'linestart'))
        line_end = float(self.text.index(cursor_at + 'lineend'))
        if line_start != line_end:
            self.text.insert(cursor_at + ' lineend', '\n')
            next_line = float(self.text.index(cursor_at)) + 1
            cursor_at = str(next_line)
        self.text.insert(cursor_at + ' linestart', '<h' + str(heading_level) + '>Heading')
        self.text.insert(cursor_at + ' lineend', '</h' + str(heading_level) + '>')
        self.tree_view('t')

        line_at = float(self.text.index(cursor_at + 'lineend'))
        self.text.mark_set('insert', '%d.%d' % (int(line_at), 4 * heading_level))
        self.text.tag_remove(SEL, '0.0', END)
        self.text.tag_add(SEL, str(int(line_at))
                          + '.' + str(4 * heading_level), str(int(line_at))
                          + '.' + str(11 + 4 * (heading_level - 1)))

    def tree_view(self, event):
        last_row = math.floor(float(self.text.index(END)))
        index = 1
        while index < last_row:
            line = self.text.get(str(index) + '.0', str(index) + '.0 lineend')
            # print(line)
            for i in range(1, 7):
                if re.match(r'.*<h' + str(i) + '>', line):
                    sisennys = '    ' * (i - 1)
                    line = re.sub('.*<h' + str(i) + '>', sisennys + '<h' + str(i) + '>', line)
                    # print(line)
                    self.text.delete(str(index) + '.0', str(index) + '.0 lineend')
                    self.text.insert(str(index) + '.0', line)
            index += 1

    def heading_up_or_down(self, event):
        try:
            direction = event.keysym
        except Exception as e:
            direction = event
        try:
            # Debug: Ei toimi, koska Alt+ylös/alas poistaa samalla valinnan!
            # Käytetään Alt+u/d, jotka ei ole kovinkaan hyvät :(
            sel_start = self.text.index(SEL_FIRST)
            sel_end = self.text.index(SEL_LAST)
            first_line = math.floor(float(self.text.index(sel_start + 'linestart')))
            last_line = math.floor(float(self.text.index(sel_end + 'linestart')))
            while first_line <= last_line:
                line = self.text.get(str(first_line) + '.0', str(first_line) + '.0 lineend')
                new_line = self.change_heading_level(line, direction)
                self.text.delete(str(first_line) + '.0', str(first_line) + '.0 lineend')
                self.text.insert(str(first_line) + '.0', new_line)
                first_line += 1
        except Exception as e:
            cursor_at = self.text.index(INSERT)
            line_num = math.floor(float(self.text.index(cursor_at + 'linestart')))
            line = self.text.get(str(line_num) + '.0', str(line_num) + '.0 lineend')
            new_line = self.change_heading_level(line, direction)
            self.text.delete(str(line_num) + '.0', str(line_num) + '.0 lineend')
            self.text.insert(str(line_num) + '.0', new_line)
        self.tree_view('t')
        self.text.tag_remove(SEL, '0.0', END)

    @staticmethod
    def change_heading_level(line, direction):
        start = 1
        stop = 6
        step = 1
        change = 1
        if direction == 'd':  # 'Down'
            start = 6
            stop = 1
            step = -1
            change = -1
        try:
            for i in range(start, stop, step):
                if re.match(r'.*</*h' + str(i) + '>', line):
                    line = re.sub('(</*h)' + str(i) + '(>)', '\g<1>' + str(i + change) + '\g<2>', line)
                    # print(line)
                    break
            return line
        except Exception as e:
            return line

    def exit_quit(self):
        self.root.quit()

    def save(self, event):
        filename = filedialog.asksaveasfilename(filetypes=[("Text files", "*.txt")])
        #print(filename)
        with open(filename, 'w') as file:
            file.write(self.text.get("1.0",END))

    def open(self, event):
        file_to_read = filedialog.askopenfile(mode="r", filetypes=[("Text files", "*.txt")])
        #print(file_to_read)
        #self.text.insert(END,file_to_read)
        self.text.delete("1.0",END)
        with open(file_to_read.name, 'r') as content:
            for line in content.readlines():
                self.text.insert(END, line)



if __name__ == "__main__":
    e = TocEditor()
