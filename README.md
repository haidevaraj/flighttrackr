
                                  "Turn your Pi into a flight radar station"

## My Fork

This is a fork of [ajharnak/flighttrackr](https://github.com/ajharnak/flighttrackr) with the following additions:

### New Features
- **Text-to-Speech Support** — Audio alerts via Bluetooth speaker
- Configurable speech alerts for detected aircraft
## Text-to-Speech (TTS) Feature

This fork adds audio alerts using **Google Text-to-Speech (gTTS)** with a real human Indian female voice.

### TTS Engine
- **Primary:** gTTS v2.3.1 (Google Text-to-Speech - High quality, real human voice)
  - Language: English with Indian accent (`lang='en'`, `tld='co.in'`)
  - Provides realistic female voice for flight alerts
  
- **Fallback:** Coqui TTS (High-quality offline synthesis using VITS models)

### Installation
TTS dependencies are included in `requirements.txt`:
```bash
git clone https://github.com/haidevaraj/PiRadar.git
cd PiRadar
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2️⃣ Configure

```bash
cp config.example.toml config.toml
nano config.toml
```

Fill in:
- `latitude` & `longitude` (your location)
- `radius_miles` (detection range)
- OpenSky API credentials
- Bluetooth speaker volume
- Snooze hours (optional)

### 3️⃣ Run

```bash
python3 main.py
```

See flights detected on your OLED and hear voice alerts! 🎉

---

## 📋 Hardware Setup

### What You'll Need

| Component | Purpose | Link |
|-----------|---------|------|
| **Raspberry Pi 5 4GB** | Main processor | [GigaParts](https://www.gigaparts.com) |
| **2.42" SSD1309 OLED** | Flight display | [Amazon](https://www.amazon.com/dp/B0CFF46319) |
| **Bluetooth Speaker** | Voice alerts | Any BT speaker |
| **Dupont Jumper Wires (120x)** | I2C connections | [Amazon](https://www.amazon.com/dp/B0B2L66ZFM) |
| **USB-C Power Supply** | Pi 5 power (5.1V/5A) | Included in starter kit |

### Wiring the OLED

```
OLED Pin → Raspberry Pi Pin
─────────────────────────────
GND      → Pin 6 (GND)
VCC      → Pin 1 (3.3V)
SDA      → Pin 3 (GPIO2)
SCL      → Pin 5 (GPIO3)
```

**Diagram:**
```
┌─────────────────────────────┐
│     Raspberry Pi 5          │
├─────────────────────────────┤
│ Pin 1  ├─────→ 3.3V (VCC)   │
│ Pin 3  ├─────→ SDA          │
│ Pin 5  ├─────→ SCL          │
│ Pin 6  ├─────→ GND          │
└─────────────────────────────┘
        ↓
    OLED Display
```

**Verify connection:**
```bash
i2cdetect -y 1
# Should show "3c" in the grid
```

## 📂 Local Data Management

### Master Airport Database
PiRadar uses the `mwgg/Airports` dataset for free airport lookups.
1. Download `airports.json` from mwgg/Airports.
2. Place it in the `assets/` folder as `assets/airports.json`.
3. PiRadar will now resolve codes like `KIAH` to "George Bush Intercontinental" instantly and offline.


## ⚙️ Configuration

Edit `config.toml` to customize:

```toml
[api_keys]
opensky_client_id = "YOUR_ID"
opensky_client_secret = "YOUR_SECRET"
airportdb_api_token = ""

[common]
latitude = 29.7604               # Houston example
longitude = -95.3698
radius_miles = 30
poll_interval_seconds = 10
cooldown_minutes = 15            # Alert cooldown per flight
alert_volume = 0.8

# Quiet hours (snooze)
snooze_start_time = "22:00"      # 10 PM
snooze_end_time = "07:00"        # 7 AM

# Text-to-speech
enable_airline_announcement = true
announcement_delay_seconds = 0.5
```

---

## 📡 API Setup

### OpenSky Network (Free, Required)

1. Sign up: https://opensky-network.org/data/api
2. Create credentials
3. Add to `config.toml`:
```toml
opensky_client_id = "YOUR_ID"
opensky_client_secret = "YOUR_SECRET"
```

### FlightAware AeroAPI (Deprecated ❌)

**FlightAware AeroAPI has been completely removed from this fork!**

Previously, the app used AeroAPI for flight enrichment (routes, aircraft type, delays). This was:
- ❌ Expensive ($1-50+/month depending on usage)
- ❌ Requires internet for every lookup
- ❌ Rate limited

**Solution:** Use the **local SQLite database** instead! See the [Local Flight Database section](#-local-flight-database-no-aeroapi-required) above.

### AirportDB (Free, Optional)

Airport name lookups (e.g., "Houston Hobby" instead of "HOU").

1. Sign up: https://airportdb.io/
2. Get API token
3. Add to `config.toml`:
```toml
airportdb_api_token = "YOUR_TOKEN"
```

---

## � Local Flight Database (No AeroAPI Required!)

**FlightAware AeroAPI has been completely removed!** FlightTrackr now uses a **local SQLite database** to store flight enrichment data instead. This means:

✅ **Zero API costs** - No more expensive AeroAPI charges  
✅ **Offline capable** - Works without internet (after initial data)  
✅ **Fast lookups** - Instant database queries vs API wait times  
✅ **Privacy** - All data stays on your device  

### How It Works

1. **OpenSky API** provides real-time flight tracking (free)
2. **Local SQLite database** caches known routes and flight data
3. **First time you see a flight**: Data stored locally for future use
4. **Next time same flight appears**: Instant lookup from database!

### Managing Your Flight Database

Use the interactive database manager to:

```bash
python3 manage_flight_db.py
```

**Menu options:**
- Add known flight routes (e.g., Houston → Denver)
- View statistics of routes you've seen
- Look up cached flight data
- Add airline callsign mappings
- Export data to JSON
- Clean up old records

### Populating Your Database

**Method 1: Automatic (Recommended)**
- Run the tracker normally with AirportDB enabled (free)
- AirportDB enriches flights, data gets cached automatically
- After 1-2 weeks of operation, your database fills up naturally

**Method 2: Manual Entry**
```bash
python3 manage_flight_db.py
# Option 1: Add known routes manually
# Enter routes you know frequent your airspace
```

**Method 3: Bulk Import**
```python
from flight_database import FlightDatabase
from pathlib import Path

db = FlightDatabase(Path("data/flighttrackr.db"))

# Add common routes from your area
routes = [
    ("KIAH", "KJFK", "B737"),  # Houston → NYC
    ("KIAH", "KLAX", "B777"),  # Houston → LA
    ("KIAH", "KORD", "A320"),  # Houston → Chicago
]

for origin, dest, aircraft in routes:
    db.add_known_route(origin, dest, aircraft)
```

### Database Files

```
data/
├── flighttrackr.db          ← Main SQLite database
└── airportdb_cache.json     ← AirportDB enrichment cache (optional)
```

### Viewing Your Database

```bash
python3 manage_flight_db.py
# Option 3: View all cached flights
# Option 2: View frequent routes
```

---

## �🐧 Raspberry Pi Setup

### 1. Flash OS

Use [Raspberry Pi Imager](https://www.raspberrypi.com/software/):
- OS: **Raspberry Pi OS Lite** (64-bit recommended)
- Username: `pi`
- Enable SSH
- Configure WiFi

### 2. First Boot

```bash
sudo apt update && sudo apt upgrade -y
```

### 3. Enable I2C (for OLED)

```bash
sudo raspi-config
# Interface Options → I2C → Enable → Finish
sudo reboot
```

### 4. Verify I2C

```bash
sudo apt install -y i2c-tools
i2cdetect -y 1
# Look for "3c" in the grid
```

### 5. Install PiRadar

```bash
cd ~
git clone https://github.com/haidevaraj/PiRadar.git
cd PiRadar
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp config.example.toml config.toml
# Edit config.toml with your API keys and location
python3 main.py
```

---

## 🤖 Bluetooth Speaker Setup

### Pair Speaker

```bash
bluetoothctl
```

Inside bluetoothctl shell:
```
power on
scan on
# Wait for speaker to appear
pair AA:BB:CC:DD:EE:FF
trust AA:BB:CC:DD:EE:FF
connect AA:BB:CC:DD:EE:FF
exit
```

### Test Audio

```bash
paplay /usr/share/sounds/alsa/Front_Center.wav
```

Should hear sound from speaker! ✅

---

## 🔄 Auto-Start on Boot

### Create Systemd Service

```bash
sudo nano /etc/systemd/system/PiRadar.service
```

Paste:
```ini
[Unit]
Description=PiRadar Flight Tracker
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/PiRadar
ExecStart=/home/pi/PiRadar/.venv/bin/python /home/pi/PiRadar/main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

### Enable Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable PiRadar.service
sudo systemctl start PiRadar.service
```

### View Logs

```bash
sudo journalctl -u PiRadar.service -f
```

**Useful commands:**
```bash
sudo systemctl status PiRadar.service
sudo systemctl stop PiRadar.service
sudo systemctl restart PiRadar.service
```

---

## 🎨 Display Features

### Alert Screen
When a flight is detected:
```
┌────────────────────────────────┐
│  UAL1234                       │  ← Callsign
│  Houston IAH → Denver DEN      │  ← Route
│  SPD: 450kt  HDG: 315°  ALT:35K │  ← Flight data
│  VS: 1200fpm ▲                 │  ← Vertical speed
└────────────────────────────────┘
```

### Idle Screen
Shows rotating airplane facts while waiting for flights.

### Snooze Indicator
Displays "SNOOZED UNTIL 7:00 AM" during quiet hours.

---

## 📊 Alert Behavior

When a new flight enters your detection radius:

1. 🔊 **Alert sound plays** (chime.mp3 or alert.mp3)
2. 📱 **OLED shows flight details**
3. 🗣️ **Voice announcement** (if enabled)
   - "Southwest Airlines SWA4389 Hartsfield Jackson Atlanta International Airport -> San Antonio International Airport. Cruising at 35,000 feet, 451 miles per hour, heading south, 15 minutes delayed."
4. 📝 **Logged to console**

**Squawk codes:**
- `7700` → Emergency (plays alert.mp3)
- `7500` → Hijack (plays alert.mp3)
- Others → Normal (plays chime.mp3)

**Cooldown:** Same callsign won't re-alert for `cooldown_minutes` (default: 15)

---

## 🛠️ Troubleshooting

### OLED Not Showing

```bash
# Check I2C connection
i2cdetect -y 1
# Should show "3c"

# Check wiring: GND, VCC, SDA, SCL
# Try raising Pi I2C voltage to 5V (if display supports it)
```

### No Audio/Bluetooth Not Working

```bash
# Check speaker is paired
bluetoothctl devices

# Restart PulseAudio
pulseaudio --kill
pulseaudio --start

# Test audio
paplay /usr/share/sounds/alsa/Front_Center.wav
```

### API Errors

```bash
# Check OpenSky credentials
curl -u YOUR_ID:YOUR_SECRET "https://opensky-network.org/api/states/all"
# Should return JSON

# Check FlightAware key
curl -H "x-apikey: YOUR_KEY" "https://aeroapi.flightaware.com/aeroapi/me"
```

### High CPU Usage

```bash
journalctl -u flighttrackr.service -f
```

Useful service commands:

- Start: `sudo systemctl start flighttrackr.service`
- Stop: `sudo systemctl stop flighttrackr.service`
- Restart: `sudo systemctl restart flighttrackr.service`
- Disable autostart: `sudo systemctl disable flighttrackr.service`

## How this works now:
Detection: A flight is detected (e.g., SWA4389).
Local DB Check: The system looks in flighttrackr.db. It finds that SWA4389 flies KATL -> KSAT.
Fallback Trigger: The FlightTracker sees KATL and KSAT are raw 4-character codes (not full names).
JSON Lookup: It asks AirportDbClient for the names.
Offline Match: AirportDbClient checks your assets/airports.json first. It instantly finds "Hartsfield Jackson Atlanta International Airport" and "San Antonio International Airport".
Update: The system announces the full names and saves the names back to your SQLite DB, so next time even the JSON lookup is skipped.
This effectively means that once you have airports.json, you will almost never need an internet connection or an API token to get high-quality airport names.
## Alert behavior

When a new flight is detected inside the configured radius, the app will:

- Play `assets/chime.mp3` for normal alerts
- Play `assets/alert.mp3` for squawk `7700` or `7500`
- Log the flight details to the console
- Show alerts and system status on the OLED when enabled
- Render a dashboard-style alert layout with a callsign header, route/type detail line, and bottom widgets for `SPD`, `HDG`, `ALT`, and `VS`
- Translate common aircraft type codes into friendlier names via `assets/aircraft_types.json`

If FlightAware is configured and the callsign looks like a known airline, the alert may also include:

- origin and destination airports
- a cleaned-up aircraft type like `CRJ-900` instead of a longer manufacturer-prefixed label

When the display is idle, it rotates airplane facts in random order without repeats until the full fact list has been shown.

## Notes

- If `pygame` cannot initialize the mixer, the app will keep running and log a warning instead of crashing.

## Author, license, and warranty

Author: A.J. Harnak

If you like this project, consider buying me a coffee - https://buymeacoffee.com/ajharnak . Totally optional but greatly appreciated!

This project is source-available for personal, hobbyist, educational, and other non-commercial use only.

You may not use this project, or a modified version of it, for commercial purposes without explicit written permission from the author.

This project is provided as-is, with no warranty of any kind. That includes no warranty for correctness, reliability, fitness for a particular purpose, hardware safety, API costs, or regulatory compliance. You are responsible for your own hardware, accounts, wiring, credentials, and operating costs.

See `LICENSE.md` for the full terms.
