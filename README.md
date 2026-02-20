# Pi Zero 2W LED Matrix Clock

A standalone LED clock built with a Raspberry Pi Zero 2 W and an Adafruit Charlieplex LED Matrix Bonnet.

This project displays the time with smooth animations, shows environmental data from a DHT22 sensor, restores time from an RTC when offline, and automatically starts on boot.

---

## ✨ Features

- 12-hour clock (no leading zero)
- Smooth minute progress bar
- Hourly explosion animation 💥
- Temperature & humidity display every minute at :30
- Smooth fade transitions
- Day/night auto brightness
- RTC offline timekeeping
- Auto-start on boot
- Low CPU usage & flicker-free display

---

## 🧰 Hardware Required

### Core
- Raspberry Pi Zero 2 W
- MicroSD card (8GB+)
- 5V power supply (2.5A recommended)

### Display
- Adafruit Charlieplex 16×8 LED Matrix Bonet

### Sensors
- DS3231 RTC module
- CR2032 battery
- DHT22 / AM2302 temperature & humidity sensor

---

## 🔌 Wiring & Pinouts

### Charlieplex Bonnet
Mount directly onto the Pi header.

It uses:
- 5V / 3.3V power
- GPIO2 (SDA)
- GPIO3 (SCL)
- Ground

---

## RTC Wiring (DS3231)

RTC shares the I²C bus with the display.

| RTC | Pi Pin | GPIO |
|-----|--------|------|
| VCC | Pin 1 | 3.3V |
| GND | Pin 6 | GND |
| SDA | Pin 3 | GPIO2 |
| SCL | Pin 5 | GPIO3 |

You can split SDA & SCL to share with the bonnet.

---

## DHT22 Wiring

### Recommended pin:

**GPIO4 (Pin 7)**

| Sensor | Pi Pin |
|--------|--------|
| VCC | Pin 1 (3.3V) |
| DATA | Pin 7 |
| GND | Pin 6 |

⚠️ Bare sensors require a **10k resistor** between DATA and VCC.

---

## 🖥️ Software Setup

### 1️⃣ Update system

```bash
sudo apt update && sudo apt upgrade -y
```

### 2️⃣ Enable interfaces
```sudo raspi-config```

## Enable:

```I2C```
SSH (optional)
  
Reboot.

### 3️⃣ Install system dependencies
```sudo apt install -y \
python3-pip \
python3-venv \
python3-pil \
i2c-tools \
gpiod \
python3-libgpiod \
libjpeg-dev \
zlib1g-dev
```

### 4️⃣ Create virtual environment
```
python3 -m venv ~/clockenv
source ~/clockenv/bin/activate
```

### 5️⃣ Install required Python libraries
```
pip install --upgrade pip
pip install \
adafruit-blinka \
adafruit-circuitpython-is31fl3731 \
adafruit-circuitpython-dht \
pillow \
RPi.GPIO
```

### ⚠️ Fix: No module named board

If you see:

```ModuleNotFoundError: No module named 'board'```

You are using system Python instead of the virtual environment.

## Run the script with:
```
source ~/clockenv/bin/activate
python clock.py
```
or:

```~/clockenv/bin/python clock.py```

Verify:

```which python```

Should show:

```/home/pi/clockenv/bin/python```

### 🔍 Verify hardware stack
``` python - <<EOF
import board, busio
import adafruit_is31fl3731
import adafruit_dht
from PIL import Image
print("Hardware stack OK")
EOF
```

### 🔎 Verify I²C devices
```i2cdetect -y 1 ```

Expected:

```74   ← LED matrix
68   ← RTC
```
### RTC Setup (Offline Timekeeping)

Enable overlay:

```sudo nano /boot/firmware/config.txt```

Add:

```dtoverlay=i2c-rtc,ds3231```

Reboot:

```sudo reboot```

Clone & Run
```
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO
source ~/clockenv/bin/activate
python clock.py
```
### 🚀 Auto-Start on Boot

Create service:

```sudo nano /etc/systemd/system/ledclock.service```

Paste:
```
[Unit]
Description=LED Matrix Clock
After=multi-user.target

[Service]
Type=simple
User=blackrock
WorkingDirectory=/home/blackrock/YOUR_REPO
ExecStart=/home/blackrock/clockenv/bin/python /home/blackrock/YOUR_REPO/clock.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```
Enable:
```
sudo systemctl daemon-reload
sudo systemctl enable ledclock
sudo systemctl start ledclock
🔄 Restart After Code Changes
sudo systemctl restart ledclock
```
## Logs:
```
journalctl -u ledclock -f
```
---

### 🕒 Display Behavior
Time  
smooth minute progress bar  
hourly explosion animation  
Every minute at :30  
temperature (5s)  
humidity (5s)  
Sensor failure displays: ```ERR```


---

### 🌙 Auto Brightness
Time	Brightness  
5 AM – 5 PM	55% Brightness  
5 PM – 5 AM	30% Brightness

---

### 🔧 Troubleshooting
  
Display not detected
```i2cdetect -y 1```

Should show ```74```.

RTC not detected
Check wiring and look for address 68.
Sensor not reading
verify pull-up resistor
check GPIO4 wiring
ensure good airflow
  
### Wi-Fi lost after power loss  
Create /boot/wpa_supplicant.conf with credentials.
```“No module named …”```
Ensure virtual environment is active.
