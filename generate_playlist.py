import json
import yt_dlp
from collections import defaultdict

def load_json(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_stream_url(url, channel_name):
    """
    Try to get HLS. If fail, return the original URL so it at least appears in the playlist.
    """
    # If not YouTube, return as is
    if 'youtube.com' not in url and 'youtu.be' not in url:
        return url

    print(f"Extracting: {channel_name} ({url})")
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'format': 'best',
        'live_from_start': True
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            hls_url = info.get('url')
            if hls_url:
                print(f"  -> Found HLS: {hls_url[:50]}...")
                return hls_url
    except Exception as e:
        print(f"  -> Extraction failed: {e}")
    
    # FALLBACK: Return the original YouTube URL instead of None
    # This ensures the channel is listed in M3U. 
    # Some players (TiviMate, VLC) can play raw YT links.
    print(f"  -> Fallback: Using raw YouTube URL")
    return url

def create_m3u(data):
    channels = data.get('all_channels', [])
    m3u_content = '#EXTM3U x-tvg-url="https://www.tsepg.cf/epg.xml.gz"\n'
    
    categories = defaultdict(list)
    
    for channel in channels:
        # ALWAYS returns a URL (HLS or Raw), never None
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
    print("Done! M3U generated.")

if __name__ == "__main__":
    main()
