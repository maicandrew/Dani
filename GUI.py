'''Dani GUI'''

import tkinter as tk
from tk_classes import Table
import json
from control import register_log_file, current_download_file

# Root widget
root = tk.Tk()
root.title('Dani')

frames = []
with open(register_log_file, 'r') as reg_file:
    data = json.load(reg_file)


def show_table(anime, frame):
    table = frame.children.get('!table', None)
    if frame.getvar('table_status') == 'hidden':
        if not table:
            table = Table(
                frame,
                title='Register data',
                headers=('Name', 'Number', 'Link')
            )
            for chapter in data['animes'][anime]['chapters']:
                row = (
                    data['animes'][anime]['name'],
                    chapter,
                    data['animes'][anime]['chapters'][chapter]
                )
                table.add_row(row)
        table.pack()
        frame.setvar('table_status', 'shown')
    else:
        table.pack_forget()
        frame.setvar('table_status', 'hidden')
        print(frame.children)


for anime in data['animes']:
    new_frame = tk.Frame(root)
    new_frame.pack(fill=tk.X)
    new_frame.setvar('table_status', 'hidden')
    name_label = tk.Label(new_frame, text=anime)
    name_label.pack(fill=tk.X)
    name_label.bind(
        '<Button-1>',
        lambda event, anime=anime, frame=new_frame: show_table(anime, frame)
    )
    frames.append(new_frame)

root.mainloop()
