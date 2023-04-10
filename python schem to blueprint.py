import tkinter, tkinter.colorchooser, numpy, amulet_nbt, traceback, re, threading#, color_tools#, tkinter.HoverInfo
from tkinter import filedialog
from tkinter.ttk import *
from PIL import Image, ImageTk, ImageOps, ImageDraw

#// &0xFF is because the array uses unsigned bytes while java uses signed ones. it converts values like -127 back to values like 129
#short blockid = (short)(blocks[blocknumber] & 0xFF);#0xFF = 255 but 256 because minecraft

class Example():
	def __init__(self):
		self.root = tkinter.Tk()
		self.root.geometry("410x410")
		self.root.title("python schem2blueprint")
		#self.strvar = tkinter.StringVar()
		self.menubar = tkinter.Menu(self.root)#binds the menubar the the root
		self.BGColor = "silver"
		self.GridColor = "black"
		self.BGridColor = ""
		self.ac1 = '#BBCBCB'
		self.ac2 = '#97AFAF'

		file = tkinter.Menu(self.menubar, tearoff=0)
		file.add_command(label="Open file", command=self.fileopen)
		Export = tkinter.Menu(file, tearoff=0)
		Export.add_command(label='Current layer', command=lambda:self.ExportImage('current layer'))
		Export.add_command(label='one image per layer', command=lambda:self.ExportImage('one per layer'))
		Export.add_command(label='To an animated Gif', command=lambda:self.ExportImage('gif'))
		file.add_cascade(label="Export", menu=Export, state='disabled')
		self.menubar.add_cascade(label="File", menu=file)

		colors = tkinter.Menu(self.menubar, tearoff=0)
		colors.add_command(label="background color", command=self.bgcolorDef, background=self.BGColor)
		colors.add_command(label="grid color", command=self.GridColorDef, background=self.GridColor, foreground='white')
		colors.add_command(label="grid hover color", command=self.BGridColorDef)#, background=self.GridColor
		counlor = tkinter.Menu(colors, tearoff=0)
		counlor.add_command(label='alternating color 1', command=lambda:self.altColorsDef(1), background=self.ac1)
		counlor.add_command(label='alternating color 2', command=lambda:self.altColorsDef(2), background=self.ac2)
		colors.add_cascade(label="block count colors", menu=counlor)
		colors.add_command(label="Restore Defaults", command=self.Default)
		self.menubar.add_cascade(label="colors", menu=colors)

		self.tools = tkinter.Menu(self.menubar, tearoff=0)
		self.tools.add_command(label="count blocks", command=self.CountBlocks)
		self.menubar.add_cascade(label="tools", menu=self.tools, state='disabled')

		comapsstyles = tkinter.Menu(self.menubar, tearoff=0)
		comapsstyles.add_command(label="moves with grid", command=lambda: self.CompasStyles('grid'))
		comapsstyles.add_command(label="locked to window", command=lambda: self.CompasStyles('window'))
		self.menubar.add_cascade(label="compass styles", menu=comapsstyles, state='disabled')

		self.misc = tkinter.Menu(self.menubar, tearoff=0)
		self.misc.add_command(label="Grid is True", command=self.GridToggle)
		self.misc.add_command(label="layer numbers", command=lambda:self.scale1.config(tickinterval=1 if int(self.scale1.config()['tickinterval'][-1]) == 0 else 0))
		#self.misc.add_command(label="thing is False", command=self.thingToggle)
		self.menubar.add_cascade(label="misc", menu=self.misc, state='disabled')
		self.root.config(menu=self.menubar)

		self.root.bind('<KeyPress>', self.layerswitch)
		self.texpath = "textures"
		#self.thing = False
		self.style = 'window'
		self.gridis = True
		self.CheckIntVar = tkinter.IntVar()
		self.myGrid = []
		#self.myGrid2 = []
		self.activeimages = []
		self.imagegrid = []
		self.pixel_width = 16
		self.pixel_height = 16
		#self.makecanvas()
		#self.fileopen()
		self.root.mainloop()
	def GridToggle(self, reset=False):
		if self.gridis:
			self.gridis = False
			self.misc.entryconfig(0, label=f'Grid is {self.gridis}')
			for i in self.myGrid:self.canvas.itemconfig(i, state='hidden')
		else:
			self.gridis = True
			self.misc.entryconfig(0, label=f'Grid is {self.gridis}')
			for i in self.myGrid:self.canvas.itemconfig(i, state='normal')
		if reset:
			self.gridis = True
			self.misc.entryconfig(0, label=f'Grid is {self.gridis}')
			for i in self.myGrid:self.canvas.itemconfig(i, state='normal')

	#def thingToggle(self):
	#	if not self.thing:
	#		self.thing = True
	#		self.misc.entryconfig(1, label=f'thing is {self.thing}')
	#	else:
	#		self.thing = False
	#		self.misc.entryconfig(1, label=f'thing is {self.thing}')
	#	self.createGrid()

	def layerswitch(self, event):
		if event.keysym == 'Up':
			self.scale1.set(self.scale1.get() + 1)
		if event.keysym == 'Down':
			self.scale1.set(self.scale1.get() - 1)

	def CompasStyles(self, style):
		for i in ['North', 'South', 'East', 'West']:
			self.canvas.delete(i)

		for i in [self.labelNorth, self.labelSouth, self.labelEast, self.labelWest]:
			i.grid_forget()

		if style == 'window':
			self.style = 'window'
			self.labelNorth.grid(row=0, column=0, sticky='n')
			self.labelSouth.grid(row=0, column=0, sticky='s')
			self.labelEast.grid(row=0, column=0, sticky='e')
			self.labelWest.grid(row=0, column=0, sticky='w')
		if style == 'grid':
			self.style = 'grid'
			self.GridToggle(True)
			self.canvas.create_text(0, 0, text="North", anchor='n', tag='North')
			self.canvas.create_text(0, 0, text="South", anchor='s', tag='South')
			self.canvas.create_text(0, 0, text="East", anchor='e', tag='East')
			self.canvas.create_text(0, 0, text="West", anchor='w', tag='West')
			firstrec = self.canvas.bbox(self.myGrid[0])#(top-left, top-right, botttom-left, bottom-right)
			lastrec  = self.canvas.bbox(self.myGrid[-1])
			#print(self.myGrid)
			#print(len(self.myGrid))
			#print(self.myGrid[0])
			#print(self.myGrid[-1])
			#print()
			#print(firstrec)
			#print(lastrec)
			#print()
			#print(firstrec[0]+1)
			#print(lastrec[3]+1)
			#print()
			#print(lastrec[3]/2)
			#cw = self.root.winfo_width()
			#ch = self.root.winfo_height()
			#true_x = self.canvas.canvasx(cw)
			#true_y = self.canvas.canvasy(ch)
			#print(f"cw:{cw} ch:{ch} true_x:{true_x} true_y:{true_y}")
			#print(f"devx:{cw/true_x} devy:{ch/true_y}")
			#w, h = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
			#print(f"w:{relwidth} h:{relheight}")
			#self.canvas.move(North, 30, 80)  # move 2 pixels right and down
			self.canvas.moveto(self.canvas.gettags('North'), lastrec[0]/2-firstrec[3], -20) # to rectangle to position 20,20
			self.canvas.moveto(self.canvas.gettags('South'), lastrec[0]/2-firstrec[3], lastrec[3]-firstrec[3]+20)
			self.canvas.moveto(self.canvas.gettags('East'), -25, (lastrec[3]/2)-9)
			self.canvas.moveto(self.canvas.gettags('West'), lastrec[0]+20, (lastrec[3]/2)-9)
			#self.canvas.coords(self.canvas.gettags('North'), w/2, 0)  # redraw the rectangle at the given coordinates
			self.GridToggle()
	def ColorPicker(self, color):return tkinter.colorchooser.askcolor(title='Pick a color', color=color)[1]
	def Default(self):
		self.BGColor, self.GridColor, self.BGridColor, self.ac1, self.ac2 = "silver", "black", "", '#BBCBCB', '#97AFAF'
		self.colorseter()
	def altColorsDef(self, direction):
		if direction == 1:self.ac1 = self.ColorPicker(self.ac1)
		if direction == 2:self.ac2 = self.ColorPicker(self.ac2)
		self.colorseter()
	def bgcolorDef(self):
		self.BGColor = self.ColorPicker(self.BGColor)
		self.colorseter()
	def GridColorDef(self):
		self.GridColor = self.ColorPicker(self.GridColor)
		self.colorseter()
	def BGridColorDef(self):
		self.BGridColor = self.ColorPicker(self.BGridColor)
		self.colorseter()
	def TCC(self, name):
		r, g, b = self.root.winfo_rgb(name)
		o = round(((r/256 * 299) + (g/256 * 587) + (b/256 * 114)) / 1000)
		return 'black' if o > 125 else 'white'
	def colorseter(self):
		try:
			self.canvas.configure(bg=self.BGColor)
		except:
			pass

		try:
			for i in self.myGrid:
				self.canvas.itemconfig(i, outline=self.GridColor)
		except:
			pass

		try:
			for i in self.myGrid:
				#print(self.canvas.itemcget(i))
				self.canvas.itemconfig(i, activefill=self.BGridColor)#, activefill='blue'
		except:
			pass

		try:
			self.BCTree.tag_configure('OddRow', background=self.ac1)
			self.BCTree.tag_configure('EvenRow', background=self.ac2)
		except:
			pass

		try:
			menuchild = self.menubar.winfo_children()[1]
			menuchild.entryconfigure(0, background=self.BGColor, foreground=self.TCC(self.BGColor))#canvas background color
			menuchild.entryconfigure(1, background=self.GridColor, foreground=self.TCC(self.GridColor))#grid color
			menuchild.entryconfigure(2, background=self.BGridColor, foreground=self.TCC(self.BGridColor if self.BGridColor != '' else 'white'))#grid hover color
			menuchild.winfo_children()[0].entryconfigure(0, background=self.ac1, foreground=self.TCC(self.ac1))#alternating color 1
			menuchild.winfo_children()[0].entryconfigure(1, background=self.ac2, foreground=self.TCC(self.ac2))#alternating color 2
		except:
			pass #print(traceback.format_exc())
	#def GetMainColor(self, img):
	#	colors = img.getcolors(256) #put a higher value if there are many colors in your image
	#	max_occurence, most_present = 0, 0
	#	colordict = {}
	#	try:
	#		for c in colors:
	#			if c[0] > max_occurence:
	#				max_occurence, most_present = c
	#				colordict[max_occurence] = most_present
	#		clr = list(colordict.keys())
	#		try:
	#			if colordict[clr[-1]].count(0) != 4:
	#				return color_convert.rgb2hex(colordict[clr[-1]])
	#			else:
	#				return color_convert.rgb2hex(colordict[clr[-2]])
	#		except Exception as e:print(traceback.format_exc())
	#	except TypeError:
	#		raise Exception("Too many colors in the image")
	def makecanvas(self):
		self.canvas = tkinter.Canvas(self.root, width=400, height=400, background=self.BGColor)
		#tkinter.HoverInfo.Label(self.canvas, cursor='arrow', bg='#7ec0ee', textvar=self.strvar)
		self.xsb = tkinter.Scrollbar(self.root, orient="horizontal", command=self.canvas.xview)
		self.ysb = tkinter.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
		self.canvas.configure(yscrollcommand=self.ysb.set, xscrollcommand=self.xsb.set)
		self.canvas.configure(scrollregion=(0,0,1000,1000))

		self.xsb.grid(row=1, column=0, sticky="ew")
		self.ysb.grid(row=0, column=1, sticky="ns")
		self.canvas.grid(row=0, column=0, sticky="nsew")
		self.root.grid_rowconfigure(0, weight=1)
		self.root.grid_columnconfigure(0, weight=1)

			#self.root.wm_attributes('-transparentcolor','black')#I don't even fucking know but it makes the window unclickable, do not use
		self.menubar.winfo_children()[0].entryconfig(1, state='normal')
		self.menubar.entryconfig(2, state='normal')
		self.menubar.entryconfig(3, state='normal')
		self.menubar.entryconfig(4, state='normal')
		self.menubar.entryconfig(5, state='normal')
		self.labelNorth = Label(self.root, text="North")
		self.labelEast = Label(self.root, text="East")
		self.labelSouth = Label(self.root, text="South")
		self.labelWest = Label(self.root, text="West")

		#self.root.update()
		#self.canvas.bind('<Configure>', lambda e: self.compasscondig(e))
		self.canvas.bind('<Motion>', self.motion)
		self.createGrid()
		self.CompasStyles('window')

		#self.canvas.create_text(50,10, anchor="nw", text="Click and drag to move the canvas\nScroll to zoom.")

		# This is what enables using the mouse:
		self.canvas.bind('<ButtonPress-1>', self.move_start)
		self.canvas.bind('<B1-Motion>', self.move_to)
		#windows scroll
		#self.canvas.bind('<MouseWheel>',self.zoom)
	def shape(self):
		#print(int(self.sf['Height']), int(self.sf['Length']), int(self.sf['Width']))
		return int(self.sf['Height']), int(self.sf['Length']), int(self.sf['Width'])
	def fileopen(self):
		self.GridToggle(True)
		self.filename = filedialog.askopenfilename(filetypes=[('Sponge schem (*.schem)', '*.schem')], initialdir='./')
		#load schematic
		self.sf = amulet_nbt.load(self.filename)[1]
		#x + z * Width + y * Width * Length
		print('x + z * Width + y * Width * Length')
		print(f"0 + 0 * {self.sf['Width']} + {self.sf['Height']} * { self.sf['Width']} * {self.sf['Length']}")
		print(0 + 0 * int(self.sf['Width']) + int(self.sf['Height']) * int(self.sf['Width']) * int(self.sf['Length']))

		self.Palette = {"normal":{}, "modifi":{}, "lamron":{}}
		#print(self.sf['Palette'])
		#self.Palette["normal"] = self.sf['Palette']
		for i in self.sf['Palette']:
			newi = i if "[" not in i else i.split("[")[0]
			self.Palette["normal"].update({i.split('[')[0]:str(self.sf['Palette'][i])})
			self.Palette["lamron"].update({int(self.sf['Palette'][i]):i})
			self.Palette["modifi"].update({int(self.sf['Palette'][i]):newi})

		self.b = numpy.reshape(self.sf['BlockData'], self.shape())
		#print(self.b)

		try:
			self.scale1.config(from_=len(self.b))
			self.scale1.set(1)
			self.size.config(text=f"Size: {int(self.sf['Length'])}x{int(self.sf['Width'])}")
			self.canvas.delete('all')
			self.createGrid()
		except:
			#self.root.winfo_width()
			#self.root.winfo_height()
			self.scale1 = tkinter.Scale(self.root, tickinterval=1, from_=len(self.b), to=1, length=self.root.winfo_height(), command=self.createGrid)
			self.scale1.grid(column=2, row=0)
			self.root.bind('<Configure>', lambda e:self.scale1.config(length=self.root.winfo_height()))
			self.size = Label(self.root, text=f"Size: {int(self.sf['Length'])}x{int(self.sf['Width'])}")
			self.BlockName = Label(self.root, text="Block Name")
			self.Data = Label(self.root, text="")
			self.size.grid(sticky='SW', column=0, row=2)
			self.BlockName.grid(sticky='SW', column=0, row=3)
			self.Data.grid(sticky='SW', column=0, row=4)
			self.makecanvas()
	def ExportImage(self, direction):
		if direction == 'current layer':
			hen = filedialog.asksaveasfilename(defaultextension='.png', initialfile='canvas export', filetypes=[('png', '*.png')])
			self.layersave('current layer', hen)
		if direction != 'current layer':
			toplevel = tkinter.Toplevel()

			self.checkbutton = tkinter.Checkbutton(toplevel, text="grid", variable=self.CheckIntVar, onvalue=True,offvalue=False)
			self.checkbutton.select()
			#toplevel.geometry("360x200")
			#toplevel.grid_rowconfigure(0, weight=1)
			#toplevel.grid_columnconfigure(0, weight=1)
			self.path = Entry(toplevel, width=40)
			self.path.insert(0, '.')
			self.progress = Progressbar(toplevel, orient='horizontal', maximum=len(self.b)-1, length=toplevel.winfo_reqwidth(), mode='determinate')
			self.trgtbtn = Button(toplevel, text="target...", command=lambda:self.entryset(self.path, toplevel))
			self.savebtn = Button(toplevel, text="save", command=self.start_thread)
			self.abortbtn = Button(toplevel, text="abort", command=lambda:toplevel.destroy())
			self.toplabel = Label(toplevel)
			self.toplabel.grid(sticky='N', column=0, row=0)
			self.savebtn.grid(sticky='SE', column=0, row=4)
			self.abortbtn.grid(sticky='SE', column=1, row=4)
			self.progress.grid(sticky='N', column=0, row=1)
			self.trgtbtn.grid(sticky='N', column=1, row=2)
			self.path.grid(sticky='N', column=0, row=2)
			self.checkbutton.grid(sticky='N', column=0, row=4)
		if direction == 'one per layer':
			self.gif = False
			toplevel.title("save one image per layer")
			self.toplabel.config(text="place holder text 1")
		if direction == 'gif':
			self.gif = True
			toplevel.title("save to animated gif")
			self.toplabel.config(text="place holder text 2")
			label1 = Label(toplevel, text="delay between images in milliseconds")
			#label2 = Label(toplevel, text="divide the time value by 1000")
			vcmd = (self.root.register(self.validate), '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
			self.derent = Entry(toplevel, width=10, validate='key', validatecommand=vcmd)
			self.derent.insert(0, 1000)
			label1.grid(sticky='N', column=0, row=3)
			#label2.grid(sticky='WN', column=0, row=3)
			self.derent.grid(sticky='N', column=1, row=3)
	def start_thread(self):
		self.thread = threading.Thread(target=lambda:self.layersave('giforalllayers'))
		self.thread.start()
		self.root.after(20, self.check_thread)
	def check_thread(self):
		if self.thread.is_alive():self.root.after(20, self.check_thread)
		else:self.thread.join()
	def validate(self, *args):
		#print(args)
		return True if args[2].isdigit() or args[2] == '' else False
		if not args[2].isdigit() or args[2] == '':self.root.bell()
	def alphareplace(self, oldimg, size=(400, 400)):
		newimg = Image.new("RGBA", size, self.BGColor)
		return Image.alpha_composite(newimg, oldimg)
	def layersave(self, direction, hen=None):
		self.imglist = []
		if direction == 'current layer':
			#firstrec = self.canvas.bbox(self.myGrid[0])
			lastrec  = self.canvas.bbox(self.myGrid[-1])[3]-1
			imgdraw = Image.new("RGBA", (lastrec, lastrec), self.BGColor)
			self.draw = ImageDraw.Draw(imgdraw)
			c = self.b[self.scale1.get()-1]
			for x in range(len(c)):
				d = c[x]
				for y in range(len(d)):
					x1 = (x * self.pixel_width)
					x2 = (x1 + self.pixel_width)
					y1 = (y * self.pixel_height)
					y2 = (y1 + self.pixel_height)
					kcolb = self.Palette["lamron"][d[y]].split('[')
					if kcolb[0] != 'minecraft:air':
						img = self.ImageLoad(kcolb)
						img1 = self.ImageManipulate(img, kcolb)
						if img1 is not None:img = img1
						self.PixelEditing(img, kcolb)
						imgdraw.paste(img, (y1, x1, y2, x2))
					if self.CheckIntVar.get():self.draw.rectangle((y1,x1,y2,x2), outline=self.GridColor)
			self.alphareplace(imgdraw, (lastrec, lastrec)).save(hen)
		if direction == 'giforalllayers':
			#firstrec = self.canvas.bbox(self.myGrid[0])
			lastrec  = self.canvas.bbox(self.myGrid[-1])[3]-1
			for i in range(len(self.b)):
				imgdraw = Image.new("RGBA", (lastrec, lastrec), self.BGColor)
				self.draw = ImageDraw.Draw(imgdraw)
				c = self.b[i]
				for x in range(len(c)):
					d = c[x]
					for y in range(len(d)):
						x1 = (x * self.pixel_width)
						x2 = (x1 + self.pixel_width)
						y1 = (y * self.pixel_height)
						y2 = (y1 + self.pixel_height)
						kcolb = self.Palette["lamron"][d[y]].split('[')
						if kcolb[0] != 'minecraft:air':
							img = self.ImageLoad(kcolb)
							img1 = self.ImageManipulate(img, kcolb)
							if img1 is not None:img = img1
							self.PixelEditing(img, kcolb)
							imgdraw.paste(img, (y1, x1, y2, x2))
						if self.CheckIntVar.get():self.draw.rectangle((y1,x1,y2,x2), outline=self.GridColor)
				self.progress.config(value=i)
				if self.gif:self.imglist.append(self.alphareplace(imgdraw, (lastrec, lastrec)))
				else:self.alphareplace(imgdraw, (lastrec, lastrec)).save(f'{self.path.get()}/canvas export{i}.png')
			if self.gif:self.imglist[0].save(f'{self.path.get()}/canvas export.gif', save_all=True, append_images=self.imglist[1:], optimize=False, duration=int(self.derent.get()), loop=0)
	def entryset(self, entry, parent):
		self.dialog = filedialog.askdirectory(parent=parent)
		entry.delete(0,'end')
		entry.insert(0, self.dialog)

	def setnosort(self, seq):
		seen = set()
		return [x for x in seq if not (x in seen or seen.add(x))]
	def CountBlocks(self):
		toplevel = tkinter.Toplevel()
		toplevel.title("Count Blocks")
		toplevel.grid_rowconfigure(0, weight=1)
		toplevel.grid_columnconfigure(0, weight=1)
		columns = ['Amount','Name']#,'id'

		self.BCTree = Treeview(toplevel, columns=columns)#, selectmode='none', height=7, show="headings"
		scrollbar = Scrollbar(toplevel, orient="vertical", command=self.BCTree.yview)
		self.BCTree.grid(sticky='NSEW', column=0, row=0)
		scrollbar.grid(sticky='NSE', column=0, row=0)
		self.BCTree.configure(yscrollcommand=scrollbar.set)

		self.BCTree.heading('#0', text='Icon')
		#for i in columns:
		self.BCTree.heading('Amount', text='Amount', anchor='center', command=lambda: self.treeview_sort_column(self.BCTree, 'Amount', False))
		self.BCTree.heading('Name', text='Name', anchor='center', command=lambda: self.treeview_sort_column(self.BCTree, 'Name', False))

		self.BCTree.column('#0', width=60)#, stretch=True
		self.BCTree.column(columns[0], width=60)
		self.BCTree.column(columns[1], width=150)
		#self.BCTree.column(columns[2], width=50)#id

		master = [y for i in self.b for x in i for y in x if y != 0]

		aliased = {}
		for i, x in self.Palette["modifi"].items():
			if 'wall_torch' in x:x = x.replace('wall_', '')
			if 'piston_head' in x:pass
			else:
				try:aliased[x].append(i)
				except:aliased.update({x:[i]})

		aliasit = [i for i, x in aliased.items() for y in x for z in master if y == z]
		aliascount = [aliasit.count(i) for i in self.setnosort(aliasit)]
		blockcount = {self.setnosort(aliasit)[i]:aliascount[i] for i in range(len(aliascount))}

		self.imagecount = []
		for key, value in blockcount.items():
			img = self.ImageLoad([key, 'blank'])
			pilImage = ImageTk.PhotoImage(img)
			self.imagecount.append(pilImage)
			self.BCTree.insert('','end', image=pilImage, values=(value, key.replace('minecraft:', ''), ''))#self.Palette['modifi'][thingset[i]]['name']
		self.BCTree.tag_configure('OddRow', background=self.ac1)
		self.BCTree.tag_configure('EvenRow', background=self.ac2)
		self.treeview_sort_column(self.BCTree, 'Amount', False)
	def treeview_sort_column(self, tv, col, reverse):
		l = [(tv.set(k, col), k) for k in tv.get_children('')]
		l.sort(key=lambda e:int(e[0]) if e[0].isdigit() else e[0], reverse=reverse)

		for index, (_, k) in enumerate(l):
			tv.move(k, '', index)
		tag = "OddRow"
		for iid in tv.get_children(""):
			tag = "OddRow" if tag == "EvenRow" else "EvenRow"
			tv.item(iid, tags=(tag,))

		tv.heading(col, command=lambda: self.treeview_sort_column(tv, col, not reverse))
	def motion(self, event=None):
		blockname = 'Name: minecraft:air'
		data = 'Data:'
		try:
			color = self.canvas.gettags("current")[0]

			if color != 'current':blockname = f"Name: {color.split('[')[0]}"
				#print(f'color "{color}"')
			reg = '\[(.*)\]'
			data = f"Data: {re.search(reg, color)[0]}"
		except:pass #print(traceback.format_exc())
		self.BlockName.configure(text=blockname)
		self.Data.configure(text=data)

	def createGrid(self, event=None):
		self.canvas.delete('all')
		self.activeimages.clear()
		self.myGrid.clear()
		#self.myGrid2.clear()
		#Plot some rectangles
		try:
			c = self.b[self.scale1.get()-1]
			for x in range(len(c)):
				d = c[x]
				for y in range(len(d)):
					x1 = (x * self.pixel_width)
					x2 = (x1 + self.pixel_width)
					y1 = (y * self.pixel_height)
					y2 = (y1 + self.pixel_height)
					#block = self.Palette["lamron"][d[y]]
					#print(block)
					Grid = self.canvas.create_rectangle(y1,x1,y2,x2, outline=self.GridColor, activefill=self.BGridColor)#, state='disabled', tag=block
					#Grid2 = self.canvas.create_rectangle(y1,x1,y2,x2, fill='green', outline=self.GridColor, activefill=self.BGridColor, tag=block)#
					self.BlockImage([y1,x1,y2,x2], self.Palette["lamron"][d[y]])
					#if self.thing:self.BlockColor(Grid, self.Palette["lamron"][d[y]])
					self.myGrid.append(Grid)
					#self.myGrid2.append(Grid2)
			#self.fuckit()
			#print([self.canvas.itemcget(i, "tag") for i in self.myGrid])

			self.canvas.configure(scrollregion = self.canvas.bbox("all"))
			if self.style == 'grid':self.CompasStyles('grid')
		except:print(traceback.format_exc())

	#def BlockColor(self, GridSquare, block):
	#	kcolb = block.split('[')
	#	if kcolb[0] != 'minecraft:air':
	#		img = self.ImageLoad(kcolb)
	#		self.canvas.itemconfig(GridSquare, fill=self.GetMainColor(img), activefill=self.BGridColor, tag=block)
	def ImageLoad(self, ImageName):
		texname = f"{ImageName[0].replace('minecraft:', '')}"
		texname = "redstone_torch" if texname == "redstone_wall_torch" else texname
		texname = "torch" if texname == "wall_torch" else texname
		texname = "sign" if "sign" in texname else texname
		texname = texname.replace("_pane", "") if "pane" in texname else texname
		return Image.open(f"{self.texpath}/{texname}.png")
	def BlockImage(self, yxyx, block):
		kcolb = block.split('[')
		if kcolb[0] != 'minecraft:air':
			img = self.ImageLoad(kcolb)
			img1 = self.ImageManipulate(img, kcolb)
			if img1 is not None:img = img1
			self.PixelEditing(img, kcolb)
			pilImage = ImageTk.PhotoImage(img)
			self.activeimages.append(pilImage)
			blocktex = self.canvas.create_image(yxyx[0], yxyx[1], image=pilImage, anchor='nw', tag=block)
			self.canvas.lower(blocktex)#makes grid above images
	def ImageManipulate(self, img, block):
		#try:
		#[blacklist := True if i in block[0] else False for i in ['piston_head', 'torch', 'sign']]
		blacklist = False
		for i in ['piston_head', 'torch', 'sign', 'ladder', 'campfire', 'door']:
			if i in block[0]:
				blacklist = True
		if len(block) != 1:
			if 'facing' in block[1] and not blacklist:
				if 'piston' in block[0]:#controls piston side
					splitt = block[1].split('facing=')[1].split(',')[0]
					replacee = re.sub(r'\[|\]', '', splitt)
					if re.search("north|south|east|west", replacee):Image.Image.paste(img, Image.open(f"{self.texpath}/piston_side.png"))
					if replacee == 'north':return img.rotate(0, Image.Resampling.NEAREST)
					if replacee == 'south':return img.rotate(180, Image.Resampling.NEAREST)
					if replacee == 'east': return img.rotate(-90, Image.Resampling.NEAREST)
					if replacee == 'west': return img.rotate(90, Image.Resampling.NEAREST)
				elif 'amethyst' in block[0]:
					if block[1].split('facing=')[1].split(',')[0] == 'north':return img.rotate(0, Image.Resampling.NEAREST)
					if block[1].split('facing=')[1].split(',')[0] == 'south':return img.rotate(180, Image.Resampling.NEAREST)
					if block[1].split('facing=')[1].split(',')[0] == 'east': return img.rotate(-90, Image.Resampling.NEAREST)
					if block[1].split('facing=')[1].split(',')[0] == 'west': return img.rotate(90, Image.Resampling.NEAREST)
				else:
					if block[1].split('facing=')[1].split(',')[0] == 'north':return img.rotate(0, Image.Resampling.NEAREST)
					if block[1].split('facing=')[1].split(',')[0] == 'south':return img.rotate(180, Image.Resampling.NEAREST)
					if block[1].split('facing=')[1].split(',')[0] == 'west': return img.rotate(-90, Image.Resampling.NEAREST)
					if block[1].split('facing=')[1].split(',')[0] == 'east': return img.rotate(90, Image.Resampling.NEAREST)
		if 'torch' in block[0]:
			if len(block) > 1:
				splitt = block[1].split('lit=')[1].split(',')[0]
				replacee = re.sub(r'\[|\]', '', splitt)
				if replacee == 'true':Image.Image.paste(img, Image.open(f"{self.texpath}/redstone_torch_lit.png"))
		if 'redstone_wire' in block[0]:
			north = re.search("(?:north)=(?:none|side|up)", block[1]).group().split('=')[1]
			south = re.search("(?:south)=(?:none|side|up)", block[1]).group().split('=')[1]
			east  =  re.search("(?:east)=(?:none|side|up)", block[1]).group().split('=')[1]
			west  =  re.search("(?:west)=(?:none|side|up)", block[1]).group().split('=')[1]

			wireT = False
			corner = False

			if north == 'side' and south == 'side' and east == 'side' and west == 'side':#cross
				Image.Image.paste(img, Image.open(f"{self.texpath}/redstone_wire-cross.png"))
			if north == 'up' and south == 'up' and east == 'up' and west == 'up':#cross, all the same.
				Image.Image.paste(img, Image.open(f"{self.texpath}/redstone_wire-cross.png"))

			if north == 'side' and south == 'side' and east == 'none' and west == 'none':return img.rotate(90, Image.Resampling.NEAREST)#straight n-s
			if north == 'up' and south == 'up' and east == 'none' and west == 'none':return img.rotate(90, Image.Resampling.NEAREST)#straight n-s, all the same.
			if north == 'up' and south == 'side' and east == 'none' and west == 'none':return img.rotate(90, Image.Resampling.NEAREST)#outlier straight n=u - s=s
			if north == 'side' and south == 'up' and east == 'none' and west == 'none':return img.rotate(90, Image.Resampling.NEAREST)#outlier straight n=s - s=u


			if north == 'side' and south == 'none' and east == 'side' and west == 'none': corner = ''    #corner n-e
			if north == 'side' and south == 'none' and east == 'none' and west == 'side': corner = '90'  #corner n-w
			if north == 'none' and south == 'side' and east == 'side' and west == 'none': corner = '-90' #corner s-e
			if north == 'none' and south == 'side' and east == 'none' and west == 'side': corner = '180' #corner s-w

			if north == 'side' and south == 'none' and east == 'up'   and west == 'side': wireT = ''    #outlier t n=s - e=u - w=s
			if north == 'side' and south == 'up'   and east == 'none' and west == 'side': wireT = '90'  #outlier t n=s - s=u - w=s
			if north == 'up'   and south == 'side' and east == 'side' and west == 'none': wireT = '-90' #outlier t n=u - s=s - e=s
			if north == 'none' and south == 'side' and east == 'side' and west == 'up':   wireT = '180' #outlier t s=s - e=s - w=u

			if north == 'side' and south == 'none' and east == 'side' and west == 'up':   wireT = ''    #outlier t n=s - e=s - w=u
			if north == 'up'   and south == 'side' and east == 'none' and west == 'side': wireT = '90'  #outlier t n=u - s=s - w=s
			if north == 'side' and south == 'up'   and east == 'side' and west == 'none': wireT = '-90' #outlier t n=s - s=u - e=s
			if north == 'none' and south == 'side' and east == 'up'   and west == 'side': wireT = '180' #outlier t s=s - e=u - w=s


			if north == 'up'   and south == 'none' and east == 'up'   and west == 'none': corner = ''    #corner n-e, all the same.
			if north == 'up'   and south == 'none' and east == 'none' and west == 'up':   corner = '90'  #corner n-w, all the same.
			if north == 'none' and south == 'up'   and east == 'up'   and west == 'none': corner = '-90' #corner s-e, all the same.
			if north == 'none' and south == 'up'   and east == 'none' and west == 'up':   corner = '180' #corner s-w, all the same.

			if north == 'side' and south == 'none' and east == 'up'   and west == 'none': corner = ''    #corner n=s - e=u
			if north == 'side' and south == 'none' and east == 'none' and west == 'up':   corner = '90'  #corner n=s - w=u
			if north == 'none' and south == 'side' and east == 'up'   and west == 'none': corner = '-90' #corner s=s - e=u
			if north == 'none' and south == 'side' and east == 'none' and west == 'up':   corner = '180' #corner s=s - w=u

			if north == 'side' and south == 'none' and east == 'up'   and west == 'up':   wireT = ''# t n=s - e=u - w=u
			if north == 'up'   and south == 'up'   and east == 'none' and west == 'side': wireT = '90'# t n=u - s=u - w=s
			if north == 'up'   and south == 'up'   and east == 'side' and west == 'none': wireT = '-90'# t n=u - s=u - e=s
			if north == 'none' and south == 'side' and east == 'up'   and west == 'up':   wireT = '180'# t s=s - e=u - w=u

			if north == 'up'   and south == 'none' and east == 'side' and west == 'side': wireT = ''    # t
			if north == 'side' and south == 'side' and east == 'none' and west == 'up':   wireT = '90'  # t n=s - s=s - w=u
			if north == 'side' and south == 'side' and east == 'up'   and west == 'none': wireT = '-90' # t n=s - s=s - e=u
			if north == 'none' and south == 'up'   and east == 'side' and west == 'side': wireT = '180' # t s=u - e=s - w=s


			if north == 'side' and south == 'none' and east == 'side' and west == 'side': wireT = ''    # t n-e-w
			if north == 'side' and south == 'side' and east == 'none' and west == 'side': wireT = '90'  # t n-s-w
			if north == 'side' and south == 'side' and east == 'side' and west == 'none': wireT = '-90' # t n-s-e
			if north == 'none' and south == 'side' and east == 'side' and west == 'side': wireT = '180' # t s-e-w

			if corner:
				Image.Image.paste(img, Image.open(f"{self.texpath}/redstone_wire-corner.png"))
				if corner == "90": return img.rotate(90, Image.Resampling.NEAREST)
				if corner == "-90":return img.rotate(-90, Image.Resampling.NEAREST)
				if corner == "180":return img.rotate(180, Image.Resampling.NEAREST)
			if wireT:
				Image.Image.paste(img, Image.open(f"{self.texpath}/redstone_wire-t.png"))
				if wireT == "90": return img.rotate(90, Image.Resampling.NEAREST)
				if wireT == "-90":return img.rotate(-90, Image.Resampling.NEAREST)
				if wireT == "180":return img.rotate(180, Image.Resampling.NEAREST)
		#except:
		#	pass #print(traceback.format_exc())
	def PixelEditing(self, img, block):
		try:
			width, height = img.size
			if 'carpet' in block[0]:
				pix = img.load()
				numlist = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
				for i in range(16):
					for x in range(16):
						if x in numlist:
							pix[i, x] = (0, 0, 0, 0)
			if 'wall' in block[0] and 'sign' not in block[0]:
				pix = img.load()
				test = [
				(0, 4), (1, 4), (2, 4), (3, 4), (4, 4),
				(0, 5), (1, 5), (2, 5), (3, 5), (4, 5),
				(0, 6), (1, 6), (2, 6), (3, 6), (4, 6),
				(0, 7), (1, 7), (2, 7), (3, 7), (4, 7),
				(0, 8), (1, 8), (2, 8), (3, 8), (4, 8),
				(0, 9), (1, 9), (2, 9), (3, 9), (4, 9),
				(0, 10), (1, 10), (2, 10), (3, 10), (4, 10),
				(0, 11), (1, 11), (2, 11), (3, 11), (4, 11),

				(15, 4), (14, 4), (13, 4), (12, 4), (11, 4),
				(15, 5), (14, 5), (13, 5), (12, 5), (11, 5),
				(15, 6), (14, 6), (13, 6), (12, 6), (11, 6),
				(15, 7), (14, 7), (13, 7), (12, 7), (11, 7),
				(15, 8), (14, 8), (13, 8), (12, 8), (11, 8),
				(15, 9), (14, 9), (13, 9), (12, 9), (11, 9),
				(15, 10), (14, 10), (13, 10), (12, 10), (11, 10),
				(15, 11), (14, 11), (13, 11), (12, 11), (11, 11)
				]
				for i,x in test:pix[i, x] = (0, 0, 0, 0)
				
			if 'slab' in block[0] or 'stairs' in block[0]:
				pix = img.load()
				if 'type' in block[1]:
					for i in range(height):
						for x in range(width):
							typee = block[1].split('type=')[1].split(',')[0]
							if typee == 'bottom':
								if x <= 8:pix[i,x] = (0, 0, 0, 0)
							if typee == 'top':
								if x >= 8:pix[i,x] = (0, 0, 0, 0)
				if 'facing' in block[1]:
					for i in range(height):
						for x in range(width):
							half = block[1].split('half=')[1].split(',')[0]
							if half == 'bottom':
								if i >= 8:pix[i,x] = (0, 0, 0, 0)
								if x >= 8:break
							if half == 'top':
								if x >= 8:pix[i,x] = (0, 0, 0, 0)
								if i <= 8:break
			if len(block) != 1:
				if 'facing' in block[1]:
					facing = block[1].split('facing=')[1].split(',')[0].replace("]", "")
					blacklist = ['minecraft:sticky_piston', 'minecraft:amethyst_cluster', 'minecraft:large_amethyst_bud', 'minecraft:medium_amethyst_bud', 'minecraft:small_amethyst_bud']
					if 'torch' in block[0]:
						if facing == 'south':direction = 'north'
						if facing == 'north':direction = 'south'
						if facing == 'west': direction = 'east'
						if facing == 'east': direction = 'west'
						self.arrowmaker(direction, img)
					elif 'stairs' in block[0]:
						if facing == 'north':direction = 'north'
						if facing == 'south':direction = 'south'
						if facing == 'east': direction = 'east'
						if facing == 'west': direction = 'west'
						self.arrowmaker(direction, img)
					elif 'sign' in block[0]:
						if facing == 'south':direction = 'north'
						if facing == 'north':direction = 'south'
						if facing == 'west': direction = 'east'
						if facing == 'east': direction = 'west'
						self.arrowmaker(direction, img)
					else:
						if 'repeater' in block[0]:img.rotate(90, Image.Resampling.NEAREST)
						if facing == 'north':direction = 'north'
						if facing == 'south':direction = 'south'
						if facing == 'west': direction = 'east'
						if facing == 'east': direction = 'west'
						if block[0] not in blacklist and facing not in ['up', 'down']:self.arrowmaker(direction, img)
		except: print(traceback.format_exc())

	#move
	def move_start(self, event):
		self.canvas.scan_mark(event.x, event.y)
	def move_to(self, event):
		self.canvas.scan_dragto(event.x, event.y, gain=1)

	#windows zoom
	def zoom(self, event):
		if (event.delta > 0):self.canvas.scale("all", 0, 0, 1.1, 1.1)
		elif (event.delta < 0):self.canvas.scale("all", 0, 0, 0.9, 0.9)
		self.canvas.configure(scrollregion=self.canvas.bbox("all"))

	def arrowmaker(self, direction, img):
		if direction:pix = img.load()
		if direction == 'north':
			test = [(7, 0),(8, 0),(6, 1),(7, 1),(8, 1),(9, 1),(5, 2),(6, 2),(7, 2),(8, 2),(9, 2),(10, 2)]
			for i, x in test: pix[i ,x] = (255, 0, 0)
		if direction == 'south':
			test = [(7, 15),(8, 15),(6, 14),(7, 14),(8, 14),(9, 14),(5, 13),(6, 13),(7, 13),(8, 13),(9, 13),(10, 13)]
			for i, x in test: pix[i, x] = (255, 0, 0)
		if direction == 'east':
			test = [(15, 7),(15, 8),(14, 6),(14, 7),(14, 8),(14, 9),(13, 5),(13, 6),(13, 7),(13, 8),(13, 9),(13, 10)]
			for i, x in test: pix[i, x] = (255, 0, 0)
		if direction == 'west':
			test = [(0, 7),(0, 8),(1, 6),(1, 7),(1, 8),(1, 9),(2, 5),(2, 6),(2, 7),(2, 8),(2, 9),(2, 10)]
			for i, x in test: pix[i, x] = (255, 0, 0)
if __name__ == "__main__":
	Example()
