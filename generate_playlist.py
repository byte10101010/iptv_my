import json
import yt_dlp
import os
import time

# --- Configuration ---
SOURCE_FILE = 'sl.json'
OUTPUT_FILE = 'myplaylist.m3u'

def get_real_stream_url(url):
    """Extracts m3u8 link from YouTube URL using yt-dlp"""
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
                
                # Check if it's a live stream (both /live and /watch?v= can be live)
                if info.get('is_live') or info.get('was_live') or 'manifest.googlevideo.com' in str(info.get('url')):
                    return info.get('url')
                
                # Fallback for standard videos
                return info.get('url')

        except Exception as e:
            print(f"   [Error] {e}")
            return None 
    
    return url 

def generate():
    # Check if JSON exists
    if not os.path.exists(SOURCE_FILE):
        print(f"Error: {SOURCE_FILE} not found in {os.getcwd()}")
        return

    print("Reading sl.json...")
    with open(SOURCE_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    channels = data.get('all_channels', [])
    print(f"Found {len(channels)} channels. Extracting links (this may take a moment)...")

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write('#EXTM3U\n') 

        for channel in channels:
            name = channel.get('name', 'Unknown')
            original_url = channel.get('url', '')
            logo = channel.get('logo', '')
            group = channel.get('group', 'Uncategorized')
            tvg_id = channel.get('tvg_id', '')
            tvg_name = channel.get('tvg_name', '')

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
                f.write(f'#EXTINF:-1 tvg-id="{tvg_id}" tvg-name="{tvg_name}" tvg-logo="{logo}" group-title="{group}",{name}\n')
                f.write(f'{stream_url}\n')

    print(f"\nDone! Playlist saved to: {os.path.abspath(OUTPUT_FILE)}")

if __name__ == "__main__":
    generate()
    # Optional: Keep window open for 5 seconds so you can see the result
    time.sleep(5)
