from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18, GLUT_BITMAP_TIMES_ROMAN_24
import math
import random
import time

# Controls:
# - Movement: W/S move forward/backward; A/D rotate left/right.
# - Camera: F toggles first/third person; Arrow keys adjust camera in third-person.
# - Combat: G toggles gun; R fires when gun is visible; E refills ammo at house when empty.
# - Shop (near shop, Level 3): B buys cow (150 score); E buys blade (450 score); Right-click plants a blade in front.
# - Farming: E equips bucket at house; Left-click dumps/picks water near pond; E equips seeds at seed container; Z switches seed type (Level 2+);
#   H harvests ready crops; C equips a crop at house (Level 3); T places torch (20); K places sprinkler (25); X removes sprinkler; P repairs fence (10) near fence.
# - Crops/Score: 0 adds stored crop; + adds 50 score.
# - Level/Night: 2 jumps to Level 2; 3 jumps to Level 3; N forces night during cycle.
# - UI: ESC pauses/resumes; Left-click activates PLAY/Resume/Restart when prompted.

show_level_msg = False
 
level_msg_start_time = 0
game_level = 1          # Track current level
show_level_msg = False
level_msg_start_time = 0
game_over = False
game_won = False
zombies_entered_count = 0

game_start_time = 0
seed_plant_time = 0
score = 0
final_boss_active = False
final_boss_spawned = False
final_boss_hp = 0
final_boss_pos = [0.0, 0.0]
final_boss_speed = 0.08
blade_count = 0
last_harvest_time = 0
show_harvest_msg = False
GROWTH_TIME_LIMIT = 45000
stored_crops = 0
show_feed_animals_msg = False
feed_animals_msg_time = 0
crop_equipped = False
zombies = []                
ZOMBIE_SPEED = 0.05
zombies_spawned_flag = False 
bullets = [] # List to store [x, y, z, dx, dy]
BULLET_SPEED = 10.0
bullet_count = 0        # Ammo remaining
missed_count = 0        # Bullets that hit the wall/boundary
fence_health = [100, 100, 100, 100] 
fence_broken = [False, False, False, False]
torches = []
TORCH_COST = 20
TORCH_RADIUS = 400
blades = []
BLADE_COST = 450
seed_type = "NORMAL"
golden_seed_lines = []
GOLD_GROWTH_TIME = 60000
sprinkler_active = False
sprinkler_pos = None
sprinkler_start_time = 0
SPRINKLER_DURATION = 90000
SPRINKLER_COST = 25

# Camera-related variables
camera_pos = (350, 0, 400)
# Calculate initial distance and angle from initial position
camera_distance = math.sqrt(camera_pos[0]**2 + camera_pos[1]**2)
camera_angle = math.degrees(math.atan2(camera_pos[1], camera_pos[0]))

fovY = 100
GRID_LENGTH = 600
rand_var = 423



FARM_RECT = {
    'x_min': -1150,
    'x_max': -500,
    'y_min': -1150,
    'y_max': -400
}
show_locked_msg = False

_cx = (FARM_RECT['x_min'] + FARM_RECT['x_max']) / 2
_cy = (FARM_RECT['y_min'] + FARM_RECT['y_max']) / 2
cow_pos = [_cx, _cy]      
cow_target = [_cx, _cy]   
cow_moving = False        
cow_idle_start_time = 0   
COW_SPEED = 2.0           
cow_angle = 0.0           

herd = []

# Player-related variables
player_pos = [0.0, 0.0, 0.0]
player_angle = 0.0
PLAYER_SPEED = 10.0
gun_visible = False
mode_first_person = True
WATER_SINK_OFFSET = -25.0
BUCKET_EQUIP_RADIUS = 250.0
SEED_EQUIP_RADIUS = 100.0

# Bucket-related variables
bucket_size = 20.0
bucket_pick_distance = 60.0
bucket_held = False
bucket_has_water = False
bucket_pos = [0.0, 0.0, bucket_size / 2]

brown_area_watered = False

seed_container_size = 40.0
_seed_grid_i = 2  # column to the right of the house (0-indexed)
_seed_grid_j = 8  # row aligned with house
_seed_grid_size = 13
_seed_floor_len = 2 * GRID_LENGTH
_seed_cell_size = (2 * _seed_floor_len) / _seed_grid_size
seed_container_pos = [
    -_seed_floor_len + (_seed_grid_i + 0.5) * _seed_cell_size,
    -_seed_floor_len + (_seed_grid_j + 0.5) * _seed_cell_size,
    seed_container_size / 2,
]
seeds_equipped = False
seeds_prompt_visible = True
seed_lines = []

ui_play_visible = True
ui_paused = False

UI_PLAY_RECT = (440, 740, 120, 40)
UI_RESUME_RECT = (420, 700, 160, 36)
UI_RESTART_RECT = (420, 650, 160, 36)
def is_night_time(): #  Determine whether the current cycle is in night phase.
    if game_start_time == 0: return False
    TRANSITION_TIME = 2 * 60 * 1000 # Matches your sky color function
    NIGHT_HOLD_TIME = 2 * 60 * 1000 
    TOTAL_CYCLE = (TRANSITION_TIME * 2) + NIGHT_HOLD_TIME
    
    current_time = int(time.time() * 1000)
    time_playing = current_time - game_start_time
    cycle_time = time_playing % TOTAL_CYCLE 
    
    # Check if we are in the Night Hold phase
    return cycle_time >= TRANSITION_TIME and cycle_time < (TRANSITION_TIME + NIGHT_HOLD_TIME)

def get_current_sky_color(): #  Compute sky color brightness over the day-night cycle.
    # 1. CHECK: Has the game started?
    if game_start_time == 0:
        return (1.0, 1.0, 1.0) # Static Daylight before play

    # 2. Define Duration Settings
    TRANSITION_TIME = 2 * 60 * 1000  # 3 Minutes for fading
    NIGHT_HOLD_TIME = 2 * 60 * 1000  # 1 Minute for staying dark
    
    # The total loop is: Fade Out + Hold Night + Fade In
    TOTAL_CYCLE = (TRANSITION_TIME * 2) + NIGHT_HOLD_TIME
    
    # 3. Calculate time passed since PLAY
    current_time = int(time.time() * 1000)
    time_playing = current_time - game_start_time
    cycle_time = time_playing % TOTAL_CYCLE 
    
    # 4. Determine which phase we are in
    brightness = 1.0 # Default
    
    # --- PHASE 1: Day to Night Transition (First 3 mins) ---
    if cycle_time < TRANSITION_TIME:
        # Go from 1.0 down to 0.0
        progress = cycle_time / TRANSITION_TIME
        brightness = 1.0 - progress
        
    # --- PHASE 2: Full Night Hold (Next 1 min) ---
    elif cycle_time < (TRANSITION_TIME + NIGHT_HOLD_TIME):
        # Stay fully black
        brightness = 0.0
        
    # --- PHASE 3: Night to Day Transition (Last 3 mins) ---
    else:
        # Calculate time passed *into* this specific phase
        # We subtract the time taken by Phase 1 and Phase 2
        time_in_phase = cycle_time - (TRANSITION_TIME + NIGHT_HOLD_TIME)
        
        # Go from 0.0 up to 1.0
        progress = time_in_phase / TRANSITION_TIME
        brightness = progress

    return (brightness, brightness, brightness)
    
def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18): #  Render bitmap text in screen coordinates.
    glColor3f(1.0, 0.0, 0.0)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    
    # Set up an orthographic projection that matches window coordinates
    gluOrtho2D(0, 1000, 0, 800)  # left, right, bottom, top

    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    # Draw text at (x, y) in screen coordinates
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    
    # Restore original projection and modelview matrices
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


def draw_floor_grid(): #  Draw the floor checkerboard including pond and brown zones.
    """Draw a 13x13 checkerboard floor grid."""
    grid_size = 13
    floor_length = 2 * GRID_LENGTH
    cell_size = (2 * floor_length) / grid_size
    
    glBegin(GL_QUADS)
    for i in range(grid_size):
        for j in range(grid_size):
            if 8 <= i <= 10 and 2 <= j <= 10:
                glColor3f(0.0, 0.4, 0.8)
            elif 6 <= i <= 7 and 2 <= j <= 10:
                if brown_area_watered:
                    glColor3f(0.45, 0.2, 0.1)
                else:
                    glColor3f(0.65, 0.3, 0.2)
            else:
                if (i + j) % 2 == 0:
                    glColor3f(0.12, 0.45, 0)
                else:
                    glColor3f(0.12, 0.50, 0)
            
            # Calculate cell corners
            x1 = -floor_length + i * cell_size
            x2 = x1 + cell_size
            y1 = -floor_length + j * cell_size
            y2 = y1 + cell_size
            
            # Draw the cell
            glVertex3f(x1, y1, 0)
            glVertex3f(x2, y1, 0)
            glVertex3f(x2, y2, 0)
            glVertex3f(x1, y2, 0)
    glEnd()
    
def draw_border(): #  Draw perimeter walls around the extended floor area.
    floor_length = 2 * GRID_LENGTH

    wall_height = 90
    glColor3f(0, 1, 0) 
    glBegin(GL_QUADS)

    glVertex3f(-floor_length, -floor_length, 0)
    glVertex3f(floor_length, -floor_length, 0)
    glVertex3f(floor_length, -floor_length, wall_height)
    glVertex3f(-floor_length, -floor_length, wall_height)
    glEnd()

    glColor3f(0.5, 0.9, 1) 
    glBegin(GL_QUADS)
    glVertex3f(-floor_length, floor_length, 0)
    glVertex3f(floor_length, floor_length, 0)
    glVertex3f(floor_length, floor_length, wall_height)
    glVertex3f(-floor_length, floor_length, wall_height)
    glEnd()

    glColor3f(0, 0, 1) 
    glBegin(GL_QUADS)
    glVertex3f(-floor_length, -floor_length, 0)
    glVertex3f(-floor_length, floor_length, 0)
    glVertex3f(-floor_length, floor_length, wall_height)
    glVertex3f(-floor_length, -floor_length, wall_height)
    glEnd()
    
    glColor3f(1, 1, 0) 
    glBegin(GL_QUADS)
    glVertex3f(floor_length, -floor_length, 0)
    glVertex3f(floor_length, floor_length, 0)
    glVertex3f(floor_length, floor_length, wall_height)
    glVertex3f(floor_length, -floor_length, wall_height)
    glEnd()


def draw_house(): #  Render the house with cube walls and a conical roof.
    """Draw a small house using a scaled cube for walls and a cone roof."""
    grid_size = 13
    floor_length = 2 * GRID_LENGTH
    cell_size = (2 * floor_length) / grid_size

    col_start = 1
    col_end = 1
    row_start = 5
    row_end = 7

    x1 = -floor_length + col_start * cell_size
    x2 = -floor_length + (col_end + 1) * cell_size
    y1 = -floor_length + row_start * cell_size
    y2 = -floor_length + (row_end + 1) * cell_size
    center_x = (x1 + x2) / 2
    center_y = (y1 + y2) / 2

    wall_w = (x2 - x1) * 0.8
    wall_d = (y2 - y1) * 0.8
    wall_h = 170.0

    glPushMatrix()
    glTranslatef(center_x, center_y, wall_h / 2)
    glScalef(wall_w, wall_d, wall_h)
    glColor3f(0.8, 0.7, 0.6)
    glutSolidCube(1)
    glPopMatrix()

    half_diag = math.sqrt((wall_w * 0.5) ** 2 + (wall_d * 0.5) ** 2)
    roof_radius = half_diag
    roof_height = 120.0
    glPushMatrix()
    glTranslatef(center_x, center_y, wall_h)
    glColor3f(0.6, 0.2, 0.1)
    quad = gluNewQuadric()
    gluCylinder(quad, roof_radius, 0.0, roof_height, 32, 6)
    glPushMatrix()
    glColor3f(0.6, 0.2, 0.1)
    half_w = wall_w * 0.5
    half_d = wall_d * 0.5
    glBegin(GL_QUADS)
    glVertex3f(-half_w, -half_d, 0)
    glVertex3f( half_w, -half_d, 0)
    glVertex3f( half_w,  half_d, 0)
    glVertex3f(-half_w,  half_d, 0)
    glEnd()
    glPopMatrix()
    glPopMatrix()


