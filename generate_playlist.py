import pandas as pd
import yt_dlp
import os
import time

# --- Configuration ---
SOURCE_FILE = 'channels.xlsx'  # Changed from .json to .xlsx
OUTPUT_FILE = 'myplaylist.m3u'

def get_real_stream_url(url):
    """Extracts m3u8 link from YouTube URL using yt-dlp"""
    if not url: return ""
    
    if "youtube.com" in url or "youtu.be" in url:
        # Options optimized for local network speed and reliability
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'format': 'best',
            'noplaylist': True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                # Check if it's a live stream
                if info.get('is_live') or info.get('was_live') or 'manifest.googlevideo.com' in str(info.get('url')):
                    return info.get('url')
                
                # Fallback for standard videos
                return info.get('url')

        except Exception as e:
            print(f"   [Error extracting {url}]: {e}")
            return None 
    
    return url 

def generate():
    # Check if Excel file exists
    if not os.path.exists(SOURCE_FILE):
        print(f"Error: {SOURCE_FILE} not found in {os.getcwd()}")
        print("Please create an Excel file with columns: name, tvg_id, tvg_name, logo, group, url")
        return

    print(f"Reading {SOURCE_FILE}...")
    
    try:
        # Read Excel file
        df = pd.read_excel(SOURCE_FILE)
        
        # Fill empty cells with empty strings so we don't get 'nan' in the playlist
        df = df.fillna('')
        
        # Convert the DataFrame to a list of dictionaries (Matches your old JSON structure)
        channels = df.to_dict('records')
        
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return

    print(f"Found {len(channels)} channels. Extracting links (this may take a moment)...")

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write('#EXTM3U\n') 

        for channel in channels:
            # Get data from dictionary (keys match Excel headers)
            name = str(channel.get('name', '')).strip()
            original_url = str(channel.get('url', '')).strip()
            logo = str(channel.get('logo', '')).strip()
            group = str(channel.get('group', 'Uncategorized')).strip()
            tvg_id = str(channel.get('tvg_id', '')).strip()
            tvg_name = str(channel.get('tvg_name', '')).strip()

            # Skip rows with no name and no URL
            if not name and not original_url:
                continue

            if original_url:
                print(f" -> Processing: {name}")
                
                stream_url = get_real_stream_url(original_url)

                if not stream_url:
                    print(f"    [Failed] Could not get live link. Keeping original.")
                    stream_url = original_url
                else:
                    # Truncate long URL for cleaner terminal output
                    display_url = (stream_url[:50] + '...') if len(stream_url) > 50 else stream_url
                    print(f"    [Success] Link generated.")

                # Write to M3U
                # Using f-string formatting to ensure clean output
                f.write(f'#EXTINF:-1 tvg-id="{tvg_id}" tvg-name="{tvg_name}" tvg-logo="{logo}" group-title="{group}",{name}\n')
                f.write(f'{stream_url}\n')

    print(f"\nDone! Playlist saved to: {os.path.abspath(OUTPUT_FILE)}")

if __name__ == "__main__":
    generate()
    time.sleep(5)
