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
        try:
            return url.split('live/')[1].split('?')[0]
        except IndexError:
            return None
    return None

def get_hls_link(video_id):
    # List of public Piped instances (APIs)
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
    if 'youtube.com' not in url and 'youtu.be' not in url:
        return url

    print(f"Processing: {channel_name}")
    video_id = get_video_id(url)
    
    if not video_id:
        print("  -> Could not extract video ID")
        return url

    hls_url = get_hls_link(video_id)
    
    if hls_url:
        print(f"  -> Success: {hls_url[:40]}...")
        return hls_url
    else:
        print("  -> Failed to get HLS from public APIs")
        return url

def create_m3u(data):
    channels = data.get('all_channels', [])
    m3u = '#EXTM3U x-tvg-url="https://www.tsepg.cf/epg.xml.gz"\n'
    
    # Corrected dictionary initialization
    categories = {}
    
    for c in channels:
        cat = c.get('group', 'Other')
        if cat not in categories: 
            categories[cat] = []
        
        final_url = get_stream_url(c['url'], c['name'])
        categories[cat].append({**c, 'url': final_url})

    for cat in categories:
        m3u += f'# ================= {cat} =================\n'
        for c in categories[cat]:
            m3u += f'#EXTINF:-1 tvg-id="{c.get("tvg_id","")}" tvg-logo="{c.get("logo","")}" group-title="{cat}",{c["name"]}\n'
            m3u += f'{c["url"]}\n\n'
            
    return m3u

if __name__ == "__main__":
    m3u = create_m3u(load_json('sl.json'))
    with open('myplaylist.m3u', 'w', encoding='utf-8') as f:
        f.write(m3u)
    print("Done.")
