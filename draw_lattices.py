import tkinter as tk
import lattices
#from D3_animate import draw_3d_utils
from D3_animate.draw_3d_utils import bunch_of_points, bind_events
import numpy as np
#print(dir(draw_3d_utils))
window_size = 400
radius = 5
root = tk.Tk()
canvas = tk.Canvas(root, width = window_size, height= window_size)
class point(object):
    def __init__(self, name, neighbors, lattice_size, pos):
        self.name = name
        self.neighbors = neighbors
        self.lattice_size = lattice_size
        self.pos = pos

#lattice, lattice_name = lattices.uncoupled_pyrochlore_lattice(point, 4, window_size)
lattice, lattice_name = lattices.cubic_lattice(point, 5, window_size)
lattice_bunch = bunch_of_points(lattice, window_size, base_radius = radius)
bind_events(canvas, lattice_bunch, pos_shift = window_size/100, theta_shift = 2*np.pi / 300)
canvas.pack()
lattice_bunch.register_all_base_points()

while True:
    canvas.delete("all")
    lattice_bunch.draw_all_points(canvas)
    lattice_bunch.draw_all_lines(canvas)
    canvas.pack()
    root.update()
