import pygame
import sys
import time

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Python-FBW Primary Flight Display (PFD)")
clock = pygame.time.Clock()

SKY_BLUE = (30, 144, 255)
EARTH_BROWN = (139, 69, 19)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
DARK_GRAY = (40, 40, 40)

font_small = pygame.font.SysFont("Arial", 16)
font_large = pygame.font.SysFont("Arial", 22, bold=True)

class Aircraft:
    def __init__(self):
        self.last_time = time.time()
        self.speed = 200.0
        self.pitch = 0.0
        self.roll = 0.0
        self.altitude = 0.0
        self.is_stalling = False
        self.dt = 0.0
        self.stall_limit_speed = 140
        self.throttle_speed = 20
        
        self.tla = 0.0
        self.n1 = 20.0
        self.target_n1 = 20.0
        self.spool_rate = 0.5
        self.base_drag = 0.0005
        self.flap_drag = 0.0
        self.gear_drag = 0.0

        self.flaps_position = 0
        self.landing_gear_position = "UP"

        self.autopilot_active = False
        self.autopilot_target_altitude = 3000

    def delta_time(self):
        current_time = time.time()
        self.dt = current_time - self.last_time
        self.last_time = current_time
        return self.dt

    def handle_input(self, keys):
        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            self.tla += self.throttle_speed * self.dt
        if keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]:
            self.tla -= self.throttle_speed * self.dt
        self.tla = max(0.0, min(100.0, self.tla))
        self.target_n1 = self.tla * 0.8 + 20.0

        if not self.autopilot_active:
            control_rate = 20 * self.dt
            if keys[pygame.K_w] and self.pitch > -15:
                self.pitch -= control_rate
            if keys[pygame.K_s] and self.pitch < 30:
                self.pitch += control_rate

            if keys[pygame.K_a] and self.roll < 67:
                self.roll += control_rate
            if keys[pygame.K_d] and self.roll > -67:
                self.roll -= control_rate

            if not keys[pygame.K_a] and not keys[pygame.K_d]:
                if self.roll > 33:
                    self.roll -= control_rate
                elif self.roll < -33:
                    self.roll += control_rate

    def update_physics(self):
        self.n1 += (self.target_n1 - self.n1) * self.spool_rate * self.dt

        # Speed Calculation
        drag_coeff = self.base_drag + self.flap_drag + self.gear_drag
        drag = self.speed * self.speed * drag_coeff
        gravity_effect = self.pitch * 0.5
        net_force = self.n1 - drag - gravity_effect
        self.speed += net_force * self.dt

        self.is_stalling = (self.speed <= self.stall_limit_speed and self.pitch > 10)
        
        vertical_speed = self.speed * self.pitch * 0.1
        if self.is_stalling:
            self.altitude -= 15 * self.dt
        else:
            self.altitude += vertical_speed * self.dt
        self.altitude = max(0.0, self.altitude)

        if self.autopilot_active:
            if self.altitude < self.autopilot_target_altitude - 20:
                self.pitch = 5
            elif self.altitude > self.autopilot_target_altitude + 20:
                self.pitch = -5
            else:
                self.pitch = 0

def draw_pfd(screen, aircraft):
    screen.fill(BLACK)
    center_x, center_y = WIDTH // 2, HEIGHT // 2

    horizon_surface = pygame.Surface((600, 600))
    horizon_surface.fill(SKY_BLUE)
    pitch_offset = aircraft.pitch * 8  
    pygame.draw.rect(horizon_surface, EARTH_BROWN, (0, 300 + pitch_offset, 600, 600))
    pygame.draw.line(horizon_surface, WHITE, (0, 300 + pitch_offset), (600, 300 + pitch_offset), 3)

    rotated_horizon = pygame.transform.rotate(horizon_surface, aircraft.roll)
    new_rect = rotated_horizon.get_rect(center=(center_x, center_y))
    
    pfd_rect = pygame.Rect(150, 50, 500, 500)
    screen.set_clip(pfd_rect)
    screen.blit(rotated_horizon, new_rect.topleft)

    pygame.draw.line(screen, YELLOW, (center_x - 40, center_y), (center_x - 10, center_y), 5)
    pygame.draw.line(screen, YELLOW, (center_x + 10, center_y), (center_x + 40, center_y), 5)
    pygame.draw.line(screen, YELLOW, (center_x, center_y - 10), (center_x, center_y + 10), 5)
    
    screen.set_clip(None) 

    pygame.draw.rect(screen, DARK_GRAY, (30, 50, 100, 500))
    pygame.draw.rect(screen, WHITE, (30, 50, 100, 500), 2)
    speed_text = font_large.render(f"{aircraft.speed:.0f} KT", True, GREEN)
    screen.blit(speed_text, (45, 280))

    pygame.draw.rect(screen, DARK_GRAY, (670, 50, 100, 500))
    pygame.draw.rect(screen, WHITE, (670, 50, 100, 500), 2)
    alt_text = font_large.render(f"{aircraft.altitude:.0f} FT", True, GREEN)
    screen.blit(alt_text, (675, 280))

    ap_status = "AP: ON" if aircraft.autopilot_active else "AP: OFF"
    ap_color = GREEN if aircraft.autopilot_active else WHITE
    screen.blit(font_large.render(ap_status, True, ap_color), (center_x - 35, 15))

    info_text = f"N1: {aircraft.n1:.1f}% | Flaps: {aircraft.flaps_position} | Gear: {aircraft.landing_gear_position}"
    screen.blit(font_small.render(info_text, True, WHITE), (center_x - 140, HEIGHT - 30))

    if aircraft.is_stalling:
        stall_text = font_large.render("STALL!", True, (255, 0, 0))
        screen.blit(stall_text, (center_x - 35, 70))

aircraft = Aircraft()
running = True

while running:
    dt = aircraft.delta_time()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_g:
                aircraft.landing_gear_position = "DOWN"
                aircraft.gear_drag = 0.0002
            elif event.key == pygame.K_h:
                aircraft.landing_gear_position = "UP"
                aircraft.gear_drag = 0.0
            elif event.key == pygame.K_1:
                aircraft.flaps_position, aircraft.flap_drag, aircraft.stall_limit_speed = 1, 0.0001, 130
            elif event.key == pygame.K_2:
                aircraft.flaps_position, aircraft.flap_drag, aircraft.stall_limit_speed = 2, 0.0002, 120
            elif event.key == pygame.K_3:
                aircraft.flaps_position, aircraft.flap_drag, aircraft.stall_limit_speed = 3, 0.0003, 110
            elif event.key == pygame.K_f:
                aircraft.flaps_position, aircraft.flap_drag, aircraft.stall_limit_speed = "FULL", 0.0004, 110
            elif event.key == pygame.K_0:
                aircraft.flaps_position, aircraft.flap_drag, aircraft.stall_limit_speed = 0, 0.0, 140
            elif event.key == pygame.K_o:
                aircraft.autopilot_active = True
            elif event.key == pygame.K_p:
                aircraft.autopilot_active = False

    keys = pygame.key.get_pressed()
    aircraft.handle_input(keys)
    aircraft.update_physics()

    draw_pfd(screen, aircraft)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
