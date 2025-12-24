import json
import yt_dlp

# Configuration
SOURCE_FILE = 'sl.json'
OUTPUT_FILE = 'myplaylist.m3u'

def get_real_stream_url(url):
    if "youtube.com" in url or "youtu.be" in url:
        ydl_opts = {
            'quiet': True,
            'format': 'best',
            'noplaylist': True,
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)

                # FIX: Handle case where URL is treated as a playlist (common for /live links)
                if 'entries' in info:
                    video_info = info['entries'][0]
                    return video_info.get('url')
                
                # Standard case
                return info.get('url')
                
        except Exception as e:
            print(f"Error extracting {url}: {e}")
            return None 
    
    return url 

def json_to_m3u():
    with open(SOURCE_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write('#EXTM3U\n') 

        channels = data.get('all_channels', [])
        
        for channel in channels:
            name = channel.get('name', 'Unknown')
            original_url = channel.get('url', '')
            logo = channel.get('logo', '')
            group = channel.get('group', 'Uncategorized')
            tvg_id = channel.get('tvg_id', '')
            tvg_name = channel.get('tvg_name', '')

            if original_url:
                print(f"Processing: {name}...")
                
                # Attempt to get the HLS link
                stream_url = get_real_stream_url(original_url)

                # Fallback: If extraction failed, use original URL so the channel isn't lost
                if not stream_url:
                    print(f"  Warning: Could not extract HLS for {name}, using original link.")
                    stream_url = original_url

                # Write the entry
                f.write(f'#EXTINF:-1 tvg-id="{tvg_id}" tvg-name="{tvg_name}" tvg-logo="{logo}" group-title="{group}",{name}\n')
                f.write(f'{stream_url}\n')

    print(f"Success: Updated playlist saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    json_to_m3u()
