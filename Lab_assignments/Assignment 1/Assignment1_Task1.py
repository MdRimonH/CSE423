
from OpenGL.GL import *     
from OpenGL.GLUT import *  
from OpenGL.GLU import *   
import math 
import random

rain_count = 500
rain_speed = 10
base_speed = 1
positions = []
bending = 0.0
step = 2
max_bending_possible = 10
sky = 0.3
sky_color_step = 0.1
rain_color = 0.5
WINDOW_WIDTH, WINDOW_HEIGHT = 800, 800
x, y = 250, 250

def convert_coordinate(x, y):
    a = x - (WINDOW_WIDTH / 2)
    b = (WINDOW_HEIGHT / 2) - y
    return a, b

def keyboard_listener(key, x, y):
    global sky
    if key == b'd':
        sky = min(1, sky+sky_color_step)
        print("The Sun is rising")
    elif key == b'n':
        sky = max(0, sky - sky_color_step)
        print("Night is coming")
    glutPostRedisplay()

def special_key_listener(key, x, y):
    global bending
    if key == GLUT_KEY_RIGHT:
        bending =min(max_bending_possible,bending+step) 
        print("Rain is bending towards right direction")
    elif key == GLUT_KEY_LEFT:
        bending = max(-max_bending_possible, bending-step)
        print("Rain is bending towards Left direction")
    glutPostRedisplay()

def mouse_listener(button, state, x, y):
    global ball_x, ball_y, new_point
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        ball_x, ball_y = convert_coordinate(x, y)
        print(f"Ball moved to ({ball_x}, {ball_y})")

    elif button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        new_point = convert_coordinate(x, y)
        print(f"New point created at {new_point}")

