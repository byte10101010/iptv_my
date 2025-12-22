import json
from datetime import datetime
from collections import defaultdict

def load_json(filename):
    """Load channels from JSON"""
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data.get('all_channels', [])

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
        categories[category].append(channel)
    
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
            m3u_content += f'{channel.get("url", "")}\n\n'
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
    
    # Optionally update JSON timestamp (for consistency)
    with open('sl.json', 'r+') as f:
        data = json.load(f)
        data["StreamFlex_A_updated_at"] = datetime.utcnow().isoformat() + "Z"
        data["StreamFlex_SL_total_channels"] = len(channels)
        f.seek(0)
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.truncate()
    
    print("✓ myplaylist.m3u generated!")
    print("✓ sl.json timestamp updated!")

if __name__ == "__main__":
    main()
