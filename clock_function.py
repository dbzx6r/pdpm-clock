import time
import random
import board
import socket
from PIL import Image, ImageDraw
from adafruit_is31fl3731.charlie_bonnet import CharlieBonnet
import adafruit_dht

# ---------------- USER SETTINGS ----------------
DAY_BRIGHTNESS = 55
NIGHT_BRIGHTNESS = 30
MAX_FAILS = 2  

# ---------------- HARDWARE SETUP ----------------
i2c = board.I2C()
display = CharlieBonnet(i2c)
# DHT22 on Pin D4
dht_device = adafruit_dht.DHT22(board.D4, use_pulseio=False)

last_temp = None
last_humidity = None
fail_count = 0

# ---------------- FONT LIBRARY ----------------
font = {
    "0":["111","101","101","101","111"], "1":["010","110","010","010","111"],
    "2":["111","001","111","100","111"], "3":["111","001","111","001","111"],
    "4":["101","101","111","001","001"], "5":["111","100","111","001","111"],
    "6":["111","100","111","101","111"], "7":["111","001","001","001","001"],
    "8":["111","101","111","101","111"], "9":["111","101","111","001","111"],
    ".":["000","000","000","000","010"], " ":["000","000","000","000","000"], 
    "S":["111","100","111","001","111"], "E":["111","100","110","100","111"],
    "T":["111","010","010","010","010"], "U":["101","101","101","101","111"],
    "P":["111","101","111","100","100"], "O":["111","101","101","101","111"],
    "F":["111","100","110","100","100"], "L":["100","100","100","100","111"],
    "I":["111","010","010","010","111"], "N":["101","111","111","101","101"],
    "C":["111","100","100","100","111"], "A":["111","101","111","101","101"],
}

# ---------------- HELPERS ----------------

def current_brightness(hour):
    return DAY_BRIGHTNESS if 6 <= hour < 20 else NIGHT_BRIGHTNESS

def get_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.5)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "Offline"

def draw_digit(draw, d, x, b):
    if d in font:
        for r, row in enumerate(font[d]):
            for c, val in enumerate(row):
                if val == "1":
                    draw.point((x+c, r+1), fill=b)

def draw_char(draw, char, x, b):
    char = char.upper()
    if char in font:
        for r, row in enumerate(font[char]):
            for c, val in enumerate(row):
                if val == "1":
                    draw.point((x+c, r+1), fill=b)

def draw_colon(draw, b):
    # Original position: Row 2 and 4
    draw.point((7, 2), fill=b)
    draw.point((7, 4), fill=b)

def draw_progress(draw, b):
    now = time.localtime()
    progress = (now.tm_sec / 60) * 16
    full = int(progress)
    for x in range(full):
        draw.point((x, 7), fill=b)
    if full < 16:
        part = progress - full
        draw.point((full, 7), fill=int(b * part))

# ---------------- SENSOR DATA ----------------

def read_dht():
    global last_temp, last_humidity, fail_count
    try:
        temp_c = dht_device.temperature
        humidity = dht_device.humidity
        if temp_c is None or humidity is None:
            raise RuntimeError
        temp_f = temp_c * 9/5 + 32
        last_temp, last_humidity, fail_count = temp_f, humidity, 0
        return temp_f, humidity
    except:
        fail_count += 1
        if last_temp is not None and fail_count <= MAX_FAILS:
            return last_temp, last_humidity
        return None, None

# ---------------- RENDERING ----------------

def render_clock(now, b):
    img = Image.new("L", (16, 8))
    draw = ImageDraw.Draw(img)

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

    draw_progress(draw, b)
    return img

def render_temp(temp, b):
    img = Image.new("L", (16, 8))
    draw = ImageDraw.Draw(img)
    val = f"{temp:04.1f}"
    # Original positioning for temp to ensure F isn't cut off
    draw_digit(draw, val[0], 0, b)
    draw_digit(draw, val[1], 4, b)
    draw_char(draw, ".", 8, b)
    draw_digit(draw, val[3], 10, b)
    # F icon
    for p in [(14,1),(15,1),(14,2),(14,3),(15,3),(14,4),(14,5)]: draw.point(p, fill=b)
    draw_progress(draw, b)
    return img

