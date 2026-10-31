import pygame
import Classes
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import states
default_cursor = pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_ARROW)
motion_cursor = pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_SIZEALL)


pygame.init()
screen = pygame.display.set_mode((1080,720),DOUBLEBUF | OPENGL)
glMatrixMode(GL_PROJECTION)
glLoadIdentity()
gluOrtho2D(0,1080,720,0)
glMatrixMode(GL_MODELVIEW)
glLoadIdentity()
glEnable(GL_BLEND)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
Classes.screen = screen
clock = pygame.time.Clock()
def main():
    running = True
    dt=0.0
    level = 1
    prev = 0
    scene = 0
    rays = []
    drags = []
    shooters = []
    mats = []
    counter = 9
    players = []
    glClearColor(0.1,0.5,0.4,1.0)
    start_button = Classes.Button("SIMULATION MODE",280,510,200,50)
    start_button_2 = Classes.Button("GAME MODE",640,510,150,50)
    restart_button = Classes.Button("PLAY AGAIN",440,510,150,80)
    welcome_text = Classes.Label("WELCOME TO RAY TRACER",50,200,80)
    game_over_text = Classes.Label("GAME OVER",300,300,80)
    level_text = Classes.Label("LEVEL 1",500,10,20)
    while running:
        mouse_pos = pygame.mouse.get_pos()
        mouse_pos = Classes.Point(mouse_pos[0],mouse_pos[1])
        glClear(GL_COLOR_BUFFER_BIT)
        for event in pygame.event.get():
            if(event.type == pygame.QUIT):
                running = False
            elif(event.type == pygame.MOUSEWHEEL):
                if(scene==1):
                    for drag_test in drags:
                        if drag_test.is_close(mouse_pos):
                            if(isinstance(drag_test.drag,Classes.Arc)):
                                keys = pygame.key.get_pressed()
                                if(keys[pygame.K_r]):
                                    drag_test.drag.rad += event.y*3
                                else:
                                    drag_test.drag.start_angle = (drag_test.drag.start_angle+event.y/5)
                                    drag_test.drag.end_angle = (drag_test.drag.end_angle-event.y/5)
                            elif(isinstance(drag_test.drag,Classes.Ray)):
                                drag_test.drag.change_size(event.y)
                    for mat in mats:
                        if(mat.is_point_inside(mouse_pos)):
                            mat.change_index(event.y)
            elif(event.type == pygame.MOUSEBUTTONDOWN):
                event_pos = event.pos
                event_pos = Classes.Point(event_pos[0],event_pos[1])
                if(scene==0):
                    if(start_button.is_close(mouse_pos)):
                        scene = 1
                        states.game_mode = 1
                    elif(start_button_2.is_close(mouse_pos)):
                        scene = 1
                        states.game_mode = 2
                        for i in range(10):
                            players.append(Classes.Player())
                elif(scene==1):
                    if(event.button in (4,5,6,7)):
                        continue
                    for drag_test in drags:
                        if drag_test.is_close(event_pos):
                            if event.button == 1:
                                drag_test.dragging = True
                                break
                            elif event.button == 3:
                                drag_test.rotating = True
                                prev = [mouse_pos.x-drag_test.drag.mid.x,mouse_pos.y-drag_test.drag.mid.y]
                                break
                    else:
                        for shooter in shooters:
                            if shooter.is_close(event_pos):
                                shooter.dragging = True
                                break
                        else:
                            for mat in mats:
                                if(mat.is_point_inside(event_pos)):
                                    mat.dragging = True
                                    break
                            else:
                                for shooter in shooters:
                                    rays.append(Classes.Ray(Classes.Point(event_pos.x-shooter.mid.x,event_pos.y-shooter.mid.y),pos=shooter.mid))
                elif(scene==2):
                     if(restart_button.is_close(mouse_pos)):
                         scene=1
                         level += 1
                         level_text.change_text("LEVEL " + str(level))
                         players = players[0].next_gen(players)
            elif event.type == pygame.MOUSEMOTION:
                if(scene==1):
                    for shooter in shooters:
                        if(shooter.dragging):
                            shooter.move_to(mouse_pos)
                    for mat in mats:
                        if(mat.dragging):
                            mat.move_to(mouse_pos)
                    for drag_test in drags:
                        if drag_test.dragging:
                            drag_test.move_to(mouse_pos)
                        if drag_test.rotating:
                            angle = drag_test.angle_bet([mouse_pos.x-drag_test.drag.mid.x,mouse_pos.y-drag_test.drag.mid.y],prev)
                            drag_test.rotate(angle)
                            prev = [mouse_pos.x-drag_test.drag.mid.x,mouse_pos.y-drag_test.drag.mid.y]
            elif(event.type==pygame.MOUSEBUTTONUP):
                if(scene==1):
                    for drag_test in drags:
                        drag_test.dragging = False
                        drag_test.rotating = False
                    for shooter in shooters:
                        shooter.dragging = False
                    for mat in mats:
                        mat.dragging = False
            elif event.type == pygame.KEYDOWN:
                if(scene==1):
                    if event.key == pygame.K_f:
                        drags.append(Classes.Dragable(Classes.Ray(Classes.Point(1,0),100)))
                    elif event.key == pygame.K_g:
                        drags.append(Classes.Dragable(Classes.Arc(1.5,100)))
                    elif event.key == pygame.K_h:
                        shooters.append(Classes.Ray_Shooter())
                    elif event.key == pygame.K_j:
                        mats.append(Classes.Material(1.33))
                    elif event.key == pygame.K_q:
                        if(states.is_collision_mode):
                            states.is_collision_mode = False
                        else:
                            states.is_collision_mode = True
                    elif event.key == pygame.K_DELETE:
                        for drag in drags:
                            if(drag.is_close(mouse_pos)):
                                drags.remove(drag)
                        for shooter in shooters:
                            if(shooter.is_close(mouse_pos)):
                                shooters.remove(shooter)
                        for mat in mats:
                            if(mat.is_point_inside(mouse_pos)):
                                mats.remove(mat)
        if(scene==0):
            start_button.draw()
            start_button_2.draw()
            welcome_text.draw()

        elif(scene==1):
            if(states.game_mode==2):
                level_text.draw()
                if(counter==9):
                    for player in players:
                        if(player.is_alive):
                            player.move(rays)
                    counter = 0
                counter += 1
            for mat in mats:
                mat.draw()
            for drag in drags:
                if drag.is_close(mouse_pos):
                    pygame.mouse.set_cursor(motion_cursor)
                    break
            else:
                for shooter in shooters:
                    if shooter.is_close(mouse_pos):
                        pygame.mouse.set_cursor(motion_cursor)
                        break
                else:
                    for mat in mats:
                        if(mat.is_point_inside(mouse_pos)):
                            pygame.mouse.set_cursor(motion_cursor)
                            break
                    else:
                        pygame.mouse.set_cursor(default_cursor)
            dt = clock.tick(60)/1000.0
            rays_to_remove = []
            for ray in rays:
                if(not screen.get_rect().collidepoint(ray.mid.x,ray.mid.y)):
                    rays_to_remove.append(ray)
                    continue
                ray.draw()
                for drag_test in drags:
                    res = drag_test.is_colliding(ray)
                    if(res[0]):
                        ray.change_dir(drag_test.reflect(ray.dir,res[1]))
                for mat in mats:
                    if(mat.is_point_inside(ray.start)!=mat.is_point_inside(ray.end)):
                        ray.change_dir(mat.refract(ray))
                if(states.game_mode==2):
                    for player in players:
                        if(player.is_colliding(ray) and player.is_alive):
                            player.health -= states.damage
                            rays_to_remove.append(ray)
                            if(player.health<=0):
                                player.is_alive = False
                    else:
                        ray.move(dt)
            for ray in rays_to_remove:
                if(ray in rays):
                    rays.remove(ray)
            if(states.game_mode==2):
                if any(p.is_alive for p in players):
                    for player in players:
                        if(player.is_alive):
                            player.draw()
                else:
                    rays = []
                    drags = []
                    shooters = []
                    mats = []
                    scene = 2
            for shooter in shooters:
                shooter.draw()
            for drag in drags:
                drag.draw()
        elif scene==2:
            restart_button.draw()
            game_over_text.draw()
        pygame.display.flip()
main()
pygame.quit()