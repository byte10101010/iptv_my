import json
import requests
import os
import sys

# Force unbuffered output for GitHub logs
sys.stdout.reconfigure(encoding='utf-8')

def load_json(filename):
    if not os.path.exists(filename):
        print(f"ERROR: {filename} not found in {os.getcwd()}")
        return {'all_channels': []}
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_hls_link(video_id):
    instances = [
        "https://pipedapi.kavin.rocks",
        "https://api.piped.privacy.com.de",
        "https://pipedapi.drgns.space",
        "https://api.piped.projectsegfau.lt"
    ]
    for instance in instances:
        try:
            print(f"    Trying {instance}...")
            resp = requests.get(f"{instance}/streams/{video_id}", timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                if 'hls' in data and data['hls']:
                    return data['hls']
        except Exception:
            continue
    return None

def get_stream_url(url, channel_name):
    if 'youtube.com' not in url and 'youtu.be' not in url:
        return url
        
    print(f"Processing: {channel_name}")
    # Extract ID
    vid = None
    if 'v=' in url: vid = url.split('v=')[1].split('&')[0]
    elif 'youtu.be/' in url: vid = url.split('youtu.be/')[1].split('?')[0]
    
    if vid:
        hls = get_hls_link(vid)
        if hls:
            print(f"  -> Success: {hls[:40]}...")
            return hls
            
    print(f"  -> Fallback to raw URL")
    return url

def create_m3u(data):
    channels = data.get('all_channels', [])
    # Header
    content = '#EXTM3U x-tvg-url="https://www.tsepg.cf/epg.xml.gz"\n'
    
    categories = {}
    for c in channels:
        cat = c.get('group', 'Other')
        if cat not in categories: categories[cat] = []
        
        final_url = get_stream_url(c['url'], c['name'])
        categories[cat].append({**c, 'url': final_url})

    for cat in categories:
        content += f'# ================= {cat} =================\n'
        for c in categories[cat]:
            content += f'#EXTINF:-1 tvg-id="{c.get("tvg_id","")}" tvg-logo="{c.get("logo","")}" group-title="{cat}",{c["name"]}\n'
            content += f'{c["url"]}\n\n'
            
    return content

if __name__ == "__main__":
    print(f"Current Directory: {os.getcwd()}")
    data = load_json('sl.json')
    m3u_content = create_m3u(data)
    
    # Print content size to verify
    print(f"Generated Content Size: {len(m3u_content)} bytes")
    
    output_file = 'myplaylist.m3u'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(m3u_content)
        f.flush()
        os.fsync(f.fileno())
        
    if os.path.exists(output_file):
        print(f"SUCCESS: {output_file} written ({os.path.getsize(output_file)} bytes).")
    else:
        print(f"FAILURE: {output_file} was NOT written.")
