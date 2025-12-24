import json
import yt_dlp

# Configuration: Updated filenames
SOURCE_FILE = 'sl.json'
OUTPUT_FILE = 'myplaylist.m3u'

def get_real_stream_url(url):
    """
    If the URL is a YouTube link, extract the .m3u8 stream.
    Otherwise, return the URL as is.
    """
    if "youtube.com" in url or "youtu.be" in url:
        ydl_opts = {
            'quiet': True,
            'format': 'best',
            'noplaylist': True,
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return info.get('url', url)
        except Exception as e:
            print(f"Failed to extract YouTube stream for {url}: {e}")
            return None 
    
    return url 

def json_to_m3u():
    try:
        # 1. Read the JSON source
        with open(SOURCE_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 2. Open M3U for writing
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
                    stream_url = get_real_stream_url(original_url)

                    if stream_url:
                        f.write(f'#EXTINF:-1 tvg-id="{tvg_id}" tvg-name="{tvg_name}" tvg-logo="{logo}" group-title="{group}",{name}\n')
                        f.write(f'{stream_url}\n')

        print(f"Success: Updated playlist saved to {OUTPUT_FILE}")

    except Exception as e:
        print(f"Critical Error: {e}")
        exit(1)

if __name__ == "__main__":
    json_to_m3u()
