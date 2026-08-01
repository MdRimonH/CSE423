from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random

WIDTH, HEIGHT = 1000, 800

Board_step = 60
board_cells = 13
board_length = (board_cells * Board_step) // 2

camera_position = [0, -650, 450] 
camera_angle = -math.pi / 2      
camera_height = 450   
camera_radius = 750  
fovY = 60
aspect_ratio = 1.25
first_person = False 

game_over = False
score = 0
lives = 5              
missed_bullets = 0
max_missed = 10  
   

player = {'x': 0, 'y': 0, 'z': 0, 'angle': 0} 
player_speed = 15
player_radius = 15     

bullets = []
bullet_speed = 50
bullet_size = 5 
fire_colddown = 0    

enemies = []
num_enemies = 5        
enemy_speed = 0.02
enemy_radius = 30
respawn_dist = 300

cheat_mode = False     
cheat_vision = False   

anim_scale = 1.0
anim_growing = True

def enemy_spawning():
    angle = random.uniform(0, 2 * math.pi)
    dist = random.uniform(200, board_length - 20)
    x = math.cos(angle) * dist
    y = math.sin(angle) * dist
    return {'x': x, 'y': y, 'z': 0}

for _ in range(num_enemies):
    enemies.append(enemy_spawning())

def distence_2d(x1, y1, x2, y2):
    return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

def bullet_firing():
    rad = math.radians(player['angle'])

    b = {
        'x': player['x'],
        'y': player['y'],
        'z': 48,
        'dx': math.cos(rad+math.pi/2) * bullet_speed,
        'dy': math.sin(rad+math.pi/2) * bullet_speed
    }
    bullets.append(b)
    print("Player Bullet Fired!")

def text_drawing(x, y, text):
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WIDTH, 0, HEIGHT)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    
def board_drawing():
    glBegin(GL_QUADS)
    start_pos = -board_length
    for i in range(board_cells): 
        for j in range(board_cells): 
            x = start_pos + (i * Board_step)
            y = start_pos + (j * Board_step)
            
            if (i + j) % 2 == 0:
                glColor3f(1.0, 1.0, 1.0) 
            else:
                glColor3f(0.7, 0.5, 0.95) 
            
            glVertex3f(x, y, 0)
            glVertex3f(x + Board_step, y, 0)
            glVertex3f(x + Board_step, y + Board_step, 0)
            glVertex3f(x, y + Board_step, 0)
    glEnd()
    wall_height = 40
    glColor3f(1, 1, 1) 
    glBegin(GL_QUADS)

    glVertex3f(-board_length, -board_length, 0)
    glVertex3f(board_length, -board_length, 0)
    glVertex3f(board_length, -board_length, wall_height)
    glVertex3f(-board_length, -board_length, wall_height)
    glEnd()

    glColor3f(0.5, 0.9, 1) 
    glBegin(GL_QUADS)
    glVertex3f(-board_length, board_length, 0)
    glVertex3f(board_length, board_length, 0)
    glVertex3f(board_length, board_length, wall_height)
    glVertex3f(-board_length, board_length, wall_height)
    glEnd()

    glColor3f(0, 0, 1) 
    glBegin(GL_QUADS)
    glVertex3f(-board_length, -board_length, 0)
    glVertex3f(-board_length, board_length, 0)
    glVertex3f(-board_length, board_length, wall_height)
    glVertex3f(-board_length, -board_length, wall_height)
    glEnd()

    glColor3f(0, 1, 0) 
    glBegin(GL_QUADS)
    glVertex3f(board_length, -board_length, 0)
    glVertex3f(board_length, board_length, 0)
    glVertex3f(board_length, board_length, wall_height)
    glVertex3f(board_length, -board_length, wall_height)
    glEnd()

