#!/usr/bin/env python3
"""
GPS Coordinate Converter Module
Handles parsing and conversion of GPS coordinates from EXIF data
"""
import re
import math
from typing import Dict, Tuple, Optional, Union, Any


class GPSConverter:
    """Handles GPS coordinate conversion and formatting."""
    
    @staticmethod
    def parse_exif_gps(gps_info: Dict[str, Any]) -> Optional[Tuple[float, float]]:
        """
        Parse GPS coordinates from EXIF GPSInfo dictionary.
        
        Args:
            gps_info: Dictionary containing GPS EXIF data
            
        Returns:
            Tuple of (latitude, longitude) in decimal degrees, or None if invalid
        """
        if not gps_info or not isinstance(gps_info, dict):
            return None
        
        try:
            # Extract latitude
            lat_ref = gps_info.get('GPSLatitudeRef', gps_info.get(1))
            lat_data = gps_info.get('GPSLatitude', gps_info.get(2))
            
            # Extract longitude
            lon_ref = gps_info.get('GPSLongitudeRef', gps_info.get(3))
            lon_data = gps_info.get('GPSLongitude', gps_info.get(4))
            
            if not all([lat_ref, lat_data, lon_ref, lon_data]):
                return None
            
            # Convert to decimal degrees
            latitude = GPSConverter._dms_to_decimal(lat_data, lat_ref)
            longitude = GPSConverter._dms_to_decimal(lon_data, lon_ref)
            
            if latitude is None or longitude is None:
                return None
            
            # Validate coordinates are within valid ranges
            if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
                return None
            
            # Check for null island (0,0) coordinates
            if latitude == 0.0 and longitude == 0.0:
                return None
            
            return (latitude, longitude)
            
        except (KeyError, ValueError, TypeError, IndexError):
            return None
    
    @staticmethod
    def _dms_to_decimal(dms_data: Any, ref: str) -> Optional[float]:
        """
        Convert DMS (Degrees, Minutes, Seconds) to decimal degrees.
        
        Args:
            dms_data: DMS data in various formats
            ref: Reference (N/S for latitude, E/W for longitude)
            
        Returns:
            Decimal degree value or None if invalid
        """
        try:
            # Handle different possible formats
            if isinstance(dms_data, (list, tuple)) and len(dms_data) >= 3:
                degrees = float(dms_data[0])
                minutes = float(dms_data[1])
                seconds = float(dms_data[2])
            elif hasattr(dms_data, '__iter__') and not isinstance(dms_data, (str, bytes)):
                # Handle IFDRational or similar objects
                dms_list = list(dms_data)
                if len(dms_list) >= 3:
                    degrees = float(dms_list[0])
                    minutes = float(dms_list[1])
                    seconds = float(dms_list[2])
                else:
                    return None
            else:
                return None
            
            # Convert to decimal
            decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)
            
            # Apply reference direction
            if isinstance(ref, str) and ref.upper() in ['S', 'W']:
                decimal = -decimal
            
            return decimal
            
        except (ValueError, TypeError, AttributeError):
            return None
    
    @staticmethod
    def to_decimal_degrees(latitude: float, longitude: float) -> str:
        """
        Format coordinates as decimal degrees string.
        
        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            
        Returns:
            Formatted string like "40.7128, -74.0060"
        """
        return f"{latitude:.6f}, {longitude:.6f}"
    
    @staticmethod
    def to_dms(latitude: float, longitude: float) -> str:
        """
        Convert decimal degrees to DMS format.
        
        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            
        Returns:
            Formatted DMS string
        """
        def decimal_to_dms(decimal_deg: float, is_latitude: bool) -> str:
            abs_deg = abs(decimal_deg)
            degrees = int(abs_deg)
            minutes_float = (abs_deg - degrees) * 60
            minutes = int(minutes_float)
            seconds = (minutes_float - minutes) * 60
            
            if is_latitude:
                ref = 'N' if decimal_deg >= 0 else 'S'
            else:
                ref = 'E' if decimal_deg >= 0 else 'W'
            
            return f"{degrees}°{minutes}'{seconds:.2f}\"{ref}"
        
        lat_dms = decimal_to_dms(latitude, True)
        lon_dms = decimal_to_dms(longitude, False)
        
        return f"{lat_dms}, {lon_dms}"
    
    @staticmethod
    def to_dmm(latitude: float, longitude: float) -> str:
        """
        Convert decimal degrees to DMM (Degrees and Decimal Minutes) format.
        
        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            
        Returns:
            Formatted DMM string
        """
        def decimal_to_dmm(decimal_deg: float, is_latitude: bool) -> str:
            abs_deg = abs(decimal_deg)
            degrees = int(abs_deg)
            minutes = (abs_deg - degrees) * 60
            
            if is_latitude:
                ref = 'N' if decimal_deg >= 0 else 'S'
            else:
                ref = 'E' if decimal_deg >= 0 else 'W'
            
            return f"{degrees}°{minutes:.4f}'{ref}"
        
        lat_dmm = decimal_to_dmm(latitude, True)
        lon_dmm = decimal_to_dmm(longitude, False)
        
        return f"{lat_dmm}, {lon_dmm}"
    
    @staticmethod
    def to_utm(latitude: float, longitude: float) -> str:
        """
        Convert decimal degrees to UTM coordinates (simplified).
        
        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            
        Returns:
            Formatted UTM string
        """
        # Simplified UTM conversion - for production use, consider using pyproj
        zone = int((longitude + 180) / 6) + 1
        
        # Determine hemisphere
        hemisphere = 'N' if latitude >= 0 else 'S'
        
        # This is a simplified representation - actual UTM conversion is more complex
        return f"Zone {zone}{hemisphere} (Approximate conversion - use specialized library for precise UTM)"
    
    @staticmethod
    def to_mgrs(latitude: float, longitude: float) -> str:
        """
        Convert decimal degrees to MGRS (placeholder implementation).
        
        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            
        Returns:
            MGRS string (placeholder)
        """
        # MGRS conversion is complex and typically requires specialized libraries
        return f"MGRS conversion requires specialized library (lat: {latitude:.6f}, lon: {longitude:.6f})"
    
    @staticmethod
    def to_geohash(latitude: float, longitude: float, precision: int = 12) -> str:
        """
        Convert decimal degrees to geohash.
        
        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            precision: Geohash precision (default 12)
            
        Returns:
            Geohash string
        """
        # Simplified geohash implementation
        lat_range = [-90.0, 90.0]
        lon_range = [-180.0, 180.0]
        
        geohash = ""
        bits = 0
        bit = 0
        ch = 0
        even = True
        
        base32 = "0123456789bcdefghjkmnpqrstuvwxyz"
        
        while len(geohash) < precision:
            if even:  # longitude
                mid = (lon_range[0] + lon_range[1]) / 2
                if longitude >= mid:
                    ch |= (1 << (4 - bit))
                    lon_range[0] = mid
                else:
                    lon_range[1] = mid
            else:  # latitude
                mid = (lat_range[0] + lat_range[1]) / 2
                if latitude >= mid:
                    ch |= (1 << (4 - bit))
                    lat_range[0] = mid
                else:
                    lat_range[1] = mid
            
            even = not even
            if bit < 4:
                bit += 1
            else:
                geohash += base32[ch]
                bit = 0
                ch = 0
        
        return geohash
    
    @staticmethod
    def to_plus_code(latitude: float, longitude: float) -> str:
        """
        Convert decimal degrees to Plus Code (placeholder implementation).
        
        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            
        Returns:
            Plus Code string (placeholder)
        """
        # Plus Code conversion is complex and typically requires specialized libraries
        return f"Plus Code conversion requires specialized library (lat: {latitude:.6f}, lon: {longitude:.6f})"
    
    @staticmethod
    def create_google_maps_url(latitude: float, longitude: float) -> str:
        """
        Create a Google Maps URL for the given coordinates.
        
        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            
        Returns:
            Google Maps URL string
        """
        return f"https://maps.google.com/maps?q={latitude:.6f},{longitude:.6f}"
    
    @staticmethod
    def get_all_formats(latitude: float, longitude: float) -> Dict[str, str]:
        """
        Get coordinates in all supported formats.
        
        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            
        Returns:
            Dictionary with all coordinate formats
        """
        return {
            'decimal_degrees': GPSConverter.to_decimal_degrees(latitude, longitude),
            'dms': GPSConverter.to_dms(latitude, longitude),
            'dmm': GPSConverter.to_dmm(latitude, longitude),
            'utm': GPSConverter.to_utm(latitude, longitude),
            'mgrs': GPSConverter.to_mgrs(latitude, longitude),
            'geohash': GPSConverter.to_geohash(latitude, longitude),
            'plus_code': GPSConverter.to_plus_code(latitude, longitude),
            'google_maps_url': GPSConverter.create_google_maps_url(latitude, longitude)
        }