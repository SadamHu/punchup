import pygame
import os
import random


pygame.init()

scalefactor = 1
SCREENWIDTH, SCREENHEIGHT = 1280 * scalefactor, 800 * scalefactor
SCREEN = SCREENWIDTH, SCREENHEIGHT
DISPWIDTH = 1280
DISPHEIGHT = 800
CENTER_X = DISPWIDTH / 2
CENTER_Y = 600

balls = []
next_spawn_time = 0
faster = 3000
running = True
clock = pygame.time.Clock()
FPS = 60
sound_volume = 0.1

# Animation timing (200 ms per frame)
character_frame_index = 0
character_frame_time = 200  # milliseconds
character_next_frame = pygame.time.get_ticks() + character_frame_time

win = pygame.display.set_mode(SCREEN, pygame.NOFRAME | pygame.SCALED)
pygame.display.set_caption("Punch Up")

# --- Paths ---
images_path = os.path.join(os.path.abspath("."), "images")
sounds_path = os.path.join(os.path.abspath("."), "sounds")

# --- Load background ---
BACKGROUND = pygame.image.load(os.path.join(images_path, "bground001.png")).convert()

# --- Load character animation frames ---
character_frames = [
    pygame.image.load(os.path.join(images_path, "char003.png")).convert_alpha(),
    pygame.image.load(os.path.join(images_path, "char004.png")).convert_alpha(),
    pygame.image.load(os.path.join(images_path, "char005.png")).convert_alpha()
]

# --- load in the character moves ---
character_moves = [
    pygame.image.load(os.path.join(images_path, "divl1.png")).convert_alpha(),
    pygame.image.load(os.path.join(images_path, "divl2.png")).convert_alpha(),
    pygame.image.load(os.path.join(images_path, "divl3.png")).convert_alpha(),
    pygame.image.load(os.path.join(images_path, "divl4.png")).convert_alpha(),
    pygame.image.load(os.path.join(images_path, "divr1.png")).convert_alpha(),
    pygame.image.load(os.path.join(images_path, "divr2.png")).convert_alpha(),
    pygame.image.load(os.path.join(images_path, "divr3.png")).convert_alpha(),
    pygame.image.load(os.path.join(images_path, "divr4.png")).convert_alpha()
]

# --- load in the barrier masks ---
character_barrier_images = [
    pygame.image.load(os.path.join(images_path, "barl1.png")).convert_alpha(),
    pygame.image.load(os.path.join(images_path, "barl2.png")).convert_alpha(),
    pygame.image.load(os.path.join(images_path, "barl3.png")).convert_alpha(),
    pygame.image.load(os.path.join(images_path, "barl4.png")).convert_alpha(),
    pygame.image.load(os.path.join(images_path, "barr1.png")).convert_alpha(),
    pygame.image.load(os.path.join(images_path, "barr2.png")).convert_alpha(),
    pygame.image.load(os.path.join(images_path, "barr3.png")).convert_alpha(),
    pygame.image.load(os.path.join(images_path, "barr4.png")).convert_alpha()
]

# --- create barrier masks from images
character_barrier_masks = []

for image_surface in character_barrier_images:
    new_mask = pygame.mask.from_surface(image_surface)
    # Add the new mask to the list
    character_barrier_masks.append(new_mask)

# --- load in character mask ---
character_mask = pygame.image.load(os.path.join(images_path, "barc0.png")).convert_alpha()
character_mask = pygame.mask.from_surface(character_mask)
# --- create character rect ---
character_rect = pygame.Rect(440, 400, 400, 400)

# --- Load basketball image and mask ---
BALL_IMAGE = pygame.image.load(os.path.join(images_path, "ball002.png")).convert_alpha()
BALL_WIDTH = BALL_IMAGE.get_width()
BALL_HEIGHT = BALL_IMAGE.get_height()
BALL_MASK = pygame.mask.from_surface(BALL_IMAGE)

