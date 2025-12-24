import json
from datetime import datetime
from collections import defaultdict
import yt_dlp  # pip install yt-dlp

def load_json(filename):
    """Load channels from JSON"""
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def get_hlsmanifest_url(url):
    """Extract HLS manifest - handles both live & replays"""
    if 'youtube.com' in url or 'youtu.be' in url:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'format': '(hls-2160p+,hls-1440p+,hls-1080p+,hls-720p+)/best',
            'live_from_start': True
        }
        # REMOVED strict live filter - works with VOD/replays too
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                hls_url = info.get('url') or info.get('hls_url') or url
                if 'manifest.googlevideo.com' in hls_url or 'googlevideo.com' in hls_url:
                    print(f"✓ HLS Manifest: {url}")
                    return hls_url
                print(f"✓ Stream URL: {hls_url[:100]}...")
                return hls_url  # Any playable stream
        except Exception as e:
            print(f"✗ Failed {url}: {e}")
            return None
    return url


def create_m3u(data):
    """Generate M3U with HLS manifests"""
    channels = data.get('all_channels', [])
    m3u_content = '''#EXTM3U x-tvg-url="https://www.tsepg.cf/epg.xml.gz"
# ===============================
#  IPTV HLS Manifest Playlist
#  Auto-Updated Every 2 Hours
# ===============================
'''
    
    categories = defaultdict(list)
    valid_channels = 0
    
    for channel in channels:
        category = channel.get('group', 'Other')
        hls_url = get_hlsmanifest_url(channel.get('url', ''))
        if hls_url:
            channel_copy = channel.copy()
            channel_copy['url'] = hls_url  # HLS manifest URL
            categories[category].append(channel_copy)
            valid_channels += 1
    
    # Category order
    category_order = ['News'] + sorted([cat for cat in categories if cat != 'News'])
    
    for category in category_order:
        m3u_content += f'# ========== {category} ({len(categories[category])}) ==========\n'
        for channel in categories[category]:
            extinf = "#EXTINF:-1"
            if 'tvg_id' in channel: extinf += f' tvg-id="{channel["tvg_id"]}"'
            if 'tvg_name' in channel: extinf += f' tvg-name="{channel["tvg_name"]}"'
            if 'logo' in channel: extinf += f' tvg-logo="{channel["logo"]}"'
            extinf += f' group-title="{category}"'
            extinf += f',{channel.get("name", "Unknown")}\n'
            m3u_content += extinf + channel["url"] + '\n\n'
        m3u_content += '\n'
    
    m3u_content += f'''# =====================================
# Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}
# {valid_channels} HLS Manifests
# Raw: https://raw.githubusercontent.com/byte10101010/iptv_my/main/myplaylist.m3u
# =====================================
'''
    return m3u_content

def main():
    data = load_json('sl.json')
    channels = data.get('all_channels', [])
    print(f"Loaded {len(channels)} channels")
    
    m3u_content = create_m3u(data)
    with open('myplaylist.m3u', 'w', encoding='utf-8') as f:
        f.write(m3u_content)
    
    # Update stats
    valid_count = sum(1 for ch in channels if get_hlsmanifest_url(ch.get('url', '')))
    data["StreamFlex_A_updated_at"] = datetime.utcnow().isoformat() + "Z"
    data["StreamFlex_SL_total_channels"] = valid_count
    
    with open('sl.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Generated {valid_count}/{len(channels)} HLS manifests!")
    print("→ https://raw.githubusercontent.com/byte10101010/iptv_my/main/myplaylist.m3u")

if __name__ == "__main__":
    main()

