import json
from datetime import datetime
from collections import defaultdict
import yt_dlp  # pip install yt-dlp

def load_json(filename):
    """Load channels from JSON"""
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def get_stream_url(url):
    """Extract live HLS URL: max res for YT, direct otherwise"""
    if 'youtube.com' in url or 'youtu.be' in url:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'format': 'hls-1080p+,hls-1440p+,hls-2160p+/bestvideo[height>=1080][vcodec^=avc1]+bestaudio/best[height>=1080]',  # Max res HLS/1080p+
            'live_from_start': True,
            'match_filter': lambda info: info.get('is_live')  # Live only
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if info.get('is_live') and info.get('url'):
                    print(f"✓ Extracted live HLS for {url}")
                    return info['url']  # Fresh manifest (no expire issues)
            print(f"✗ No live stream at {url} (offline/VOD?)")
            return None
        except Exception as e:
            print(f"✗ YT extraction failed {url}: {e}")
            return None
    return url  # Direct HLS/M3U8

def create_m3u(data):
    """Generate M3U from channels with categories"""
    channels = data.get('all_channels', [])
    # Header
    m3u_content = '''#EXTM3U x-tvg-url="https://www.tsepg.cf/epg.xml.gz"
# ===============================
#  Your Custom IPTV Playlist
#  News + Custom Channels (Auto-Updated)
# ===============================
'''
    
    # Group by category + extract streams
    categories = defaultdict(list)
    valid_channels = 0
    
    for channel in channels:
        category = channel.get('group', 'Other')
        stream_url = get_stream_url(channel.get('url', ''))
        if stream_url:  # Skip invalid/offline
            channel_copy = channel.copy()
            channel_copy['url'] = stream_url
            categories[category].append(channel_copy)
            valid_channels += 1
    
    # Category order: News first
    category_order = ['News'] + sorted([cat for cat in categories if cat != 'News'])
    
    # Add channels by category
    for category in category_order:
        m3u_content += f'# ========== {category} ({len(categories[category])}) ==========\n'
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
    m3u_content += f'''# =====================================
# Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}
# {valid_channels} live channels
# Edit sl.json → Auto-updates every 2hrs
# =====================================
'''
    return m3u_content

def main():
    data = load_json('sl.json')
    channels = data.get('all_channels', [])
    print(f"Loaded {len(channels)} channels from sl.json")
    
    # Generate M3U
    m3u_content = create_m3u(data)
    with open('myplaylist.m3u', 'w', encoding='utf-8') as f:
        f.write(m3u_content)
    
    # Update JSON stats
    valid_count = sum(1 for ch in channels if get_stream_url(ch.get('url', '')))
    data["StreamFlex_A_updated_at"] = datetime.utcnow().isoformat() + "Z"
    data["StreamFlex_SL_total_channels"] = valid_count
    
    with open('sl.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"✓ myplaylist.m3u generated! ({valid_count}/{len(channels)} live)")
    print("✓ sl.json updated with fresh timestamps!")
    print("→ Raw M3U: https://raw.githubusercontent.com/byte10101010/iptv_my/main/myplaylist.m3u")

if __name__ == "__main__":
    main()

