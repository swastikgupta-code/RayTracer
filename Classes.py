import math
import pygame
import random
from OpenGL.GL import *
from OpenGL.GLU import *
from pygame.locals import *
import numpy as np
import states
screen = None
class Point:
    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.mag = math.sqrt(x**2+y**2)

    def add(self,point):
        x = self.x + point.x
        y = self.y + point.y
        return Point(x,y)

    def sub(self,point):
        x = self.x - point.x
        y = self.y - point.y
        return Point(x,y)

    def mul(self,num):
        x = self.x*num
        y = self.y*num
        return Point(x,y)

    def dot(self,point):
        return (self.x*point.x + self.y*point.y)

    def cross(self,point):
        return (self.x*point.y - self.y*point.x)

    def dis(self,point):
        sub = self.sub(point)
        return sub.mag

    def lerp(self,point,t):
        sub = point.sub(self)
        return (self.add(sub.mul(t)))

    def norm(self):
        return self.mul(1/self.mag)

    def toarray(self):
        return [self.x,self.y]

    def copy(self):
        return Point(self.x,self.y)
ini_pos = Point(100,360)
    
class Ray:
    def __init__(self,dir,size=10.0,pos=ini_pos,color=(0.8,0.2,0.4,1)):
        self.dir = Point(dir.x,dir.y).norm()
        self.speed = 420
        self.size = size
        self.start = Point(pos.x,pos.y)
        self.end = self.start.add(self.dir.mul(self.size))
        self.mid = self.start.add(self.end).mul(1/2)
        self.color = color

    def move(self,dt):
        change = self.dir.mul(self.speed*dt)
        self.start = self.start.add(change)
        self.end = self.end.add(change)
        self.mid = self.mid.add(change)

    def change_dir(self,dir):
        if(dir is None):
            return
        dir = Point(dir[0],dir[1])
        self.dir = dir
        self.start = self.end.copy()
        self.end = self.start.add(self.dir.mul(self.size))

    def draw(self):
        glColor4f(*self.color)
        glLineWidth(2)
        glBegin(GL_LINES)
        glVertex2f(self.start.x,self.start.y)
        glVertex2f(self.end.x,self.end.y)
        glEnd()

    def change_size(self,ds):
        rate = 3
        change = self.dir.mul((self.size+ds)/2)
        self.start = self.mid.add(change)
        self.end = self.mid.sub(change)
        self.size += ds*rate

class Arc:
    def __init__(self,angle,rad,pos=ini_pos,start=None,color=(0.7,0.5,0.1)):
        self.rad = rad
        if(start is None):
            self.start_angle = (angle/2) % (2 * math.pi)
            self.end_angle = (-angle/2) % (2 * math.pi)
        else:
            self.start_angle = start % (2*math.pi)
            self.end_angle = (start+angle) % (2*math.pi)
        self.mid = Point(pos.x,pos.y)
        self.size = rad
        self.color = color

    def draw(self,segments=60):
        step = (self.end_angle-self.start_angle)/segments
        if(step<0):
            step += (2*math.pi)/segments
        glColor3f(*self.color)
        glBegin(GL_LINE_STRIP)
        for i in range(segments+1):
            angle = (self.start_angle + i*step)%(math.pi*2)
            x= self.mid.x + self.rad*math.cos(angle)
            y= self.mid.y + self.rad*math.sin(angle)
            glVertex2f(x,y)
        glEnd()

    def is_colliding(self,ray):
        n = 20
        for t in range(0,n+1):
            t=t/n
            point = ray.start.lerp(ray.end,t)
            dis = point.dis(self.mid)
            ob = Dragable(Ray(Point(1,0),10))
            dir = point.sub(self.mid)
            di = Point(1,0)
            angle = (-ob.angle_bet(dir,di))%(2*math.pi)
            if(abs(dis-self.rad)<0.5):
               if(self.start_angle<self.end_angle and angle>self.start_angle and angle<self.end_angle):
                   return True,point
               elif(self.start_angle>self.end_angle and (angle>self.start_angle or angle<self.end_angle)):
                   return True,point
        return False,None

