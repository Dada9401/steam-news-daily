import requests
import datetime
import time
import feedparser

def get_steam_data(clan_id):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    url = f"https://store.steampowered.com/events/ajaxgetadjacentevents/?appid=0&clanid={clan_id}&count=10&l=schinese&t={int(time.time())}"
    try:
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code == 200:
            return r.json().get('events', [])
    except:
        pass
    return []

def format_slide(e):
    gid = e.get('announcement_body', {}).get('gid', '')
    img = e.get('jsondata', {}).get('image_url', '')
    img_url = f"https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/0/events/{gid}/{img}" if img else "https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/594650/capsule_617x353.jpg"
    return f'''
    <div class="swiper-slide cursor-pointer" onclick="window.open('https://store.steampowered.com/news/view/{gid}', '_blank')">
        <div class="relative h-full w-full overflow-hidden rounded-2xl bg-slate-900 border border-white/10">
            <img src="{img_url}" class="absolute inset-0 w-full h-full object-cover opacity-50">
            <div class="absolute inset-0 bg-gradient-to-t from-black via-transparent to-transparent"></div>
            <div class="absolute bottom-0 p-4 w-full">
                <h2 class="text-sm font-bold text-white line-clamp-2">{e.get('event_name', 'Steam News')}</h2>
            </div>
        </div>
    </div>'''

def update_web():
    # 1. 行业简报
    ticker_text = "行业简报同步中..."
    try:
        feed = feedparser.parse("https://www.gamespot.com/feeds/news/")
        if feed.entries:
            ticker_text = " • ".join([f"【{e.title}】" for e in feed.entries[:10]])
    except: pass

    # 2. Steam 数据
    featured_html = "".join([format_slide(e) for e in get_steam_data("39154431")])
    official_html = "".join([format_slide(e) for e in get_steam_data("4")])
    
    if not featured_html: featured_html = '<div class="p-10 text-gray-500">正在尝试重新连接 Steam 精选源...</div>'
    if not official_html: official_html = '<div class="p-10 text-gray-500">正在尝试重新连接 Steam 官方源...</div>'

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # 3. 页面模板
    full_html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Steam & Industry Monitor</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.css" />
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body {{ background: #05070a; color: white; font-family: sans-serif; overflow-x: hidden; padding-bottom: 80px; }}
        .swiper {{ width: 100%; height: 280px; padding: 20px 0; overflow: visible !important; }}
        .swiper-slide {{ width: 320px; opacity: 0.4; transition: 0.4s; transform: scale(0.8); }}
        .swiper-slide-active {{ opacity: 1; transform: scale(1); }}
        .ticker-wrap {{ position: fixed; bottom: 0; left: 0; width: 100%; background: #2563eb; color: white; padding: 12px 0; z-index: 100; }}
        .ticker {{ display: inline-block; white-space: nowrap; animation: scroll 80s linear infinite; font-size: 13px; font-weight: bold; }}
        @keyframes scroll {{ 0% {{ transform: translateX(100%); }} 100% {{ transform: translateX(-100%); }} }}
    </style>
</head>
<body class="p-6">
    <div class="max-w-6xl mx-auto">
        <header class="mb-10 border-b border-white/10 pb-4 flex justify-between items-end">
            <h1 class="text-3xl font-black italic tracking-tighter text-blue-500">MONITOR 2026</h1>
            <span class="text-[10px] font-mono opacity-40">LAST SYNC: {now}</span>
        </header>

        <h2 class="text-lg font-bold mb-4 flex items-center gap-2"><span class="w-1 h-5 bg-blue-600"></span> FEATURED 精选</h2>
        <div class="swiper mySwiper"><div class="swiper-wrapper">{featured_html}</div></div>

        <h2 class="text-lg font-bold mt-10 mb-4 flex items-center gap-2"><span class="w-1 h-5 bg-blue-400"></span> OFFICIAL 官方</h2>
        <div class="swiper mySwiper"><div class="swiper-wrapper">{official_html}</div></div>
    </div>

    <div class="ticker-wrap"><div class="ticker">INDUSTRY BRIEF: {ticker_text}</div></div>

    <script src="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.js"></script>
    <script>
        document.querySelectorAll('.mySwiper').forEach(el => {{
            new Swiper(el, {{ effect: "coverflow", grabCursor: true, centeredSlides: true, slidesPerView: "auto", loop: true, autoplay: {{ delay: 3500 }} }});
        }});
    </script>
</body>
</html>'''

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(full_html)

if __name__ == "__main__":
    update_web()
