class FilenamePopup:
    def __init__(self, master):
        top = self.top = Toplevel(master)
        self.lbl = Label(top, text="Choose a file name:")
        self.lbl.pack()
        self.ent_filename = Entry(top)
        self.ent_filename.pack()
        self.btn_ok = Button(top, text='Ok', command=self.cleanup)
        self.btn_ok.pack()

    def cleanup(self):
        self.filename = self.ent_filename.get()
        self.top.destroy()

class Paint(object):
    DEFAULT_COLOR = 'black'

    def __init__(self):
        self.root = Tk()
        self.root.geometry("400x400")
        self.root.title("GUI Image Viewer")
        self.root.resizable(False, False)

        self.brush_button = Button(self.root, text='Brush',
                                   command=self.use_brush)
        self.brush_button.grid(row=0, column=0, sticky="ew")

        self.eraser_button = Button(self.root, text='Eraser',
                                    command=self.use_eraser)
        self.eraser_button.grid(row=0, column=1, sticky="ew")

        self.size_scale = Scale(self.root, from_=1, to=5,
                                orient='horizontal')
        self.size_scale.grid(row=2, column=1, sticky="ew")

        self.save_button = Button(self.root, text="Save",
                                  command=self.save_file)
        self.save_button.grid(row=2, column=0, sticky="ew")
          
        self.c = Canvas(self.root, width=250, height=250)
        self.image1 = ImageTk.PhotoImage(Image.open("stupid.tif"))
        self.c.create_image(125, 125, image = self.image1)
        self.c.grid(row=1)

        self.setup()
        self.root.mainloop()
    def setup(self):
        self.old_x, self.old_y = None, None
        self.color = self.DEFAULT_COLOR
        self.eraser_on = False
        self.active_button = None
        self.size_multiplier = 10

        self.activate_button(self.brush_button)
        self.c.bind('<B1-Motion>', self.paint)
        self.c.bind('<ButtonRelease-1>', self.reset)

        self.c.bind('<Button-1>', self.point)
        self.line_start = (None, None)

    def use_brush(self):
        self.activate_button(self.brush_button)

    def use_eraser(self):
        self.activate_button(self.eraser_button, eraser_mode=True)

    def activate_button(self, some_button, eraser_mode=False):
        if self.active_button:
            self.active_button.config(relief='raised')
        some_button.config(relief='sunken')
        self.active_button = some_button
        self.eraser_on = eraser_mode

    def paint(self, event):
        line_width = self.size_scale.get() * self.size_multiplier
        paint_color = 'white' if self.eraser_on else self.color
        if self.old_x and self.old_y:
            self.c.create_line(self.old_x, self.old_y, event.x, event.y,
                               width=line_width, fill=paint_color,
                               capstyle='round', smooth=True, splinesteps=36)
        self.old_x = event.x
        self.old_y = event.y
    
    def point(self, event):
        btn = self.active_button["text"]
        if btn in ("Line", "Polygon"):
            self.size_multiplier = 1
            if any(self.line_start):
                self.line(event.x, event.y)
                self.line_start = ((None, None) if btn == 'Line'
                                   else (event.x, event.y))
            else:
                self.line_start = (event.x, event.y)

    def reset(self, event):
        self.old_x, self.old_y = None, None
    
    def color_default(self):
        self.color = self.DEFAULT_COLOR

    def save_file(self):
        self.popup = FilenamePopup(self.root)
        self.save_button["state"] = "disabled"
        self.root.wait_window(self.popup.top)

        filepng = self.popup.filename + '.png'

        if not os.path.exists(filepng) or \
                messagebox.askyesno("File already exists", "Overwrite?"):
            fileps = self.popup.filename + '.eps'

            self.c.postscript(file=fileps)
            img = Image.open(fileps)
            img = Image.open(fileps)
            img.save(filepng, 'png')
            os.remove(fileps)

            self.save_button["state"] = "normal"

            messagebox.showinfo("File Save", "File saved!")
        else:
            messagebox.showwarning("File Save", "File not saved!")

        self.save_button["state"] = "normal"

if __name__ == '__main__':
    Paint()
