from tkinter import *
import time
import numpy as np
from Electrostatic_Utils import draw_arrow, norm
import random
import copy 
from matplotlib import pyplot as plt
import math 

size_shift = 3
window_size = 512.
root = Tk()
canvas = Canvas(root, width = window_size, height= window_size)
canvas.pack()
k = 10000
G = 2000
g = 20

glob_num_in_line = None

time_speed = 10 ** 3



class particle(object):
    def __init__(self, name, pos = np.array([window_size* .5, window_size * .5]), mom = np.array([0.,0.]), mass = 1., charge = 0,
     constraint = [None, None], colliding = False, wall_collide = False, grid_index = [None, None], active = True):
        self.pos = pos
        self.mom = mom
        self.mass = mass
        self.charge = charge
        self.constraint = constraint
        self.colliding = colliding
        self.wall_collide = wall_collide
        self.grid_index = grid_index
        self.name = name
        self.active = active

        #COLOR based on
        if self.charge >= 0:
            self.color = '#%02x%02x%02x' % (255, 255 - math.floor(51/2) * self.charge, 255 - math.floor(51/2) * self.charge)
        if self.charge <= 0:
            self.color = '#%02x%02x%02x' % (255 + math.floor(51/2) * self.charge, 255 + math.floor(51 /2) * self.charge, 255)
        if self.charge == 0:
            self.color = "white"

    def radius(self):
        return size_shift * (self.mass ** (1 / 2))

    def KE(self):
        return ((self.mom[0] ** 2) + (self.mom[1] ** 2)) / (2 * self.mass)

    def get_corners(self):
        xy0 = np.array(
            [self.pos[0] - self.radius(), self.pos[1] + self.radius()])
        xy1 = np.array(
            [self.pos[0] + self.radius(), self.pos[1] - self.radius()])
        return xy0, xy1


    def draw(self):
        xy0, xy1 = self.get_corners()
        canvas.create_oval(xy0[0], xy0[1], xy1[0], xy1[1],
                           outline="black", fill=self.color)
        


    def force(self, particles, type, damping):
        if "basic_grav" in type:
            total_force_vec = np.array([0., g * self.mass])
        else:
            total_force_vec = np.array([0., 0.])
        total_force_vec += -damping * self.mom / self.mass
        if self.active:
            for other_part in particles:
                if other_part.name != self.name:
                    #print("other particle: " + str(other_part.name) + " position initial: " + str(other_part.pos))
                    r = self.pos - other_part.pos
                    r_abs = np.linalg.norm(r)
                    r_unit = r / r_abs
                    side_overlap = max(0, -r_abs + self.radius() + other_part.radius())
                    distance = r_abs
                    overlap_force = 10000000000 * (distance ** -6)
                    force_abs = 0
                    #if side_overlap != 0:
                        #print(overlap_force)
                    if "electrostatic" in type:
                        force_abs += (k * self.charge * (other_part.charge / (r_abs ** 2))) 
                    if "gravitational" in type:
                        force_abs += (-1 * G * self.mass * (other_part.mass / (r_abs ** 2))) 
                    if "strong_nuclear" in type:
                        if ("proton" in self.name) and ("proton" in other_part.name):
                            force_abs += -10000000 * (distance ** -4)
                    if "repulsive" in type:
                        force_abs +=  (G * self.mass * (other_part.mass / (r_abs ** 2))) 
                    if "basic_grav" in type:
                        force_abs += 0
                    if "spring" in type:
                        force_abs += (-1 * (r_abs - side_overlap) ** 2) 
                    if "nearest_neighbor_spring" in type:
                        if (abs(self.grid_index[0] - other_part.grid_index[0]) <= 1) and (abs(self.grid_index[1] - other_part.grid_index[1]) <= 0) or (abs(self.grid_index[0] - other_part.grid_index[0]) <= 0) and (abs(self.grid_index[1] - other_part.grid_index[1]) <= 1):
                            force_abs += (-1000  * ((r_abs / (window_size / glob_num_in_line)) ** 2))
                    force_abs += overlap_force
                    #if abs(force_abs) > 10000:
                    #    force_abs = 10000 * abs(force_abs) / force_abs     
                    force_vec = r_unit * force_abs
                    total_force_vec += force_vec
                    if "D" in type:
                        total_force_vec += np.array([0.0, 0.0])
        else:
            total_force_vec = np.array([0.0, 0.0])
        return total_force_vec

    def update_momentum(self, particles, walls, walldamp, type, damping, torus, time_step):
        allow_force_x = True
        allow_force_y = True
        main_force = copy.copy(self.force(particles, type, damping))
        if walls:
            if ((self.pos[0] + self.radius()) >= window_size) and (self.mom[0] >= 0):
                self.mom[0] = -1 * walldamp * self.mom[0]
                allow_force_y = False
                allow_force_x = False
            if ((self.pos[0] - self.radius()) <= 0) and (self.mom[0] <= 0):
                self.mom[0] = -1 * walldamp * self.mom[0]
                allow_force_y = False
                allow_force_x = False
            if ((self.pos[1] + self.radius()) >= window_size) and (self.mom[1] >+ 0):
                self.mom[1] = -1 * walldamp * self.mom[1]
                allow_force_y = False
                allow_force_x = False
            if ((self.pos[1] - self.radius()) <= 0) and (self.mom[1] <= 0):
                self.mom[1] = -1 * walldamp * self.mom[1]
                allow_force_y = False
                allow_force_x = False
            if self.constraint[0] == "x":
                self.mom[0] = 0
                allow_force_x = False
            if self.constraint[1] == "y":
                self.mom[1] = 0
                allow_force_y = False
        if torus:
            if self.pos[0] > window_size:
                self.pos[0] -= window_size
            if self.pos[1] > window_size:
                self.pos[1] -= window_size
            if self.pos[0] < 0:
                self.pos[0] += window_size
            if self.pos[1] < 0:
                self.pos[1] += window_size
            allow_force_x = True
            allow_force_y = True
        if self.constraint[0]:
            allow_force_x = False
        if self.constraint[1]:
            allow_force_y = False
        if allow_force_x and not allow_force_y:
            self.mom[0] = self.mom[0] + (time_step / self.mass) * main_force[0]
        if allow_force_y and not allow_force_x:
            self.mom[1] = self.mom[1] + (time_step / self.mass) * main_force[1]
        if allow_force_y and allow_force_x:
            self.mom = self.mom + (time_step / self.mass) * main_force