def get_house_center(): #  Return the center coordinates of the house footprint.
    grid_size = 13
    floor_length = 2 * GRID_LENGTH
    cell_size = (2 * floor_length) / grid_size
    col_start = 1
    col_end = 1
    row_start = 5
    row_end = 7

    x1 = -floor_length + col_start * cell_size
    x2 = -floor_length + (col_end + 1) * cell_size
    y1 = -floor_length + row_start * cell_size
    y2 = -floor_length + (row_end + 1) * cell_size
    center_x = (x1 + x2) / 2
    center_y = (y1 + y2) / 2
    return center_x, center_y

def draw_shop(): #  Render the shop building near the house.
    """Draw a shop near the house."""
    grid_size = 13
    floor_length = 2 * GRID_LENGTH
    cell_size = (2 * floor_length) / grid_size
    col_start = 1
    col_end = 1
    row_start = 8
    row_end = 10

    x1 = -floor_length + col_start * cell_size
    x2 = -floor_length + (col_end + 1) * cell_size
    y1 = -floor_length + row_start * cell_size
    y2 = -floor_length + (row_end + 1) * cell_size
    center_x = (x1 + x2) / 2
    center_y = (y1 + y2) / 2

    wall_w = (x2 - x1) * 0.8
    wall_d = (y2 - y1) * 0.8
    wall_h = 170.0

    glPushMatrix()
    glTranslatef(center_x, center_y, wall_h / 2)
    glScalef(wall_w, wall_d, wall_h)
    glColor3f(0.8, 0.7, 0.6)
    glutSolidCube(1)
    glPopMatrix()

    half_diag = math.sqrt((wall_w * 0.5) ** 2 + (wall_d * 0.5) ** 2)
    roof_radius = half_diag
    roof_height = 120.0
    glPushMatrix()
    glTranslatef(center_x, center_y, wall_h)
    glColor3f(0.2, 0.6, 0.2)
    quad = gluNewQuadric()
    gluCylinder(quad, roof_radius, 0.0, roof_height, 32, 6)
    glPushMatrix()
    glColor3f(0.2, 0.6, 0.2)
    half_w = wall_w * 0.5
    half_d = wall_d * 0.5
    glBegin(GL_QUADS)
    glVertex3f(-half_w, -half_d, 0)
    glVertex3f( half_w, -half_d, 0)
    glVertex3f( half_w,  half_d, 0)
    glVertex3f(-half_w,  half_d, 0)
    glEnd()
    glPopMatrix()
    glPopMatrix()

def get_shop_center(): #  Return the center coordinates of the shop footprint.
    grid_size = 13
    floor_length = 2 * GRID_LENGTH
    cell_size = (2 * floor_length) / grid_size
    col_start = 1
    col_end = 1
    row_start = 8
    row_end = 10

    x1 = -floor_length + col_start * cell_size
    x2 = -floor_length + (col_end + 1) * cell_size
    y1 = -floor_length + row_start * cell_size
    y2 = -floor_length + (row_end + 1) * cell_size
    center_x = (x1 + x2) / 2
    center_y = (y1 + y2) / 2
    return center_x, center_y

def is_near_shop(x, y, radius=200): #  Check if the player is within a radius of the shop.
    """Check if player is within radius of the shop."""
    shop_x, shop_y = get_shop_center()
    return math.hypot(x - shop_x, y - shop_y) <= radius

def get_field_center(): #  Get the center of the crop field area.
    grid_size = 13
    floor_length = 2 * GRID_LENGTH
    cell_size = (2 * floor_length) / grid_size
    row_center = 6.5
    col_center = 6.0
    cx = -floor_length + row_center * cell_size
    cy = -floor_length + col_center * cell_size
    return cx, cy

def check_win_condition(): #  Ensure Level 3 win only after all enemies are eliminated.
    global game_level, final_boss_active, final_boss_spawned, zombies, game_over, game_won
    if game_over:
        return
    if game_level == 3 and final_boss_spawned and (not final_boss_active) and len(zombies) == 0:
        game_over = True
        game_won = True

def spawn_zombies(): #  Populate zombies based on current level configuration.
    global zombies
    zombies = [] # Clear list
    floor_limit = 2 * GRID_LENGTH
    
    # --- LEVEL 3 CONFIGURATION ---
    if game_level == 3:
        # 10 Sprinters: HP=3, Speed=Fast
        for _ in range(10): 
            add_safe_zombie(3, 3, 0.18, "SPRINTER", floor_limit)
        # 10 Tanks: HP=10, Speed=Slow
        for _ in range(10): 
            add_safe_zombie(10, 10, 0.04, "TANK", floor_limit)
        # 5 Boss: HP=15, Speed=Medium
        for _ in range(5):
            add_safe_zombie(15, 15, 0.10, "BOSS", floor_limit)
    # --- LEVEL 2 CONFIGURATION ---
    elif game_level == 2:
        # 15 Sprinters: HP=2, Speed=Fast
        for _ in range(15): 
            add_safe_zombie(2, 2, 0.15, "SPRINTER", floor_limit)
        # 7 Tanks: HP=7, Speed=Slow
        for _ in range(7): 
            add_safe_zombie(7, 7, 0.03, "TANK", floor_limit)
    else:
        # LEVEL 1: 5 Normal Zombies
        for _ in range(10):
            add_safe_zombie(1, 1, 0.08, "NORMAL", floor_limit)

def add_safe_zombie(hp, max_hp, speed, z_type, floor_limit): #  Add a boundary-spawned zombie avoiding house and fence.
    """Helper to try finding a spawn spot that isn't inside the Farm/House."""
    while True:
        # Pick a random side: 0=Left, 1=Right, 2=Bottom, 3=Top
        side = random.randint(0, 3)
        if side == 0: # Left
            zx, zy = -floor_limit, random.uniform(-floor_limit, floor_limit)
        elif side == 1: # Right
            zx, zy = floor_limit, random.uniform(-floor_limit, floor_limit)
        elif side == 2: # Bottom
            zx, zy = random.uniform(-floor_limit, floor_limit), -floor_limit
        else: # Top
            zx, zy = random.uniform(-floor_limit, floor_limit), floor_limit
            
        # Check if this random spot is valid (not inside Farm/House)
        # We add a small buffer (50) to be safe
        if not is_inside_house(zx, zy) and not is_colliding_with_fence(zx, zy):
            # Structure: [x, y, current_hp, max_hp, speed, type]
            zombies.append([zx, zy, hp, max_hp, speed, z_type])
            return # Success, break loop
        
def update_zombies(): #  Move zombies, handle fence attacks, and blade collisions.
    global zombies, zombies_entered_count, game_over, blades
    tx, ty = get_field_center()
    
    # Field Boundaries for "Game Over" check
    grid_size = 13
    floor_length = 2 * GRID_LENGTH
    cell_size = (2 * floor_length) / grid_size
    field_x_min = -floor_length + 6 * cell_size
    field_x_max = -floor_length + 8 * cell_size
    field_y_min = -floor_length + 2 * cell_size
    field_y_max = -floor_length + 11 * cell_size

    for i in range(len(zombies) - 1, -1, -1):
        zx, zy, hp, max_hp, speed, z_type = zombies[i]
        
# 1. Check if Zombie is INSIDE the crop field (Game Over condition)
        if (field_x_min <= zx <= field_x_max) and (field_y_min <= zy <= field_y_max):
            del zombies[i]
            zombies_entered_count += 1
            
            # --- NEW: DYNAMIC LIMIT ---
            # Set limit based on level
            limit = 5
            if game_level == 2:
                limit = 11
            elif game_level == 3:
                limit = 15
                
            if zombies_entered_count >= limit:
                game_over = True
            # --------------------------
            
            continue

        # --- NEW: BLADE COLLISION CHECK ---
        # Check if any blade arm hits this zombie
        for blade in blades:
            blade_x, blade_y = blade['x'], blade['y']
            # Calculate blade rotation based on time
            rot = (int(time.time() * 1000) / 3) % 360
            # Calculate 3 arm positions (120 degrees apart, 200 units from center at 10x scale)
            arm_dist = 200  # Half of arm_length (400)
            for arm_idx in range(3):
                arm_angle = math.radians(rot + arm_idx * 120)
                arm_x = blade_x + arm_dist * math.cos(arm_angle)
                arm_y = blade_y + arm_dist * math.sin(arm_angle)
                # Check if zombie is near this arm
                arm_hitbox = 50  # Hitbox radius for arm
                dist_to_arm = math.sqrt((zx - arm_x)**2 + (zy - arm_y)**2)
                if dist_to_arm < arm_hitbox:
                    zombies[i][2] -= 1  # Reduce zombie HP by 1
                    if zombies[i][2] <= 0:
                        del zombies[i]
                        check_win_condition()
                    break  # Only hit once per frame
        
        if i >= len(zombies):
            continue  # Zombie was deleted, skip further processing

        # 2. Movement Calculation
        # Apply Torch Slowdown
        multiplier = get_zombie_speed_multiplier(zx, zy)
        current_speed = speed * multiplier

        dx = tx - zx
        dy = ty - zy
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > 0:
            vx = (dx / distance) * current_speed
            vy = (dy / distance) * current_speed
            
            # --- FIX: IMPROVED FENCE ATTACK LOGIC ---
            x_min, x_max = FARM_RECT['x_min'], FARM_RECT['x_max']
            y_min, y_max = FARM_RECT['y_min'], FARM_RECT['y_max']
            
            hit_fence = False
            
            # ATTACK_RANGE must be larger than the collision buffer (30)
            # We use 45 to ensure they attack BEFORE they hit the invisible wall
            ATTACK_RANGE = 20
            
            # We also add a CORNER_BUFFER (20) so they don't slip through edges
            
            # 0: Bottom Wall
            if not fence_broken[0]:
                # Check if close to Y line AND within X span (plus margins)
                if abs(zy - y_min) < ATTACK_RANGE and (x_min - 20 < zx < x_max + 20):
                    fence_health[0] -= 1; hit_fence = True
            
            # 2: Top Wall
            elif not fence_broken[2]:
                if abs(zy - y_max) < ATTACK_RANGE and (x_min - 20 < zx < x_max + 20):
                    fence_health[2] -= 1; hit_fence = True
            
            # 3: Left Wall
            elif not fence_broken[3]:
                if abs(zx - x_min) < ATTACK_RANGE and (y_min - 20 < zy < y_max + 20):
                    fence_health[3] -= 1; hit_fence = True

            # Check Fence Health
            for f in range(4):
                if fence_health[f] <= 0: fence_broken[f] = True

            # If attacking, STOP moving
            if hit_fence:
                continue 
            
            # --- MOVEMENT & COLLISION ---
            next_x = zx + vx
            next_y = zy + vy
            
            # Try moving X
            if not is_inside_house(next_x, zy) and not is_colliding_with_fence(next_x, zy):
                zombies[i][0] = next_x
            
            # Try moving Y
            cur_x = zombies[i][0]
            if not is_inside_house(cur_x, next_y) and not is_colliding_with_fence(cur_x, next_y):
                zombies[i][1] = next_y


