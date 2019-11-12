import tkinter as tk
import lattices
#from D3_animate import draw_3d_utils
from D3_animate.draw_3d_utils import bunch_of_points, bind_events
from particle_utils import string_to_array
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

def neighbor_force(particle, particle_dict, pos_dependant_force):
    total_force = np.array([0., 0., 0.])
    print("++++++++++++++++++++++++++++++")
    print("the name of the particle is %s, with neighbors %s" %(particle.name, particle.neighbors))
    print("position of particle %s is %s"%(particle.name , particle.pos))
    print("the particle has constraint %s" %particle.constraint)

    for other_particle_key in particle.neighbors:
        other_part = particle_dict[other_particle_key]
        new_force = pos_dependant_force(particle.pos, other_part.pos)
        total_force += new_force
    #print("magntitude of the force is %s"%np.linalg.norm(total_force))
    #print("total_force is %s"%total_force)
    return total_force

def spring_force(x1, x2, strength, relax_dist):
    r = x1 - x2
    r_abs = np.linalg.norm(r)
    r_unit = r / r_abs
    distance = r_abs

    force_abs = strength * (distance - relax_dist) 
    force_vec = r_unit * force_abs
    return force_vec

def neighbor_spring_force(particle, particle_pos, particle_dict):
    return neighbor_force(particle, particle_dict, lambda x1, x2: spring_force(x1, x2, 1, 0))

def euler_newton_update(particle, particles, time_step):
    try: 
        constraint = particle.constraint
    except:
        constraint = [False, False, False]
    if not constraint[0]:
        particle.mom[0] = (particle.mom + time_step*particle.force(particle.pos, particles))[0]
    if not constraint[1]:
        particle.mom[1] = (particle.mom + time_step*particle.force(particle.pos, particles))[1]
    if not constraint[2]:
        particle.mom[2] = (particle.mom + time_step*particle.force(particle.pos, particles))[2]
    
    particle.pos = (particle.pos + time_step*particle.mom/particle.mass)

class lattice_particle(object):
    def __init__(self, name, neighbors, lattice_size, pos, mom = np.array([0., 0., 0.]), mass = 1.):
        self.name = name
        self.pos = pos
        self.set_force = neighbor_spring_force
        self.neighbors = neighbors

        self.mom = mom
        self.mass = mass
        self.name = name

        name_array = string_to_array(name)
        constraint = [False, False, False]
        for i in range(len(name_array)):
            if name_array[i] == 0 or (name_array[i] == (5 - 1)):
                constraint[i] = True
        self.constraint = constraint

    def force(self, self_pos, particles):
        return self.set_force(self, self_pos, particles)



#lattice, lattice_name = lattices.uncoupled_pyrochlore_lattice(point, 4, window_size)
lattice, lattice_name = lattices.cubic_lattice(lattice_particle, 5, window_size)

time_step = 0.1
lattice_bunch = bunch_of_points(lattice, window_size, base_radius = radius)
bind_events(canvas, lattice_bunch, pos_shift = window_size/100, theta_shift = 2*np.pi / 300)
canvas.pack()
lattice_bunch.register_all_base_points()
def edit_lattice(lattice):
    for name, particle in lattice.items():
        if string_to_array(name)[0] % 2 == 0:
            particle.pos[0] += 0
    return lattice

lattice = edit_lattice(lattice)
lattice_bunch.update(lattice)
while True:
    for name, particle in lattice.items():
        euler_newton_update(particle, lattice, time_step)
    lattice_bunch.update(lattice)
    canvas.delete("all")
    lattice_bunch.draw_all_points(canvas)
    lattice_bunch.draw_all_lines(canvas)
    canvas.pack()
    root.update()