def display_grid(grid_density, grid_color):
    canvas.delete("all")
    for x in np.arange(0, window_size, grid_density):
        canvas.create_line(x, 0, x, window_size, fill=grid_color)
    for y in np.arange(0, window_size, grid_density):
        canvas.create_line(0, y, window_size, y, fill=grid_color)


# particle_1 = particle(charge = 8, mass = 2., pos = np.array([window_size /2, window_size /2]), mom = np.array([0, -80.]))
# particle_2 = particle(charge = 8., pos = np.array([window_size * .7, window_size /2]), mass = 90., mom = np.array([0., 80.]))
# particle_3 = particle(charge = 8., pos = np.array([window_size * 4/5,window_size /2]), mass = 3., mom = np.array([0., -10.]))
# particles = np.array([particle_1, particle_2])

def cluster(number, charge_range = 10, mass_range = 10, mom_range = 10):
    particles = [None]*number
    for i in np.arange(0, number):
        particles[i] = particle(
            name = i,
            charge = random.randint(-1 * charge_range, charge_range),
            mass = float(random.randint(1, mass_range)),
            pos = np.array([window_size * random.uniform(0,1), window_size * random.uniform(0,1)]),
            mom = np.array([random.uniform(-1 * mom_range, mom_range), 
                random.uniform(-1 * mom_range, mom_range)]))
    return particles

def protons_and_electrons(num_prot, num_elect, mom_range = 0):
    protons = [None] * num_prot
    for i in np.arange(0, num_prot):
        protons[i] = particle(
            name = "proton: " + str(i),
            charge = 1,
            mass = 9,
            pos = np.array([window_size * random.uniform(0,1), window_size * random.uniform(0,1)]),
            mom = np.array([random.uniform(-1 * mom_range, mom_range), 
                random.uniform(-1 * mom_range, mom_range)]))
    electrons = [None] * num_elect
    for i in np.arange(0, num_elect):
        electrons[i] = particle(
            name = "electron: " + str(i),
            charge = -1,
            mass = .5,
            pos = np.array([window_size * random.uniform(0,1), window_size * random.uniform(0,1)]),
            mom = np.array([random.uniform(-1 * mom_range, mom_range), 
                random.uniform(-1 * mom_range, mom_range)]))
    return protons + electrons