def spawn_final_boss(): #  Initialize and place the final boss at a fixed grid location.
    """Spawn the final boss at grid column 12, row 7 (1-indexed)."""
    global final_boss_active, final_boss_hp, final_boss_pos, final_boss_spawned, zombies
    grid_size = 13
    floor_length = 2 * GRID_LENGTH
    cell_size = (2 * floor_length) / grid_size
    col_index = 11  # column 12 (1-indexed)
    row_index = 6   # row 7 (1-indexed)
    x = -floor_length + col_index * cell_size + cell_size / 2
    y = -floor_length + row_index * cell_size + cell_size / 2
    final_boss_pos = [x, y]
    final_boss_hp = 30
    final_boss_active = True
    final_boss_spawned = True

    # Spawn 6 TYRANT enemies at random rows on the same column
    spawned = 0
    attempts = 0
    while spawned < 6 and attempts < 50:
        attempts += 1
        rand_row = random.randint(0, grid_size - 1)
        # Skip the boss's exact row to avoid overlap
        if rand_row == row_index:
            continue
        zx = -floor_length + col_index * cell_size + cell_size / 2
        zy = -floor_length + rand_row * cell_size + cell_size / 2
        # Avoid spawning inside house or colliding with fence
        if is_inside_house(zx, zy) or is_colliding_with_fence(zx, zy):
            continue
        zombies.append([zx, zy, 12, 12, 0.09, "TYRANT"])  # hp, max_hp, speed, type
        spawned += 1


def update_final_boss(): #  Move boss toward field center and apply damage from blades/bullets.
    """Move and handle damage for the final boss."""
    global final_boss_pos, final_boss_hp, final_boss_active, game_over, game_won, blades
    if not final_boss_active:
        return

    # Blade collision
    for blade in blades:
        blade_x, blade_y = blade['x'], blade['y']
        rot = (int(time.time() * 1000) / 3) % 360
        arm_dist = 200
        for arm_idx in range(3):
            arm_angle = math.radians(rot + arm_idx * 120)
            arm_x = blade_x + arm_dist * math.cos(arm_angle)
            arm_y = blade_y + arm_dist * math.sin(arm_angle)
            arm_hitbox = 50
            dist_to_arm = math.sqrt((final_boss_pos[0] - arm_x)**2 + (final_boss_pos[1] - arm_y)**2)
            if dist_to_arm < arm_hitbox:
                final_boss_hp -= 1
                if final_boss_hp <= 0:
                    final_boss_active = False
                    check_win_condition()
                return  # Only one hit per frame

    # Movement toward field center
    tx, ty = get_field_center()
    bx, by = final_boss_pos
    dx = tx - bx
    dy = ty - by
    dist = math.sqrt(dx*dx + dy*dy)
    if dist > 0:
        step = final_boss_speed
        vx = (dx / dist) * step
        vy = (dy / dist) * step
        next_x = bx + vx
        next_y = by + vy
        if not is_inside_house(next_x, by) and not is_colliding_with_fence(next_x, by):
            bx = next_x
        if not is_inside_house(bx, next_y) and not is_colliding_with_fence(bx, next_y):
            by = next_y
        final_boss_pos = [bx, by]
            
def draw_zombies(): #  Render zombies with visual variety and health bars.
    """Draw zombies with visual variety and HP Bars."""
    for zx, zy, z_hp, max_hp, speed, z_type in zombies:
        glPushMatrix()
        glTranslatef(zx, zy, 25) 
        is_slowed = get_zombie_speed_multiplier(zx, zy) < 1.0

        if z_type == "SPRINTER":
            glScalef(0.8, 0.8, 0.8)       
            body_color = (1.0, 0.5, 0.0)  # Orange
        elif z_type == "TANK":
            glScalef(1.8, 1.8, 1.8)       
            body_color = (0.0, 0.4, 0.0)  # Dark Green
        elif z_type == "BOSS":
            glScalef(2.2, 2.2, 2.2)       
            body_color = (0.5, 0.0, 0.5)  # Purple
        elif z_type == "TYRANT":
            glScalef(1.6, 1.6, 1.6)
            body_color = (0.6, 0.0, 0.0)  # Dark Red
        else:
            glScalef(1.0, 1.0, 1.0)
            body_color = (1.0, 0.0, 0.0)  # Red
        
        if is_slowed:
            body_color = (0.0, 0.5, 1.0) # Bright Blue (Frozen look)
        glColor3f(*body_color) 
        gluSphere(gluNewQuadric(), 30, 20, 20) 
        glTranslatef(0, 0, 25) 
        glColor3f(0.0, 0.0, 0.0) 
        gluSphere(gluNewQuadric(), 15, 20, 20) 
        glPushMatrix()
        glTranslatef(0, 0, 35) # Above head
        ratio = z_hp / max_hp
        glPushMatrix()
        glColor3f(0.5, 0.0, 0.0) 
        glScalef(2.0, 0.2, 0.2) 
        glutSolidCube(20)        
        glPopMatrix()
        if ratio > 0:
            glPushMatrix()
            glColor3f(0.0, 1.0, 0.0) 
            glScalef(2.0 * ratio, 0.25, 0.25) 
            glutSolidCube(20)
            glPopMatrix()
        glPopMatrix()
        glPopMatrix()

# --- NEW: BULLET LOGIC ---
def update_bullets(): #  Advance bullets and resolve collisions with enemies and boss.
    global bullets, zombies, score, missed_count, final_boss_hp, final_boss_active, final_boss_pos, game_over, game_won
    floor_limit = 2 * GRID_LENGTH
    
    for b in bullets:
        b[0] += b[3] * BULLET_SPEED
        b[1] += b[4] * BULLET_SPEED
        
    for i in range(len(bullets) - 1, -1, -1):
        bx, by, bz, _, _ = bullets[i]
        hit = False
        
        for j in range(len(zombies) - 1, -1, -1):
            # unpack all 6 items, even if we only use zx, zy, hp
            zx, zy, hp, max_hp, speed, z_type = zombies[j] 
            
            dist = math.sqrt((bx - zx)**2 + (by - zy)**2)
            
            # Hitbox adjustment: Tanks are bigger, Sprinters smaller, Boss biggest
            if z_type == "BOSS":
                hit_radius = 80
            elif z_type == "TANK":
                hit_radius = 60
            elif z_type == "TYRANT":
                hit_radius = 70
            else:
                hit_radius = 35
            
            if dist < hit_radius: 
                zombies[j][2] -= 1 # Reduce HP
                hit = True
                
                if zombies[j][2] <= 0:
                    # Dynamic scoring based on zombie type and max HP
                    if z_type == "BOSS":
                        score += 50
                    elif z_type == "TANK":
                        score += 40 if max_hp >= 10 else 30
                    elif z_type == "TYRANT":
                        score += 35
                    elif z_type == "SPRINTER":
                        score += 15
                    else:
                        score += 10
                    del zombies[j]
                    check_win_condition()
                break 
        
        if hit:
            del bullets[i] 
        elif abs(bx) > floor_limit or abs(by) > floor_limit:
             missed_count += 1
             del bullets[i]

        # Final boss collision check
        if not hit and final_boss_active:
            dist_boss = math.sqrt((bx - final_boss_pos[0])**2 + (by - final_boss_pos[1])**2)
            hit_radius_boss = 90
            if dist_boss < hit_radius_boss:
                final_boss_hp -= 1
                hit = True
                if final_boss_hp <= 0:
                    final_boss_active = False
                    check_win_condition()
                del bullets[i]
             
def draw_bullets(): #  Render bullets as small spheres.
    glColor3f(1.0, 0.8, 0.0)
    for b in bullets:
        glPushMatrix()
        glTranslatef(b[0], b[1], b[2])
        gluSphere(gluNewQuadric(), 5, 12, 12)
        glPopMatrix()
# -------------------------

    def check_win_condition(): #  Ensure Level 3 win only after all enemies are eliminated.
        global game_level, final_boss_active, final_boss_spawned, zombies, game_over, game_won
        if game_over:
            return
        if game_level == 3 and final_boss_spawned and (not final_boss_active) and len(zombies) == 0:
            game_over = True
            game_won = True

                      
def draw_player_model(): #  Draw the player with limbs, head, and optional gun.
    """Draw a player model matching assignment3.py structure"""
    glPushMatrix()
    
    # Apply player position and rotation
    glTranslatef(player_pos[0], player_pos[1], player_pos[2])
    glRotatef(player_angle, 0, 0, 1)  # Rotate around z-axis
    
    # Left Leg
    glTranslatef(15, 0, 0)      
    glColor3f(0.0, 0.0, 1.0)
    gluCylinder(gluNewQuadric(), 5, 10, 50, 10, 10)  # base radius, top radius, height, slices, stacks
    
    # Right Leg
    glTranslatef(-30, 0, 0)     
    glColor3f(0.0, 0.0, 1.0)
    gluCylinder(gluNewQuadric(), 5, 10, 50, 10, 10) 
    
    # Body
    glTranslatef(15, 0, 50+20)  
    glColor3f(1.0, 0.647, 0.0)  # Orange color
    glutSolidCube(40)
    
    # Head
    glTranslatef(0, 0, 40)      
    glColor3f(0.0, 0.0, 0.0)  # Black
    gluSphere(gluNewQuadric(), 20, 10, 10)  # radius, slices, stacks
    
    # Left Arm
    glTranslatef(20, -60, -30)   
    glRotatef(-90, 1, 0, 0)      
    glColor3f(254/255, 223/255, 188/255)  # Skin color
    gluCylinder(gluNewQuadric(), 4, 8, 50, 10, 10)  # base radius, top radius, height, slices, stacks
    
    # Right Arm
    glRotatef(90, 1, 0, 0)      
    glTranslatef(-40, 0, 0)     
    glRotatef(-90, 1, 0, 0)     
    glColor3f(254/255, 223/255, 188/255)  # Skin color
    gluCylinder(gluNewQuadric(), 4, 8, 50, 10, 10)  # base radius, top radius, height, slices, stacks
    
    # Gun
    if gun_visible:
        glRotatef(90, 1, 0, 0)      # Reset rotation
        glTranslatef(10, -40, 5)    
        glRotatef(-90, 1, 0, 0)     
        glColor3f(192/255, 192/255, 192/255)  # Gray
        gluCylinder(gluNewQuadric(), 1, 10, 80, 10, 10)  # base radius, top radius, height, slices, stacks
    
    glPopMatrix()


def draw_bucket(): #  Render the bucket in hand or on ground with water surface.
    """Draw the bucket; attach to player hand when held."""
    glPushMatrix()
    bx, by, bz = get_bucket_world_position()

    glTranslatef(bx, by, bz)
    # Align bucket with player yaw when held so it stays stable in both camera modes
    if bucket_held:
        glRotatef(player_angle, 0, 0, 1)
    glColor3f(0.55, 0.27, 0.07)  # Brown bucket
    glutSolidCube(bucket_size)

    # Draw top surface to indicate water
    half = bucket_size * 0.5
    inset = bucket_size * 0.05  # almost full surface to match bucket top
    # Render water only when present; otherwise keep lid the same brown as the bucket
    if bucket_has_water:
        glColor3f(0.0, 0.4, 0.8)  # Water surface
    else:
        glColor3f(0.55, 0.27, 0.07)  # Match bucket color
    glBegin(GL_QUADS)
    glVertex3f(-half + inset, -half + inset, half + 0.01)
    glVertex3f( half - inset, -half + inset, half + 0.01)
    glVertex3f( half - inset,  half - inset, half + 0.01)
    glVertex3f(-half + inset,  half - inset, half + 0.01)
    glEnd()
    glPopMatrix()


