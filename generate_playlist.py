import json
import requests
from collections import defaultdict

def load_json(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_stream_url(url, channel_name):
    """
    1. Try Piped API to get HLS (bypasses local IP blocks).
    2. Fallback to raw URL.
    """
    # If not YouTube, return as is
    if 'youtube.com' not in url and 'youtu.be' not in url:
        return url

    print(f"Processing: {channel_name}")
    
    # Extract Video ID
    video_id = None
    if 'v=' in url:
        video_id = url.split('v=')[1].split('&')[0]
    elif 'youtu.be/' in url:
        video_id = url.split('youtu.be/')[1].split('?')[0]
    
    if video_id:
        # Try Piped API (Public instance)
        try:
            print(f"  -> Querying Piped API for ID: {video_id}")
            api_url = f"https://pipedapi.kavin.rocks/streams/{video_id}"
            response = requests.get(api_url, timeout=10)
            data = response.json()
            
            # Find HLS stream
            hls_url = data.get('hls')
            if hls_url:
                print(f"  -> Success (Piped): {hls_url[:60]}...")
                return hls_url
        except Exception as e:
            print(f"  -> Piped API failed: {e}")

    # FALLBACK: Return raw URL
    print(f"  -> Fallback: Using raw YouTube URL")
    return url

def create_m3u(data):
    channels = data.get('all_channels', [])
    m3u_content = '#EXTM3U x-tvg-url="https://www.tsepg.cf/epg.xml.gz"\n'
    m3u_content += '# Auto-generated playlist (Piped API method)\n\n'
    
    categories = defaultdict(list)
    
    for channel in channels:
        final_url = get_stream_url(channel.get('url'), channel.get('name'))
        categories[channel.get('group', 'Other')].append({
            'name': channel['name'],
            'url': final_url,
            'logo': channel.get('logo', ''),
            'tvg_id': channel.get('tvg_id', ''),
            'group': channel.get('group', 'Other')
        })

    for category, channel_list in categories.items():
        m3u_content += f'# ================= {category} =================\n'
        for ch in channel_list:
            m3u_content += f'#EXTINF:-1 tvg-id="{ch["tvg_id"]}" tvg-logo="{ch["logo"]}" group-title="{ch["group"]}",{ch["name"]}\n'
            m3u_content += f'{ch["url"]}\n\n'

    return m3u_content

def main():
    data = load_json('sl.json')
    m3u = create_m3u(data)
    with open('myplaylist.m3u', 'w', encoding='utf-8') as f:
        f.write(m3u)
    print("Done!")

if __name__ == "__main__":
    main()
