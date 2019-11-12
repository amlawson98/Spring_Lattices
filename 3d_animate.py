import pygame, sys, os, math
 
 
def lock_mouse(): pygame.event.get(); pygame.mouse.get_rel(); pygame.mouse.set_visible(0); pygame.event.set_grab(1)
 
 
def rotate2d(pos,rot): x,y = pos; s,c = rot; return x*c-y*s,y*c+x*s
 
 
class Cam:
    def __init__(self,pos=(0,0,0),rot=(0,0)):
        self.pos = list(pos)
        self.rot = list(rot)
        self.update_rot()
 
    def update_rot(self):
        self.rotX = math.sin(self.rot[0]),math.cos(self.rot[0])
        self.rotY = math.sin(self.rot[1]),math.cos(self.rot[1])
 
    def events(self,event):
        if event.type == pygame.MOUSEMOTION:
            x,y = event.rel; x/=200; y/=200
            self.rot[0]+=y; self.rot[1]+=x
            self.update_rot()
 
    def update(self,dt,key):
        s = dt*10
 
        if key[pygame.K_LSHIFT]: self.pos[1]+=s
        if key[pygame.K_SPACE]: self.pos[1]-=s
 
        x,y = s*math.sin(self.rot[1]),s*math.cos(self.rot[1])
        if key[pygame.K_w]: self.pos[0]+=x; self.pos[2]+=y
        if key[pygame.K_s]: self.pos[0]-=x; self.pos[2]-=y
        if key[pygame.K_a]: self.pos[0]-=y; self.pos[2]+=x
        if key[pygame.K_d]: self.pos[0]+=y; self.pos[2]-=x
 
 
class Cube:
    vertices = (-0.5,-0.5,-0.5),(0.5,-0.5,-0.5),(0.5,0.5,-0.5),(-0.5,0.5,-0.5),(-0.5,-0.5,0.5),(0.5,-0.5,0.5),(0.5,0.5,0.5),(-0.5,0.5,0.5)
    faces = (0,1,2,3),(4,5,6,7),(0,1,5,4),(2,3,7,6),(0,3,7,4),(1,2,6,5)
    colors = (255,0,0),(255,128,0),(255,255,0),(255,255,255),(0,0,255),(0,255,0)
    def __init__(self,pos=(0,0,0)): x,y,z=pos; self.verts=[(x+X,y+Y,z+Z) for X,Y,Z in self.vertices]
 
# dont need to check if z is 0 (we clip z at min value)
def get2D(v): return cx+int(v[0]/v[2]*projX),cy+int(v[1]/v[2]*projY)
 
def get3D(v):
    x,y,z = v[0]-cam.pos[0], v[1]-cam.pos[1], v[2]-cam.pos[2]
    x,z = rotate2d((x,z),cam.rotY)
    y,z = rotate2d((y,z),cam.rotX)
    return x,y,z
 
def getZ(A,B,newZ):
    if B[2]==A[2] or newZ<A[2] or newZ>B[2]: return None
    dx,dy,dz = B[0]-A[0],B[1]-A[1],B[2]-A[2]
    i=(newZ-A[2])/dz
    return A[0]+dx*i,A[1]+dy*i,newZ
 
minZ = 1

