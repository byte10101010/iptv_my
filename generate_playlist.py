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
    return None

def get_hls_from_apis(video_id):
    # List of public Piped/Invidious APIs
    apis = [
        f"https://pipedapi.kavin.rocks/streams/{video_id}",
        f"https://api.piped.privacy.com.de/streams/{video_id}",
        f"https://pipedapi.drgns.space/streams/{video_id}",
        f"https://inv.tux.pizza/api/v1/videos/{video_id}",
    ]
    
    for api in apis:
        try:
            print(f"    ...trying {api}")
            resp = requests.get(api, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                
                # Check Piped format
                if 'hls' in data and data['hls']:
                    return data['hls']
                
                # Check Invidious format
                if 'formatStreams' in data:
                    for fmt in data['formatStreams']:
                        if fmt.get('container') == 'm3u8':
                            return fmt['url']
        except:
            continue
    return None

def get_stream_url(url, channel_name):
    if 'youtube.com' not in url and 'youtu.be' not in url:
        return url

    print(f"Processing: {channel_name}")
    vid = get_video_id(url)
    if vid:
        hls = get_hls_from_apis(vid)
        if hls:
            print(f"  -> Success: {hls[:40]}...")
            return hls
            
    print(f"  -> Fallback to raw URL")
    return url

def create_m3u(data):
    channels = data.get('all_channels', [])
    m3u = '#EXTM3U x-tvg-url="https://www.tsepg.cf/epg.xml.gz"\n'
    
    # Group by category
    cats = {}
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