def orbit():
    particle_1 = particle(charge=0,
                          mass = 2.,
                          pos = np.array([window_size * 3/4, window_size * .5]),
                          mom = np.array([0., 79.056]),
                          name = 0)
    particle_2 = particle(charge= 0,
                          mass = 100.,
                          pos = np.array([window_size * .5, window_size * .5]),
                          mom = np.array([0., 79.056]),
                          constraint= np.array([None, None]),
                          name = 1)
    return [particle_1, particle_2]

def free_grid(number = 4, mass = 4, init_mom = np.array([0.,0.])):
    particles = np.empty((number, number), particle)
    for i in range(number):
        for j in range(number):
            particles[i, j] = particle(pos = np.array([(window_size / (2 * number)) + i * window_size / number, (window_size / (2 * number)) + j * window_size / number]),
             mass = mass,
             name = [i, j],
             mom = init_mom)
    global glob_num_in_line
    glob_num_in_line = number 
    return particles.reshape(number ** 2)

def edged_grid(number = 5, mass = 10, speed = 0., net_mom = np.array([0., 0.])):
    particles = np.empty((number, number), particle)
    for i in range(number):
        for j in range(number):
            constraint_ij = [None, None]
            if i == 0 or i == (number - 1):
                constraint_ij[0] = "x"
            if j == 0 or j == (number - 1):
                constraint_ij[1] = "y"
            particles[i, j] = particle(pos = np.array([(window_size / (2 * number)) + i * window_size / number, (window_size / (2 * number)) + j * window_size / number]),
            name = [i, j],
            mass = mass,
            charge =-5,
            mom = np.array([random.randint(-speed, speed), random.randint(-speed, speed)]) + net_mom,
            constraint = constraint_ij,
            grid_index = [i, j])       
    global glob_num_in_line
    glob_num_in_line = number    
    return particles.reshape(number ** 2)

def edged_grid_disp(number = 5, mass = 10, speed = 0., net_mom = np.array([0., 0.])):
    particles = np.empty((number, number), particle)
    for i in range(number):
        for j in range(number):
            constraint_ij = [None, None]
            if i == 0 or i == (number - 1):
                constraint_ij = ["x", "y"]
            if j == 0 or j == (number - 1):
                constraint_ij = ["x", "y"]
            if i == 2 and j != 0 and j != (number - 1):
                particles[i, j] = particle(pos = np.array([(window_size / (2 * number)) + i * window_size / number, (window_size / (2 * number)) + (j * (window_size / number)) + 50]),
            name = [i, j],
            mass = mass,
            mom = np.array([random.randint(-speed, speed), random.randint(-speed, speed)]) + net_mom,
            constraint = constraint_ij,
            grid_index = [i, j])  
            else:
                particles[i, j] = particle(pos = np.array([(window_size / (2 * number)) + i * window_size / number, (window_size / (2 * number)) + j * window_size / number]),
            name = [i, j],
            mass = mass,
            mom = np.array([random.randint(-speed, speed), random.randint(-speed, speed)]) + net_mom,
            constraint = constraint_ij,
            grid_index = [i, j])       
    global glob_num_in_line
    glob_num_in_line = number    
    return particles.reshape(number ** 2)

def semiconductor(numb_prot = 5, numb_elect = 5, mass_prot = 10, mass_elect = 2, speed = 0.0, net_mom = np.array([0.0, 0.0])):
    protons = np.empty((numb_prot, numb_prot), particle)
    electrons = np.empty((numb_elect, numb_elect), particle)
    for i in range(numb_prot):
        for j in range(numb_prot):
            protons[i, j] = particle(
            pos = np.array([(window_size / (2 * numb_prot)) + i * window_size / numb_prot,
            (window_size / (2 * numb_prot)) + (j * (window_size / numb_prot)) + 25]),
            name = "proton:" + str([i, j]),
            mass = mass_prot,
            charge = 5,
            active = False,
            constraint = ["x", "y"],
            grid_index = [i, j])
    for i in range(numb_elect):
        for j in range(numb_elect):      
            electrons[i, j] = particle(
            pos = np.array([(window_size / (2 * numb_elect)) + (i * window_size / numb_elect),
             (window_size / (2 * numb_elect)) + (j * (window_size / numb_elect)) + 0]),
            name = "electron" + str([i, j]),
            mass = mass_elect,
            charge = -5,
            mom = np.array([random.randint(-speed, speed), random.randint(-speed, speed)]) + net_mom,
            grid_index = [i, j]) 
    return np.append(protons.reshape(numb_prot ** 2), (electrons.reshape(numb_elect ** 2)))

