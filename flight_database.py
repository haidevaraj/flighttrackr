"""
SQLite-based flight enrichment database.
Stores known flight routes, aircraft types, and other enrichment data locally.
No external API calls needed (except for initial OpenSky data).
"""

import sqlite3
import logging
from pathlib import Path
from datetime import UTC, datetime, timedelta
from models import FlightDetails

logger = logging.getLogger(__name__)


class FlightDatabase:
    """Local SQLite database for storing and retrieving flight enrichment data."""

    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize_db()

    def _initialize_db(self) -> None:
        """Create tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Table for storing flight information by callsign
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS flights (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    callsign TEXT UNIQUE NOT NULL,
                    origin TEXT,
                    destination TEXT,
                    aircraft_type TEXT,
                    airline_name TEXT,
                    delay_minutes INTEGER,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP
                )
            """)
            
            # Table for caching airline information by callsign prefix
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS airline_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    callsign_prefix TEXT UNIQUE NOT NULL,
                    airline_name TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Table for known routes
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS known_routes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    origin_code TEXT NOT NULL,
                    destination_code TEXT NOT NULL,
                    aircraft_type TEXT,
                    frequency INTEGER DEFAULT 1,
                    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(origin_code, destination_code, aircraft_type)
                )
            """)
            
            conn.commit()
            logger.info(f"✓ Flight database initialized at {self.db_path}")

    def get_flight_details(self, callsign: str) -> FlightDetails | None:
        """
        Retrieve enrichment data for a flight by callsign.
        Returns None if not found or expired.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            now = datetime.now(UTC)
            
            cursor.execute("""
                SELECT origin, destination, aircraft_type, delay_minutes
                FROM flights
                WHERE callsign = ? AND (expires_at IS NULL OR expires_at > ?)
                LIMIT 1
            """, (callsign, now.isoformat()))
            
            row = cursor.fetchone()
            if row:
                origin, destination, aircraft_type, delay_minutes = row
                logger.info(f"✓ Flight DB cache hit for {callsign}")
                return FlightDetails(
                    origin=origin,
                    destination=destination,
                    aircraft_type=aircraft_type,
                    delay_minutes=delay_minutes
                )
            
            return None

    def store_flight_details(
        self,
        callsign: str,
        origin: str | None = None,
        destination: str | None = None,
        aircraft_type: str | None = None,
        delay_minutes: int | None = None,
        expires_in_hours: int = 24
    ) -> None:
        """Store flight enrichment data in the database."""
        expires_at = (datetime.now(UTC) + timedelta(hours=expires_in_hours)).isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Try to update existing record, or insert if doesn't exist
            cursor.execute("""
                INSERT OR REPLACE INTO flights
                (callsign, origin, destination, aircraft_type, delay_minutes, expires_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (callsign, origin, destination, aircraft_type, delay_minutes, expires_at))
            
            conn.commit()
            logger.info(f"✓ Stored flight data for {callsign}: {origin} -> {destination}")

    def add_airline_prefix(self, prefix: str, airline_name: str) -> None:
        """Store a callsign prefix to airline mapping for reference."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR IGNORE INTO airline_cache (callsign_prefix, airline_name)
                VALUES (?, ?)
            """, (prefix.upper(), airline_name))
            
            conn.commit()

    def get_airline_by_prefix(self, prefix: str) -> str | None:
        """Retrieve airline name by callsign prefix."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT airline_name FROM airline_cache
                WHERE callsign_prefix = ?
                LIMIT 1
            """, (prefix.upper(),))
            
            row = cursor.fetchone()
            return row[0] if row else None

    def add_known_route(
        self,
        origin: str,
        destination: str,
        aircraft_type: str | None = None
    ) -> None:
        """
        Store a known route for reference and statistics.
        Useful for learning patterns of flights in your area.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO known_routes (origin_code, destination_code, aircraft_type)
                VALUES (?, ?, ?)
                ON CONFLICT(origin_code, destination_code, aircraft_type)
                DO UPDATE SET
                    frequency = frequency + 1,
                    last_seen = CURRENT_TIMESTAMP
            """, (origin.upper(), destination.upper(), aircraft_type))
            
            conn.commit()

    def get_frequent_routes(self, limit: int = 10) -> list[dict]:
        """Get most frequently seen routes in your area."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT origin_code, destination_code, aircraft_type, frequency
                FROM known_routes
                ORDER BY frequency DESC
                LIMIT ?
            """, (limit,))
            
            return [
                {
                    "origin": row[0],
                    "destination": row[1],
                    "aircraft_type": row[2],
                    "frequency": row[3]
                }
                for row in cursor.fetchall()
            ]

    def get_all_flights(self) -> list[dict]:
        """Get all stored flight records for debugging/analysis."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT callsign, origin, destination, aircraft_type, delay_minutes, last_updated
                FROM flights
                ORDER BY last_updated DESC
                LIMIT 50
            """)
            
            return [
                {
                    "callsign": row[0],
                    "origin": row[1],
                    "destination": row[2],
                    "aircraft_type": row[3],
                    "delay_minutes": row[4],
                    "last_updated": row[5]
                }
                for row in cursor.fetchall()
            ]

    def cleanup_expired(self) -> int:
        """Remove expired flight records. Returns count of deleted records."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            now = datetime.now(UTC).isoformat()
            
            cursor.execute("""
                DELETE FROM flights
                WHERE expires_at IS NOT NULL AND expires_at < ?
            """, (now,))
            
            deleted = cursor.rowcount
            conn.commit()
            
            if deleted > 0:
                logger.info(f"✓ Cleaned up {deleted} expired flight records")
            
            return deleted