# --- Load sounds ---
strike_sounds = [
    pygame.mixer.Sound(os.path.join(sounds_path, "strike000.wav")),
    pygame.mixer.Sound(os.path.join(sounds_path, "strike001.wav")),
    pygame.mixer.Sound(os.path.join(sounds_path, "strike002.wav")),
    pygame.mixer.Sound(os.path.join(sounds_path, "strike003.wav")),
    pygame.mixer.Sound(os.path.join(sounds_path, "strike004.wav")),
    pygame.mixer.Sound(os.path.join(sounds_path, "strike005.wav")),
    pygame.mixer.Sound(os.path.join(sounds_path, "strike006.wav")),
    pygame.mixer.Sound(os.path.join(sounds_path, "strike007.wav"))
]

# Iterate through each Sound object in the list
for sound in strike_sounds:
    # Set the volume for the current sound object
    sound.set_volume(sound_volume)

dead_sounds = [
    pygame.mixer.Sound(os.path.join(sounds_path, "dead000.wav")),
    pygame.mixer.Sound(os.path.join(sounds_path, "dead001.wav")),
    pygame.mixer.Sound(os.path.join(sounds_path, "dead003.wav")),
    pygame.mixer.Sound(os.path.join(sounds_path, "dead004.wav")),
    pygame.mixer.Sound(os.path.join(sounds_path, "dead005.wav"))
]

# Iterate through each Sound object in the list
for sound in dead_sounds:
    # Set the volume for the current sound object
    sound.set_volume(sound_volume)

bounce_sounds = [
    pygame.mixer.Sound(os.path.join(sounds_path, "ball000.wav")),
    pygame.mixer.Sound(os.path.join(sounds_path, "ball001.wav")),
    pygame.mixer.Sound(os.path.join(sounds_path, "ball002.wav"))
]

# Iterate through each Sound object in the list
for sound in bounce_sounds:
    # Set the volume for the current sound object
    sound.set_volume(sound_volume)

gong_sound = pygame.mixer.Sound(os.path.join(sounds_path, "gong000.wav"))
gong_sound.set_volume(sound_volume)

# --- Load Fonts ---
pygame.font.init()

