import time
import random
import board
from PIL import Image, ImageDraw
from adafruit_is31fl3731.charlie_bonnet import CharlieBonnet
import adafruit_dht

# ---------- USER SETTINGS ----------

DAY_BRIGHTNESS = 55
NIGHT_BRIGHTNESS = 30

TRANSITION_STEPS = 6
TRANSITION_DELAY = 0.04

# ---------- Hardware Setup ----------

i2c = board.I2C()
display = CharlieBonnet(i2c)

dht = adafruit_dht.DHT22(board.D4)

# ---------- Digit Font ----------

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

# ---------- Brightness Control ----------

def current_brightness(hour):
    if 5 <= hour < 17:
        return DAY_BRIGHTNESS
    else:
        return NIGHT_BRIGHTNESS

# ---------- Drawing Helpers ----------

def draw_digit(draw, d, x, b):
    for r,row in enumerate(digits[d]):
        for c,val in enumerate(row):
            if val == "1":
                draw.point((x+c, r+1), fill=b)

def draw_colon(draw, b):
    draw.point((7,2), fill=b)
    draw.point((7,4), fill=b)

def draw_progress(draw, now, b):
    progress = (now.tm_sec + now.tm_sec/60) / 60 * 16
    full_leds = int(progress)
    partial = progress - full_leds

    for x in range(full_leds):
        draw.point((x, 7), fill=b)

    if full_leds < 16:
        level = int(b * partial)
        if level > 0:
            draw.point((full_leds, 7), fill=level)

# ---------- Screen Renderers ----------

def render_clock(now, b):
    image = Image.new("L", (display.width, display.height))
    draw = ImageDraw.Draw(image)

    hour = time.strftime("%I", now)
    minute = time.strftime("%M", now)

    if hour.startswith("0"):
        hour = hour[1]

    if len(hour) == 1:
        draw_digit(draw, hour, 2, b)
        draw_colon(draw, b)
        draw_digit(draw, minute[0], 9, b)
        draw_digit(draw, minute[1], 13, b)
    else:
        draw_digit(draw, hour[0], 0, b)
        draw_digit(draw, hour[1], 4, b)
        draw_colon(draw, b)
        draw_digit(draw, minute[0], 9, b)
        draw_digit(draw, minute[1], 13, b)

    draw_progress(draw, now, b)
    return image


def render_temp(temp_f, b):
    image = Image.new("L", (display.width, display.height))
    draw = ImageDraw.Draw(image)
    text = str(int(round(temp_f)))

    if len(text) == 2:
        draw_digit(draw, text[0], 0, b)
        draw_digit(draw, text[1], 4, b)
    else:
        draw_digit(draw, text, 2, b)

    # degree symbol
    draw.point((12,1), fill=b)
    draw.point((13,1), fill=b)
    draw.point((12,2), fill=b)
    draw.point((13,2), fill=b)

    return image


def render_humidity(humidity, b):
    image = Image.new("L", (display.width, display.height))
    draw = ImageDraw.Draw(image)
    text = str(int(round(humidity)))

    if len(text) == 2:
        draw_digit(draw, text[0], 0, b)
        draw_digit(draw, text[1], 4, b)
    else:
        draw_digit(draw, text, 2, b)

    # percent symbol
    draw.point((11,1), fill=b)
    draw.point((13,3), fill=b)
    draw.point((12,2), fill=b)

    return image


def render_error(b):
    image = Image.new("L", (display.width, display.height))
    draw = ImageDraw.Draw(image)

    # simple block text: ERR
    letters = [
        (0,1),(1,1),(2,1),(0,2),(0,3),(1,3),(0,4),(1,4),(2,4),   # E
        (4,1),(5,1),(4,2),(5,2),(4,3),(5,3),(4,4),(5,4),         # R
        (7,1),(8,1),(7,2),(8,2),(7,3),(8,3),(7,4),(8,4)          # R
    ]

    for p in letters:
        draw.point(p, fill=b)

    return image

# ---------- Smooth Fade ----------

def transition(from_img, to_img):
    if from_img is None:
        display.image(to_img)
        return
    for step in range(TRANSITION_STEPS + 1):
        blended = Image.blend(from_img, to_img, step / TRANSITION_STEPS)
        display.image(blended)
        time.sleep(TRANSITION_DELAY)

# ---------- Sensor Reading ----------

def read_dht():
    try:
        temp_c = dht.temperature
        humidity = dht.humidity

        if temp_c is None or humidity is None:
            return None, None

        temp_f = temp_c * 9/5 + 32
        return temp_f, humidity

    except RuntimeError:
        return None, None

# ---------- Explosion Animation ----------

def explosion(b):
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
                draw.point((x, y), fill=b)

        display.image(image)
        time.sleep(0.03)

# ---------- Main Loop ----------

last_hour = -1
last_sensor_minute = -1
previous_image = None

while True:
    now = time.localtime()
    brightness = current_brightness(now.tm_hour)

    # hourly explosion
    if now.tm_min == 0 and now.tm_sec == 0 and now.tm_hour != last_hour:
        explosion(brightness)
        last_hour = now.tm_hour

    # sensor display at :30
    if now.tm_sec == 30 and now.tm_min != last_sensor_minute:
        temp_f, humidity = read_dht()

        if temp_f is None or humidity is None:
            err_img = render_error(brightness)
            transition(previous_image, err_img)
            time.sleep(5)
            previous_image = err_img
        else:
            temp_img = render_temp(temp_f, brightness)
            transition(previous_image, temp_img)
            time.sleep(5)

            hum_img = render_humidity(humidity, brightness)
            transition(temp_img, hum_img)
            time.sleep(5)
            previous_image = hum_img

        last_sensor_minute = now.tm_min

    clock_img = render_clock(now, brightness)
    display.image(clock_img)
    previous_image = clock_img

    time.sleep(0.1)
