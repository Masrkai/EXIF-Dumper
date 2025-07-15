#!/usr/bin/env python3
"""
EXIF Processor for single image operations
"""
import shutil
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import piexif

class EXIFProcessor:
    """Handles EXIF data extraction, editing, and deletion for a single image."""

    def __init__(self, image_path: str):
        self.image_path = image_path

    def extract(self) -> dict:
        """Extracts EXIF data from the image."""
        try:
            image = Image.open(self.image_path)
            exif_data = {}
            if hasattr(image, '_getexif') and image._getexif():
                exif = image._getexif()
                for tag_id, value in exif.items():
                    tag = TAGS.get(tag_id, tag_id)
                    if tag == 'GPSInfo':
                        gps_data = {}
                        for gps_tag_id, gps_value in value.items():
                            gps_tag = GPSTAGS.get(gps_tag_id, gps_tag_id)
                            gps_data[gps_tag] = gps_value
                        exif_data[tag] = gps_data
                    else:
                        exif_data[tag] = value
            return exif_data
        except Exception as e:
            raise Exception(f"Failed to extract EXIF data: {e}")

    def edit(self, exif_data: dict, preserve_original: bool):
        """Edits the EXIF data in the image."""
        try:
            if preserve_original:
                backup_path = self.image_path + ".backup"
                shutil.copy2(self.image_path, backup_path)
            
            exif_dict = piexif.load(self.image_path)
            for key, value in exif_data.items():
                if key in exif_dict:
                    exif_dict[key].update(value)
                else:
                    exif_dict[key] = value
            
            exif_bytes = piexif.dump(exif_dict)
            piexif.insert(exif_bytes, self.image_path)
            return {"status": "success", "message": "EXIF data updated successfully"}
        except Exception as e:
            raise Exception(f"Failed to edit EXIF data: {e}")

    def delete(self, preserve_original: bool):
        """Deletes all EXIF data from the image."""
        try:
            if preserve_original:
                backup_path = self.image_path + ".backup"
                shutil.copy2(self.image_path, backup_path)
            
            piexif.remove(self.image_path)
            return {"status": "success", "message": "EXIF data deleted successfully"}
        except Exception as e:
            raise Exception(f"Failed to delete EXIF data: {e}")