def draw_seed_container(): #  Draw the seed container cube near the house.
    """Draw the cube-shaped seed container beside the house."""
    glPushMatrix()
    glTranslatef(seed_container_pos[0], seed_container_pos[1], seed_container_pos[2])
    glColor3f(0.8, 0.6, 0.2)  # Golden-brown container
    glutSolidCube(seed_container_size)
    glPopMatrix()


def generate_seed_lines(lines_per_cell=15): #  Create random seed line markers in brown area cells.
    """Generate short line markers within each brown grid cell (15 lines per cell)."""
    global seed_lines, seed_plant_time
    seed_plant_time = int(time.time() * 1000)
    grid_size = 13
    floor_length = 2 * GRID_LENGTH
    cell_size = (2 * floor_length) / grid_size

    # Brown area cells: rows 6-7, cols 2-10 (inclusive)
    row_indices = [6, 7]
    col_indices = list(range(2, 11))

    seed_lines = []
    for i in row_indices:
        for j in col_indices:
            cell_x1 = -floor_length + i * cell_size
            cell_x2 = cell_x1 + cell_size
            cell_y1 = -floor_length + j * cell_size
            cell_y2 = cell_y1 + cell_size
            for _ in range(lines_per_cell):
                rx = random.uniform(cell_x1, cell_x2)
                ry = random.uniform(cell_y1, cell_y2)
                seed_lines.append((rx, ry))


def draw_seed_lines(): #  Render planted seed rods that grow over time.
    """Render planted seed lines on the dark brown area."""
    if not seed_lines:
        return
    
# 1. Calculate time passed
    current_time = int(time.time() * 1000)
    elapsed_time = current_time - seed_plant_time
    
    max_growth_time = GROWTH_TIME_LIMIT
    final_height = 60.0
    
    growth_factor = min(elapsed_time, max_growth_time) / max_growth_time
    
    current_height = 2.0 + (final_height * growth_factor)
    
    glColor3f(0.1, 0.6, 0.1)
    for (rx, ry) in seed_lines:
        glPushMatrix()
        glTranslatef(rx, ry, current_height * 0.5)
        glScalef(1.5, 1.5, current_height)
        glutSolidCube(1)
        glPopMatrix()


def is_point_in_rect(px, py, rect): #  Check if a point lies within a UI rectangle.
    x, y, w, h = rect
    return x <= px <= x + w and y <= py <= y + h


def screen_to_ui_coords(mouse_x, mouse_y): #  Convert GLUT mouse coords to UI ortho coordinates.
    """Convert GLUT mouse coords (origin top-left) to our UI ortho (origin bottom-left)."""
    ui_x = mouse_x
    ui_y = 800 - mouse_y  # window height is 800
    return ui_x, ui_y


def can_player_move(): #  Determine if player input is allowed given UI state.
# --- DISABLE MOVE ON GAME OVER ---
    return (not ui_play_visible) and (not ui_paused) and (not game_over)


def restart_game(): #  Reset all game state and entities to initial conditions.
    global player_pos, player_angle, bucket_held, bucket_has_water, bucket_pos
    global brown_area_watered, seeds_equipped, seeds_prompt_visible, seed_lines
    global ui_paused, ui_play_visible, seed_plant_time,score,show_harvest_msg
    global zombies, zombies_spawned_flag, bullets, bullet_count, missed_count
    # --- Reset Level & Game Over ---
    global game_level, show_level_msg, game_over, game_won, zombies_entered_count
    global fence_health, fence_broken, torches, sprinkler_active, blades, blade_count
    global game_start_time, golden_seed_lines, seed_type
    global stored_crops, show_feed_animals_msg
    global final_boss_active, final_boss_spawned, final_boss_hp, final_boss_pos
    
    game_level = 1
    show_level_msg = False
    game_over = False
    game_won = False
    zombies_entered_count = 0
    player_pos = [0.0, 0.0, 0.0]
    player_angle = 0.0
    bucket_held = False
    bucket_has_water = False
    bucket_pos = [0.0, 0.0, bucket_size / 2]
    brown_area_watered = False
    seeds_equipped = False
    seeds_prompt_visible = True
    seed_lines = []
    seed_plant_time = 0
    score = 0
    zombies = []
    zombies_spawned_flag = False
    bullets = [] # Reset bullets
    # --- Reset Counts ---
    bullet_count = 0
    missed_count = 0
    ui_paused = False
    ui_play_visible = True
    game_start_time = 0
    
    # Level 2 resets
    fence_health = [100, 100, 100, 100]
    fence_broken = [False, False, False, False]
    torches = []
    blades = []
    blade_count = 0
    sprinkler_active = False
    golden_seed_lines = []
    seed_type = "NORMAL"
    final_boss_active = False
    final_boss_spawned = False
    final_boss_hp = 0
    final_boss_pos = [0.0, 0.0]
    
    # Crop storage reset
    stored_crops = 0
    show_feed_animals_msg = False
    

def get_bucket_world_position(): #  Compute bucket position in world space based on player.
    """Return bucket position in world space (in hand if held, else on ground)."""
    if bucket_held:
        angle_rad = math.radians(player_angle)
        # Place bucket at front edge of right hand (visible in first-person)
        forward = 30.0
        right = 12.0
        hand_height = 85.0
        forward_x = math.sin(angle_rad)
        forward_y = -math.cos(angle_rad)
        right_x = math.cos(angle_rad)
        right_y = math.sin(angle_rad)
        bx = player_pos[0] + forward * forward_x + right * right_x
        by = player_pos[1] + forward * forward_y + right * right_y
        bz = player_pos[2] + hand_height
        return bx, by, bz
    return bucket_pos[0], bucket_pos[1], bucket_pos[2]


def is_near_house(x, y, radius=BUCKET_EQUIP_RADIUS): #  Check proximity to the house within equip radius.
    """Check if player is within equip radius of the house."""
    cx, cy = get_house_center()
    return math.hypot(x - cx, y - cy) <= radius


def is_in_pond(x, y): #  Determine if a world position lies within pond cells.
    """Check if world position (x,y) is within actual pond grid area (for sinking)."""
    grid_size = 13
    floor_length = 2 * GRID_LENGTH
    cell_size = (2 * floor_length) / grid_size
    i = int((x + floor_length) / cell_size)
    j = int((y + floor_length) / cell_size)
    if i < 0 or i >= grid_size or j < 0 or j >= grid_size:
        return False
    return 8 <= i <= 10 and 2 <= j <= 10


def is_near_pond(x, y, margin=50): #  Check proximity to pond bounds within margin.
    """Check if position is within margin distance from pond boundary (for water pickup)."""
    grid_size = 13
    floor_length = 2 * GRID_LENGTH
    cell_size = (2 * floor_length) / grid_size
    
    # Calculate pond boundaries
    x1 = -floor_length + 8 * cell_size
    x2 = -floor_length + 11 * cell_size
    y1 = -floor_length + 2 * cell_size
    y2 = -floor_length + 11 * cell_size
    
    # Check if position is within pond bounds plus margin
    return (x1 - margin) <= x <= (x2 + margin) and (y1 - margin) <= y <= (y2 + margin)


def is_near_brown_area(x, y, margin=50): #  Check proximity to brown farming area within margin.
    """Check if position is within margin distance from brown area boundary."""
    grid_size = 13
    floor_length = 2 * GRID_LENGTH
    cell_size = (2 * floor_length) / grid_size
    
    # Calculate brown area boundaries (rows 6-7, columns 2-10)
    x1 = -floor_length + 6 * cell_size
    x2 = -floor_length + 8 * cell_size
    y1 = -floor_length + 2 * cell_size
    y2 = -floor_length + 11 * cell_size
    
    # Check if position is within brown area bounds plus margin
    return (x1 - margin) <= x <= (x2 + margin) and (y1 - margin) <= y <= (y2 + margin)


def is_near_seed_container(x, y, radius=SEED_EQUIP_RADIUS): #  Check proximity to the seed container.
    """Check if player is within equip radius of the seed container."""
    return math.hypot(x - seed_container_pos[0], y - seed_container_pos[1]) <= radius


def is_near_cow(x, y, radius=320): #  Check proximity to any cow for interaction.
    """Check if player is within interaction radius of any cow (main or herd)."""
    positions = [(cow_pos[0], cow_pos[1])] + [(hc['pos'][0], hc['pos'][1]) for hc in herd]
    for cx, cy in positions:
        if math.hypot(x - cx, y - cy) <= radius:
            return True
    return False

def is_near_fence(x, y, margin=60): #  Check proximity to any farm fence segment.
    """Check if player is near any fence segment of the farm area."""
    x_min, x_max = FARM_RECT['x_min'], FARM_RECT['x_max']
    y_min, y_max = FARM_RECT['y_min'], FARM_RECT['y_max']
    near_bottom = abs(y - y_min) <= margin and (x_min - 20 <= x <= x_max + 20)
    near_top = abs(y - y_max) <= margin and (x_min - 20 <= x <= x_max + 20)
    near_left = abs(x - x_min) <= margin and (y_min - 20 <= y <= y_max + 20)
    near_right = abs(x - x_max) <= margin and (y_min - 20 <= y <= y_max + 20)
    return near_bottom or near_top or near_left or near_right

def get_cow_count_in_farm(): #  Return total cows in the farm (main plus herd).
    """Count cows in animal area: main cow + herd."""
    return 1 + len(herd)


def is_inside_house(x, y): #  Test collision inside house footprint with margin.
    """Check if position (x,y) is inside the house boundaries."""
    grid_size = 13
    floor_length = 2 * GRID_LENGTH
    cell_size = (2 * floor_length) / grid_size
    col_start = 1
    col_end = 1
    row_start = 5
    row_end = 7

    x1 = -floor_length + col_start * cell_size
    x2 = -floor_length + (col_end + 1) * cell_size
    y1 = -floor_length + row_start * cell_size
    y2 = -floor_length + (row_end + 1) * cell_size

    # Add small margin for collision
    margin = 20
    return (x1 - margin) <= x <= (x2 + margin) and (y1 - margin) <= y <= (y2 + margin)


def is_inside_shop(x, y): #  Test collision inside shop footprint with margin.
    """Check if position (x,y) is inside the shop boundaries."""
    grid_size = 13
    floor_length = 2 * GRID_LENGTH
    cell_size = (2 * floor_length) / grid_size
    col_start = 1
    col_end = 1
    row_start = 8
    row_end = 10

    x1 = -floor_length + col_start * cell_size
    x2 = -floor_length + (col_end + 1) * cell_size
    y1 = -floor_length + row_start * cell_size
    y2 = -floor_length + (row_end + 1) * cell_size

    # Add small margin for collision
    margin = 20
    return (x1 - margin) <= x <= (x2 + margin) and (y1 - margin) <= y <= (y2 + margin)


def update_player_height(): #  Set player Z based on water sinking in pond tiles.
    """Lower the player when standing on water tiles."""
    player_pos[2] = WATER_SINK_OFFSET if is_in_pond(player_pos[0], player_pos[1]) else 0.0
    
def draw_cylinder_segment(x1, y1, z1, x2, y2, z2, radius, r, g, b): #  Draw a cylinder between two points for fence segments.
    """Helper to draw a cylinder (bamboo/wood) between two points."""
    dx = x2 - x1
    dy = y2 - y1
    dz = z2 - z1
    dist = math.sqrt(dx*dx + dy*dy + dz*dz)

    glPushMatrix()
    glTranslatef(x1, y1, z1)
    
    # Calculate rotation to align cylinder with the vector (dx, dy, dz)
    if dist > 0:
        # Angle with Z axis
        angle = math.acos(dz / dist) * 180.0 / math.pi
        if dz < 0:
            angle = -angle
        # Axis of rotation is cross product of Z axis and vector
        ax = -dy * dz
        ay = dx * dz
        az = 0 # Z cross Z is 0
        if ax == 0 and ay == 0:
            # Case where vector is parallel to Z (no rotation needed or 180 flip)
            if dz < 0: glRotatef(180, 1, 0, 0)
        else:
            glRotatef(angle, -dy, dx, 0) # Simplified cross product axis

    glColor3f(r, g, b)
    gluCylinder(gluNewQuadric(), radius, radius, dist, 8, 1)
    glPopMatrix()


