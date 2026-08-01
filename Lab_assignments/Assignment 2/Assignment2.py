from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random

WINDOW_WIDTH, WINDOW_HEIGHT = 400, 600
current_score = 0
game_over_flag = False
game_paused_flag = False
cheat_mode_flag = False

catcher_cord_x = 200
catcher_cord_y = 5
catcher_width = 75
catcher_height = 15
catcher_color = [1.0, 1.0, 1.0]

diamond_cord_x = random.randint(5, 395)
diamond_cord_y = 600
diamond_speed = 0.1
diamond_color = [random.random(), random.random(), random.random()]

button_ymin = 540
button_ymax = 580


def zone_determine(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    if abs(dx) >= abs(dy):
        if dx >= 0 and dy >= 0: return 0
        if dx < 0 and dy >= 0: return 3
        if dx < 0 and dy < 0: return 4
        if dx >= 0 and dy < 0: return 7
    else:
        if dx >= 0 and dy >= 0: return 1
        if dx < 0 and dy >= 0: return 2
        if dx < 0 and dy < 0: return 5
        if dx >= 0 and dy < 0: return 6

def zone_0_convertion(x, y, zone):
    if zone == 0: return x, y
    if zone == 1: return y, x
    if zone == 2: return y, -x
    if zone == 3: return -x, y
    if zone == 4: return -x, -y
    if zone == 5: return -y, -x
    if zone == 6: return -y, x
    if zone == 7: return x, -y

def zone_0_to_original(x, y, zone):
    if zone == 0: return x, y
    if zone == 1: return y, x
    if zone == 2: return -y, x
    if zone == 3: return -x, y
    if zone == 4: return -x, -y
    if zone == 5: return -y, -x
    if zone == 6: return y, -x
    if zone == 7: return x, -y

def line_drawing(x1, y1, x2, y2, color):

    zone = zone_determine(x1, y1, x2, y2)
    
    zone0_of_x1, zone0_of_y1 = zone_0_convertion(x1, y1, zone)
    zone0_of_x2, zone0_of_y2 = zone_0_convertion(x2, y2, zone)
    
    dx = zone0_of_x2 - zone0_of_x1
    dy = zone0_of_y2 - zone0_of_y1
    
    d_init = 2 * dy - dx
    del_dE = 2 * dy
    del_dNE = 2 * (dy - dx)
    
    x, y = zone0_of_x1, zone0_of_y1
    
    glColor3f(color[0], color[1], color[2])
    glPointSize(2)
    glBegin(GL_POINTS)
    
    while x <= zone0_of_x2:
        
        original_x, original_y = zone_0_to_original(x, y, zone)
        glVertex2f(original_x, original_y)
        
        if d_init < 0:
            x += 1
            d_init += del_dE
        else:
            x += 1
            y += 1
            d_init += del_dNE
    glEnd()


def catcher_drawing():
    global catcher_color
    if game_over_flag:
        c = [1.0, 0.0, 0.0] 
    else:
        c = catcher_color
    
    x_position_bottom_left, y_positon_bottom_left, c_width, c_height = catcher_cord_x, catcher_cord_y, catcher_width, catcher_height
    
    line_drawing(x_position_bottom_left, y_positon_bottom_left, x_position_bottom_left + c_width, y_positon_bottom_left, c) 
    line_drawing(x_position_bottom_left - 10, y_positon_bottom_left + c_height, x_position_bottom_left + c_width + 10, y_positon_bottom_left + c_height, c) 
    line_drawing(x_position_bottom_left, y_positon_bottom_left, x_position_bottom_left - 10, y_positon_bottom_left + c_height, c) 
    line_drawing(x_position_bottom_left + c_width, y_positon_bottom_left, x_position_bottom_left + c_width + 10, y_positon_bottom_left + c_height, c) 

def diamond_drawing():
    
    x, y = int(diamond_cord_x), int(diamond_cord_y)
    d_c = diamond_color

    line_drawing(x, y, x + 10, y - 15, d_c) 
    line_drawing(x + 10, y - 15, x, y - 30, d_c)
    line_drawing(x, y - 30, x - 10, y - 15, d_c)
    line_drawing(x - 10, y - 15, x, y, d_c)

def draw_buttons():
    
    c_arrow = [0.0, 1.0, 1.0]
    line_drawing(30, 560, 70, 560, c_arrow)
    line_drawing(30, 560, 50, 575, c_arrow) 
    line_drawing(30, 560, 50, 545, c_arrow) 

    c_play_pause = [1.0, 0.75, 0.0]
    if game_paused_flag:

        line_drawing(180, 580, 180, 540, c_play_pause)
        line_drawing(180, 580, 220, 560, c_play_pause)
        line_drawing(180, 540, 220, 560, c_play_pause)
    else:
       
        line_drawing(190, 580, 190, 540, c_play_pause)
        line_drawing(210, 580, 210, 540, c_play_pause)

    c_cross = [1.0, 0.0, 0.0]
    line_drawing(350, 580, 390, 540, c_cross)
    line_drawing(350, 540, 390, 580, c_cross)


def collision_checking():
    global current_score, diamond_cord_y, diamond_cord_x, diamond_speed, diamond_color
       
    box_catcher_x_min = catcher_cord_x - 10
    box_catcher_x_max = catcher_cord_x + catcher_width + 10
    box_catcher_y_min = catcher_cord_y
    box_catcher_y_max = catcher_cord_y + catcher_height
    
    box_diamond_x_min = diamond_cord_x - 10
    box_diamond_x_max = diamond_cord_x + 10
    box_diamond_y_min = diamond_cord_y - 30
    box_diamond_y_max = diamond_cord_y
    
    if (box_catcher_x_min < box_diamond_x_max and box_catcher_x_max > box_diamond_x_min and
        box_catcher_y_min < box_diamond_y_max and box_catcher_y_max > box_diamond_y_min):
        return True
    return False

def continuous_diamond_falling():
    global diamond_cord_x, diamond_cord_y, diamond_speed, diamond_color
    diamond_cord_y = 600
    diamond_cord_x = random.randint(20, 380)
    diamond_speed += 0.003
    diamond_color = [random.random(), random.random(), random.random()]

def game_restarting():
    global current_score, game_over_flag, game_paused_flag, diamond_speed, catcher_color
    print("Starting over!")
    current_score = 0
    game_over_flag = False
    game_paused_flag = False
    diamond_speed =0.1
    catcher_color = [1.0, 1.0, 1.0]
    continuous_diamond_falling()


def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    
    catcher_drawing()
    diamond_drawing()
    draw_buttons()
    
    glutSwapBuffers()

def animate():
    global diamond_cord_y, game_over_flag, current_score, catcher_cord_x
    
    if not game_paused_flag and not game_over_flag:
        diamond_cord_y -= diamond_speed
        if cheat_mode_flag:
            center_x = catcher_cord_x + (catcher_width // 2)
            if center_x < diamond_cord_x:
                catcher_cord_x += diamond_speed
            elif center_x > diamond_cord_x:
                catcher_cord_x -= diamond_speed
            if catcher_cord_x < 10:
                catcher_cord_x = 10
            elif catcher_cord_x > WINDOW_WIDTH - catcher_width - 10:
                catcher_cord_x = WINDOW_WIDTH - catcher_width - 10

        if collision_checking():
            current_score += 1
            print(f"Score: {current_score}")
            continuous_diamond_falling()
            
        elif diamond_cord_y < 0:
            game_over_flag = True
            print(f"Game Over! Score: {current_score}")
            
    glutPostRedisplay()

def keyboard_listener(key, x, y):
    global cheat_mode_flag
    if key == b'c':
        cheat_mode_flag = not cheat_mode_flag
        if cheat_mode_flag:
            current_state = "ON" 
        else:
            current_state = "OFF"
        print(f"Cheat Mode {current_state}")

def special_listener(key, x, y):
    global catcher_cord_x
    if not game_over_flag and not game_paused_flag:
        step = 18
        if key == GLUT_KEY_LEFT:
            catcher_cord_x = max(10, catcher_cord_x - step)
        if key == GLUT_KEY_RIGHT:
            catcher_cord_x = min(WINDOW_WIDTH - catcher_width - 10, catcher_cord_x + step)

def mouse_listener(button, state, x, y):
    global game_paused_flag, game_over_flag
    mouse_to_mysys_convert = WINDOW_HEIGHT - y 
    
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
    
        if button_ymin <= mouse_to_mysys_convert <= button_ymax:
           
            if 20 <= x <= 80:
                game_restarting()
            
            elif 170 <= x <= 230:
                game_paused_flag = not game_paused_flag
                
            elif 340 <= x <= 400:
                print(f"Goodbye! Final Score: {current_score}")
                glutLeaveMainLoop()

def init():
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT, 0, 1)
    glMatrixMode(GL_MODELVIEW)

def main():
    glutInit()
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    glutInitWindowPosition(100, 100)
    glutCreateWindow(b"Catch the Diamonds!")
    
    init()
    
    glutDisplayFunc(display)
    glutIdleFunc(animate)
    glutKeyboardFunc(keyboard_listener)
    glutSpecialFunc(special_listener)
    glutMouseFunc(mouse_listener)
    
    glutMainLoop()

if __name__ == "__main__":
    main()