# Flight Database Guide - No AeroAPI Required! 🎉

## Overview

FlightTrackr now uses a **local SQLite database** instead of the expensive FlightAware AeroAPI. This means:

- ✅ **$0 cost** - No more API bills
- ✅ **Fast** - Instant local lookups instead of waiting for API
- ✅ **Private** - All data stays on your device
- ✅ **Works offline** - Once cached, no internet needed for lookups

## Quick Start

### 1. Generate Initial Data (30 seconds)

```bash
# Start the tracker normally (with AirportDB enabled if you have it)
python3 main.py

# Let it run for a few minutes, catch a few flights
# The database will automatically populate from:
# - AirportDB enrichment (free)
# - Manual entries you add

# Stop with Ctrl+C
```

### 2. Manage Your Database

```bash
python3 manage_flight_db.py
```

**Available options:**
- **1**: Add known routes (e.g., IAH → JFK)
- **2**: View frequently seen routes
- **3**: View all cached flight records
- **4**: Add airline callsign prefixes
- **5**: Look up airlines
- **6**: Clean up expired records
- **7**: Export to JSON

### 3. Populate with Known Routes

Manually add routes you expect to see in your area:

```bash
python3 manage_flight_db.py
# Select option 1
# Enter: KIAH (Houston origin)
# Enter: KJFK (New York destination)
# Enter: B737 (optional aircraft type)
```

## Database Structure

### Flights Table
Stores enriched flight data cached from lookups:
```sql
callsign TEXT          -- Flight identifier
origin TEXT            -- ICAO departure airport code
destination TEXT       -- ICAO arrival airport code
aircraft_type TEXT     -- Aircraft model (e.g., B737, A320)
delay_minutes INTEGER  -- Minutes delayed/early
expires_at TIMESTAMP   -- When this entry expires
```

### Known Routes Table
Tracks routes you've seen, with frequency stats:
```sql
origin_code TEXT       -- Departure airport
destination_code TEXT  -- Arrival airport
aircraft_type TEXT     -- Aircraft model
frequency INTEGER      -- How many times seen
last_seen TIMESTAMP    -- When we last saw this route
```

### Airline Cache Table
Maps callsign prefixes to airline names:
```sql
callsign_prefix TEXT   -- E.g., "UAL" for United
airline_name TEXT      -- E.g., "United Airlines"
```

## Workflow Examples

### Example 1: Track Houston-Miami Flights

```bash
python3 manage_flight_db.py

# Option 1: Add known route
# Origin: KIAH
# Destination: KMIA
# Aircraft: B738

# Next time Southwest SWA5000 Houston→Miami is detected,
# the system will look it up from the database instantly!
```

### Example 2: Export Your Data

```bash
python3 manage_flight_db.py
# Option 7: Export to JSON
# Creates: flight_data_export.json

cat flight_data_export.json
# View all your cached flights and frequent routes
```

### Example 3: Clean Old Data

```bash
python3 manage_flight_db.py
# Option 6: Cleanup expired records
# Removes entries older than 24 hours (default)
```

## Python API Usage

If you want to programmatically interact with the database:

```python
from flight_database import FlightDatabase
from pathlib import Path
from models import FlightDetails

# Initialize database
db = FlightDatabase(Path("data/flighttrackr.db"))

# Get cached flight data
details = db.get_flight_details("UAL1234")
if details:
    print(f"From: {details.origin}")
    print(f"To: {details.destination}")
    print(f"Aircraft: {details.aircraft_type}")
    print(f"Delay: {details.delay_minutes} min")

# Store new flight data
db.store_flight_details(
    callsign="UAL1234",
    origin="KIAH",
    destination="KJFK",
    aircraft_type="B787",
    delay_minutes=15,
    expires_in_hours=24
)

# Add a known route
db.add_known_route("KIAH", "KJFK", "B787")

# Get statistics
routes = db.get_frequent_routes(limit=10)
for route in routes:
    print(f"{route['origin']} → {route['destination']}: {route['frequency']} times")

# Get all cached flights
all_flights = db.get_all_flights()
print(f"Total cached flights: {len(all_flights)}")
```

## Migration from FlightAware

If you were previously using FlightAware AeroAPI:

1. **Stop paying** - No more API key needed ✅
2. **Remove FlightAware from config.toml** - It's ignored now
3. **Let the system learn** - Run normally, it will auto-populate
4. **Or populate manually** - Use `manage_flight_db.py` to add routes

## Tips & Tricks

### Keep Your Database Fresh
```bash
# Run occasionally to clean up old data
python3 manage_flight_db.py
# Option 6: Cleanup (removes entries > 24 hours old)
```

### Track Specific Airlines
```bash
python3 manage_flight_db.py
# Option 4: Add airline prefix
# Prefix: UAL
# Name: United Airlines

# Now the system knows UAL = United Airlines
```

### Share Your Routes
Export and share common routes in your area:
```bash
python3 manage_flight_db.py
# Option 7: Export

# Share flight_data_export.json with other users!
```

### Analyze Traffic Patterns
```python
from flight_database import FlightDatabase
from pathlib import Path

db = FlightDatabase(Path("data/flighttrackr.db"))
routes = db.get_frequent_routes(limit=50)

# Show top 10 routes
for route in routes[:10]:
    print(f"{route['origin']:5} → {route['destination']:5}  "
          f"({route['aircraft_type']:8}) {route['frequency']:3} times")
```

## Troubleshooting

**Q: "No cached data found for flight X"**  
A: First time seeing it! The system will cache after first detection. Or manually add the route.

**Q: How do I see what's in my database?**  
A: Run `python3 manage_flight_db.py` and select option 3 (View all cached flights)

**Q: Can I import from a backup?**  
A: Yes! Database is a standard SQLite file at `data/flighttrackr.db`. Use any SQLite tool.

**Q: Database file seems large?**  
A: Clean up old entries: `python3 manage_flight_db.py` → Option 6

## Summary

| Feature | FlightAware | Local Database |
|---------|------------|----------------|
| **Cost** | $1-50+/month | $0 |
| **Lookup Speed** | 1-2 seconds (API wait) | Instant (local) |
| **Requires Internet** | Yes, always | Only for new enrichment |
| **Privacy** | Data sent to FlightAware | All local |
| **Setup** | Credit card, API key | Just run the tracker |
| **Monthly Limits** | 1000 calls | Unlimited local lookups |

**You now have unlimited free flight tracking!** 🚀
