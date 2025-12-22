import json
from datetime import datetime
from collections import defaultdict
import yt_dlp  # pip install yt-dlp

def load_json(filename):
    """Load channels from JSON"""
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data.get('all_channels', [])

def get_stream_url(url):
    """Extract stream URL: yt-dlp for YT, direct otherwise"""
    if 'youtube.com' in url or 'youtu.be' in url:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'format': 'best[height<=720][ext=mp4]/best',  # Prioritize 720p MP4/HLS for IPTV
            'live_from_start': True
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return info.get('url') or url  # HLS/M3U8 or fallback
        except Exception:
            print(f"Failed YT extraction for {url}, using raw")
            return url
    return url  # Direct HLS/M3U8

def create_m3u(channels):
    """Generate M3U from channels with categories"""
    # Header
    m3u_content = '''#EXTM3U x-tvg-url="https://www.tsepg.cf/epg.xml.gz"
# ===============================
#  Your Custom IPTV Playlist
#  News + Custom Channels
#  Auto-Updated via GitHub
# ===============================
'''
    
    # Group by category
    categories = defaultdict(list)
    for channel in channels:
        category = channel.get('group', 'Other')
        stream_url = get_stream_url(channel.get('url', ''))
        if stream_url:  # Skip invalid
            channel_copy = channel.copy()
            channel_copy['url'] = stream_url
            categories[category].append(channel_copy)
    
    # Category order: Prioritize News, then others alphabetically
    category_order = ['News'] + sorted([cat for cat in categories if cat != 'News'])
    
    # Add channels by category
    for category in category_order:
        m3u_content += f'# ========== {category} ==========\n'
        for channel in categories[category]:
            # Build EXTINF
            extinf = "#EXTINF:-1"
            if 'tvg_id' in channel:
                extinf += f' tvg-id="{channel["tvg_id"]}"'
            if 'tvg_name' in channel:
                extinf += f' tvg-name="{channel["tvg_name"]}"'
            if 'logo' in channel:
                extinf += f' tvg-logo="{channel["logo"]}"'
            extinf += f' group-title="{category}"'
            extinf += f',{channel.get("name", "Unknown")}\n'
            m3u_content += extinf
            m3u_content += f'{channel["url"]}\n\n'
        m3u_content += '\n'
    
    # Footer
    m3u_content += '''# =====================================
# Generated: ''' + datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC') + '''
# Edit sl.json to add channels
# =====================================
'''
    return m3u_content

def main():
    channels = load_json('sl.json')
    print(f"Loaded {len(channels)} channels from sl.json")
    
    # Generate M3U
    m3u_content = create_m3u(channels)
    with open('myplaylist.m3u', 'w', encoding='utf-8') as f:
        f.write(m3u_content)
    
    # Update JSON timestamp/count
    with open('sl.json', 'r+') as f:
        data = json.load(f)
        data["StreamFlex_A_updated_at"] = datetime.utcnow().isoformat() + "Z"
        data["StreamFlex_SL_total_channels"] = len([c for c in channels if get_stream_url(c.get('url', ''))])
        f.seek(0)
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.truncate()
    
    print("✓ myplaylist.m3u generated with YT streams extracted!")
    print("✓ sl.json timestamp updated!")

if __name__ == "__main__":
    main()

