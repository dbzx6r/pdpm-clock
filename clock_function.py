import time
import random
import board
import busio
from datetime import datetime
from adafruit_is31fl3731.charlieplex import CharliePlex

# ---------- DISPLAY ----------
i2c = busio.I2C(board.SCL, board.SDA)
display = CharliePlex(i2c)
display.brightness = 40   # adjust brightness

WIDTH = 16
HEIGHT = 8

buffer = [[0]*WIDTH for _ in range(HEIGHT)]

def clear():
    for y in range(HEIGHT):
        for x in range(WIDTH):
            buffer[y][x] = 0

def pixel(x,y,v=1):
    if 0 <= x < WIDTH and 0 <= y < HEIGHT:
        buffer[y][x] = v

def render():
    for y in range(HEIGHT):
        for x in range(WIDTH):
            display.pixel(x,y,buffer[y][x])

# ---------- FONT ----------
digits = {
"0":["111","101","101","101","111"],
"1":["010","110","010","010","111"],
"2":["111","001","111","100","111"],
"3":["111","001","111","001","111"],
"4":["101","101","111","001","001"],
"5":["111","100","111","001","111"],
"6":["111","100","111","101","111"],
"7":["111","001","001","001","001"],
"8":["111","101","111","101","111"],
"9":["111","101","111","001","111"],
"-":["000","000","111","000","000"]
}

def draw_digit(d,x,y):
    pattern = digits[d]
    for r in range(5):
        for c in range(3):
            if pattern[r][c]=="1":
                pixel(x+c,y+r)

def draw_colon(on):
    if on:
        pixel(7,1)
        pixel(7,3)

# ---------- CLOCK DISPLAY ----------
def draw_clock(now):
    clear()

    hour = now.strftime("%H")
    minute = now.strftime("%M")
    month = now.strftime("%m")
    day = now.strftime("%d")

    # Time
    draw_digit(hour[0],0,0)
    draw_digit(hour[1],4,0)
    draw_digit(minute[0],9,0)
    draw_digit(minute[1],13,0)
    draw_colon(now.second % 2 == 0)

    # Date
    draw_digit(month[0],1,3)
    draw_digit(month[1],5,3)
    draw_digit("-",8,3)
    draw_digit(day[0],10,3)
    draw_digit(day[1],14,3)

    render()

# ---------- EXPLOSION EFFECT ----------
def explosion():
    center_x = WIDTH // 2
    center_y = HEIGHT // 2

    particles = []

    for _ in range(40):
        particles.append([
            center_x,
            center_y,
            random.uniform(-1.5,1.5),
            random.uniform(-1.0,1.0)
        ])

    for frame in range(25):
        clear()

        for p in particles:
            p[0] += p[2]
            p[1] += p[3]
            pixel(int(p[0]), int(p[1]))

        render()
        time.sleep(0.04)

# ---------- MAIN LOOP ----------
last_hour = -1

while True:
    now = datetime.now()

    # trigger explosion at top of hour
    if now.minute == 0 and now.second == 0 and now.hour != last_hour:
        explosion()
        last_hour = now.hour

    draw_clock(now)
    time.sleep(0.25)