class Dragable:
    def __init__(self,drag):
        self.drag = drag
        self.dragging = False
        self.rotating = False

    def is_close(self,point:Point,dis=5):
        dis += self.drag.size
        dist = self.drag.mid.dis(point)
        if (dist<dis):
            return True
        else:
            return False
        
    def move_to(self,point:Point):
        mid = self.drag.mid.copy()
        if(isinstance(self.drag,Ray)):
            self.drag.start = self.drag.start.add(point.sub(mid))
            self.drag.end = self.drag.end.add(point.sub(mid))
        self.drag.mid = point.copy()

    def is_colliding(self,ray):
        if(isinstance(self.drag,Ray)):
            return self.segmentIntersect(self.drag.start.x,self.drag.start.y,self.drag.end.x,self.drag.end.y,ray.start.x,ray.start.y,ray.end.x,ray.end.y),None
        else:
            return self.drag.is_colliding(ray)
        
    def segmentIntersect(self,x1,y1,x2,y2,x3,y3,x4,y4):
        denom = (y4-y3)*(x2-x1)-(x4-x3)*(y2-y1)
        if(denom==0):
            cross = (x3-x3)*(y2-y1)-(y3-y1)*(x2-x1)
            if(cross != 0): return False
            dx = x2-x1
            dy = y2-y1
            lensq = dx*dx+dy*dy
            t3 = ((x3-x1)*dx+(y3-y1)*dy)/lensq
            t4 = ((x4-x1)*dx+(y4-y1)*dy)/lensq
            tMin = min(t3,t4)
            tMax = max(t3,t4)
            return (max(0,tMin) <= min(1,tMax))
        s = ((x4-x3)*(y1-y3)-(y4-y3)*(x1-x3))/denom
        t = ((x2-x1)*(y1-y3)-(y2-y1)*(x1-x3))/denom
        return (s>=0 and s<=1) and (t>=0 and t<=1)
    def reflect(self,dir:Point,point):
        if(isinstance(dir,Point)):
            dir1 = np.array(dir.toarray(),dtype=float)
        else:
            dir1 = np.array(dir,dtype=float)
        if(isinstance(self.drag,Ray)):
            dir2 = np.array(self.drag.dir.toarray(),dtype=float)
            nor = np.array([-dir2[1],dir2[0]],dtype=float)
        elif(isinstance(self.drag,Arc)):
            nor = np.array([self.drag.mid.x-point.x,self.drag.mid.y-point.y],dtype=float)
        nsq = np.dot(nor,nor)
        r = dir1 - 2 * np.dot(dir1,nor) / nsq * nor
        return r
    def angle_bet(self,dir,di):
        if(isinstance(dir,Point)):
            dir1 = np.array(dir.toarray(),dtype=float)
        else:
            dir1 = np.array(dir,dtype=float)
        if(isinstance(di,Point)):
            dir2 = np.array(di.toarray(),dtype=float)
        else:
            dir2 = np.array(di,dtype=float)
        nor1 = np.linalg.norm(dir1)
        nor2 = np.linalg.norm(dir2)
        cross_product = dir1[0] * dir2[1] - dir1[1] * dir2[0]
        if nor1==0 or nor2==0:
            return 0.0
        dot_product = np.dot(dir1,dir2)
        cos = np.clip(dot_product/(nor1*nor2),-1.0,1.0)
        angle_val = np.arccos(cos)
        angle_val = -1*np.arctan2(cross_product, dot_product)
        return float(angle_val)

    def rotate_point(self,angle,p1:Point,p2=None):
        if p2 is None:
            p2 = Point(0,0)
        dx = p1.sub(p2)
        dy = p1.sub()
        x = (dx * np.cos(angle) - dy * np.sin(angle)) + p2.x
        y = (dx * np.sin(angle) + dy * np.cos(angle)) + p2.y
        return Point(x,y)

    def rotate(self,angle):
        if(isinstance(self.drag,Ray)):
            new_start = self.rotate_point(angle,self.drag.start,p2=self.drag.mid)
            self.drag.end = self.rotate_point(angle,self.drag.end,p2=self.drag.mid)
            self.drag.start = new_start
            self.rotate_dir(angle)
        elif(isinstance(self.drag,Arc)):
            angle = -angle
            self.drag.start_angle = (self.drag.start_angle-angle)%(2*math.pi)
            self.drag.end_angle = (self.drag.end_angle-angle)%(2*math.pi)
            

    def rotate_dir(self,angle):
        x,y = self.drag.dir
        cos = math.cos(angle)
        sin = math.sin(angle)
        nx = x*cos-y*sin
        ny = x*sin+y*cos
        self.drag.dir = [nx,ny]

    def draw(self):
        self.drag.draw()

