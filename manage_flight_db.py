#!/usr/bin/env python3
"""
Utility to manage the local flight database.
Allows adding known routes, viewing statistics, and managing cached flight data.
"""

import argparse
import sys
from pathlib import Path
from flight_database import FlightDatabase


def show_menu():
    """Display the main menu."""
    print("\n" + "="*60)
    print("Flight Database Manager")
    print("="*60)
    print("1. Add a known flight route")
    print("2. View frequent routes")
    print("3. View all cached flights")
    print("4. Add airline prefix mapping")
    print("5. Get airline by callsign prefix")
    print("6. Cleanup expired records")
    print("7. Export database to JSON")
    print("8. Exit")
    print("="*60)


def add_route(db: FlightDatabase):
    """Interactively add a known route."""
    print("\n--- Add Known Flight Route ---")
    origin = input("Enter origin airport code (e.g., KIAH): ").upper().strip()
    destination = input("Enter destination airport code (e.g., KJFK): ").upper().strip()
    aircraft = input("Enter aircraft type (optional, e.g., B737): ").strip() or None
    
    db.add_known_route(origin, destination, aircraft)
    print(f"✓ Added route: {origin} -> {destination} ({aircraft or 'any aircraft'})")


def view_routes(db: FlightDatabase):
    """Display frequently seen routes."""
    print("\n--- Most Frequent Routes ---")
    routes = db.get_frequent_routes(limit=20)
    
    if not routes:
        print("No routes recorded yet.")
        return
    
    print(f"{'From':<6} {'To':<6} {'Aircraft':<10} {'Frequency':<10}")
    print("-" * 35)
    for route in routes:
        aircraft = route["aircraft_type"] or "Any"
        print(f"{route['origin']:<6} {route['destination']:<6} {aircraft:<10} {route['frequency']:<10}")


def view_flights(db: FlightDatabase):
    """Display all cached flight records."""
    print("\n--- Cached Flight Records ---")
    flights = db.get_all_flights()
    
    if not flights:
        print("No cached flights.")
        return
    
    print(f"{'Callsign':<10} {'From':<6} {'To':<6} {'Aircraft':<12} {'Delay (min)':<12} {'Updated':<20}")
    print("-" * 70)
    for flight in flights:
        origin = flight["origin"] or "N/A"
        dest = flight["destination"] or "N/A"
        aircraft = flight["aircraft_type"] or "N/A"
        delay = str(flight["delay_minutes"] or "On-time")
        print(f"{flight['callsign']:<10} {origin:<6} {dest:<6} {aircraft:<12} {delay:<12} {flight['last_updated']:<20}")


def add_airline(db: FlightDatabase):
    """Interactively add an airline prefix mapping."""
    print("\n--- Add Airline Prefix ---")
    prefix = input("Enter callsign prefix (e.g., UAL for United): ").upper().strip()
    airline = input("Enter airline name (e.g., United Airlines): ").strip()
    
    db.add_airline_prefix(prefix, airline)
    print(f"✓ Added mapping: {prefix} -> {airline}")


def get_airline(db: FlightDatabase):
    """Look up airline by prefix."""
    print("\n--- Lookup Airline ---")
    prefix = input("Enter callsign prefix (e.g., UAL): ").upper().strip()
    
    airline = db.get_airline_by_prefix(prefix)
    if airline:
        print(f"✓ {prefix} -> {airline}")
    else:
        print(f"✗ No mapping found for {prefix}")


def cleanup(db: FlightDatabase):
    """Clean up expired records."""
    print("\n--- Cleanup Expired Records ---")
    deleted = db.cleanup_expired()
    print(f"✓ Deleted {deleted} expired records")


def export_to_json(db: FlightDatabase):
    """Export database to JSON file."""
    import json
    from datetime import datetime
    
    print("\n--- Export to JSON ---")
    
    flights = db.get_all_flights()
    routes = db.get_frequent_routes(limit=100)
    
    export_data = {
        "exported_at": datetime.now().isoformat(),
        "flights": flights,
        "routes": routes
    }
    
    export_file = Path("flight_data_export.json")
    with open(export_file, "w") as f:
        json.dump(export_data, f, indent=2)
    
    print(f"✓ Exported {len(flights)} flights and {len(routes)} routes to {export_file}")


def main():
    """Main interactive menu loop."""
    parser = argparse.ArgumentParser(description="Manage flight database")
    parser.add_argument("--db", default="data/flighttrackr.db", help="Path to database file")
    args = parser.parse_args()
    
    db_path = Path(args.db)
    db = FlightDatabase(db_path)
    
    while True:
        show_menu()
        choice = input("Enter your choice (1-8): ").strip()
        
        try:
            if choice == "1":
                add_route(db)
            elif choice == "2":
                view_routes(db)
            elif choice == "3":
                view_flights(db)
            elif choice == "4":
                add_airline(db)
            elif choice == "5":
                get_airline(db)
            elif choice == "6":
                cleanup(db)
            elif choice == "7":
                export_to_json(db)
            elif choice == "8":
                print("\nGoodbye!")
                sys.exit(0)
            else:
                print("Invalid choice. Please try again.")
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            sys.exit(0)
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