def house():
       
    glBegin(GL_TRIANGLES)  
    glColor3f(sky,sky,sky)
        
    glVertex2d(250,250)
    glVertex2d(-250,140)
    glVertex2d(250,140)  
    glVertex2d(250,250)
    glVertex2d(-250,250)
    glVertex2d(-250,140)
    
    glEnd()
    
    glBegin(GL_TRIANGLES)
    glColor3f(0.5,0.35,0.05)
        
    glVertex2d(250,140)
    glVertex2d(-250,-250)
    glVertex2d(250,-250)  
    glVertex2d(250,140)
    glVertex2d(-250,140)
    glVertex2d(-250,-250)
    
    glEnd()
    
    glBegin(GL_TRIANGLES) 
    glColor3f(0,0.9,0)
        
    glVertex2d(-237.5,125)
    glVertex2d(-250,70)
    glVertex2d(-225,70)
    glVertex2d(-212.5,125)
    glVertex2d(-225,70)
    glVertex2d(-200,70)
    glVertex2d(-187.5,125)
    glVertex2d(-200,70)
    glVertex2d(-175,70)
    glVertex2d(-162.5,125)
    glVertex2d(-175,70)
    glVertex2d(-150,70)
    glVertex2d(-137.5,125)
    glVertex2d(-150,70)
    glVertex2d(-125,70)
    glVertex2d(-112.5,125)
    glVertex2d(-125,70)
    glVertex2d(-100,70)
    glVertex2d(-87.5,125)
    glVertex2d(-100,70)
    glVertex2d(-75,70)
    glVertex2d(-62.5,125)
    glVertex2d(-75,70)
    glVertex2d(-50,70)
    glVertex2d(-37.5,125)
    glVertex2d(-50,70)
    glVertex2d(-25,70)
    glVertex2d(-12.5,125)
    glVertex2d(-25,70)
    glVertex2d(0,70)
    glVertex2d(12.5,125)
    glVertex2d(0,70)
    glVertex2d(25,70)
    glVertex2d(37.5,125)
    glVertex2d(25,70)
    glVertex2d(50,70)
    glVertex2d(62.5,125)
    glVertex2d(50,70)
    glVertex2d(75,70)
    glVertex2d(87.5,125)
    glVertex2d(75,70)
    glVertex2d(100,70)
    glVertex2d(112.5,125)
    glVertex2d(100,70)
    glVertex2d(125,70)
    glVertex2d(137.5,125)
    glVertex2d(125,70)
    glVertex2d(150,70)
    glVertex2d(162.5,125)
    glVertex2d(150,70)
    glVertex2d(175,70)
    glVertex2d(187.5,125)
    glVertex2d(175,70)
    glVertex2d(200,70)
    glVertex2d(212.5,125)
    glVertex2d(200,70)
    glVertex2d(225,70)
    glVertex2d(237.5,125)
    glVertex2d(225,70)
    glVertex2d(250,70)
    glVertex2d(262.5,125)
    glVertex2d(250,70)
    glVertex2d(275,70) 
    
    glEnd()
     
    glBegin(GL_TRIANGLES) 
    glColor3f(1,0.65,0.5)
        
    glVertex2d(100, 30)
    glVertex2d(-100, -30)
    glVertex2d(100, -30)  
    glVertex2d(100, 30)
    glVertex2d(-100, 30)
    glVertex2d(-100, -30)
    
    glEnd()
    
    glBegin(GL_TRIANGLES) 
    glColor3f(1,1,1)
    
    glVertex2d(80, 80)
    glVertex2d(-80, 30)
    glVertex2d(80, 30)  
    glVertex2d(80, 80)
    glVertex2d(-80, 80)
    glVertex2d(-80, 30)
    
    glEnd()
      
    glBegin(GL_TRIANGLES)
    glColor3f(1,1,0.5)
    
    glVertex2d(0,150)
    glVertex2d(-130,80)
    glVertex2d(130,80)
    glEnd()
    
    glBegin(GL_TRIANGLES) 
    glColor3f(0.59,0.44,0.20)
        
    glVertex2d(15,60)
    glVertex2d(-15,30)
    glVertex2d(15,30)  
    glVertex2d(15,60)
    glVertex2d(-15,60)
    glVertex2d(-15,30)
    
    glEnd()
    
    glPointSize(5) 
    glBegin(GL_POINTS) 
    glColor3f(0,0,0)  
    glVertex2f(10,45) 
           
    glEnd() 
    
    glBegin(GL_TRIANGLES) 
    glColor3f(0,0,0)
        
    glVertex2d(55,60)
    glVertex2d(35,40)
    glVertex2d(55,40)  
    glVertex2d(55,60)
    glVertex2d(35,60)
    glVertex2d(35,40)      
    glVertex2d(-55,60)
    glVertex2d(-35,40)
    glVertex2d(-55,40)  
    glVertex2d(-55,60)
    glVertex2d(-35,60)
    glVertex2d(-35,40)
    
    glEnd()
    
    glBegin(GL_LINES)
    glColor3f(1,1,1)
    glVertex2d(35,60)
    glVertex2d(35,40)
    glVertex2d(40,60)
    glVertex2d(40,40)
    glVertex2d(45,60)
    glVertex2d(45,40)
    glVertex2d(50,60)
    glVertex2d(50,40)
    glVertex2d(-35,60)
    glVertex2d(-35,40)
    glVertex2d(-40,60)
    glVertex2d(-40,40)
    glVertex2d(-45,60)
    glVertex2d(-45,40)
    glVertex2d(-50,60)
    glVertex2d(-50,40)
    glEnd()


def rain():
    global positions
    for i in range(rain_count):
        a = random.uniform(-250,250)
        b = random.uniform(-250,250)
        positions.append([a,b])
     
def rain_drawing():
    global positions,bending
    glColor3f(0.5,0.5,1)
    glLineWidth(1)
    glBegin(GL_LINES)
    for i,j in positions:
        glVertex2d(i,j)
        glVertex2d(i+bending,j-8)
    glEnd()
    
def setup_projection():
    """Defines a 2D orthographic coordinate system."""
    glViewport(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT) #xmin ymin, w, h
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(-250, 250, -250, 250, 0, 1)
    glMatrixMode(GL_MODELVIEW)

def display():
    """Main display callback for rendering each frame."""
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    setup_projection()
    house()
    rain_drawing()
    glutSwapBuffers()

def animate():
    global positions,bending,base_speed
    current_speed = base_speed
    using_bending = bending
    for i in range(rain_count):
        positions[i][1] -= current_speed
        positions[i][0] += using_bending*0.3
        if positions[i][1] < -250:
            positions[i][1] = 250
            positions[i][0] = random.uniform(-250,250)
        if positions[i][0] > 250:
            positions[i][0] = -250
        elif positions[i][0] < -250:
            positions[i][0] = 250

    glutPostRedisplay()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_RGBA)
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"Assignment-1(House & points)")

    glutDisplayFunc(display)
    glutIdleFunc(animate)
    glutKeyboardFunc(keyboard_listener)
    glutSpecialFunc(special_key_listener)
    glutMouseFunc(mouse_listener)
    rain()

    glutMainLoop()

if __name__ == "__main__":
    main()
