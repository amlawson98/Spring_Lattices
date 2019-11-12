from tkinter import *
window_size = 400
top_space = 40
root = Tk()
#root.geometry(height= window_size, width= window_size)

f1 = Frame(root, width =window_size, height = window_size - top_space)
f2 = Frame(root, width =window_size, height = top_space)
canvas = Canvas(f1, width = window_size, height= window_size-top_space)

def set_with_temp_scale(scale_val):
	global scale_temp
	scale_temp = float(scale_val)

temp_scale = Scale(f2, from_=0., to=10.,resolution= 0.00001, orient= HORIZONTAL, showvalue=1, command= set_with_temp_scale, label = "Temp")
temp_scale.place()#rely = 30, relx = 80)
temp_scale.pack(fill=BOTH, side=LEFT)

def set_with_H_scale(scale_val):
	global scale_H
	scale_H = float(scale_val)

H_scale = Scale(f2, from_=5, to=0,resolution= 0.01, orient= HORIZONTAL, showvalue=1, command= set_with_H_scale, label = "H (feild ext eng.)")
H_scale.place()#rely = 30, relx = 80)
H_scale.pack(fill=BOTH, side=LEFT)

def set_with_J_scale(scale_val):
	global scale_J
	scale_J = float(scale_val)

J_scale = Scale(f2, from_=1, to=-1,resolution= 1, orient= HORIZONTAL, showvalue=1, command= set_with_J_scale, label = "J (interaction eng.)")
J_scale.place()#rely = 30, relx = 80)
J_scale.pack(fill=BOTH, side=LEFT)

running = False
txt_var = StringVar()
txt_var.set("Play")
def pause_play():
	global running
	if running:
		txt_var.set("Play")
	if not running:
		txt_var.set("Pause")	
	running = not running
pause_button = Button(f2,textvariable=txt_var, command= pause_play)
pause_button.pack()

quit_button = Button(f2, text="Quit", command = root.destroy)
quit_button.pack()

annealing = BooleanVar()
annealing_button = Checkbutton(f2, text="Annealing", variable=annealing)
annealing_button.pack()
temp=0


def update_temp():
	global temp
	decrease_rate = -0.0004
	temp = temp*(1 + decrease_rate)

f1.pack(side=BOTTOM)
f2.pack(side=TOP)
while True:
	circ = canvas.create_oval(10 + temp, 10+temp, 15+temp, 15+temp)
	canvas.pack()
	canvas.update()
	if running:
		temp = temp_scale.get()
	if annealing.get() and running:
		update_temp()
		temp_scale.set(temp)
	canvas.delete(circ)

