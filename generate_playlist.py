import json
from datetime import datetime
from collections import defaultdict
import yt_dlp

def load_json(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def get_stream_url(url, channel_name):
    """
    Robust extraction:
    1. Try grabbing HLS manifest (best quality).
    2. If fails/None, return None (to filter it out) or raw URL if desired.
    """
    if 'youtube.com' in url or 'youtu.be' in url:
        print(f"Processing: {channel_name} ({url})")
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'format': 'best', # Simply get best available (HLS or other)
            'live_from_start': True,
            'skip_download': True,
            # 'match_filter': lambda info: info.get('is_live') # REMOVED strict filter
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                # Check for HLS URL specifically first
                hls_url = info.get('url') # yt-dlp puts HLS manifest link here for lives
                
                if not hls_url:
                     # Fallback to 'formats' search if main 'url' is empty
                     for f in info.get('formats', []):
                         if f.get('protocol') == 'm3u8_native':
                             hls_url = f.get('url')
                             break
                
                if hls_url:
                    print(f"  -> Success: {hls_url[:60]}...")
                    return hls_url
                else:
                    print(f"  -> WARNING: No URL found in info dict for {channel_name}")
                    return None
                    
        except Exception as e:
            print(f"  -> ERROR for {channel_name}: {e}")
            return None
    
    return url # Return non-YT URLs as-is

def create_m3u(data):
    channels = data.get('all_channels', [])
    # Header
    m3u_content = '#EXTM3U x-tvg-url="https://www.tsepg.cf/epg.xml.gz"\n'
    m3u_content += '# Auto-generated playlist\n\n'
    
    categories = defaultdict(list)
    valid_count = 0
    
    for channel in channels:
        stream_url = get_stream_url(channel.get('url'), channel.get('name'))
        
        if stream_url:
            valid_count += 1
            # Add to category list
            categories[channel.get('group', 'Other')].append({
                'name': channel['name'],
                'url': stream_url,
                'logo': channel.get('logo', ''),
                'tvg_id': channel.get('tvg_id', ''),
                'group': channel.get('group', 'Other')
            })
        else:
            print(f"Skipping {channel['name']} - No valid stream found.")

    # Write M3U
    for category, channel_list in categories.items():
        m3u_content += f'# ================= {category} =================\n'
        for ch in channel_list:
            m3u_content += f'#EXTINF:-1 tvg-id="{ch["tvg_id"]}" tvg-logo="{ch["logo"]}" group-title="{ch["group"]}",{ch["name"]}\n'
            m3u_content += f'{ch["url"]}\n\n'

    return m3u_content, valid_count

def main():
    data = load_json('sl.json')
    m3u_content, count = create_m3u(data)
    
    with open('myplaylist.m3u', 'w', encoding='utf-8') as f:
        f.write(m3u_content)
        
    print(f"\nDone. Generated M3U with {count} channels.")

if __name__ == "__main__":
    main()

