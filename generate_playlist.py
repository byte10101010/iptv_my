import json
import requests
import time

def load_json(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_video_id(url):
    if 'v=' in url:
        return url.split('v=')[1].split('&')[0]
    elif 'youtu.be/' in url:
        return url.split('youtu.be/')[1].split('?')[0]
    elif 'live/' in url:
        return url.split('live/')[1].split('?')[0]
    return None

def get_hls_link(video_id):
    # List of public Piped instances (APIs)
    # These act as proxies to get the .m3u8 link for you
    instances = [
        "https://pipedapi.kavin.rocks",
        "https://api.piped.privacy.com.de",
        "https://pipedapi.drgns.space",
        "https://api.piped.projectsegfau.lt",
        "https://pipedapi.moomoo.me"
    ]
    
    for instance in instances:
        try:
            print(f"    Trying {instance}...")
            # Piped API to get stream info
            resp = requests.get(f"{instance}/streams/{video_id}", timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                hls = data.get('hls')
                if hls:
                    return hls
        except Exception:
            continue
    return None

def get_stream_url(url, channel_name):
    # If not YouTube, return as-is (e.g., your SET HD link)
    if 'youtube.com' not in url and 'youtu.be' not in url:
        return url

    print(f"Processing: {channel_name}")
    video_id = get_video_id(url)
    
    if not video_id:
        # If it's a channel URL like @Tv9Telugu/live, we can't easily get ID without yt-dlp.
        # But for your specific case (II_m28Bm-iM), we have the ID.
        print("  -> Could not extract video ID from URL")
        return url

    hls_url = get_hls_link(video_id)
    
    if hls_url:
        print(f"  -> Success: {hls_url[:40]}...")
        return hls_url
    else:
        print("  -> Failed to get HLS from public APIs")
        return url # Fallback (might not work in player, but better than nothing)

def create_m3u(data):
    channels = data.get('all_channels', [])
    m3u = '#EXTM3U x-tvg-url="https://www.tsepg.cf/epg.xml.gz"\n'
    
    categories = {}
    for c in channels:
        cat = c.get('group', 'Other')
        if cat not in cats: cats[cat] = []
        
        final_url = get_stream_url(c['url'], c['name'])
        cats[cat].append({**c, 'url': final_url})

    for cat in cats:
        m3u += f'# ================= {cat} =================\n'
        for c in cats[cat]:
            m3u += f'#EXTINF:-1 tvg-id="{c.get("tvg_id","")}" tvg-logo="{c.get("logo","")}" group-title="{cat}",{c["name"]}\n'
            m3u += f'{c["url"]}\n\n'
            
    return m3u

if __name__ == "__main__":
    m3u = create_m3u(load_json('sl.json'))
    with open('myplaylist.m3u', 'w', encoding='utf-8') as f:
        f.write(m3u)
    print("Done.")
