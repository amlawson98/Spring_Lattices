import tkinter as tk

import numpy as np
# from strings import square_string, gaussian
import copy
from numba import jit
def cos(theta): 
	return np.cos(theta)
def sin(theta): 
	return np.sin(theta)

# window_size = 512
#root= tk.Tk()
y_shift = 0
x_shift = 0

# film_dist = window_size/2

def draw_dot(mid_pos, dist_from_obs, radius, canvas, film_dist):
	#print("radius is %s"% radius)
	size = film_dist*radius/dist_from_obs
	#print("size is %s"%size)
	canvas.create_oval(mid_pos[0] + size,
		mid_pos[1] + size,
		mid_pos[0] - size, 
		mid_pos[1] - size, 
		fill="black")

def draw_pt(pos, base_radius, canvas, window_size, film_dist):
	x1 = window_size / 2 + film_dist * pos[0]/pos[1]
	z1 = window_size / 2 + film_dist * pos[2]/pos[1]
	dist_from_obs = (pos[0]**2 + pos[1]**2 +pos[2]**2)**.5
	draw_dot((x1, z1), dist_from_obs, base_radius, canvas, film_dist)

def draw_line(pos1, pos2, canvas, window_size, film_dist):
	xy1 = np.array([window_size/2, window_size/2]) + film_dist * np.array([pos1[0]/ pos1[1], pos1[2] /pos1[1]])
	xy2 = np.array([window_size/2, window_size/2]) + film_dist * np.array([pos2[0]/ pos2[1], pos2[2] /pos2[1]])
	canvas.create_line(xy1[0], xy1[1], xy2[0], xy2[1], fill='blue')

# pts = []
# for i in range(1, 40):
# 	pts.append((30,30, i))

def translate(pt, x, y, z):
	return [pt[0] + x, pt[1] + y, pt[2] + z]
@jit
def rotate_x(pt, theta):
	return np.matmul(np.array(
		[[1,0,0],
		[0,cos(theta),-sin(theta)], 
		[0,sin(theta),cos(theta)]]), np.array(pt))
@jit
def rotate_y(pt, theta):
	return [cos(theta)*pt[0]+ sin(theta)*pt[2], 
	pt[1],
	 -sin(theta)*pt[0] + cos(theta)*pt[2]]
@jit
def rotate_z(pt, theta):
	return np.matmul(np.array(
		[[cos(theta),-sin(theta),0],
		[sin(theta),cos(theta),0], 
		[0,0,1]]), np.array(pt))

def get_com(dict_of_points):
	unnormed_com = None
	mass_total = 0
	for key, pt in dict_of_points.items():
		try:
			mass = pt.mass
		except:
			mass = 1
		if unnormed_com is None:
			unnormed_com = pt.pos * mass
		else:
			unnormed_com += pt.pos * mass
		mass_total += mass
	return unnormed_com / mass_total



class bunch_of_points():
	def __init__(self, dict_of_points, window_size, base_radius = 1, x_shift=0, x_rot =0, y_shift=0, y_rot =0, z_shift=0, z_rot=0):
		self.points_dict = dict_of_points
		self.window_size = window_size

		self.film_dist = window_size/2

		self.base_radius = base_radius

		self.x_shift = x_shift
		self.y_shift = y_shift
		self.z_shift = z_shift

		self.com = get_com(dict_of_points)
		self.cof = np.array([0, window_size, 0]) 

		self.rot_matrix = np.array([[1,0,0], [0,1,0], [0,0,1]])

		self.x_rot = x_rot
		self.y_rot = y_rot
		self.z_rot = z_rot

	def register_all_base_points(self):
		self.all_base_coordinates = [point.pos for point in self.points_dict.values()]
		#self.all_base_coordinates = copy.copy([point.pos for point in self.points_dict.values()])

	def update(self, points):
		self.points_dict = points
		self.register_all_base_points()

	def apply_rot_matrix(self, pt):
		return np.matmul(self.rot_matrix, pt)

	def adjust_point(self, pt):
		self.com = get_com(self.points_dict)
		return translate(
				self.apply_rot_matrix(translate(pt, -self.com[0], -self.com[1], -self.com[2])),
				 self.x_shift + self.cof[0], 
				 self.y_shift + self.cof[1], 
				 self.z_shift + self.cof[2])


	def adjust_point_old(self, pt):
		return translate(
				rotate_z(rotate_y(rotate_x(translate(pt, 0, 0, 0), self.x_rot), self.y_rot), self.z_rot),
				 self.x_shift, self.y_shift + self.center_dist, self.z_shift)

	def all_adjusted_points(self):
		pts_new = []
		for pt in self.all_base_coordinates:
			pts_new.append(self.adjust_point(pt))
		return pts_new

	def draw_all_points(self, canvas):
		for pt in self.all_adjusted_points():
			draw_pt(pt, self.base_radius, canvas, self.window_size, self.film_dist)


	def all_adjusted_lines(self):
		lines_new = []
		for key, particle in self.points_dict.items():
			main_pos = particle.pos
			for neighbor in particle.neighbors:
				neighbor_pos = self.points_dict[neighbor].pos
				half_pos = (main_pos + neighbor_pos) / 2
				lines_new.append([self.adjust_point(main_pos), self.adjust_point(half_pos)])
		return lines_new

	def draw_all_lines(self, canvas):
		for pt_pair in self.all_adjusted_lines():
			if np.linalg.norm(np.array(pt_pair[0]) - np.array(pt_pair[1])) < (self.window_size/ 4):
				draw_line(pt_pair[0], pt_pair[1], canvas, self.window_size, self.film_dist)

	def shift_x(self, amt):
		self.x_shift += amt
	def shift_y(self, amt):
		self.y_shift += amt
	def shift_z(self, amt):
		self.z_shift += amt

	def rot_x(self, amt):
		self.rot_matrix = rotate_x(self.rot_matrix, amt)
	def rot_y(self, amt):
		self.rot_matrix = rotate_y(self.rot_matrix, amt)
	def rot_z(self, amt):
		self.rot_matrix = rotate_z(self.rot_matrix, amt)

	def rot_x_old(self, amt):
		self.x_rot += amt
	def rot_y_old(self, amt):
		self.y_rot += amt
	def rot_z_old(self, amt):
		self.z_rot += amt

	def print_config(self):
		print("self.x_shift is %s" % self.x_shift)
		print("self.y_shift is %s" % self.y_shift)
		print("self.z_shift is %s" % self.z_shift)
		print("self.x_rot is %s" % self.x_rot)
		print("self.y_rot is %s" % self.y_rot)
		print("self.z_rot is %s" % self.z_rot)