def draw_bamboo_fence(): #  Render the farm fence, skipping broken sections and gate.
    """Draws fence, skipping broken sections."""
    x_min, x_max = FARM_RECT['x_min'], FARM_RECT['x_max']
    y_min, y_max = FARM_RECT['y_min'], FARM_RECT['y_max']
    
    post_radius = 4; rail_radius = 2; height = 110; density = 20
    br, bg, bb = 0.76, 0.60, 0.42

    # Define the 4 sides: Bottom, Right(Gate), Top, Left
    # Coordinates for each wall
    walls = [
        (x_min, y_min, x_max, y_min, False), # 0: Bottom
        (x_max, y_min, x_max, y_max, True),  # 1: Right (Gate)
        (x_max, y_max, x_min, y_max, False), # 2: Top
        (x_min, y_max, x_min, y_min, False)  # 3: Left
    ]

    for i, (x1, y1, x2, y2, is_gate) in enumerate(walls):
        # IF FENCE IS BROKEN, DRAW RUBBLE INSTEAD
        if fence_broken[i]:
            glColor3f(0.5, 0.3, 0.2) # Darker broken wood
            mid_x = (x1 + x2) / 2
            mid_y = (y1 + y2) / 2
            glPushMatrix()
            glTranslatef(mid_x, mid_y, 5)
            glScalef(1.0, 0.2, 0.2) if i%2==0 else glScalef(0.2, 1.0, 0.2) # Align with wall
            glutSolidCube(40) # Rubble pile
            glPopMatrix()
            continue # Skip drawing the actual fence
            
        # --- ORIGINAL DRAWING LOGIC ---
        length = math.hypot(x2-x1, y2-y1)
        steps = int(length / density)
        
        for k in range(steps + 1):
            t = k / steps
            px = x1 + (x2 - x1) * t
            py = y1 + (y2 - y1) * t
            if is_gate and 0.35 < t < 0.65: continue
            
            glPushMatrix()
            glTranslatef(px, py, 0)
            glColor3f(br, bg, bb)
            gluCylinder(gluNewQuadric(), post_radius, post_radius, height, 8, 1)
            glPopMatrix()

def draw_cow(x, y, angle): #  Render a cow oriented to its movement direction.
    """Draws a cow rotated to face its movement direction."""
    glPushMatrix()
    glTranslatef(x, y, 50) 
    
    # --- NEW: Apply Rotation ---
    glRotatef(angle, 0, 0, 1) # Rotate around Z-axis based on movement
    # ---------------------------

    glScalef(2.5, 2.5, 2.5)
    
    # 1. Body
    glPushMatrix()
    glScalef(2.0, 1.0, 1.0) 
    glColor3f(0.9, 0.9, 0.9) 
    glutSolidCube(30)
    glPopMatrix()
    
    # 2. Spots
    glPushMatrix()
    glTranslatef(10, 5, 5)
    glColor3f(0.1, 0.1, 0.1) 
    glutSolidCube(12)
    glPopMatrix()

    # 3. Head
    glPushMatrix()
    glTranslatef(30, 0, 15)
    glColor3f(0.9, 0.9, 0.9)
    glutSolidCube(20)
    
    # Eyes
    glColor3f(0.0, 0.0, 0.0) 
    glPushMatrix()
    glTranslatef(10.1, 5, 3) 
    glutSolidCube(3)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(10.1, -5, 3) 
    glutSolidCube(3)
    glPopMatrix()
    
    # Horns
    glColor3f(0.6, 0.6, 0.6) 
    glPushMatrix()
    glTranslatef(5, 5, 10) 
    glRotatef(-45, 0, 1, 0)
    gluCylinder(gluNewQuadric(), 2, 0, 10, 8, 1)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(5, -5, 10) 
    glRotatef(-45, 0, 1, 0)
    gluCylinder(gluNewQuadric(), 2, 0, 10, 8, 1)
    glPopMatrix()
    glPopMatrix() 

    # 4. Tail
    glPushMatrix()
    glTranslatef(-30, 0, 5) 
    glRotatef(-45, 0, 1, 0)  
    glColor3f(0.9, 0.9, 0.9)
    glScalef(1.5, 0.2, 0.2) 
    glutSolidCube(10)
    glScalef(1/1.5, 1/0.2, 1/0.2) 
    glTranslatef(-8, 0, 0) 
    glColor3f(0.1, 0.1, 0.1) 
    glutSolidCube(4)
    glPopMatrix()

    # 5. Legs
    glColor3f(0.9, 0.9, 0.9)
    leg_coords = [(-20, -10), (-20, 10), (20, -10), (20, 10)]
    for lx, ly in leg_coords:
        glPushMatrix()
        glTranslatef(lx, ly, -15)
        glScalef(0.5, 0.5, 1.5)
        glutSolidCube(15)
        glPopMatrix()

    glPopMatrix()

    

def update_cow_behavior(): #  Update the main cow’s wandering, rotation, and movement.
    """Handles random cow movement: Long pauses, then rotation and movement."""
    global cow_pos, cow_target, cow_moving, cow_idle_start_time, cow_angle
    
    if game_level < 2:
        return

    current_time = int(time.time() * 1000)

    # 1. Logic: If Idle, wait for a LONG time (Realism)
    if not cow_moving:
        # Wait for 8 to 15 seconds (Much slower behavior)
        if current_time - cow_idle_start_time > random.randint(25000, 30000):
            padding = 80 
            rand_x = random.uniform(FARM_RECT['x_min'] + padding, FARM_RECT['x_max'] - padding)
            rand_y = random.uniform(FARM_RECT['y_min'] + padding, FARM_RECT['y_max'] - padding)
            
            cow_target = [rand_x, rand_y]
            
            # --- Calculate Rotation Angle ---
            # The cow rotates to face the new target BEFORE it starts moving
            dx = rand_x - cow_pos[0]
            dy = rand_y - cow_pos[1]
            
            # Calculate angle in degrees
            cow_angle = math.degrees(math.atan2(dy, dx))
            # -------------------------------------

            cow_moving = True

    # 2. Logic: Move towards target
    else:
        cx, cy = cow_pos
        tx, ty = cow_target
        
        dx = tx - cx
        dy = ty - cy
        dist = math.sqrt(dx*dx + dy*dy)
        
        # If very close to target, stop.
        if dist < COW_SPEED:
            cow_pos = [tx, ty]
            cow_moving = False
            cow_idle_start_time = current_time # Start the long wait again
        else:
            # Move forward
            vx = (dx / dist) * COW_SPEED
            vy = (dy / dist) * COW_SPEED
            cow_pos[0] += vx
            cow_pos[1] += vy

    
                
def update_herd_behavior(): #  Update purchased herd cows’ wandering and movement.
    """Update movement for all purchased cows in the herd."""
    global herd
    if not herd:
        return

    current_time = int(time.time() * 1000)
    for cow in herd:
        if not cow['moving']:
            if current_time - cow['idle_start'] > random.randint(25000, 30000):
                padding = 80
                rand_x = random.uniform(FARM_RECT['x_min'] + padding, FARM_RECT['x_max'] - padding)
                rand_y = random.uniform(FARM_RECT['y_min'] + padding, FARM_RECT['y_max'] - padding)
                cow['target'] = [rand_x, rand_y]
                dx = rand_x - cow['pos'][0]
                dy = rand_y - cow['pos'][1]
                cow['angle'] = math.degrees(math.atan2(dy, dx))
                cow['moving'] = True
        else:
            cx, cy = cow['pos']
            tx, ty = cow['target']
            dx = tx - cx
            dy = ty - cy
            dist = math.sqrt(dx*dx + dy*dy)
            if dist < COW_SPEED:
                cow['pos'] = [tx, ty]
                cow['moving'] = False
                cow['idle_start'] = current_time
            else:
                vx = (dx / dist) * COW_SPEED
                vy = (dy / dist) * COW_SPEED
                cow['pos'][0] += vx
                cow['pos'][1] += vy

def update_farm_status(): #  Toggle locked farm UI based on player position and level.
    """Checks if player is stepping on the locked farm area."""
    global show_locked_msg
    if game_level == 1:
        px, py = player_pos[0], player_pos[1]
        # Check if inside FARM_RECT
        if (FARM_RECT['x_min'] <= px <= FARM_RECT['x_max'] and 
            FARM_RECT['y_min'] <= py <= FARM_RECT['y_max']):
            show_locked_msg = True
        else:
            show_locked_msg = False
    else:
        show_locked_msg = False    

def is_colliding_with_cow(x, y): #  Prevent walking through the cow via hitbox test.
    """Prevents player from walking through the Cow (Dynamic Position)."""
    if game_level < 2: 
        return False
        
    # USE GLOBAL COW POSITION
    cx, cy = cow_pos[0], cow_pos[1]
    
    # Cow Dimensions (approx based on scale 2.5)
    hitbox_len = 95
    hitbox_wid = 60
    
    return (cx - hitbox_len <= x <= cx + hitbox_len) and \
           (cy - hitbox_wid <= y <= cy + hitbox_wid)


def is_colliding_with_fence(x, y): #  Prevent walking through fence unless broken/gate area.
    """Prevents walking through fence unless broken."""
    if game_level < 2: return False

    x_min, x_max = FARM_RECT['x_min'], FARM_RECT['x_max']
    y_min, y_max = FARM_RECT['y_min'], FARM_RECT['y_max']
    thickness = 15 
    
    if not (x_min - 30 <= x <= x_max + 30 and y_min - 30 <= y <= y_max + 30):
        return False

    # 0: Bottom Wall (Check if NOT broken)
    if not fence_broken[0] and abs(y - y_min) < thickness and x_min <= x <= x_max:
        return True
    # 2: Top Wall
    if not fence_broken[2] and abs(y - y_max) < thickness and x_min <= x <= x_max:
        return True
    # 3: Left Wall
    if not fence_broken[3] and abs(x - x_min) < thickness and y_min <= y <= y_max:
        return True
    # 1: Right Wall (Gate Side)
    if not fence_broken[1] and abs(x - x_max) < thickness:
        wall_len = y_max - y_min
        gate_start = y_min + (wall_len * 0.35)
        gate_end = y_min + (wall_len * 0.65)
        if not (gate_start <= y <= gate_end):
            return True
            
    return False  

def draw_torch(x, y): #  Draw a torch with a wooden stick and flame.
    """Draws a simple torch stand."""
    glPushMatrix()
    glTranslatef(x, y, 0)
    glColor3f(0.4, 0.2, 0.0)
    gluCylinder(gluNewQuadric(), 3, 3, 40, 6, 1)
    glTranslatef(0, 0, 40)
    glColor3f(1.0, 0.5, 0.0)
    gluSphere(gluNewQuadric(), 8, 16, 16)
    glColor3f(1.0, 1.0, 0.0) 
    gluSphere(gluNewQuadric(), 4, 16, 16)
    glPopMatrix()

def draw_sprinkler(x, y): #  Draw a spinning sprinkler with a rotating arm.
    """Draws a spinning sprinkler."""
    glPushMatrix()
    glTranslatef(x, y, 0)
    glColor3f(0.5, 0.5, 0.5)
    glutSolidCube(10)
    glTranslatef(0, 0, 10)
    rot = (int(time.time() * 1000) / 5) % 360
    glRotatef(rot, 0, 0, 1)
    glColor3f(0.0, 0.0, 1.0) # Blue
    glPushMatrix()
    glScalef(30, 4, 2)
    glutSolidCube(1)
    glPopMatrix()
    glPopMatrix()