def main():
    global projX,projY,cx,cy,cam,minZ
    pygame.init()
    w,h = 800,600; cx,cy = w//2,h//2
   
    fov = 90/180*math.pi; half_fov = fov/2
    half_w,half_h = w/2,h/2
    projY = half_h/math.tan(half_fov)
    projX = half_w/math.tan(half_fov)/(w/h)
   
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    pygame.display.set_caption('3D Graphics')
    screen = pygame.display.set_mode((w,h))
    fpsclock = pygame.time.Clock()
 
    lock_mouse()
    cam = Cam((0,0,-5))
 
    pacman_points = [(0,0),(1,0),(2,0),(3,0),(4,0),(5,0),(6,0),(7,0),(8,0),(9,0),(10,0),(11,0),(12,0),(13,0),(14,0),(15,0),(16,0),(17,0),(18,0),(19,0),(20,0),(21,0),(22,0),(23,0),(24,0),(25,0),(26,0),(27,0),(0,1),(13,1),(14,1),(27,1),(0,2),(2,2),(3,2),(4,2),(5,2),(7,2),(8,2),(9,2),(10,2),(11,2),(13,2),(14,2),(16,2),(17,2),(18,2),(19,2),(20,2),(22,2),(23,2),(24,2),(25,2),(27,2),(0,3),(2,3),(3,3),(4,3),(5,3),(7,3),(8,3),(9,3),(10,3),(11,3),(13,3),(14,3),(16,3),(17,3),(18,3),(19,3),(20,3),(22,3),(23,3),(24,3),(25,3),(27,3),(0,4),(2,4),(3,4),(4,4),(5,4),(7,4),(8,4),(9,4),(10,4),(11,4),(13,4),(14,4),(16,4),(17,4),(18,4),(19,4),(20,4),(22,4),(23,4),(24,4),(25,4),(27,4),(0,5),(27,5),(0,6),(2,6),(3,6),(4,6),(5,6),(7,6),(8,6),(10,6),(11,6),(12,6),(13,6),(14,6),(15,6),(16,6),(17,6),(19,6),(20,6),(22,6),(23,6),(24,6),(25,6),(27,6),(0,7),(2,7),(3,7),(4,7),(5,7),(7,7),(8,7),(10,7),(11,7),(12,7),(13,7),(14,7),(15,7),(16,7),(17,7),(19,7),(20,7),(22,7),(23,7),(24,7),(25,7),(27,7),(0,8),(7,8),(8,8),(13,8),(14,8),(19,8),(20,8),(27,8),(0,9),(1,9),(2,9),(3,9),(4,9),(5,9),(7,9),(8,9),(9,9),(10,9),(11,9),(13,9),(14,9),(16,9),(17,9),(18,9),(19,9),(20,9),(22,9),(23,9),(24,9),(25,9),(26,9),(27,9),(5,10),(7,10),(8,10),(9,10),(10,10),(11,10),(13,10),(14,10),(16,10),(17,10),(18,10),(19,10),(20,10),(22,10),(5,11),(7,11),(8,11),(19,11),(20,11),(22,11),(5,12),(7,12),(8,12),(10,12),(11,12),(12,12),(15,12),(16,12),(17,12),(19,12),(20,12),(22,12),(0,13),(1,13),(2,13),(3,13),(4,13),(5,13),(7,13),(8,13),(10,13),(17,13),(19,13),(20,13),(22,13),(23,13),(24,13),(25,13),(26,13),(27,13),(10,14),(17,14),(0,15),(1,15),(2,15),(3,15),(4,15),(5,15),(7,15),(8,15),(10,15),(17,15),(19,15),(20,15),(22,15),(23,15),(24,15),(25,15),(26,15),(27,15),(5,16),(7,16),(8,16),(10,16),(11,16),(12,16),(13,16),(14,16),(15,16),(16,16),(17,16),(19,16),(20,16),(22,16),(5,17),(7,17),(8,17),(19,17),(20,17),(22,17),(5,18),(7,18),(8,18),(10,18),(11,18),(12,18),(13,18),(14,18),(15,18),(16,18),(17,18),(19,18),(20,18),(22,18),(0,19),(1,19),(2,19),(3,19),(4,19),(5,19),(7,19),(8,19),(10,19),(11,19),(12,19),(13,19),(14,19),(15,19),(16,19),(17,19),(19,19),(20,19),(22,19),(23,19),(24,19),(25,19),(26,19),(27,19),(0,20),(13,20),(14,20),(27,20),(0,21),(2,21),(3,21),(4,21),(5,21),(7,21),(8,21),(9,21),(10,21),(11,21),(13,21),(14,21),(16,21),(17,21),(18,21),(19,21),(20,21),(22,21),(23,21),(24,21),(25,21),(27,21),(0,22),(2,22),(3,22),(4,22),(5,22),(7,22),(8,22),(9,22),(10,22),(11,22),(13,22),(14,22),(16,22),(17,22),(18,22),(19,22),(20,22),(22,22),(23,22),(24,22),(25,22),(27,22),(0,23),(4,23),(5,23),(22,23),(23,23),(27,23),(0,24),(1,24),(2,24),(4,24),(5,24),(7,24),(8,24),(10,24),(11,24),(12,24),(13,24),(14,24),(15,24),(16,24),(17,24),(19,24),(20,24),(22,24),(23,24),(25,24),(26,24),(27,24),(0,25),(1,25),(2,25),(4,25),(5,25),(7,25),(8,25),(10,25),(11,25),(12,25),(13,25),(14,25),(15,25),(16,25),(17,25),(19,25),(20,25),(22,25),(23,25),(25,25),(26,25),(27,25),(0,26),(7,26),(8,26),(13,26),(14,26),(19,26),(20,26),(27,26),(0,27),(2,27),(3,27),(4,27),(5,27),(6,27),(7,27),(8,27),(9,27),(10,27),(11,27),(13,27),(14,27),(16,27),(17,27),(18,27),(19,27),(20,27),(21,27),(22,27),(23,27),(24,27),(25,27),(27,27),(0,28),(2,28),(3,28),(4,28),(5,28),(6,28),(7,28),(8,28),(9,28),(10,28),(11,28),(13,28),(14,28),(16,28),(17,28),(18,28),(19,28),(20,28),(21,28),(22,28),(23,28),(24,28),(25,28),(27,28),(0,29),(27,29),(0,30),(1,30),(2,30),(3,30),(4,30),(5,30),(6,30),(7,30),(8,30),(9,30),(10,30),(11,30),(12,30),(13,30),(14,30),(15,30),(16,30),(17,30),(18,30),(19,30),(20,30),(21,30),(22,30),(23,30),(24,30),(25,30),(26,30),(27,30)]
    cubes = [Cube((x,0,z)) for x,z in pacman_points]
 
    while True:
        dt = fpsclock.tick()/1000
        pygame.display.set_caption('3D Graphics - FPS: %.2f'%fpsclock.get_fps())
 
        key = pygame.key.get_pressed()
        cam.update(dt,key)
 
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F4 and key[pygame.K_LALT]: pygame.quit(); sys.exit()
                elif event.key == pygame.K_ESCAPE: pygame.quit(); sys.exit()
                elif event.key == pygame.K_0: minZ = 0.4
                elif event.key == pygame.K_1: minZ = 1
                elif event.key == pygame.K_2: minZ = 2
                elif event.key == pygame.K_9: minZ = 9
                elif event.key == pygame.K_MINUS: minZ=max(0.4,minZ-1)
                elif event.key == pygame.K_EQUALS: minZ+=1
            cam.events(event)
 
        screen.fill((128,128,255))
 
        face_list = []; face_color = []; depth = [] # store faces (polygons / colors / depth for sorting)
 
        for obj in cubes: # go through all models
 
            vert_list = [get3D(v) for v in obj.verts] # get translated 3d vertices for entire model
 
            for f in range(len(obj.faces)): # go through faces (build from indexing)
 
                verts = [vert_list[i] for i in obj.faces[f]] # get verts for poly
 
                # clip verts
 
                i=0
                while i<len(verts):
                    if verts[i][2]<minZ: # behind camera
                        sides=[]
                        l = verts[i-1]
                        r = verts[(i+1)%len(verts)]
                        if l[2]>=minZ:sides+=[getZ(verts[i],l,minZ)]
                        if r[2]>=minZ:sides+=[getZ(verts[i],r,minZ)]
                        verts = verts[:i]+sides+verts[i+1:]
                        i+=len(sides)-1;
                    i+=1
 
                if len(verts)>2:
                    # add face (gen 2d poly / get color / average face depth)
                    face_list += [[get2D(v) for v in verts]]
                    face_color += [obj.colors[f]]
                    depth += [sum(sum(v[i]/len(verts) for v in verts)**2 for i in range(3))]
 
 
        # sort and render all polygons
        order = sorted(range(len(face_list)),key=lambda i:depth[i],reverse=1)
        for i in order:
            try: pygame.draw.polygon(screen,face_color[i],face_list[i])
            except: pass
 
        pygame.display.flip()
 
 
 
if __name__ == '__main__':
    main()