class Ray_Shooter(Dragable):
    def __init__(self,color=(0.9,0.1,0.3)):
        self.rad = 15
        self.mid = Point(ini_pos.x,ini_pos.y)
        self.dragging = False
        self.color = color

    def draw(self,segments=60):
        step = 2*math.pi/segments
        glColor3f(*self.color)
        glBegin(GL_TRIANGLE_FAN)
        glVertex2f(self.mid.x,self.mid.y)
        for i in range(segments+1):
            angle = i*step
            x = self.mid.x + self.rad*math.cos(angle)
            y = self.mid.y + self.rad*math.sin(angle)
            glVertex2f(x,y)
        glEnd()
        

    def is_close(self,point):
            dis = self.rad
            dist = point.dis(self.mid)
            if (dist<dis):
                return True
            else:
                return False

    def move_to(self,point):
        self.mid = point

class Material:
    def __init__(self,index,color=(0.8,0.2,0.4)):
        self.index = index
        self.surface = Arc(0.0001,50)
        self.dragging = False
        self.color = color

    def draw(self,segments=60):
        col = (self.color[0],self.color[1],self.color[2],(1-1/self.index))
        step = 2*math.pi/segments
        glColor4f(*col)
        glBegin(GL_TRIANGLE_FAN)
        glVertex2f(self.surface.mid.x,self.surface.mid.y)
        for i in range(segments+1):
            angle = i*step
            x = self.surface.mid.x + self.surface.rad*math.cos(angle)
            y = self.surface.mid.y + self.surface.rad*math.sin(angle)
            glVertex2f(x,y)
        glEnd()
        self.surface.draw()

    def change_index(self,change):
        self.index += change
        if(self.index<1):
            self.index=1

    def move_to(self,point):
        self.surface.mid = point.copy()

    def is_inside(self,ray:Ray):
        return self.is_point_inside(ray.start) or self.is_point_inside(ray.end)

    def is_point_inside(self,point):
        mid = self.surface.mid
        dis = mid.dis(point)
        if(dis<self.surface.rad):
            return True
        return False

    def refract(self,ray):
        point = self.get_collision_point(ray)
        if(point==None):
            return 
        nor = np.array((self.surface.mid.x-point.x,self.surface.mid.y-point.y))
        nor = nor/np.linalg.norm(nor)
        inc = np.array((ray.dir.x,ray.dir.y))
        inc = inc/np.linalg.norm(inc)
        cos1 = -1*np.dot(nor,inc)
        meu = self.index
        if(cos1<0):
            nor = -nor
            cos1 = -cos1
            meu = 1.0/meu
        k = 1 - (meu**2)*(1-cos1**2)
        if(k<0):
            ob = Dragable(Arc(2*math.pi,self.surface.rad))
            return ob.reflect(inc,point)
        refrac = meu*inc+(meu*cos1-math.sqrt(k))*nor
        return refrac

    def get_collision_point(self,ray):
        n = 20
        for t in range(n+1):
            t = t/n
            point = ray.start.lerp(ray.end,t)
            dis = self.surface.mid.dis(point)
            rad = self.surface.rad
            diff = abs(dis-rad)
            if(diff<0.3):
                return point.copy()
        return None
    