class cube():
	def __init__(self, size, center_dist, x_shift=0,x_rot =0, y_shift=0, y_rot =0, z_shift=0, z_rot=0):
		self.size = size
		self.center_dist = center_dist
		self.x_shift = x_shift
		self.y_shift = y_shift
		self.z_shift = z_shift

		self.x_rot = x_rot
		self.y_rot = y_rot
		self.z_rot = z_rot

	def base_pts(self):
		return [[self.size, self.size, self.size], 
			[self.size, self.size, -self.size], 
			[self.size, -self.size, self.size], 
			[self.size, -self.size,-self.size],
			[-self.size, self.size, self.size], 
			[-self.size, self.size, -self.size], 
			[-self.size, -self.size, self.size], 
			[-self.size, -self.size, -self.size]]

	def pts(self):
		pts_new = []
		for pt in self.rot_pts():
			pts_new.append(translate(pt, self.x_shift, self.y_shift, self.z_shift))
		return pts_new

	def rot_pts(self):
		pts_new = []
		for pt in self.base_pts():
			pts_new.append(rotate_z(rotate_y(rotate_x(pt, self.x_rot), self.y_rot), self.z_rot))
		return pts_new

	def shift_x(self, amt):
		self.x_shift += amt
	def shift_y(self, amt):
		self.y_shift += amt
	def shift_z(self, amt):
		self.z_shift += amt

	def rot_x(self, amt):
		self.x_rot += amt
	def rot_y(self, amt):
		self.y_rot += amt
	def rot_z(self, amt):
		self.z_rot += amt

	def print_config(self):
		print("self.x_shift is %s" % self.x_shift)
		print("self.y_shift is %s" % self.y_shift)
		print("self.z_shift is %s" % self.z_shift)
		print("self.x_rot is %s" % self.x_rot)
		print("self.y_rot is %s" % self.y_rot)
		print("self.z_rot is %s" % self.z_rot)


	

def right(event, cube, pos_shift):
	cube.shift_x(-pos_shift)
def left(event, cube, pos_shift):
	cube.shift_x(pos_shift)
def up(event, cube, pos_shift):
	cube.shift_z(-pos_shift)
def down(event, cube, pos_shift):
	cube.shift_z(pos_shift)
def away(event, cube, pos_shift):
	cube.shift_y(-pos_shift)
def toward(event, cube, pos_shift):
	cube.shift_y(pos_shift)


def rot_x_cl(event, cube, theta_shift):
	cube.rot_x(theta_shift)
def rot_x_cn(event, cube, theta_shift):
	cube.rot_x(-theta_shift)
def rot_y_cl(event, cube, theta_shift):
	cube.rot_y(theta_shift)
def rot_y_cn(event, cube, theta_shift):
	cube.rot_y(-theta_shift)
def rot_z_cl(event, cube, theta_shift):
	cube.rot_z(theta_shift)
def rot_z_cn(event, cube, theta_shift):
	cube.rot_z(-theta_shift)

def print_configuration(event, cube):
	cube.print_config()

#canvas = tk.Canvas(root, height = window_size, width = window_size)

def bind_events(canvas, bunch, pos_shift = 0.01, theta_shift=2*np.pi / 96):
	canvas.bind("<1>", lambda event: canvas.focus_set())

	canvas.bind("w", lambda event: up(event, bunch, pos_shift))
	canvas.bind("s", lambda event: down(event, bunch, pos_shift))
	canvas.bind("a", lambda event: right(event, bunch, pos_shift))
	canvas.bind("d", lambda event: left(event, bunch, pos_shift))
	canvas.bind("q", lambda event: toward(event, bunch, pos_shift))
	canvas.bind("e", lambda event: away(event, bunch, pos_shift))

	canvas.bind("r", lambda event: rot_x_cl(event, bunch, theta_shift))
	canvas.bind("f", lambda event: rot_x_cn(event, bunch, theta_shift))
	canvas.bind("t", lambda event: rot_y_cl(event, bunch, theta_shift))
	canvas.bind("g", lambda event: rot_y_cn(event, bunch, theta_shift))
	canvas.bind("y", lambda event: rot_z_cl(event, bunch, theta_shift))
	canvas.bind("h", lambda event: rot_z_cn(event, bunch, theta_shift))

	canvas.bind("p", lambda event: print_configuration(event, bunch))

# a_particle_dict = square_string(lambda x: 100 * gaussian(x, window_size / 2, 100), number = 50)
# point_bunch = bunch_of_points(a_particle_dict, -200)
# point_bunch.register_all_base_points()


# while True:
# 	canvas.delete("all")
# 	bind_events(canvas, point_bunch)

# 	#point_bunch.draw_all_points()
# 	point_bunch.draw_all_lines()
# 	canvas.pack()
# 	root.update()