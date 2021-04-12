import tkinter as tk
from tkinter import ttk
import tkinter.font as tkFont
import json
from control import register_log_file, current_download_file


class Dani(tk.Frame):
    """Main application frame."""

    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.notebook = My_Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=tk.YES,
                           padx=10, pady=10, side=tk.LEFT)


class My_Notebook(ttk.Notebook):
    """Notebook class to manage the register and other tabs."""

    def __init__(self, parent, *args, **kwargs):
        ttk.Notebook.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        with open(register_log_file, 'r') as reg_file:
            register_data = json.load(reg_file)
        self.register_frame = RegisterFrame(self, register_data)
        self.register_frame._populate()
        self.downloads = ActiveDownloadFrame(self)
        self.downloads._populate()
        self.add(self.register_frame, text='Register', padding=20)
        self.add(self.downloads, text='Downloads', padding=20)


class Table(tk.Frame):
    """Table class for showing info with scrollbars."""

    def __init__(self, parent=None, title="", headers=[], height=10, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self._title = tk.Label(
            self, text=title, background="grey", font=("Helvetica", 16))
        self._headers = headers
        self._tree = ttk.Treeview(
            self,
            height=height,
            columns=self._headers,
            show="headings"
        )
        self._title.pack(side=tk.TOP, fill=tk.X)

        # Agregamos dos scrollbars
        vsb = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self._tree.yview)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb = ttk.Scrollbar(self, orient=tk.HORIZONTAL,
                            command=self._tree.xview)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)

        self._tree.configure(xscrollcommand=hsb.set, yscrollcommand=vsb.set)
        self._tree.pack(side=tk.LEFT, expand=tk.YES)

        for header in self._headers:
            self._tree.heading(header, text=header.title())
            self._tree.column(header, stretch=True,
                              width=tkFont.Font().measure(header.title()))

    def add_row(self, row):
        self._tree.insert('', 'end', values=row)
        for i, item in enumerate(row):
            col_width = tkFont.Font().measure(item)
            if self._tree.column(self._headers[i], width=None) < col_width:
                self._tree.column(self._headers[i], width=col_width)


class LTFrame(tk.Frame):
    """Frame with a label and table inside."""

    def __init__(self, parent=None, data=None, headers=None, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self._data = data
        self._headers = headers
        self._label = tk.Label(self, text=data['name'], bg='white')
        self._label.bind(
            '<Button-1>',
            lambda _: self.toggle_table()
        )
        self._shown_table = False
        self._label.pack(fill=tk.X)
        self._table = None
        self._make_table()

    def _make_table(self):
        '''Creates the table'''
        table = Table(
            self,
            title='Register data',
            headers=self._headers
        )
        for chapter in self._data['chapters']:
            row = (
                self._data['name'],
                chapter,
                self._data['chapters'][chapter]
            )
            table.add_row(row)
        self._table = table

    def toggle_table(self):
        if not self._shown_table:
            self._table.pack()
            self._shown_table = True
        else:
            self._table.pack_forget()
            self._shown_table = False


class ScrollableFrame(tk.Frame):
    """Frame with a canvas inside it so user can scroll
    through it. and can be fulfilled with anything the
    developer needs to put inside.
    Scrolling in the canvas doesn't seems to work for
    some reason, so I had to do it in the scrollable_frame
    and the parent binding directly the events with the
    bind_scroll_events function."""

    def __init__(self, parent, data={}, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.data = data
        self.canvas = tk.Canvas(self)
        self.scrollable_frame = tk.Frame(self.canvas)
        self.scrollbar = tk.Scrollbar(
            self.canvas, orient=tk.VERTICAL
        )
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.configure(command=self.canvas.yview)
        int_id = self.canvas.create_window(
            (0, 0), window=self.scrollable_frame, anchor=tk.NW)

        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda _: self.canvas.configure(
                scrollregion=self.canvas.bbox('all')
            )
        )

        def _configure_canvas(event):
            if self.scrollable_frame.winfo_reqwidth() != self.canvas.winfo_width():
                # update the inner frame's width to fill the canvas
                self.canvas.itemconfigure(
                    int_id, width=self.canvas.winfo_width())
        self.canvas.bind('<Configure>', _configure_canvas)
        self.bind_scroll_events()

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(event, tk.UNITS)

    def bind_scroll_events(self):
        """Bind scroll events to the inner frame and parent."""
        self.scrollable_frame.bind(
            "<Button-4>",
            lambda e: self._on_mousewheel(-1)
        )
        self.scrollable_frame.bind(
            "<Button-5>",
            lambda e: self._on_mousewheel(1)
        )
        self.parent.bind(
            "<Button-4>",
            lambda e: self._on_mousewheel(-1)
        )
        self.parent.bind(
            "<Button-5>",
            lambda e: self._on_mousewheel(1)
        )

    def _populate(self):
        """Fill the inner frame."""
        pass


class RegisterFrame(ScrollableFrame):
    """Subclass to overwrite the _populate method so
    the table have right data being inserted"""

    def _populate(self):
        """Fill the inner frame with the information of
         the data in the register file."""
        for anime in self.data['animes']:
            new_frame = LTFrame(
                self.scrollable_frame,
                data=self.data['animes'][anime],
                headers=('Name', 'Chapter', 'Link')
            )
            new_frame.pack()


class ActiveDownloadFrame(ScrollableFrame):
    """Frame for placing downloads."""

    def _populate(self):
        """Fill the inner frame with the information
        about the current download. """
        progressbar = ttk.Progressbar(self.scrollable_frame)
        progressbar.pack(side=tk.LEFT, fill=tk.X, expand=tk.YES)
        progressbar.step(40)