def player_drawing():
    global first_person, game_over

    glPushMatrix()
    glTranslatef(player['x'], player['y'], player['z'])
    glRotatef(player['angle'], 0, 0, 1) 
    if game_over:
        glRotate(90,1,0,0)
        glTranslatef(0,0,-15)


    glColor3f(0, 0, 1) 
    

    glPushMatrix()
    glTranslatef(12, 0, 0)
    gluCylinder(gluNewQuadric(), 3, 10, 25, 30, 30) 
    glPopMatrix()


    glPushMatrix()
    glTranslatef(-12, 0, 0)
    gluCylinder(gluNewQuadric(), 3, 10, 25, 30, 30)
    glPopMatrix()


    if not first_person or (cheat_mode and cheat_vision):
        glColor3f(0.2, 0.6, 0.2) 
        glPushMatrix()
        glTranslatef(0, 0, 35)   
        glScalef(1.1, 0.6, 1.3)  
        glutSolidCube(30)
        glPopMatrix()

    if not first_person or (cheat_mode and cheat_vision):
        glColor3f(0, 0, 0)
        glPushMatrix()
        glTranslatef(0, 0, 65) 
        glutSolidSphere(12, 20, 20)
        glPopMatrix()


    glColor3f(0.8, 0.8, 0.8) 
    glPushMatrix()
    glTranslatef(0, 0, 48)  
    glRotatef(270, 1, 0, 0)  
    gluCylinder(gluNewQuadric(), 8, 3, 60, 10, 10) 
    glPopMatrix()

 
    glColor3f(1, 0.8, 0.6) 
    

    glPushMatrix()
    glTranslatef(13, 0, 48) 
    glRotatef(270, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 8, 3, 40, 10, 10) 
    glPopMatrix()

    glPushMatrix()
    glTranslatef(-13, 0, 48)
    
    glRotatef(270, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 8, 3, 40, 10, 10) 
    glPopMatrix()

    glPopMatrix()

def enemies_drawing():
    global anim_scale
    for e in enemies:
        glPushMatrix()
        glTranslatef(e['x'], e['y'], 10)
        glScalef(anim_scale, anim_scale, anim_scale)
        glColor3f(1, 0, 0)
        glutSolidSphere(22, 30, 30) 
        glColor3f(0, 0, 0)
        glTranslatef(0, 0, 20)
        glutSolidSphere(11, 30, 30)  
        glPopMatrix()

def bullets_drawing():
    glColor3f(1, 1, 0) 
    for b in bullets:
        glPushMatrix()
        glTranslatef(b['x'], b['y'], b['z'])
        glutSolidCube(bullet_size)
        glPopMatrix()

def keyboardListener(key, x, y):
    global player, cheat_mode, cheat_vision, lives, score, missed_bullets, game_over
    
    if key == b'r': 
        game_over = False
        cheat_mode = False
        score = 0
        missed_bullets = 0
        lives = 5
        player['x'], player['y'], player['angle'] = 0, 0, 90 
        bullets.clear()
        enemies.clear()
        for _ in range(num_enemies): 
            enemies.append(enemy_spawning())

    if game_over: return
    
    rad = math.radians(player['angle'])
    if key == b'w': 

        player['x'] += math.cos(rad + math.pi/2) * player_speed
        player['y'] += math.sin(rad + math.pi/2) * player_speed

    if key == b's': 

        player['x'] -= math.cos(rad + math.pi/2) * player_speed
        player['y'] -= math.sin(rad + math.pi/2) * player_speed

    if key == b'a': player['angle'] += 4
    if key == b'd': player['angle'] -= 4
    

    limit = board_length - 20
    player['x'] = max(-limit, min(limit, player['x']))
    player['y'] = max(-limit, min(limit, player['y']))

    if key == b'c': 
        cheat_mode = not cheat_mode
        print(f"Cheat Mode: {cheat_mode}")
    if key == b'v': 
        if cheat_mode:
            cheat_vision = not cheat_vision

    glutPostRedisplay()

def specialKeyListener(key, x, y):
    global camera_angle, camera_height
    if key == GLUT_KEY_LEFT: camera_angle -= 0.05
    if key == GLUT_KEY_RIGHT: camera_angle += 0.05
    if key == GLUT_KEY_UP: camera_height += 10
    if key == GLUT_KEY_DOWN: camera_height -= 10
    glutPostRedisplay()

def mouseListener(button, state, x, y):
    global first_person, game_over
    if game_over: return
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        bullet_firing()
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        first_person = not first_person