def render_humidity(h, b):
    img = Image.new("L", (16, 8))
    draw = ImageDraw.Draw(img)
    val = f"{h:04.1f}"
    draw_digit(draw, val[0], 0, b)
    draw_digit(draw, val[1], 4, b)
    draw_char(draw, ".", 8, b)
    draw_digit(draw, val[3], 10, b)
    # % mark
    draw.point((14,1), fill=b); draw.point((13,2), fill=b); draw.point((15,3), fill=b)
    draw_progress(draw, b)
    return img

# ---------------- ANIMATIONS ----------------

def slide_up_transition(img_old, img_new, b, steps=8, delay=0.05):
    for i in range(steps + 1):
        combined = Image.new("L", (16, 8))
        combined.paste(img_old.crop((0,0,16,7)), (0, -i))
        combined.paste(img_new.crop((0,0,16,7)), (0, 7 - i))
        draw = ImageDraw.Draw(combined)
        draw_progress(draw, b)
        display.image(combined)
        time.sleep(delay)

def wipe_right_transition(img_old, img_new, b, steps=16, delay=0.03):
    for i in range(steps + 1):
        combined = Image.new("L", (16, 8))
        combined.paste(img_old)
        part_new = img_new.crop((0, 0, i, 7))
        combined.paste(part_new, (0, 0))
        draw = ImageDraw.Draw(combined)
        draw_progress(draw, b)
        display.image(combined)
        time.sleep(delay)

def explosion(b):
    particles = [[8, 4, random.uniform(-1.5, 1.5), random.uniform(-1.0, 1.0)] for _ in range(25)]
    for _ in range(15):
        img = Image.new("L", (16, 8))
        draw = ImageDraw.Draw(img)
        for p in particles:
            p[0] += p[2]; p[1] += p[3]
            x, y = int(p[0]), int(p[1])
            if 0 <= x < 16 and 0 <= y < 7:
                draw.point((x, y), fill=b)
        draw_progress(draw, b)
        display.image(img)
        time.sleep(0.03)

def scroll_text(text, b, delay=0.04):
    text_width = len(text) * 4
    canvas = Image.new("L", (text_width + 16, 7))
    draw_canvas = ImageDraw.Draw(canvas)
    for i, char in enumerate(text):
        draw_char(draw_canvas, char, 16 + (i * 4), b)
    for x in range(text_width + 16):
        img = Image.new("L", (16, 8))
        img.paste(canvas.crop((x, 0, x + 16, 7)), (0, 0))
        draw_img = ImageDraw.Draw(img)
        draw_progress(draw_img, b)
        display.image(img)
        time.sleep(delay)

# ---------------- MAIN LOOP ----------------

print("Clock Starting - Original Layout Restored.")
last_hour = -1
last_sensor_min = -1

while True:
    try:
        now = time.localtime()
        brightness = current_brightness(now.tm_hour)

        # 1. Hour Blast
        if now.tm_min == 0 and now.tm_sec == 0 and now.tm_hour != last_hour:
            explosion(brightness)
            last_hour = now.tm_hour

        # 2. Network Check (Every 5 mins if Offline)
        if now.tm_min % 5 == 0 and now.tm_sec == 0:
            if get_ip() == "Offline":
                scroll_text("CONNECT TO CLOCK SETUP", NIGHT_BRIGHTNESS)

        # 3. Sensor Cycle at 30s
        if now.tm_sec == 30 and now.tm_min != last_sensor_min:
            temp, hum = read_dht()
            if temp is not None:
                clock_snap = render_clock(now, brightness)
                t_img = render_temp(temp, brightness)
                h_img = render_humidity(hum, brightness)
                
                slide_up_transition(clock_snap, t_img, brightness)
                for _ in range(50): 
                    display.image(render_temp(temp, brightness))
                    time.sleep(0.1)
                
                slide_up_transition(t_img, h_img, brightness)
                for _ in range(50):
                    display.image(render_humidity(hum, brightness))
                    time.sleep(0.1)
                
                now_after = time.localtime()
                wipe_right_transition(h_img, render_clock(now_after, brightness), brightness)
            last_sensor_min = now.tm_min

        # 4. Standard Clock
        else:
            display.image(render_clock(now, brightness))

        time.sleep(0.1)

    except Exception as e:
        print(f"Error: {e}")
        time.sleep(1)