def simulate(walls, walldamp, arrows, type, particles, grid_density = 32, damping = 0, damp_at_KE = 1000000, torus = False, time_step = 0.05):
    KE_array = []
    time_array =[]
    time = 0
    try: 
        while True:
            total_KE = 0
            display_grid(grid_density, "gray")
            particles_old = []
            for particle in particles:
                particles_old.append(copy.copy(particle))
            #Move particles
            for particle in particles:
                #print("particle " + str(particle.name) +   " position initial:" + str(particle.pos))
                if particle.active:
                    particle.update_momentum(particles_old, walls, walldamp, type, damping, torus, time_step)
                    particle.pos = (time_step / particle.mass) * particle.mom + particle.pos
                    total_KE += particle.KE()
                    if total_KE > damp_at_KE:
                        damping = 1
                    else:
                        damping = 0
                    KE_array.append(total_KE)
                    if arrows:
                        draw_arrow(canvas, particle.pos, 
                        norm(particle.force(particles_old, type, damping)) * np.sqrt(np.abs(particle.force(particles_old, type, damping))) * 3)
                #print("particle " + str(particle.name) +   " position final: " + str(particle.pos))
                particle.draw()

            time += time_step  
            #print(time)  
            time_array.append(time)   
            canvas.pack()
            #time.sleep(2)   
            root.update()
            #print("===============================================")
            #time.sleep(time_step / time_speed)
            #print("time:" + str(time) + "  total_KE:" + str(total_KE))
    except:
        fig = plt.figure()
        ax = fig.add_subplot(111)
        plt.plot(time_array, KE_array)
        ax.set_xlabel("time")
        ax.set_ylabel("Kinetic Energy")
        plt.show()
        #time.sleep(time_step / time_speed)
        plt.show()


#simulate(arrows=True, walls=True, walldamp = 1, type = ["gravitational"], particles = orbit(), time_step = 0.02)

#simulate(arrows=True, walls=True, walldamp = 1, type = ["electrostatic"], particles = cluster(6, mom_range = 6), time_step = 0.01)

#simulate(arrows=True, walls=True, walldamp = 1, type = ["electrostatic"], particles = cluster(15, mom_range = 10), time_step = 0.005)

#simulate(arrows=False, walls=True, walldamp = 1, type = ["strong_nuclear"], particles = protons_and_electrons(2, 0, mom_range = 1000), damp_at_KE = 300)

#simulate(arrows=False, walls=True, walldamp = .5, type = ["gravitational"], particles = cluster(15), damping = .2)

simulate(arrows=True, walls=True, walldamp = 1, type = ["nearest_neighbor_spring"], particles = edged_grid(8, speed = 0, net_mom = np.array([190.0, 30.0])), time_step = 0.3)

#simulate(arrows=False, walls=True, walldamp = 1, damping = 2, type = ["gravitational", "nearest_neighbor_spring"], particles = edged_grid(speed = 100, net_mom = np.array([0.0, 0.0]), number = 6))
#simulate(arrows=True, walls=True, walldamp = 1, damping = .2, type = ["basic_grav"], particles = cluster(15), time_step = 0.02)
#simulate(arrows=True, walls=True, walldamp = 1, type = ["gravitational"], particles = free_grid(5))
#simulate(arrows=True, walls=True, walldamp = .5, type = ["gravitational"], particles = free_grid(6), damping = .3)
#simulate(arrows = False, walls= False, torus = True, type = ["electrostatic", "D"], particles = semiconductor(speed = 10.0), walldamp = 1, time_step = 0.001)