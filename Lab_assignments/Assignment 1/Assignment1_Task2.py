from OpenGL.GL import *
from OpenGL.GLUT import * 
from OpenGL.GLU import *    
import random
import time

WINDOW_WIDTH, WINDOW_HEIGHT = 800, 800
boundary_bound_max = 250
boundary_bound_min = -250
movable_point_size = 7
movable_point_speed = 0.01
froze_flag = False
blink_flag = False
last_flip_sec = 0
col_black = False
flip_time = 0.5
point_list = []
        
def convert_coordinate(x, y):

    a = x - (WINDOW_WIDTH / 2)
    b = (WINDOW_HEIGHT / 2) - y
    return a, b

def draw_point():
    glPointSize(movable_point_size)
    glBegin(GL_POINTS)
    for i in point_list:
        glColor3f(i[4],i[5],i[6])
        glVertex2f(i[0],i[1])
    glEnd()

def keyboard_listener(key, x, y):

    global froze_flag
    if key == b' ':  
        froze_flag = not froze_flag
        if froze_flag:
            print("Display is Frozen")
        else:
            print("Display is Unfrozen")
    glutPostRedisplay()

def special_key_listener(key, x, y):
 
    global movable_point_speed, froze_flag
    if froze_flag:
        return
    if key == GLUT_KEY_UP:
        movable_point_speed = min(4,movable_point_speed + 0.01)
        print("Speed increased")
    elif key == GLUT_KEY_DOWN:
        movable_point_speed = max(0.01, movable_point_speed - 0.01)
        print("Speed decreased")
    glutPostRedisplay()

def mouse_listener(button, state, x, y):

    global point_list, blink_flag, froze_flag,flip_time,col_black,last_flip_sec
    if froze_flag:
        return
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        point_x, point_y = convert_coordinate(x, y)
        color1 = random.uniform(0.25,1)
        color2 = random.uniform(0.25,1)
        color3 = random.uniform(0.25,1)
        diagonal_direction_x = random.choice([-1,1])
        diagonal_direction_y = random.choice([-1,1])
        new_point = [point_x,point_y,diagonal_direction_x,diagonal_direction_y,color1,color2,color3,color1,color2,color3,movable_point_size]
        point_list.append(new_point)
        print(f"Point is at {point_x}, {point_y}")
        
    elif button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        blink_flag = not blink_flag    
        if blink_flag:
            last_flip_sec = time.time()
            col_black = False
            print("Blinking is On")
        else:
            for i in point_list:
                i[4],i[5],i[6] = i[7],i[8],i[9]
            print("Blinking is off")
                        
    glutPostRedisplay()

def setup_projection():

    glViewport(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(-250, 250, -250, 250, 0, 1)
    glMatrixMode(GL_MODELVIEW)

def display():
    
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    setup_projection()
    draw_point()
    glutSwapBuffers()

def animate():
    global point_list, movable_point_speed,blink_flag,froze_flag,flip_time,col_black,last_flip_sec
    if froze_flag:
        glutPostRedisplay()
        return
    else:                 
        for i in point_list:
            i[0] += i[2]*movable_point_speed
            i[1] += i[3]*movable_point_speed
            if i[0] > boundary_bound_max:
                i[0] = boundary_bound_max
                i[2] *= -1
            elif i[0] < boundary_bound_min:
                i[0] = boundary_bound_min
                i[2] *= -1
            if i[1] > boundary_bound_max:
                i[1] = boundary_bound_max
                i[3] *= -1
            elif i[1] < boundary_bound_min:
                i[1] = boundary_bound_min
                i[3] *= -1
        if blink_flag:
                current_time = time.time()
                if current_time - last_flip_sec >= flip_time:
                    col_black = not col_black
                    last_flip_sec = current_time
                if col_black:
                    for i in point_list:
                        i[4],i[5],i[6] = 0,0,0
                else:
                    for i in point_list:
                        i[4],i[5],i[6]= i[7],i[8],i[9]
        else:
            for i in point_list:
                i[4],i[5],i[6]= i[7],i[8],i[9]

    glutPostRedisplay()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_RGBA)
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    glutInitWindowPosition(100, 100)
    glutCreateWindow(b"OpenGL Interactive Animation")

    glutDisplayFunc(display)
    glutIdleFunc(animate)
    glutKeyboardFunc(keyboard_listener)
    glutSpecialFunc(special_key_listener)
    glutMouseFunc(mouse_listener)
    glutMainLoop()

if __name__ == "__main__":
    main()
