'''Dani GUI'''

import tkinter as tk
from tk_classes import Dani

if __name__ == '__main__':
    root = tk.Tk()
    Dani(root).pack(fill=tk.BOTH, expand=tk.YES)
    root.title('Dani')
    root.geometry('1000x400+200+200')
    root.minsize(1000, 400)
    root.mainloop()