def draw_blade(x, y): #  Draw a large rotating three-armed blade trap.
    """Draws a fan-like blade with 3 rotating arms (10x larger, like a sprinkler)."""
    glPushMatrix()
    glTranslatef(x, y, 0)
    
    # Base/Hub (10x larger)
    glColor3f(0.4, 0.4, 0.4)
    # Replace glutSolidSphere with gluSphere
    gluSphere(gluNewQuadric(), 80, 20, 20)
    
    # Rotating arms (3 blades, 120 degrees apart)
    rot = (int(time.time() * 1000) / 3) % 360  # Spin faster than sprinkler
    glRotatef(rot, 0, 0, 1)
    
    glColor3f(0.2, 0.6, 0.8)  # Light blue
    arm_length = 400  # 10x larger
    arm_width = 60    # 10x larger
    
    # Draw 3 arms at 120-degree intervals
    for i in range(3):
        glPushMatrix()
        glRotatef(i * 120, 0, 0, 1)
        glTranslatef(arm_length / 2, 0, 0)
        glScalef(arm_length, arm_width, 30)  # 10x in z as well
        glutSolidCube(1)
        glPopMatrix()
    
    glPopMatrix()


def draw_final_boss(x, y): #  Render the cube-based robot final boss scaled up.
    """Draw a cube-based robot boss."""
    glPushMatrix()
    glTranslatef(x, y, 60)
    glScalef(8.0, 8.0, 8.0)

    glColor3f(0.2, 0.2, 0.2)
    glPushMatrix()
    glTranslatef(0, 0, 12)
    glScalef(18, 12, 16)
    glutSolidCube(2)
    glPopMatrix()

    glColor3f(0.3, 0.3, 0.35)
    glPushMatrix()
    glTranslatef(0, 0, 26)
    glScalef(10, 10, 10)
    glutSolidCube(2)
    glPopMatrix()

    glColor3f(1.0, 0.0, 0.0)
    glPushMatrix(); glTranslatef(6, 4, 28); gluSphere(gluNewQuadric(), 1.5, 10, 10); glPopMatrix()
    glPushMatrix(); glTranslatef(6, -4, 28); gluSphere(gluNewQuadric(), 1.5, 10, 10); glPopMatrix()

    glColor3f(0.25, 0.25, 0.3)
    for offset in (-12, 12):
        glPushMatrix()
        glTranslatef(0, offset, 12)
        glScalef(14, 4, 4)
        glutSolidCube(2)
        glPopMatrix()

    glColor3f(0.18, 0.18, 0.22)
    for offset in (-5, 5):
        glPushMatrix()
        glTranslatef(-4, offset, -6)
        glScalef(5, 5, 12)
        glutSolidCube(2)
        glPopMatrix()

    glPopMatrix()


def draw_golden_corn(): #  Render golden corn rods growing over time.
    """Render Golden Corn lines."""
    if not golden_seed_lines:
        return
    
    current_time = int(time.time() * 1000)
    elapsed_time = current_time - seed_plant_time
    
    max_growth = GOLD_GROWTH_TIME
    final_height = 80.0 
    growth_factor = min(elapsed_time, max_growth) / max_growth
    current_height = 2.0 + (final_height * growth_factor)
    
    glColor3f(1.0, 0.84, 0.0)
    for (rx, ry) in golden_seed_lines:
        glPushMatrix()
        glTranslatef(rx, ry, current_height * 0.5)
        glScalef(1.5, 1.5, current_height)
        glutSolidCube(1)
        glPopMatrix()

def reset_modelview_stack(): #  No-op to avoid querying modelview stack depth.
    """No-op to avoid using glGetIntegerv; ensure matching push/pop usage."""
    return

def get_zombie_speed_multiplier(zx, zy): #  Compute speed multiplier based on torch proximity.
    """Returns 0.5 if zombie is near a torch, else 1.0"""
    for t in torches:
        dist = math.hypot(zx - t['x'], zy - t['y'])
        if dist < TORCH_RADIUS:
            return 0.4 # Slow down significantly
    return 1.0    

def keyboardListener(key, x, y): #  Handle keyboard inputs for movement, actions, and camera.
    """
    Handles keyboard inputs for player movement, gun rotation, camera updates, and cheat mode toggles.
    """
    global player_pos, player_angle, gun_visible, bucket_held, bucket_pos, mode_first_person, seeds_equipped, ui_paused, ui_play_visible
    global score, seed_lines, golden_seed_lines, brown_area_watered, seeds_prompt_visible, show_harvest_msg, last_harvest_time
    global zombies, zombies_spawned_flag, bullets, bullet_count
    global sprinkler_active, sprinkler_start_time, sprinkler_pos, seed_type, seed_plant_time
    global game_level, show_level_msg, level_msg_start_time, game_start_time
    global stored_crops, show_feed_animals_msg, feed_animals_msg_time, crop_equipped, blade_count
    # Pause/resume (ESC)
    if key == b'\x1b':
        if ui_play_visible:
            return
        ui_paused = not ui_paused
        return

    if not can_player_move():
        return

    # Toggle gun visibility (G key)
    if key == b'g' or key == b'G':
        gun_visible = not gun_visible
        if gun_visible:
             bullet_count = 10
        return

    # F key: Feed cow when carrying crop near fence; else toggle camera
    if key == b'f' or key == b'F':
        if crop_equipped and game_level >= 3 and is_near_fence(player_pos[0], player_pos[1]):
            if stored_crops >= 1:
                stored_crops -= 1
                crop_equipped = False
                # Feeding the cows rewards score
                score += 200
                show_feed_animals_msg = True
                feed_animals_msg_time = int(time.time() * 1000)
            return
        # Default: toggle camera
        mode_first_person = not mode_first_person
        return

    # --- CHEAT KEYS ---
    # Cheat: Jump to Level 2 (Key '2')
    if key == b'2':
        if game_level == 1:
            game_level = 2
            zombies = []
            show_level_msg = True
            level_msg_start_time = int(time.time() * 1000)
        return
    
    # Cheat: Jump to Level 3 (Key '3')
    if key == b'3':
        if game_level == 1 or game_level == 2:
            game_level = 3
            zombies = []
            show_level_msg = True
            level_msg_start_time = int(time.time() * 1000)
            # Ensure Level 3 starts with 2 cows: add one to herd if none
            if len(herd) < 1:
                padding = 80
                start_x = random.uniform(FARM_RECT['x_min'] + padding, FARM_RECT['x_max'] - padding)
                start_y = random.uniform(FARM_RECT['y_min'] + padding, FARM_RECT['y_max'] - padding)
                now = int(time.time() * 1000)
                herd.append({
                    'pos': [start_x, start_y],
                    'target': [start_x, start_y],
                    'moving': False,
                    'idle_start': now,
                    'angle': 0.0
                })
        return
    
    # Cheat: Start Night Cycle (Key 'N')
    if key == b'n' or key == b'N':
        if game_start_time > 0:
            # Force night by setting game_start_time to make it night
            # Night occurs during TRANSITION_TIME to TRANSITION_TIME + NIGHT_HOLD_TIME
            TRANSITION_TIME = 2 * 60 * 1000
            # Set time so we're just entering the night phase
            current = int(time.time() * 1000)
            game_start_time = current - TRANSITION_TIME - 1000  # 1 second into night
        return
    
    # Cheat: Add 50 Score (Key '+')
    if key == b'+':
        score += 50
        return
    # --- END CHEAT KEYS ---

    # Key: Increase stored crops (0)
    if key == b'0':
        stored_crops += 1
        return

    # B key: Buy an additional cow at the shop (Level 3)
    if key == b'b' or key == b'B':
        if game_level >= 3 and is_near_shop(player_pos[0], player_pos[1]):
            if score >= 150:
                score -= 150
                # Spawn a new cow in the farm area
                padding = 80
                start_x = random.uniform(FARM_RECT['x_min'] + padding, FARM_RECT['x_max'] - padding)
                start_y = random.uniform(FARM_RECT['y_min'] + padding, FARM_RECT['y_max'] - padding)
                now = int(time.time() * 1000)
                herd.append({
                    'pos': [start_x, start_y],
                    'target': [start_x, start_y],
                    'moving': False,
                    'idle_start': now,
                    'angle': 0.0
                })
        return

    # E key: Plant seeds, refill ammo, equip bucket, or equip seeds
    if key == b'e' or key == b'E':
        # 0. Buy Blade at shop on Level 3
        if game_level >= 3 and is_near_shop(player_pos[0], player_pos[1]):
            if score >= 450:
                score -= 450
                blade_count += 1
            return
        # 1. Priority: Plant seeds if equipped and in brown area
        if seeds_equipped and seeds_prompt_visible and brown_area_watered:
            if is_near_brown_area(player_pos[0], player_pos[1], margin=100):
                seeds_prompt_visible = False
                
                # --- NEW: Check Seed Type ---
                if seed_type == "GOLD":
                    # Generate Yellow Lines
                    golden_seed_lines = []
                    grid_size = 13; floor_len = 2 * GRID_LENGTH; cell = (2 * floor_len) / grid_size
                    for i in [6, 7]:
                        for j in range(2, 11):
                            cx1 = -floor_len + i * cell; cy1 = -floor_len + j * cell
                            for _ in range(15):
                                rx = random.uniform(cx1, cx1 + cell)
                                ry = random.uniform(cy1, cy1 + cell)
                                golden_seed_lines.append((rx, ry))
                    
                    # Set Timer
                    seed_plant_time = int(time.time() * 1000)
                    score += 5 
                    
                else:
                    # Normal Planting
                    generate_seed_lines() 
                    score += 5
                # -----------------------------
                return
        
        # 2. Refill ammo at house if ammo is empty
        if bullet_count <= 0 and is_near_house(player_pos[0], player_pos[1], radius=BUCKET_EQUIP_RADIUS):
            bullet_count = 20
            return
        
        # 3. Equip bucket at house
        if not bucket_held and is_near_house(player_pos[0], player_pos[1]):
            bucket_held = True
            return
        
        # 4. Equip seeds at seed container
        if not seeds_equipped and is_near_seed_container(player_pos[0], player_pos[1]):
            if brown_area_watered:
                seeds_equipped = True
            return
