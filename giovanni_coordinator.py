# GIOVANNI FILE COORDINATOR v1.0
# "Nothing Vital Lives Below Root"
# Project: Giuseppe Skyrider / Giovanni Core

import os
import shutil
import time
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from PIL import Image, ExifTags

class GiovanniCortex(FileSystemEventHandler):
    def __init__(self, watch_dir, vault_dir):
        self.watch_dir = watch_dir
        self.vault_dir = vault_dir
        
        # Define where Giovanni routes the assets
        self.photo_dir = os.path.join(self.vault_dir, "Photos")
        self.doc_dir = os.path.join(self.vault_dir, "Documents")
        self.media_dir = os.path.join(self.vault_dir, "Media_Assets")
        
        # Ensure Giovanni's vault exists
        for d in [self.photo_dir, self.doc_dir, self.media_dir]:
            os.makedirs(d, exist_ok=True)

    def on_created(self, event):
        if event.is_directory:
            return
            
        file_path = event.src_path
        filename = os.path.basename(file_path)
        ext = filename.lower().split('.')[-1]
        
        # 1-second delay to ensure Mac/iCloud has finished writing the file
        time.sleep(1) 
        
        if ext in ['jpg', 'jpeg', 'png', 'heic', 'raw']:
            self.process_photo(file_path, filename)
        elif ext in ['pdf', 'doc', 'docx', 'txt', 'md']:
            self.process_document(file_path, filename)
        elif ext in ['mp4', 'mov', 'mp3', 'wav']:
            self.process_media(file_path, filename)

    def process_photo(self, file_path, filename):
        try:
            # The 'Brain': Read EXIF data for the true Carbon timeline
            img = Image.open(file_path)
            exif = img._getexif()
            creation_date = None
            
            if exif:
                for tag_id, val in exif.items():
                    tag = ExifTags.TAGS.get(tag_id, tag_id)
                    if tag == 'DateTimeOriginal':
                        creation_date = val
                        break
            
            if creation_date:
                # Format: "YYYY:MM:DD HH:MM:SS" -> Route to "YYYY/MM"
                dt = datetime.strptime(creation_date, '%Y:%m:%d %H:%M:%S')
                folder_path = os.path.join(self.photo_dir, str(dt.year), f"{dt.month:02d}")
            else:
                folder_path = os.path.join(self.photo_dir, "Unsorted_Syncs")
                
            os.makedirs(folder_path, exist_ok=True)
            
            # The 'Hands': Move the file
            dest_path = os.path.join(folder_path, filename)
            shutil.move(file_path, dest_path)
            print(f"[GIOVANNI CORTEX] Photo Coordinated: {filename} -> {folder_path}")
            
        except Exception as e:
            print(f"[GIOVANNI ERROR] EXIF scan failed on {filename}: {e}")

    def process_document(self, file_path, filename):
        dest_path = os.path.join(self.doc_dir, filename)
        shutil.move(file_path, dest_path)
        print(f"[GIOVANNI CORTEX] Document Filed: {filename}")

    def process_media(self, file_path, filename):
        dest_path = os.path.join(self.media_dir, filename)
        shutil.move(file_path, dest_path)
        print(f"[GIOVANNI CORTEX] Media Asset Secured: {filename}")

def wake_giovanni_eyes(watch_directory, vault_directory):
    print(f"[GIOVANNI SYSTEM] Activating visual monitoring on {watch_directory}...")
    event_handler = GiovanniCortex(watch_directory, vault_directory)
    observer = Observer()
    observer.schedule(event_handler, watch_directory, recursive=False)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("[GIOVANNI SYSTEM] Monitoring suspended.")
    observer.join()

if __name__ == "__main__":
    # Example wiring: Point this at your Mac's Downloads or an iCloud drop folder
    WATCH_FOLDER = os.path.expanduser("~/Downloads")
    GIOVANNI_VAULT = os.path.expanduser("~/Giovanni_Organized")
    
    wake_giovanni_eyes(WATCH_FOLDER, GIOVANNI_VAULT)
