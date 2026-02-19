import time
import random
import board
from PIL import Image, ImageDraw
from adafruit_is31fl3731.charlie_bonnet import CharlieBonnet

BRIGHTNESS = 64

i2c = board.I2C()
display = CharlieBonnet(i2c)

# 3x5 compact digits
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
}

def draw_digit(draw, d, x):
    for r,row in enumerate(digits[d]):
        for c,val in enumerate(row):
            if val == "1":
                draw.point((x+c, r+1), fill=BRIGHTNESS)

def draw_colon(draw, visible):
    if visible:
        draw.point((7,2), fill=BRIGHTNESS)
        draw.point((7,4), fill=BRIGHTNESS)

def draw_progress(draw, now):
    # smooth sweep across minute
    progress = (now.tm_sec + now.tm_sec/60) / 60 * 16

    full_leds = int(progress)
    partial = progress - full_leds

    # solid LEDs
    for x in range(full_leds):
        draw.point((x, 7), fill=BRIGHTNESS)

    # fractional leading LED (smooth motion)
    if full_leds < 16:
        level = int(BRIGHTNESS * partial)
        if level > 0:
            draw.point((full_leds, 7), fill=level)

def draw_time(now):
    image = Image.new("L", (display.width, display.height))
    draw = ImageDraw.Draw(image)

    hour = time.strftime("%I", now)
    minute = time.strftime("%M", now)

    if hour.startswith("0"):
        hour = hour[1]

    if len(hour) == 1:
        draw_digit(draw, hour, 2)
        draw_colon(draw, True)
        draw_digit(draw, minute[0], 9)
        draw_digit(draw, minute[1], 13)
    else:
        draw_digit(draw, hour[0], 0)
        draw_digit(draw, hour[1], 4)
        draw_colon(draw, True)
        draw_digit(draw, minute[0], 9)
        draw_digit(draw, minute[1], 13)

    draw_progress(draw, now)

    display.image(image)

def explosion():
    particles = []
    cx, cy = 8, 4

    for _ in range(25):
        particles.append([
            cx, cy,
            random.uniform(-1.5, 1.5),
            random.uniform(-1.0, 1.0)
        ])

    for _ in range(25):
        image = Image.new("L", (display.width, display.height))
        draw = ImageDraw.Draw(image)

        for p in particles:
            p[0] += p[2]
            p[1] += p[3]
            x = int(p[0])
            y = int(p[1])
            if 0 <= x < 16 and 0 <= y < 8:
                draw.point((x, y), fill=BRIGHTNESS)

        display.image(image)
        time.sleep(0.03)

last_hour = -1

while True:
    now = time.localtime()

    # hourly explosion
    if now.tm_min == 0 and now.tm_sec == 0 and now.tm_hour != last_hour:
        explosion()
        last_hour = now.tm_hour

    draw_time(now)

    # faster refresh for smooth sweep
    time.sleep(0.1)