# --- HARVEST LOGIC ---
    if key == b'h' or key == b'H':
        current = int(time.time() * 1000)
        
        # 1. Check for NORMAL Crops
        if seed_lines:
            if current - seed_plant_time >= GROWTH_TIME_LIMIT: # 45 seconds
                if is_near_brown_area(player_pos[0], player_pos[1]):
                    score += 10                  
                    seed_lines = []              # Clear crops
                    # Store 3 crops at level 3, otherwise 1
                    stored_crops += 3 if game_level >= 3 else 1
                    
                    # --- FIX: Don't dry the land if sprinkler is active ---
                    if not sprinkler_active:
                        brown_area_watered = False
                        seeds_prompt_visible = True
                    # ------------------------------------------------------

                    seeds_equipped = False
                    
                    last_harvest_time = current
                    show_harvest_msg = True
                    return

        # 2. Check for GOLDEN Crops (Level 2)
        if golden_seed_lines:
            if current - seed_plant_time >= GOLD_GROWTH_TIME: # 60 seconds
                if is_near_brown_area(player_pos[0], player_pos[1]):
                    score += 25                  
                    golden_seed_lines = []       # Clear crops
                    # Store 3 crops at level 3, otherwise 1
                    stored_crops += 3 if game_level >= 3 else 1
                    
                    # --- FIX: Don't dry the land if sprinkler is active ---
                    if not sprinkler_active:
                        brown_area_watered = False
                        seeds_prompt_visible = True
                    # ------------------------------------------------------
                    
                    seeds_equipped = False
                    
                    last_harvest_time = current
                    show_harvest_msg = True
                    return
    
    # C key: Equip a crop for feeding (Level 3 only)
    if key == b'c' or key == b'C':
        if game_level >= 3 and is_near_house(player_pos[0], player_pos[1]):
            if stored_crops >= 1:
                crop_equipped = True
                show_feed_animals_msg = True
                feed_animals_msg_time = int(time.time() * 1000)
        return
    
    # Store current position
    current_x, current_y = player_pos[0], player_pos[1]
    new_x, new_y = current_x, current_y
    
    # Move forward (W key)
    if key == b'w' or key == b'W':
        new_x += PLAYER_SPEED * math.sin(math.radians(player_angle))
        new_y -= PLAYER_SPEED * math.cos(math.radians(player_angle))

    # Move backward (S key)
    if key == b's' or key == b'S':
        new_x -= PLAYER_SPEED * math.sin(math.radians(player_angle))
        new_y += PLAYER_SPEED * math.cos(math.radians(player_angle))
    if key == b'r' or key == b'R':
        if gun_visible:
            # Only allow shooting if there's ammo left
            if bullet_count > 0:
                # Bullet math
                angle_rad = math.radians(player_angle)
                dx = math.sin(angle_rad)
                dy = -math.cos(angle_rad)
                
                # Start from player center, slightly raised
                bx = player_pos[0]
                by = player_pos[1]
                bz = player_pos[2] + 45 # Height of gun roughly
                
                bullets.append([bx, by, bz, dx, dy])
                bullet_count -= 1 # Decrease ammo
        return
    # -------------------
    # Clamp player position to current floor size (floor spans -2*GRID_LENGTH to +2*GRID_LENGTH)
# ... previous movement code (calculating new_x, new_y) ...

    # Clamp player position to current floor size
    boundary_margin = 30  
    floor_half_extent = 2 * GRID_LENGTH
    max_range = floor_half_extent - boundary_margin
    new_x = max(-max_range, min(max_range, new_x))
    new_y = max(-max_range, min(max_range, new_y))
    
    # --- UPDATED COLLISION CHECK ---
    # Check House AND Shop AND Cow AND Fence
    if (not is_inside_house(new_x, new_y) and 
        not is_inside_shop(new_x, new_y) and 
        not is_colliding_with_cow(new_x, new_y) and 
        not is_colliding_with_fence(new_x, new_y)):
        
        player_pos[0] = new_x
        player_pos[1] = new_y
        update_player_height()
    # -------------------------------

    # Rotate left (A key)
    if key == b'a' or key == b'A':
        player_angle += 5.0
        player_angle %= 360

    # Rotate right (D key)
    if key == b'd' or key == b'D':
        player_angle -= 5.0
        player_angle %= 360
    
    # ... inside keyboardListener ...
    
    # --- LEVEL 2+ CONTROLS ---
    if game_level >= 2:
        # 1. Switch Seeds (Z)
        if key == b'z' or key == b'Z':
            seed_type = "GOLD" if seed_type == "NORMAL" else "NORMAL"
            return

        # 2. Place Torch (T) - Cost 20
        if key == b't' or key == b'T':
            if score >= TORCH_COST:
                score -= TORCH_COST
                torches.append({'x': player_pos[0], 'y': player_pos[1]})
            return

        # 3. Place Sprinkler (K) - Cost 50
        if key == b'k' or key == b'K':
            # Must be on brown area
            if score >= SPRINKLER_COST and is_near_brown_area(player_pos[0], player_pos[1]):
                score -= SPRINKLER_COST
                sprinkler_active = True
                sprinkler_start_time = int(time.time() * 1000)
                sprinkler_pos = (player_pos[0], player_pos[1])
            return
        
        # 5. Remove Sprinkler (X)
        if key == b'x' or key == b'X':
            # Check if player is near the farm and sprinkler exists
            if sprinkler_active and is_near_brown_area(player_pos[0], player_pos[1]):
                sprinkler_active = False
            return
        
        # 4. Repair Fence (P)
        if key == b'p' or key == b'P':
            # Check which wall is close
            px, py = player_pos[0], player_pos[1]
            repair_range = 100
            cost = 10
            if score >= cost:
                # Bottom
                if fence_broken[0] and abs(py - FARM_RECT['y_min']) < repair_range:
                    fence_broken[0] = False; fence_health[0] = 100; score -= cost
                # Top
                elif fence_broken[2] and abs(py - FARM_RECT['y_max']) < repair_range:
                    fence_broken[2] = False; fence_health[2] = 100; score -= cost
                # Left
                elif fence_broken[3] and abs(px - FARM_RECT['x_min']) < repair_range:
                    fence_broken[3] = False; fence_health[3] = 100; score -= cost
                # Right
                elif fence_broken[1] and abs(px - FARM_RECT['x_max']) < repair_range:
                    fence_broken[1] = False; fence_health[1] = 100; score -= cost
    # ------------------------

def specialKeyListener(key, x, y): #  Handle arrow keys to adjust camera in third-person.
    """
    Handles special key inputs (arrow keys) for adjusting the camera angle and height.
    """
    global camera_pos, camera_angle, camera_distance
    if mode_first_person:
        return
    cx, cy, cz = camera_pos
    
    # Move camera up (UP arrow key)
    if key == GLUT_KEY_UP:
        cz += 3  # Increase height

    # Move camera down (DOWN arrow key)
    if key == GLUT_KEY_DOWN:
        cz -= 3  # Decrease height
        if cz < 50:  # Don't go below floor
            cz = 50

    # Rotate camera left (LEFT arrow key)
    if key == GLUT_KEY_LEFT:
        camera_angle += 3  # Rotate counterclockwise

    # Rotate camera right (RIGHT arrow key)
    if key == GLUT_KEY_RIGHT:
        camera_angle -= 3  # Rotate clockwise

    # Calculate new camera position based on angle
    cx = camera_distance * math.cos(math.radians(camera_angle))
    cy = camera_distance * math.sin(math.radians(camera_angle))
    
    camera_pos = (cx, cy, cz)


def mouseListener(button, state, x, y): #  Handle mouse inputs for firing, planting blades, and UI clicks.
    """
    Handles mouse inputs for firing bullets (left click) and toggling camera mode (right click).
    """
    global game_start_time, bucket_has_water, brown_area_watered, seeds_prompt_visible, ui_play_visible, ui_paused, seeds_equipped, seed_plant_time, score
    global show_level_msg, level_msg_start_time
    global golden_seed_lines, seed_type, blade_count, blades
    # UI clicks (convert to UI coords)
    ui_x, ui_y = screen_to_ui_coords(x, y)

    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        # Play click
        if ui_play_visible and is_point_in_rect(ui_x, ui_y, UI_PLAY_RECT):
            ui_play_visible = False
            ui_paused = False
            game_start_time = int(time.time() * 1000)
            # NEW: Trigger Level 1 Message
            show_level_msg = True
            level_msg_start_time = int(time.time() * 1000)
            return
        # --- NEW: Check Restart if GAME OVER ---
        if game_over:
             if is_point_in_rect(ui_x, ui_y, UI_RESTART_RECT):
                restart_game()
                return
        # ---------------------------------------
        # Resume / Restart clicks when paused
        if ui_paused:
            if is_point_in_rect(ui_x, ui_y, UI_RESUME_RECT):
                ui_paused = False
                return
            if is_point_in_rect(ui_x, ui_y, UI_RESTART_RECT):
                restart_game()
                return

    # Right mouse button: plant blade anywhere on the floor (if available)
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        if game_level >= 3:
            if blade_count > 0:
                blade_count -= 1
                # Place blade in front of player
                offset_dist = 150  # distance in front of player
                angle_rad = math.radians(player_angle)
                blade_x = player_pos[0] + offset_dist * math.sin(angle_rad)
                blade_y = player_pos[1] - offset_dist * math.cos(angle_rad)
                blades.append({'x': blade_x, 'y': blade_y})
        return

    if not can_player_move():
        return

    # Left mouse button: dump if filled, otherwise pick water when near pond
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        if bucket_held:
            if bucket_has_water:
                bx, by, _ = get_bucket_world_position()
                # Check if dumping near brown area to water it
                if is_near_brown_area(bx, by) and not brown_area_watered:
                    brown_area_watered = True
                bucket_has_water = False
            else:
                bx, by, _ = get_bucket_world_position()
                if is_near_pond(bx, by):
                    bucket_has_water = True

        # Plant seeds on dark brown area and hide prompt
        if seeds_equipped and seeds_prompt_visible and brown_area_watered:
            if is_near_brown_area(player_pos[0], player_pos[1], margin=100):
                seeds_prompt_visible = False
                
                # --- NEW: Check Seed Type ---
                if seed_type == "GOLD":
                    # Generate Yellow Lines
                    golden_seed_lines = []
                    grid_size = 13; floor_len = 2 * GRID_LENGTH; cell = (2 * floor_len) / grid_size
                    for i in [6, 7]:
                        for j in range(2, 11):
                            cx1 = -floor_len + i * cell; cy1 = -floor_len + j * cell
                            for _ in range(15):
                                rx = random.uniform(cx1, cx1 + cell)
                                ry = random.uniform(cy1, cy1 + cell)
                                golden_seed_lines.append((rx, ry))
                    
                    # Set Timer
                    seed_plant_time = int(time.time() * 1000)
                    score += 5 
                    
                else:
                    # Normal Planting
                    generate_seed_lines() 
                    score += 5
                # -----------------------------




def setupCamera(): #  Configure projection and view matrices for camera modes.
    """
    Configures the camera's projection and view settings.
    Uses a perspective projection and positions the camera to look at the target.
    """
    glMatrixMode(GL_PROJECTION)  # Switch to projection matrix mode
    glLoadIdentity()  # Reset the projection matrix
    gluPerspective(fovY, 1.25, 0.1, 3500)
    glMatrixMode(GL_MODELVIEW)  # Switch to model-view matrix mode
    glLoadIdentity()  # Reset the model-view matrix

    if mode_first_person:
        # First-person camera above player's head
        eye_x = player_pos[0]
        eye_y = player_pos[1]
        eye_z = player_pos[2] + 140

        center_z = eye_z
        angle_rad = math.radians(player_angle)
        forward_x = math.sin(angle_rad)
        forward_y = -math.cos(angle_rad)
        center_x = eye_x + forward_x * 100
        center_y = eye_y + forward_y * 100

        gluLookAt(eye_x, eye_y, eye_z,
                  center_x, center_y, center_z,
                  0, 0, 1)
    else:
        # Third-person camera
        x, y, z = camera_pos
        gluLookAt(x, y, z,  # Camera position
                  0, 0, 0,  # Look-at target
                  0, 0, 1)  # Up vector (z-axis)


def idle(): #  Progress simulation and request redraw when active.
    """
    Idle function that runs continuously:
    - Triggers screen redraw for real-time updates.
    """
    # Baby cow system removed
    
# --- FREEZE IF GAME OVER ---
    if not ui_paused and not ui_play_visible and not game_over:
        if game_level == 3 and is_night_time() and not final_boss_spawned:
            spawn_final_boss()
        update_zombies()
        update_bullets()
        update_cow_behavior() # <--- NEW: Move the cow
        update_herd_behavior()       # Update purchased cows
        update_final_boss()
    # ---------------------------
    glutPostRedisplay()