class Button:
    def __init__(self, text, x, y, width, height,size=24):
        if not pygame.font.get_init():
            pygame.font.init()
            
        self.font = pygame.font.SysFont("Arial", size, bold=True)
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.color = (233, 22, 100)
        self.tex_id, self.tex_w, self.tex_h = self.create_text_texture()

    def create_text_texture(self):
        surf = self.font.render(self.text, True, (255, 255, 255))
        w, h = surf.get_size()
        data = pygame.image.tobytes(surf, "RGBA", True)

        tex_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, data)
        glBindTexture(GL_TEXTURE_2D, 0)

        return tex_id, w, h

    def is_close(self, point):
        return self.rect.collidepoint(point.x, point.y)

    def draw(self):
        while glGetError() != GL_NO_ERROR:
            pass
        glColor3f(self.color[0] / 255.0, self.color[1] / 255.0, self.color[2] / 255.0)
        glBegin(GL_QUADS)
        glVertex2f(self.rect.x, self.rect.y)
        glVertex2f(self.rect.x + self.rect.width, self.rect.y)
        glVertex2f(self.rect.x + self.rect.width, self.rect.y + self.rect.height)
        glVertex2f(self.rect.x, self.rect.y + self.rect.height)
        glEnd()
        text_x = self.rect.x + (self.rect.width - self.tex_w) / 2.0
        text_y = self.rect.y + (self.rect.height - self.tex_h) / 2.0

        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.tex_id)
        glColor4f(1.0, 1.0, 1.0, 1.0)

        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 1.0); glVertex2f(text_x, text_y)
        glTexCoord2f(1.0, 1.0); glVertex2f(text_x + self.tex_w, text_y)
        glTexCoord2f(1.0, 0.0); glVertex2f(text_x + self.tex_w, text_y + self.tex_h)
        glTexCoord2f(0.0, 0.0); glVertex2f(text_x, text_y + self.tex_h)
        glEnd()

        glBindTexture(GL_TEXTURE_2D, 0)
        glDisable(GL_TEXTURE_2D)
class Label:
    def __init__(self,text,x,y,size,color=(1,1,1)):
        if not pygame.font.get_init():
            pygame.font.init()
            
        self.font = pygame.font.SysFont("Arial", size, bold=True)
        self.text = text
        self.color = color
        self.pos = Point(x,y)
        self.tex_id, self.tex_w, self.tex_h = self.create_text_texture()

    def create_text_texture(self):
        surf = self.font.render(self.text, True, (255, 255, 255))
        w, h = surf.get_size()
        data = pygame.image.tobytes(surf, "RGBA", True)

        tex_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, data)
        glBindTexture(GL_TEXTURE_2D, 0)
        
        return tex_id,w,h

    def draw(self):
        while glGetError() != GL_NO_ERROR:
            pass
        text_x = self.pos.x
        text_y = self.pos.y

        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.tex_id)
        glColor3f(*self.color)

        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 1.0); glVertex2f(text_x, text_y)
        glTexCoord2f(1.0, 1.0); glVertex2f(text_x + self.tex_w, text_y)
        glTexCoord2f(1.0, 0.0); glVertex2f(text_x + self.tex_w, text_y + self.tex_h)
        glTexCoord2f(0.0, 0.0); glVertex2f(text_x, text_y + self.tex_h)
        glEnd()

        glBindTexture(GL_TEXTURE_2D, 0)
        glDisable(GL_TEXTURE_2D)

