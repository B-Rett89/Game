import pygame
import random
import os
import math

WIDTH, HEIGHT = 800, 600
FPS = 60
TILE_SIZE = 40
NUM_UPGRADES = 20

# Colors for textures generated programmatically
LEVEL_COLORS = [(i * 12 % 255, i * 5 % 255, i * 3 % 255) for i in range(NUM_UPGRADES)]
ENEMY_COLORS = [(i * 5 % 255, i * 11 % 255, i * 7 % 255) for i in range(NUM_UPGRADES)]
GUN_COLORS = [(i * 3 % 255, i * 7 % 255, i * 13 % 255) for i in range(NUM_UPGRADES)]
HUD_COLORS = [(i * 4 % 255, i * 9 % 255, i * 2 % 255) for i in range(NUM_UPGRADES)]

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)

# Simple textures stored as surfaces
def create_surface(color, size=(TILE_SIZE, TILE_SIZE)):
    surf = pygame.Surface(size)
    surf.fill(color)
    return surf

def generate_textures(colors):
    return [create_surface(c) for c in colors]

level_textures = generate_textures(LEVEL_COLORS)
enemy_textures = generate_textures(ENEMY_COLORS)

# gun texture is 60x20
gun_textures = [create_surface(c, (60, 20)) for c in GUN_COLORS]

# HUD is 100x40
hud_textures = [create_surface(c, (100, 40)) for c in HUD_COLORS]