def showScreen(): #  Render the full scene, entities, UI, and transitions.
    global show_harvest_msg
    global show_level_msg, level_msg_start_time
    global zombies, zombies_spawned_flag, bullet_count, missed_count
    global game_level, score, seed_lines, golden_seed_lines, sprinkler_active, brown_area_watered
    global game_over, game_won, zombies_entered_count
    global show_feed_animals_msg, blade_count
    global final_boss_active, final_boss_pos, final_boss_hp

    # --- 1. LEVEL UP CHECK ---
    if score >= 100 and game_level == 1:
        game_level = 2                 
        zombies = []                   
        show_level_msg = True          
        level_msg_start_time = int(time.time() * 1000)
    elif score >= 220 and game_level == 2:
        game_level = 3
        zombies = []
        show_level_msg = True
        level_msg_start_time = int(time.time() * 1000)
        # Ensure Level 3 starts with 2 cows: add one to herd if none
        if len(herd) < 1:
            padding = 80
            start_x = random.uniform(FARM_RECT['x_min'] + padding, FARM_RECT['x_max'] - padding)
            start_y = random.uniform(FARM_RECT['y_min'] + padding, FARM_RECT['y_max'] - padding)
            now = int(time.time() * 1000)
            herd.append({
                'pos': [start_x, start_y],
                'target': [start_x, start_y],
                'moving': False,
                'idle_start': now,
                'angle': 0.0
            })

    # --- ZOMBIE SPAWN LOGIC ---
    if is_night_time():
        # Check if EITHER normal seeds OR golden seeds exist
        if seed_lines or golden_seed_lines: 
            if not zombies_spawned_flag:
                spawn_zombies()
                zombies_spawned_flag = True
    else:
        zombies = []
        zombies_spawned_flag = False
   
    
    # --- RENDERING ---
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)

    setupCamera()

    # Skybox
    sky_r, sky_g, sky_b = get_current_sky_color()
    if sky_r > 0.01: 
        glColor3f(sky_r, sky_g, sky_b)
        glPushMatrix()
        if mode_first_person:
            glTranslatef(player_pos[0],player_pos[1],player_pos[2])
        else:
            glTranslatef(camera_pos[0], camera_pos[1], camera_pos[2])
        glutSolidCube(2500) 
        glPopMatrix()
        glClear(GL_DEPTH_BUFFER_BIT)

    glPushMatrix()
    glTranslatef(-GRID_LENGTH, GRID_LENGTH, 0)
    glColor3f(1, 1, 1)
    glScalef(5, 5, 5)
    glutSolidCube(1)
    glPopMatrix()

    # Floor Background
    glBegin(GL_QUADS)
    # White background for grid
    glColor3f(1, 1, 1)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(0, GRID_LENGTH, 0)
    glVertex3f(0, 0, 0)
    glVertex3f(-GRID_LENGTH, 0, 0)

    glVertex3f(GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(0, -GRID_LENGTH, 0)
    glVertex3f(0, 0, 0)
    glVertex3f(GRID_LENGTH, 0, 0)

    glColor3f(0.7, 0.5, 0.95)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(-GRID_LENGTH, 0, 0)
    glVertex3f(0, 0, 0)
    glVertex3f(0, -GRID_LENGTH, 0)

    glVertex3f(GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, 0, 0)
    glVertex3f(0, 0, 0)
    glVertex3f(0, GRID_LENGTH, 0)
    glEnd()

    draw_floor_grid()
    draw_border()
    
    # === FARM AREA LOGIC ===
    update_farm_status() # Check player position
    
    if game_level == 1:
        # LEVEL 1: Draw RED LOCKED AREA
        # This will now appear to the LEFT of the house
        glBegin(GL_QUADS)
        glColor3f(0.8, 0.2, 0.2) # Redish color
        glVertex3f(FARM_RECT['x_min'], FARM_RECT['y_min'], 1.0) 
        glVertex3f(FARM_RECT['x_max'], FARM_RECT['y_min'], 1.0)
        glVertex3f(FARM_RECT['x_max'], FARM_RECT['y_max'], 1.0)
        glVertex3f(FARM_RECT['x_min'], FARM_RECT['y_max'], 1.0)
        glEnd()
    else:
        # LEVEL 2: Draw FENCE and COW
        reset_modelview_stack()  # Ensure matrix stack isn't overflowing before drawing
        draw_bamboo_fence()
        
        # Draw Cow with rotation
        draw_cow(cow_pos[0], cow_pos[1], cow_angle)
        # Draw purchased herd cows
        for hc in herd:
            draw_cow(hc['pos'][0], hc['pos'][1], hc['angle'])
        # Baby cow removed
    # ========================

    draw_house()
    draw_shop()
    draw_seed_container()
    draw_player_model()
    draw_zombies()
    if final_boss_active:
        draw_final_boss(final_boss_pos[0], final_boss_pos[1])
    draw_bullets()
    
    # Draw Torches
    for t in torches:
        draw_torch(t['x'], t['y'])
    
    # Draw Blades
    for b in blades:
        draw_blade(b['x'], b['y'])
    
    # Draw Sprinkler
    if sprinkler_active:
        draw_sprinkler(sprinkler_pos[0], sprinkler_pos[1])
        # Auto-water logic
        if int(time.time() * 1000) - sprinkler_start_time < SPRINKLER_DURATION:
            brown_area_watered = True
        else:
            sprinkler_active = False 
    
    # Draw Golden Corn
    draw_golden_corn()        

    # --- UI OVERLAYS ---

    if zombies and not game_over:
        if not gun_visible:
            glColor3f(1.0, 0.0, 0.0) 
            draw_text(300, 720, "Zombies have arrived! Press G to equip GUN")
        glColor3f(1.0, 0.0, 0.0) 
        draw_text(10, 740, f"Invasion: {zombies_entered_count}/5")

    # Victory requirement reminder when boss defeated but enemies remain
    if (game_level == 3) and final_boss_spawned and (not final_boss_active) and zombies and not game_over:
        glColor3f(1.0, 0.0, 0.0)
        draw_text(280, 700, "Boss defeated! Eliminate remaining enemies to win")

    # --- LOCKED MESSAGE (Level 1) ---
    if show_locked_msg and game_level == 1:
        glColor3f(1.0, 0.0, 0.0) # Red Text
        draw_text(300, 500, "The Farm is Currently Locked!", font=GLUT_BITMAP_TIMES_ROMAN_24)
        draw_text(340, 470, "Unlocks on Level 2!", font=GLUT_BITMAP_HELVETICA_18)
    # --------------------------------

    if show_level_msg:
        if int(time.time() * 1000) - level_msg_start_time < 2000:
            glColor3f(1.0, 0.0, 0.0)
            if game_level == 1:
                draw_text(460, 400, "LEVEL 1") 
            elif game_level == 2:
                draw_text(380, 420, "You have leveled up", font=GLUT_BITMAP_HELVETICA_18)
                draw_text(430, 390, "Level 1 -> 2", font=GLUT_BITMAP_HELVETICA_18)
            elif game_level == 3:
                draw_text(380, 420, "You have leveled up", font=GLUT_BITMAP_HELVETICA_18)
                draw_text(430, 390, "Level 2 -> 3", font=GLUT_BITMAP_HELVETICA_18)
        else:
            show_level_msg = False

    if bucket_held:
        draw_bucket()
        
    if is_near_house(player_pos[0], player_pos[1]):
        # Show stored crops count always when near house
        draw_text(10, 740, f"Stored Crops: {stored_crops}")
        # Level 3: Show crop equip option
        if game_level >= 3:
            draw_text(300, 730, "Press C to get crop")
        # Bucket prompt if not equipped
        if not bucket_held:
            draw_text(10, 770, "Press E to equip bucket")

    if is_near_shop(player_pos[0], player_pos[1]):
        if game_level >= 3:
            draw_text(320, 750, "Press B to buy cow for 150 Score")
            draw_text(320, 730, "Press E to buy Blade for 450 Score")
        else:
            draw_text(380, 750, "Shop unlocks at level 3")

    if is_near_seed_container(player_pos[0], player_pos[1]):
        if not seeds_equipped:
            if brown_area_watered:
                draw_text(400, 760, "Equip seeds? Press E")
            else:
                draw_text(400, 760, "Water the land first!")
        elif seeds_prompt_visible:
            draw_text(360, 760, "Seed equipped, plant into wet land")

    draw_seed_lines()
    draw_text(850,770,f"Score: {score}")
    # Show crop equipped status under score
    if crop_equipped:
        draw_text(850, 750, "Crop equipped")

    if gun_visible:
         if bullet_count > 0:
             draw_text(850, 740, f"Ammo: {bullet_count}")
         else:
             draw_text(850, 740, f"Ammo: {bullet_count}")
             # Show ammo refill message when out of ammo
             glColor3f(1.0, 0.0, 0.0)
             draw_text(300, 700, "Go to house and press E for ammo")
         draw_text(850, 710, f"Missed: {missed_count}")

    if seed_lines:
        current_time = int(time.time() * 1000)
        elapsed = current_time - seed_plant_time
        if elapsed >= GROWTH_TIME_LIMIT:
            draw_text(350,780, "Crops are ready to be harvested")
            draw_text(350,760, "Press H to harvest")

    if show_harvest_msg:
        if int(time.time() * 1000) - last_harvest_time < 3000:
            draw_text(300, 780, f"Crops stored in house. Current point is {score}")
        else:
            show_harvest_msg = False
    
    # Show feed prompt when carrying crop and near fence
    if crop_equipped and is_near_fence(player_pos[0], player_pos[1]):
        draw_text(320, 730, "Press F to feed Cow")
    # Legacy feed animals popup (timed)
    if show_feed_animals_msg:
        if int(time.time() * 1000) - feed_animals_msg_time < 3000:
            draw_text(350, 780, "Feed the animals")
        else:
            show_feed_animals_msg = False
            
    # Level 2+ Stats
    if game_level >= 2:
        glColor3f(1.0, 0.0, 0.0)
        draw_text(10, 680, f"Seed: {seed_type} (Press Z)")
        draw_text(10, 650, f"Fence Health: {int(sum(fence_health)/4)}%")
        draw_text(10, 630, f"Blades: {blade_count}")        

    if game_over:
        glColor3f(1.0, 0.0, 0.0)
        if game_won:
            draw_text(420, 420, "You Won!!", font=GLUT_BITMAP_TIMES_ROMAN_24)
        else:
            draw_text(420, 420, "GAME OVER", font=GLUT_BITMAP_TIMES_ROMAN_24)
        draw_text(420, 380, f"Final Score: {score}")
        draw_text(UI_RESTART_RECT[0] + 10, UI_RESTART_RECT[1] + 10, "Restart")
    
    if ui_play_visible:
        draw_text(UI_PLAY_RECT[0] + 10, UI_PLAY_RECT[1] + 10, "PLAY")
        
    if ui_paused:
        draw_text(UI_RESUME_RECT[0] + 10, UI_RESUME_RECT[1] + 10, "Resume")
        draw_text(UI_RESTART_RECT[0] + 10, UI_RESTART_RECT[1] + 10, "Restart")

    glutSwapBuffers()

# Main function to set up OpenGL window and loop
def main(): #  Initialize GLUT, register callbacks, and start the main loop.
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)  # Double buffering, RGB color, depth test
    glutInitWindowSize(1000, 800)  # Window size
    glutInitWindowPosition(0, 0)  # Window position
    wind = glutCreateWindow(b"3D OpenGL Intro")  # Create the window

    glutDisplayFunc(showScreen)  # Register display function
    glutKeyboardFunc(keyboardListener)  # Register keyboard listener
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)  # Register the idle function to move the bullet automatically

    glutMainLoop()  # Enter the GLUT main loop


if __name__ == "__main__":
    main()