class Player:
    def __init__(self,pos=None,col=(23,50,100)):
        if(pos is None):
            pos=(random.uniform(0,1080),random.uniform(0,720))
        self.pos = Point(pos[0],pos[1])
        self.step = 4
        self.color = col
        self.health = states.max_player_health
        self.collider = Capsule(52,23,self.pos.add(Point(0,8)))
        self.brain = Brain(8,10,2)
        self.fitness = 0
        self.is_alive = True

    def format_input(self,rays,n=60):
        inputs = []
        max_ray_dis = 500
        for ray in rays:
            dist = 10000
            for i in range(n+1):
                t = i/n
                point = ray.start.lerp(ray.end,t)
                dis = point.dis(self.pos)
                if(dist>dis):
                    dist = dis
            dis = max(0,1-dist/max_ray_dis)
            inputs.append(dis)
        inputs.sort(reverse=True)
        inputs = inputs[:8]
        while(len(inputs)<8):
            inputs.append(0)
        return inputs


    def move(self,rays):
        move = [0,0]
        inputs = self.format_input(rays)
        thought = self.brain.predict(inputs)
        move[0] = thought[0]
        move[1] = thought[1]
        mag = math.sqrt(move[0]**2+move[1]**2)
        if(mag==0):
            return
        move[0] = move[0]/mag*self.step
        move[1] = move[1]/mag*self.step
        target_x = self.pos.x + move[0]
        target_y = self.pos.y + move[1]
        target_x = max(20,min(target_x,1080-20))
        target_y = max(20,min(target_y,720-20))
        actual_move = [target_x-self.pos.x,target_y-self.pos.y]
        self.pos.x += actual_move[0]
        self.pos.y += actual_move[1]
        self.collider.move(actual_move)
 
    def next_gen(self,dead_players):
        dead_players.sort(key=lambda p:p.fitness,reverse=True)
        champ = dead_players[0]
        new_pop = []
        champ_clone = Player()
        champ_clone.brain = champ.brain.clone()
        new_pop.append(champ_clone)

        for i in range(9):
            child = Player()
            child.brain = champ.brain.clone()
            child.brain.mutate()
            new_pop.append(child)

        return new_pop

    def is_colliding(self,line:Ray,n = 60):
        for i in range(n+1):
            t = i/n
            point = line.start.lerp(line.end,t)
            if(self.collider.is_colliding(point)):
                return True
        return False

    def draw(self,segments=60):
        scale = 1
        torso_width = 7*scale
        inner_torso_width = 3*scale
        torso_height = 10*scale
        face_rad = 5*scale
        head_cen = [self.pos.x,self.pos.y-torso_height-face_rad]
        sh_angle = 30/180*math.pi
        sh_width = 3*scale
        leg_width = 6*scale
        leg_height = 15*scale
        step = 2*math.pi/segments
        glBegin(GL_QUADS)
        #torso
        glColor3f(0.48, 0.04, 0.09)
        glVertex2f(self.pos.x-torso_width,self.pos.y-torso_height)
        glVertex2f(self.pos.x+torso_width,self.pos.y-torso_height)
        glVertex2f(self.pos.x+torso_width,self.pos.y+torso_height)
        glVertex2f(self.pos.x-torso_width,self.pos.y+torso_height)
        glEnd()
        glBegin(GL_TRIANGLE_FAN)
        #head
        glColor3f(0.95, 0.76, 0.64)
        glVertex2f(head_cen[0],head_cen[1])
        for i in range(segments+1):
            angle = i*step
            x = head_cen[0]+math.cos(angle)*face_rad
            y = head_cen[1]+math.sin(angle)*face_rad
            glVertex2f(x,y)
        glEnd()
        glBegin(GL_QUADS)
        #shoulders
        glColor3f(0.48, 0.04, 0.09)

        glVertex2f(self.pos.x+torso_width,self.pos.y-torso_height)
        glVertex2f(self.pos.x+torso_width+sh_width,self.pos.y-torso_height+2)
        glVertex2f(self.pos.x+torso_width+sh_width,self.pos.y+torso_height-2)
        glVertex2f(self.pos.x+torso_width+1,self.pos.y+torso_height-2)

        glVertex2f(self.pos.x-torso_width,self.pos.y-torso_height)
        glVertex2f(self.pos.x-torso_width-sh_width,self.pos.y-torso_height+2)
        glVertex2f(self.pos.x-torso_width-sh_width,self.pos.y+torso_height-2)
        glVertex2f(self.pos.x-torso_width-1,self.pos.y+torso_height-2)
        #hands
        glColor3f(0.95, 0.76, 0.64)

        glVertex2f(self.pos.x-torso_width-sh_width,self.pos.y+torso_height-2)
        glVertex2f(self.pos.x-torso_width-1,self.pos.y+torso_height-2)
        glVertex2f(self.pos.x-torso_width-1,self.pos.y+torso_height)
        glVertex2f(self.pos.x-torso_width-sh_width,self.pos.y+torso_height)

        glVertex2f(self.pos.x+torso_width+sh_width,self.pos.y+torso_height-2)
        glVertex2f(self.pos.x+torso_width+1,self.pos.y+torso_height-2)
        glVertex2f(self.pos.x+torso_width+1,self.pos.y+torso_height)
        glVertex2f(self.pos.x+torso_width+sh_width,self.pos.y+torso_height)
        #leg
        glColor3f(0.11, 0.12, 0.15)

        glVertex2f(self.pos.x+torso_width,self.pos.y+torso_height)
        glVertex2f(self.pos.x,self.pos.y+torso_height)
        glVertex2f(self.pos.x+1,self.pos.y+torso_height+leg_height)
        glVertex2f(self.pos.x+1+leg_width,self.pos.y+torso_height+leg_height)

        glVertex2f(self.pos.x-torso_width,self.pos.y+torso_height)
        glVertex2f(self.pos.x,self.pos.y+torso_height)
        glVertex2f(self.pos.x-1,self.pos.y+torso_height+leg_height)
        glVertex2f(self.pos.x-1-leg_width,self.pos.y+torso_height+leg_height)
        #feet
        glColor3f(0.24, 0.16, 0.12)

        glVertex2f(self.pos.x+1,self.pos.y+torso_height+leg_height)
        glVertex2f(self.pos.x+1+leg_width,self.pos.y+torso_height+leg_height)
        glVertex2f(self.pos.x+1+leg_width,self.pos.y+torso_height+leg_height+4)
        glVertex2f(self.pos.x+1,self.pos.y+torso_height+leg_height+4)

        glVertex2f(self.pos.x-1,self.pos.y+torso_height+leg_height)
        glVertex2f(self.pos.x-1-leg_width,self.pos.y+torso_height+leg_height)
        glVertex2f(self.pos.x-1-leg_width,self.pos.y+torso_height+leg_height+4)
        glVertex2f(self.pos.x-1,self.pos.y+torso_height+leg_height+4)
        #stomach
        glColor3f(0,0,0)

        glVertex2f(self.pos.x-inner_torso_width,self.pos.y-torso_height)
        glVertex2f(self.pos.x+inner_torso_width,self.pos.y-torso_height)
        glVertex2f(self.pos.x+inner_torso_width,self.pos.y+torso_height)
        glVertex2f(self.pos.x-inner_torso_width,self.pos.y+torso_height)

        glEnd()
        if(states.is_collision_mode):
            self.collider.draw()

