import requests
import datetime
import re
import feedparser # 需要在 daily.yml 加上这个库

def get_steam_data(clan_id):
    url = f"https://store.steampowered.com/events/ajaxgetadjacentevents/?appid=0&clanid={clan_id}&count=10&l=schinese&t={datetime.datetime.now().timestamp()}"
    try:
        return requests.get(url, timeout=10).json().get('events', [])
    except: return []

def update_web():
    # 1. 抓取 Steam 数据
    featured = get_steam_data("39154431")
    official = get_steam_data("4")
    
    # 2. 抓取行业简报 (使用顶级游戏媒体源)
    industry_feed = feedparser.parse("https://www.gamespot.com/feeds/news/")
    briefs = [f"【{entry.title}】" for entry in industry_feed.entries[:15]]
    ticker_text = " • ".join(briefs)

    # 3. 组装卡片逻辑 (同前)
    def make_slides(events, cat):
        html = ""
        for e in events:
            gid = e.get('announcement_body', {}).get('gid', '')
            img = e.get('jsondata', {}).get('image_url', '')
            img_url = f"https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/0/events/{gid}/{img}" if img else "https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/594650/capsule_617x353.jpg"
            html += f"""
            <div class="swiper-slide cursor-pointer" onclick="window.open('https://store.steampowered.com/news/view/{gid}', '_blank')">
                <div class="relative h-full w-full overflow-hidden rounded-3xl border border-white/10 group bg-slate-900">
                    <img src="{img_url}" class="absolute inset-0 w-full h-full object-cover opacity-50 group-hover:scale-105 transition-transform duration-500">
                    <div class="absolute inset-0 bg-gradient-to-t from-[#05070a] to-transparent"></div>
                    <div class="absolute bottom-0 p-6 w-full"><h2 class="text-xl font-bold text-white">{e.get('event_name')}</h2></div>
                </div>
            </div>"""
        return html

    now_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # 4. 生成最终 HTML
    full_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Steam & 行业监控站</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.css" />
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body {{ background: #05070a; color: white; font-family: sans-serif; overflow-x: hidden; padding-bottom: 60px; }}
        .swiper {{ width: 100%; height: 350px; padding: 20px 0; }}
        .swiper-slide {{ width: 420px; opacity: 0.5; transition: 0.3s; }}
        .swiper-slide-active {{ opacity: 1; }}
        .ticker-wrap {{ position: fixed; bottom: 0; left: 0; width: 100%; background: #3b82f6; color: white; padding: 10px 0; z-index: 100; overflow: hidden; }}
        .ticker {{ display: inline-block; white-space: nowrap; animation: ticker 60s linear infinite; font-weight: bold; font-size: 0.9rem; }}
        @keyframes ticker {{ 0% {{ transform: translateX(100%); }} 100% {{ transform: translateX(-100%); }} }}
    </style>
</head>
<body class="p-4 md:p-12">
    <div class="max-w-7xl mx-auto">
        <header class="flex justify-between items-center border-b border-blue-900/30 pb-6">
            <h1 class="text-4xl font-black italic text-blue-500">NEWS MONITOR</h1>
            <p class="text-[10px] font-mono opacity-50 italic uppercase tracking-[0.3em]">Last Sync: {now_time}</p>
        </header>

        <h2 class="mt-12 text-2xl font-black italic text-white/90">FEATURED 精选</h2>
        <div class="swiper mySwiper"><div class="swiper-wrapper">{make_slides(featured, "精选")}</div></div>

        <h2 class="mt-8 text-2xl font-black italic text-blue-400/90">OFFICIAL 官方</h2>
        <div class="swiper mySwiper"><div class="swiper-wrapper">{make_slides(official, "官方")}</div></div>
    </div>

    <div class="ticker-wrap">
        <div class="ticker text-sm uppercase">
             TOP INDUSTRY HEADLINES: {ticker_text}
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.js"></script>
    <script>
        document.querySelectorAll('.mySwiper').forEach(el => {{
            new Swiper(el, {{ effect: "coverflow", grabCursor: true, centeredSlides: true, slidesPerView: "auto", loop: true, autoplay: {{ delay: 4000 }} }});
        }});
    </script>
</body>
</html>"""

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(full_html)

if __name__ == "__main__":
    update_web()