def idle():
    global fire_colddown, anim_scale, anim_growing, score, lives, missed_bullets, game_over, player
   
    if game_over: return
    
    
    if fire_colddown> 0:
        fire_colddown -= 1


    if anim_growing:
        anim_scale += 0.001
        if anim_scale > 1.5: anim_growing = False
    else:
        anim_scale -= 0.001
        if anim_scale < 0.8: anim_growing = True

    for b in bullets[:]:
        b['x'] += b['dx']
        b['y'] += b['dy']
        if abs(b['x']) > board_length or abs(b['y']) > board_length:
            bullets.remove(b)
            missed_bullets += 1
            print(f'bullet missed: {missed_bullets}')
            if missed_bullets >= max_missed:
                game_over = True


    for e in enemies:
        angle_to_player = math.atan2(player['y'] - e['y'], player['x'] - e['x'])
        e['x'] += math.cos(angle_to_player) * enemy_speed
        e['y'] += math.sin(angle_to_player) * enemy_speed
        
        if distence_2d(e['x'], e['y'], player['x'], player['y']) < (player_radius + enemy_radius):
            lives -= 1
            print(f"Remaining Player Life: {lives}")
            new_pos = enemy_spawning()
            e['x'], e['y'] = new_pos['x'], new_pos['y']
            if lives <= 0: game_over = True

        for b in bullets[:]:
            if distence_2d(b['x'], b['y'], e['x'], e['y']) < enemy_radius + bullet_size:
                score += 1
                bullets.remove(b)
                new_pos = enemy_spawning()
                e['x'], e['y'] = new_pos['x'], new_pos['y']
                break


    if cheat_mode:
        

        player['angle'] += 0.4

        if fire_colddown <= 0:
            
            gun_angle = (player['angle'] + 90) % 360
            
            for e in enemies:
                dx = e['x'] - player['x']
                dy = e['y'] - player['y']
                target_rad = math.atan2(dy, dx)
                target_deg = math.degrees(target_rad)
                
          
                if target_deg < 0: 
                    target_deg += 360
                
                diff = abs(gun_angle - target_deg)
                if diff > 180: 
                    diff = 360 - diff
                
                if diff < 15: 
                    player['angle'] = target_deg - 90
                    bullet_firing()
                    fire_colddown = 15
                    break 

    glutPostRedisplay()

def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, aspect_ratio, 1, 2000)
    
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    if cheat_mode and cheat_vision and first_person:
        rad = math.radians(player['angle'])
        eyeX = player['x'] - math.cos(rad + math.pi/2) * 35
        eyeY = player['y'] - math.sin(rad + math.pi/2) * 35
        eyeZ = 105
        

        lookX = player['x'] + math.cos(rad + math.pi/2) * 100
        lookY = player['y'] + math.sin(rad + math.pi/2) * 100
        lookZ = 50
        
        gluLookAt(eyeX, eyeY, eyeZ, lookX, lookY, lookZ, 0, 0, 1)
    
    elif first_person:

        rad = math.radians(player['angle'])
        lookX = player['x'] + math.cos(rad + math.pi/2) * 100
        lookY = player['y'] + math.sin(rad + math.pi/2) * 100
        gluLookAt(player['x'], player['y'], 60, lookX, lookY, 60, 0, 0, 1)
   

    else:

        eyeX = math.cos(camera_angle) * camera_radius
        eyeY = math.sin(camera_angle) * camera_radius

        gluLookAt(eyeX, eyeY, camera_height, 0, 0, 0, 0, 0, 1)

def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    setupCamera()
    
    board_drawing()
    player_drawing()
    enemies_drawing()
    bullets_drawing()
    
    text_drawing(10, 770, f"Player Life Remaining: {lives}")
    text_drawing(10, 740, f"Game Score: {score}")
    text_drawing(10, 710, f"Player Bullet Missed: {missed_bullets}")
    
    if game_over:
        text_drawing(400, 400, "GAME OVER - Press R")

    glutSwapBuffers()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WIDTH, HEIGHT)
    glutCreateWindow(b"Bullet Frenzy Final")
    glutDisplayFunc(showScreen)
    glutIdleFunc(idle)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glEnable(GL_DEPTH_TEST)
    glutMainLoop()

if __name__ == "__main__":
    main()