class Capsule:

    def __init__(self,height,rad,pos:Point):
        self.height = height
        self.rad = rad
        self.pos = Point(pos.x,pos.y)
        self.top = self.pos.sub(Point(0,self.height/2))
        self.bottom = self.pos.add(Point(0,self.height/2))

    def is_colliding(self,point:Point):
        if(point.y<(self.top.y-self.rad) or point.y>(self.bottom.y+self.rad)):
            return False
        closest_point = Point(self.pos.x,point.y)
        dis = closest_point.dis(point)
        if(dis>self.rad):
            return False
        return True

    def move(self,move):
        self.top.x += move[0]
        self.top.y += move[1]
        self.bottom.x += move[0]
        self.bottom.y += move[1]
        self.pos.x += move[0]
        self.pos.y += move[1]

    def draw(self,segments=60):
        glColor4f(0,0.1,0.4,0.3)
        glBegin(GL_QUADS)
        glVertex2f(self.pos.x+self.rad,self.pos.y+self.height/2)
        glVertex2f(self.pos.x+self.rad,self.pos.y-self.height/2)
        glVertex2f(self.pos.x-self.rad,self.pos.y-self.height/2)
        glVertex2f(self.pos.x-self.rad,self.pos.y+self.height/2)
        glEnd()
        glBegin(GL_TRIANGLE_FAN)
        step = math.pi/segments
        glVertex2f(self.pos.x,self.pos.y+self.height/2)
        for i in range(segments+1):
            angle = i*step
            x = self.pos.x + self.rad*math.cos(angle)
            y = self.pos.y + self.height/2 + self.rad*math.sin(angle)
            glVertex2f(x,y)
        glEnd()
        glBegin(GL_TRIANGLE_FAN)
        glVertex2f(self.pos.x,self.pos.y-self.height/2)
        for i in range(segments+1):
            angle = math.pi + i*step
            x = self.pos.x + self.rad*math.cos(angle)
            y = self.pos.y - self.height/2 + self.rad*math.sin(angle)
            glVertex2f(x,y)
        glEnd()

class Brain:
    def __init__(self,input_nodes,hidden_nodes,output_nodes):
        self.weights_ih = np.random.randn(input_nodes,hidden_nodes)
        self.weights_ho = np.random.randn(hidden_nodes,output_nodes)

    def predict(self,inputs):
        hidden = np.dot(inputs,self.weights_ih)
        hidden = np.tanh(hidden)

        output = np.dot(hidden,self.weights_ho)
        output = np.tanh(output)

        return output

    def clone(self):
        new_brain = Brain(self.weights_ih.shape[0],self.weights_ih.shape[1],self.weights_ho.shape[1])
        new_brain.weights_ih = np.copy(self.weights_ih)
        new_brain.weights_ho = np.copy(self.weights_ho)
        return new_brain

    def mutate(self,mutation_rate = 0.1):
        self.weights_ih += np.random.randn(*self.weights_ih.shape)*mutation_rate
        self.weights_ho += np.random.randn(*self.weights_ho.shape)*mutation_rate