# Player attributes
player_pos = [WIDTH // 2, HEIGHT // 2]
player_speed = 5
player_health = 100
player_ammo = 50
points = 0

# Upgrade levels
upgrades = {
    'level': 0,
    'enemy': 0,
    'gun': 0,
    'hud': 0
}

# Simple map (0 = floor, 1 = wall)
MAP_WIDTH, MAP_HEIGHT = 20, 15
level_map = [[0 for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)]
# Surrounding walls
for y in range(MAP_HEIGHT):
    level_map[y][0] = level_map[y][-1] = 1
for x in range(MAP_WIDTH):
    level_map[0][x] = level_map[-1][x] = 1

# Place random walls
for _ in range(40):
    x = random.randint(1, MAP_WIDTH-2)
    y = random.randint(1, MAP_HEIGHT-2)
    level_map[y][x] = 1

# Enemy list
enemies = []
for _ in range(5):
    while True:
        x = random.randint(1, MAP_WIDTH-2)
        y = random.randint(1, MAP_HEIGHT-2)
        if level_map[y][x] == 0:
            enemies.append({'pos':[x*TILE_SIZE+TILE_SIZE//2, y*TILE_SIZE+TILE_SIZE//2], 'alive':True})
            break

# Coins
coins = []
for _ in range(10):
    while True:
        x = random.randint(1, MAP_WIDTH-2)
        y = random.randint(1, MAP_HEIGHT-2)
        if level_map[y][x] == 0:
            coins.append({'pos':[x*TILE_SIZE+TILE_SIZE//2, y*TILE_SIZE+TILE_SIZE//2], 'collected':False})
            break

bullets = []

exit_button = pygame.Rect(WIDTH-80, HEIGHT-80, 60, 40)

state = 'play'


def draw_level():
    tex = level_textures[upgrades['level']]
    wall_tex = pygame.transform.scale(tex, (TILE_SIZE, TILE_SIZE))
    for y,row in enumerate(level_map):
        for x, cell in enumerate(row):
            if cell == 1:
                screen.blit(wall_tex, (x*TILE_SIZE, y*TILE_SIZE))

def draw_enemies():
    tex = enemy_textures[upgrades['enemy']]
    for e in enemies:
        if e['alive']:
            rect = tex.get_rect(center=e['pos'])
            screen.blit(tex, rect)

def draw_coins():
    for c in coins:
        if not c['collected']:
            pygame.draw.circle(screen, (255,215,0), c['pos'], 5)

def draw_gun():
    tex = gun_textures[upgrades['gun']]
    rect = tex.get_rect(center=(WIDTH//2, HEIGHT-50))
    screen.blit(tex, rect)

def draw_hud():
    tex = hud_textures[upgrades['hud']]
    rect = tex.get_rect(topleft=(10,10))
    screen.blit(tex, rect)
    health_text = font.render(f"HP: {player_health}", True, (255,255,255))
    ammo_text = font.render(f"Ammo: {player_ammo}", True, (255,255,255))
    points_text = font.render(f"Pts: {points}", True, (255,255,0))
    screen.blit(health_text, (15,15))
    screen.blit(ammo_text, (15,35))
    screen.blit(points_text, (15,55))

def handle_input():
    keys = pygame.key.get_pressed()
    if keys[pygame.K_a]:
        player_pos[0] -= player_speed
    if keys[pygame.K_d]:
        player_pos[0] += player_speed
    if keys[pygame.K_w]:
        player_pos[1] -= player_speed
    if keys[pygame.K_s]:
        player_pos[1] += player_speed


def shoot(target_pos):
    global player_ammo
    if player_ammo > 0:
        dx = target_pos[0] - player_pos[0]
        dy = target_pos[1] - player_pos[1]
        dist = math.hypot(dx, dy)
        if dist == 0:
            dist = 1
        vel = [dx / dist * 10, dy / dist * 10]
        bullets.append({'pos': [player_pos[0], player_pos[1]], 'vel': vel})
        player_ammo -= 1


def update_bullets():
    global points
    for b in bullets:
        b['pos'][0] += b['vel'][0]
        b['pos'][1] += b['vel'][1]
    for e in enemies:
        if e['alive']:
            e_rect = pygame.Rect(0,0,TILE_SIZE,TILE_SIZE)
            e_rect.center = e['pos']
            for b in bullets:
                b_rect = pygame.Rect(b['pos'][0]-2,b['pos'][1]-2,4,4)
                if e_rect.colliderect(b_rect):
                    e['alive'] = False
                    points += 5
    bullets[:] = [b for b in bullets if 0<b['pos'][1]<HEIGHT]


def check_coins():
    global points
    for c in coins:
        if not c['collected']:
            c_rect = pygame.Rect(0,0,10,10)
            c_rect.center = c['pos']
            p_rect = pygame.Rect(0,0,20,20)
            p_rect.center = player_pos
            if p_rect.colliderect(c_rect):
                c['collected'] = True
                points += 1


def all_enemies_defeated():
    return all(not e['alive'] for e in enemies)


def draw_exit_button():
    if all_enemies_defeated():
        pygame.draw.rect(screen, (0,255,0), exit_button)
        txt = font.render('Exit', True, (0,0,0))
        screen.blit(txt, exit_button.move(10,10))


def check_exit():
    if all_enemies_defeated():
        p_rect = pygame.Rect(0,0,20,20)
        p_rect.center = player_pos
        if p_rect.colliderect(exit_button):
            return True
    return False


def draw_bullets():
    for b in bullets:
        pygame.draw.circle(screen, (255,0,0), b['pos'], 2)


def pause_menu():
    screen.fill((0, 0, 0))
    txt = font.render('Paused - ESC to resume, Q to quit', True, (255, 255, 255))
    screen.blit(txt, (WIDTH // 2 - txt.get_width() // 2, HEIGHT // 2))
    pygame.display.flip()


def upgrade_menu():
    global state, points
    screen.fill((0,0,0))
    menu_text = [
        'Upgrade Menu',
        f'Points: {points}',
        'Press G to upgrade gun',
        'Press E to upgrade enemies',
        'Press L to upgrade level',
        'Press H to upgrade HUD',
        'Press ENTER to return'
    ]
    for i, line in enumerate(menu_text):
        txt = font.render(line, True, (255,255,255))
        screen.blit(txt, (100,100+i*30))

    pygame.display.flip()

    upgrading = True
    while upgrading:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    upgrading = False
                elif event.key == pygame.K_g and upgrades['gun'] < NUM_UPGRADES-1 and points>=10:
                    upgrades['gun'] +=1
                    points -=10
                elif event.key == pygame.K_e and upgrades['enemy']<NUM_UPGRADES-1 and points>=10:
                    upgrades['enemy']+=1
                    points-=10
                elif event.key == pygame.K_l and upgrades['level']<NUM_UPGRADES-1 and points>=10:
                    upgrades['level']+=1
                    points-=10
                elif event.key == pygame.K_h and upgrades['hud']<NUM_UPGRADES-1 and points>=10:
                    upgrades['hud']+=1
                    points-=10
        clock.tick(FPS)

    state = 'play'


def main():
    global state, points
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if state == 'pause':
                        state = 'play'
                    else:
                        state = 'pause'
                elif event.key == pygame.K_u and state == 'play':
                    state = 'upgrade'
                elif event.key == pygame.K_q and state == 'pause':
                    running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and state == 'play':
                shoot(event.pos)
        if state == 'play':
            handle_input()
            update_bullets()
            check_coins()
            screen.fill((30,30,30))
            draw_level()
            draw_coins()
            draw_enemies()
            draw_bullets()
            draw_exit_button()
            draw_gun()
            draw_hud()
            if check_exit():
                points += 20
                upgrade_menu()
            pygame.display.flip()
            clock.tick(FPS)
        elif state == 'upgrade':
            upgrade_menu()
        elif state == 'pause':
            pause_menu()
    pygame.quit()


if __name__ == '__main__':
    main()