# --- Ball class ---
class Ball:
    def __init__(self):
        # Spawn off-screen left or right
        side = random.choice(["left", "right"])
        if side == "left":
            self.x = -BALL_WIDTH
            self.speed_x = random.uniform(2, 5)
        else:
            self.x = DISPWIDTH + BALL_WIDTH
            self.speed_x = random.uniform(-5, -2)

        # Random vertical spawn
        self.y = random.randint(50, int(DISPHEIGHT - BALL_HEIGHT - 100))

        # Upward throw
        self.speed_y = random.uniform(-10, -15)
        self.gravity = 0.5

        self.angle = 0

    def update(self):
        global running
        self.x += self.speed_x
        self.y += self.speed_y
        self.speed_y += self.gravity
        self.angle -= self.speed_x * 2

        # Bounce floor
        if self.y + BALL_HEIGHT >= DISPHEIGHT - 10:
            self.y = DISPHEIGHT - BALL_HEIGHT - 10
            self.speed_y *= -0.9
            bounce_sounds[2].play()

            if abs(self.speed_y) < 1:
                self.speed_y = 0

        # --- Does the ball hit the character ---
        ball_rect = pygame.Rect(self.x, self.y, BALL_WIDTH, BALL_HEIGHT)

        if ball_rect.colliderect(character_rect):
            if BALL_MASK.overlap(character_mask, (character_rect.x - ball_rect.x, character_rect.y - ball_rect.y)):
                #dead = random.choice(dead_sounds)
                #dead.play()
                #running = False
                print("dead")

            for index, bar in enumerate(barriers):
                if bar.active:
                    if BALL_MASK.overlap(character_barrier_masks[index], (character_rect.x - ball_rect.x, character_rect.y - ball_rect.y)):
                        # 1. Calculate the vector from the Screen Center to the Ball
                        # This vector defines the direction the ball will shoot.
                        dx = (self.x + BALL_WIDTH / 2) - CENTER_X
                        dy = (self.y + BALL_HEIGHT / 2) - CENTER_Y
                        
                        # 2. Calculate the length (magnitude) of the vector
                        # This is used to normalize the vector (make its length 1)
                        distance = (dx**2 + dy**2)**0.5
                        
                        # 3. Define the desired speed increase
                        NEW_SPEED = 25.0 # Set the magnitude of the new velocity
                        
                        if distance != 0:
                            # Normalize the vector (dx/distance, dy/distance)
                            # and multiply by the new desired speed
                            self.speed_x = (dx / distance) * NEW_SPEED
                            self.speed_y = (dy / distance) * NEW_SPEED
                        else:
                            # Handle the rare case where the ball is exactly at the center
                            self.speed_x = NEW_SPEED
                            self.speed_y = 0 

                        # Reposition ball slightly to prevent immediate re-collision
                        self.x += self.speed_x * 0.1 
                        self.y += self.speed_y * 0.1

                        bounce_sounds[2].play()
                        gong_sound.play()
                        break # Exit the barrier loop once a hit is registered

    def draw(self):
        # Shadow
        shadow_scale = 0.5 + (self.y / DISPHEIGHT) * 0.5
        shadow_width = max(1, int(BALL_WIDTH * shadow_scale))
        shadow_height = max(1, int(BALL_HEIGHT * 0.2 * shadow_scale))
        shadow_x = self.x + (BALL_WIDTH - shadow_width) // 2
        shadow_y = DISPHEIGHT - 10
        shadow_surface = pygame.Surface((shadow_width, shadow_height), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surface, (0, 0, 0, 50), shadow_surface.get_rect())
        win.blit(shadow_surface, (shadow_x, shadow_y))

        # Rotated ball
        rotated_ball = pygame.transform.rotate(BALL_IMAGE, self.angle)
        rotated_rect = rotated_ball.get_rect(center=(self.x + BALL_WIDTH // 2, self.y + BALL_HEIGHT // 2))
        win.blit(rotated_ball, rotated_rect.topleft)

    def is_off_screen(self):
        return (self.x < -BALL_WIDTH or
                self.x > DISPWIDTH + BALL_WIDTH)

class PolygonalButton:
    def __init__(self, points, color, hover_color, action):
        self.points = points
        self.color = color
        self.hover_color = hover_color
        self.current_color = color
        self.action = action
        self.active = False

    def is_point_inside(self, point):
        x, y = point
        n = len(self.points)
        inside = False

        p1x, p1y = self.points[0]

        for i in range(n + 1):
            p2x, p2y = self.points[i % n]

            if y > min(p1y, p2y) and y <= max(p1y, p2y):
                if p1y != p2y:
                    x_intersect = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if x_intersect > x:
                        inside = not inside
            
            p1x, p1y = p2x, p2y
        
        return inside

    def draw(self, surface):
        pygame.draw.polygon(surface, self.current_color, self.points)

def on_barl1_click():
    pass

def on_barl2_click(): 
    pass

def on_barl3_click(): 
    pass

def on_barl4_click(): 
    pass

def on_barr1_click(): 
    pass

def on_barr2_click():
    pass

def on_barr3_click():
    pass

def on_barr4_click():
    pass

# --- Define barriers and Create Button Instances ---
barl1 = PolygonalButton(
    [(640, 800), (640, 675), (0, 675), (0, 800)],
    color=(150, 50, 200),
    hover_color=(255, 255, 0),
    action=on_barl1_click,
)

barl2 = PolygonalButton(
    [(640, 675), (640, 550), (0, 550), (0, 675)],
    color=(50, 150, 50),
    hover_color=(100, 200, 100),
    action=on_barl2_click,
)

barl3 = PolygonalButton(
    [(640, 550), (90, 0), (0, 0), (0, 550),],
    color=(50, 50, 200),
    hover_color=(100, 100, 255),
    action=on_barl3_click,
)

barl4 = PolygonalButton(
    [(640, 550), (640, 0), (90, 0)],
    color=(200, 50, 50),
    hover_color=(255, 100, 100),
    action=on_barl4_click,
)

barr1 = PolygonalButton(
    [(640, 800), (640, 675), (1280, 675), (1280, 800)],
    color=(150, 50, 200),
    hover_color=(255, 255, 0),
    action=on_barr1_click,
)

barr2 = PolygonalButton(
    [(640, 675), (640, 550), (1280, 550), (1280, 675)],
    color=(50, 150, 50),
    hover_color=(100, 200, 100),
    action=on_barr2_click,
)

barr3 = PolygonalButton(
    [(640, 550), (1190, 0), (1280, 0), (1280,550)],
    color=(50, 50, 200),
    hover_color=(100, 100, 255),
    action=on_barr3_click,
)

barr4 = PolygonalButton(
    [(640, 550), (640, 0), (1190, 0)],
    color=(200, 50, 50),
    hover_color=(255, 100, 100),
    action=on_barr4_click,
)



# List of all barriers buttons
barriers = [barl1, barl2, barl3, barl4, barr1, barr2, barr3, barr4,]

# --- Draw functions ---
def draw_background():
    win.blit(BACKGROUND, (0, 0))

def draw_character():
    global character_frame_index, character_next_frame

    
    for index, bar in enumerate(barriers):
        if bar.active:
            win.blit(character_moves[index], (440, 400))
        
    # 2. Check the negation of that condition:
    if not any(bar.active for bar in barriers):
    
        # Character is idle (no barrier is active)
        # Update animation frame based on time
        current_time = pygame.time.get_ticks()
        if current_time >= character_next_frame:
            character_frame_index = (character_frame_index + 1) % len(character_frames)
            character_next_frame = current_time + character_frame_time

        # Draw current animation frame
        win.blit(character_frames[character_frame_index], (440, 400))

def draw_text(strtext, loctext, rgbcolor, sizetext):
    my_font = pygame.font.Font(None, sizetext)
    text_surface = my_font.render(strtext, True, rgbcolor) # White text
    win.blit(text_surface, loctext)

while running:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_AC_BACK):
                running = False
        
    # Continuous Mouse Down Check (NEW LOGIC)
    # Get the state of all mouse buttons: (left, middle, right)
    mouse_down = pygame.mouse.get_pressed()
    
    # Check if the Left Mouse Button (index 0) is currently held down
    if mouse_down[0]:
        mouse_pos = pygame.mouse.get_pos()
        
        # Check every barrier if the mouse is down
        for bar in barriers:
            if bar.is_point_inside(mouse_pos):
                if  not bar.active:
                    strike = random.choice(strike_sounds)
                    strike.play()
                    bar.active = True
            else:
                bar.active = False
    else:
        for bar in barriers:
            bar.active = False

    # Spawn new balls at random intervals (1 - 3 seconds)
    #if faster > 1:
    #    faster -= 1
    current_time = pygame.time.get_ticks()
    if current_time >= next_spawn_time:
        balls.append(Ball())
        next_spawn_time = current_time + random.randint(1, faster)

    # Update balls and remove those off-screen
    for ball in balls[:]:
        ball.update()
        if ball.is_off_screen():
            balls.remove(ball)

    # Draw everything
    draw_background()

    draw_character()

    for ball in balls: ball.draw()

    draw_text("Faster " + str(faster), (100, 100), (0, 0, 0), 30)
    draw_text("Balls " + str(len(balls)), (100, 130), (0, 0, 0), 30)
    draw_text(str(barriers[0].active), (100, 160), (0 ,0, 0), 30)
    draw_text(str(barriers[1].active), (100, 190), (0 ,0, 0), 30)
    draw_text(str(barriers[2].active), (100, 220), (0 ,0, 0), 30)
    draw_text(str(barriers[3].active), (100, 250), (0 ,0, 0), 30)
    draw_text(str(barriers[4].active), (100, 280), (0 ,0, 0), 30)
    draw_text(str(barriers[5].active), (100, 310), (0 ,0, 0), 30)
    draw_text(str(barriers[6].active), (100, 340), (0 ,0, 0), 30)
    draw_text(str(barriers[7].active), (100, 370), (0 ,0, 0), 30)

    # Draw all barriers
    #for bar in barriers: bar.draw(win)


    if scalefactor > 1:
        scaled_surface = pygame.transform.scale(win, (SCREENWIDTH * scalefactor, SCREENHEIGHT * scalefactor))
        win.blit(scaled_surface, (0, 0))
    
    pygame.display.update()

pygame.quit()