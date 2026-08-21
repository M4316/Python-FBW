
import keyboard
import time

last_time = time.time()

tla = 0
n1 = 20
target_n1 = 20
spool_rate = 0.5
dt = 0
drag_coefficient = 0.0005
is_stalling = False
flaps_position = 0
stall_limit_speed = 140
landing_gear_position = "UP"
base_drag = 0.0005
flap_drag = 0.0
gear_drag = 0.0
autopilot_active = False
autopilot_target_altitude = 0

altitude = 0.0
speed = 200 
pitch = 0.0
roll = 0.0

old_speed, old_pitch, old_roll, old_tla, old_n1, old_altitude, old_flaps_position, old_landing_gear_position = 200, 0.0, 0.0, 0, 20, 0, 0, "UP"

def update_display():
    global speed, pitch, roll, old_speed, old_pitch, old_roll, tla, old_tla, n1, old_n1, target_n1, altitude, old_altitude, flaps_position, old_flaps_position, landing_gear_position, old_landing_gear_position

    if speed != old_speed or pitch != old_pitch or roll != old_roll or tla != old_tla or n1 != old_n1 or altitude != old_altitude or flaps_position != old_flaps_position or landing_gear_position != old_landing_gear_position:
        print(f"Knot: {speed:.1f} | Pitch: {pitch:.1f} | Roll: {roll:.1f} | TLA: {tla:.1f} | Target N1: {target_n1:.1f} | N1: {n1:.1f} | Altitude: {altitude:.1f} | Flaps: {flaps_position} | Landing Gear: {landing_gear_position}")
        old_speed = speed
        old_pitch = pitch
        old_roll = roll
        old_tla = tla
        old_n1 = n1
        old_altitude = altitude
        old_landing_gear_position = landing_gear_position

def delta_time():
    global last_time
    current_time = time.time()
    dt = current_time - last_time
    last_time = current_time
    return dt

def calculate_engine(dt):
    global tla

    throttle_speed = 20

    if keyboard.is_pressed("shift"):
        tla += throttle_speed * dt
    if keyboard.is_pressed("ctrl"):
        tla -= throttle_speed * dt
    if tla > 100:
        tla = 100
    if tla < 0:
        tla = 0

def update_speed(dt):
    global speed, pitch, n1

    drag_coefficient = base_drag + flap_drag + gear_drag
    
    drag = (speed * speed * drag_coefficient)
    gravity_effect = (pitch * 0.5)
    engine_thrust = n1 
    net_force = engine_thrust - drag - gravity_effect
    
    speed += net_force * dt
    
def update_n1(dt):
    global n1
    n1 += (target_n1 - n1) * spool_rate * dt

def fbw_pitch_control(dt):
    if autopilot_active == True: return
    global pitch
    control_rate = 20 * dt
    if keyboard.is_pressed("w") and pitch > -15:
        pitch -= control_rate
    if keyboard.is_pressed("s") and pitch < 30:
        pitch += control_rate

def fbw_roll_control(dt):
    if autopilot_active == True: return
    global roll
    control_rate = 20 * dt
    if keyboard.is_pressed("a") and roll < 67:
        roll += control_rate
    if keyboard.is_pressed("d") and roll > -67:
        roll -= control_rate

    if not keyboard.is_pressed("a") and not keyboard.is_pressed("d"):
        if roll > 33:
            roll -= control_rate
        elif roll < -33:
            roll += control_rate

def update_altitude(dt):
    global altitude, is_stalling
    vertical_speed = speed * pitch * 0.1
    if is_stalling == True:
        altitude -= 15 * dt
    else:
        altitude += vertical_speed * dt
    if altitude < 0:
        altitude = 0
        
def check_stall(dt):
    global altitude, is_stalling
    if speed <= stall_limit_speed and pitch > 10:
        is_stalling = True
    else:
        is_stalling = False

def flaps(dt):
    global flaps_position, drag_coefficient, stall_limit_speed, flap_drag

    if keyboard.is_pressed("1"):
        flaps_position = 1
        flap_drag = 0.0001
        stall_limit_speed = 130
    if keyboard.is_pressed("2"):
        flaps_position = 2
        flap_drag = 0.0002
        stall_limit_speed = 120
    if keyboard.is_pressed("3"):
        flaps_position = 3
        flap_drag = 0.0003
        stall_limit_speed = 110
    if keyboard.is_pressed("f"):
        flaps_position = "FULL"
        flap_drag = 0.0004
        stall_limit_speed = 110
    if keyboard.is_pressed("0"):
        flaps_position = 0
        flap_drag  = 0.0
        stall_limit_speed = 140
        
def landing_gear(dt):
    global drag_coefficient, landing_gear_position, gear_drag
    
    if keyboard.is_pressed("g"):
        landing_gear_position = "DOWN"
        gear_drag = 0.0002
    if keyboard.is_pressed("h"):
        landing_gear_position = "UP"
        gear_drag = 0.0
    
def autopilot(dt):
    global autopilot_active, autopilot_target_altitude, altitude, pitch

    if keyboard.is_pressed("o"):
        autopilot_active = True
        autopilot_target_altitude = 3000  

    if keyboard.is_pressed("p"):
        autopilot_active = False

    if autopilot_active == True:
        if altitude < autopilot_target_altitude - 20:
            pitch = 5
        elif altitude > autopilot_target_altitude + 20:
            pitch = -5
        else:
            pitch = 0

while True:
    dt = delta_time()
    calculate_engine(dt)

    target_n1 = tla * 0.8 + 20

    autopilot(dt)
    landing_gear(dt)
    update_n1(dt)   
    flaps(dt)
    check_stall(dt)
    fbw_pitch_control(dt)
    fbw_roll_control(dt)
    update_speed(dt)
    update_altitude(dt)
    update_display()
    
    time.sleep(0.05)