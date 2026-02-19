# LED Matrix Clock (Raspberry Pi + Charlieplex Bonnet)

A minimalist, offline-capable LED clock built with a Raspberry Pi and an Adafruit Charlieplex 16×8 LED Matrix Bonnet.

Designed to function as a standalone appliance with RTC timekeeping and automatic startup.

---

## ✨ Features

- 12-hour time display
- Clean pixel-style digits for high readability
- Smooth minute progress bar
- Hourly explosion animation 💥
- Offline timekeeping via RTC
- Auto-start on boot
- Low CPU usage & flicker-free rendering

---

## 📷 Display Layout

9:42
██████░░░░░░░░


- Time centered for readability  
- Bottom row shows minute progress  
- Explosion animation at top of hour  

---

## 🧰 Required Hardware

### Core Components
- Raspberry Pi (Zero 2 W recommended)
- MicroSD card (8GB+)
- 5V power supply

### Display
- [Adafruit Charlieplex 16×8 LED Matrix Bonet (cool white)](https://www.adafruit.com/product/3467)

### Timekeeping (Recommended)
- DS3231 RTC module
- CR2032 coin cell battery

### Optional
- STEMMA QT cable (for RTC)
- Case or enclosure

---

## 🔌 Wiring

If the bonnet is mounted on the Pi header → **no wiring required**.

### RTC Wiring (DS3231)

| RTC | Raspberry Pi |
|-----|-------------|
| VCC | 5V (Pin 2) |
| GND | GND (Pin 6) |
| SDA | GPIO2 / Pin 3 |
| SCL | GPIO3 / Pin 5 |

---

## 🖥️ Software Setup

### 1️⃣ Install Raspberry Pi OS
Raspberry Pi OS Lite is recommended.

---

### 2️⃣ Enable I²C

```bash
sudo raspi-config
```
Interface Options → I2C → Enable

Reboot if prompted.

### 3️⃣ Install dependencies
```
sudo apt update
sudo apt install python3-pip python3-pil python3-smbus i2c-tools
```

### 4️⃣ Create virtual environment
```
python3 -m venv ~/clockenv
source ~/clockenv/bin/activate
```

### 6️⃣ Clone the repository
```
git clone https://github.com/dbzx6r/pdpm-clock.git
cd YOUR_REPO
```

### 7️⃣ Test the clock
```
source ~/clockenv/bin/activate
python clock.py
```

If everything is correct, the clock will appear.

---

### ⏱️ RTC Setup (DS3231)

Edit boot configuration:
```
sudo nano /boot/firmware/config.txt
```

Add:
```
dtoverlay=i2c-rtc,ds3231
```
Reboot:
```
sudo reboot
```

Verify detection:
```
i2cdetect -y 1
```

You should see:
```
68
```

---

### 🚀 Auto-Start on Boot

Create the service:
```
sudo nano /etc/systemd/system/ledclock.service
```
Paste:
```
[Unit]
Description=LED Matrix Clock
After=multi-user.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/home/**YOUR_USERNAME**
ExecStart=/home/**YOUR_USERNAME**/clockenv/bin/python /home/**YOUR_USERNAME**/**YOUR_REPO**/clock.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```
Enable and start:
```
sudo systemctl daemon-reload
sudo systemctl enable ledclock
sudo systemctl start ledclock
```
---

### 🔄 Updating After Code Changes

Restart the clock service:
```
sudo systemctl restart ledclock
```

View logs:
```
journalctl -u ledclock -f
```

---

### 🎛️ Customization
Adjust brightness
```
BRIGHTNESS = 64
```
Change refresh smoothness
``` time.sleep(0.1) ```

Disable explosion animation

Remove or comment the explosion() call.
