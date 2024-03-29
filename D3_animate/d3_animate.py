import tkinter as tk
import sys, math
import pygame

run= False

sensitivity = 100 #Low Number means high sensitivity

def rotate2d(pos, rad): x, y=pos; s,c = math.sin(rad), math.cos(rad); return x*c-y*s, y*c+x*s

class Cam:
	def __init__(self, pos=(0,0,0), rot = (0,0)):
		self.pos = list(pos)
		self.rot = list(rot)

	def events(self, event):
		if event.type == pygame.MOUSEMOTION:
			x, y = event.rel
			x/=sensitivity; y/=sensitivity;
			self.rot[0]+=y; self.rot[1]+=x;

	def update(self, dt, key):
		s = dt * 10

		x, y = s*math.sin(self.rot[0]), s*math.cos(self.rot[1])

		if key[pygame.K_w]: self.pos[0]+=x; self.pos[2]+=y
		if key[pygame.K_s]: self.pos[0]-=x; self.pos[2]-=y
		if key[pygame.K_a]: self.pos[0]-=y; self.pos[2]+=x
		if key[pygame.K_a]: self.pos[0]+=y; self.pos[2]-=x

if run:
	pygame.init()
	w, h = 400, 400; cx, cy = w//2, h//2
	screen = pygame.display.set_mode((w, h))
	clock = pygame.time.Clock()

	distance = 200

	verts = (-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1), (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1) 
	edges = (0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5, 6), (6, 7), (7, 4), (0, 4), (1, 5), (2, 6), (7, 3) 

	cam = Cam((0,0,-5))

	pygame.event.get(); pygame.mouse.get_rel()
	pygame.mouse.set_visible(1); pygame.event.set_grab(1)

	while True:
		dt = clock.tick()/1000

		for event in pygame.event.get():
				if event.type == pygame.QUIT: pygame.quit(); sys.exit()
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_ESCAPE: pygame.quit(); sys.exit()
				cam.events(event)

		screen.fill((255, 255, 255))

		# for x, y, z in verts:
		# 	z += 5

		# 	f = distance/z

		# 	x, y = x*f, y*f

		# 	pygame.draw.circle(screen, (0,0,0), (cx + int(x), cy + int(y)), 6)

		for edge in edges:
			points = []
			for x,y,z in (verts[edge[0]], verts[edge[1]]):

				x -= cam.pos[0]
				y -= cam.pos[1]
				z -= cam.pos[2]

				x, z = rotate2d((x, z), cam.rot[1])
				y, z = rotate2d((y, z), cam.rot[0])

				f = distance/z
				x, y = x*f, y*f
				points += [(cx+int(x), cy+int(y))]
			pygame.draw.line(screen, (0,0,255), points[0], points[1], 1)


		pygame.display.flip()
		key = pygame.key.get_pressed()
		cam.update(dt, key)

