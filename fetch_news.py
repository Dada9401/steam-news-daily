import requests
import datetime
import re

def get_steam_news(clan_id):
    # 使用 Steam 官方 Web 接口获取实时数据
    url = f"https://store.steampowered.com/events/ajaxgetadjacentevents/?appid=0&clanid={clan_id}&count=10&l=schinese"
    try:
        resp = requests.get(url, timeout=10).json()
        events = resp.get('events', [])
        return events
    except:
        return []

def format_slide(event):
    # 提取标题、链接和图片
    title = event.get('event_name', 'Steam News')
    gid = event.get('announcement_body', {}).get('gid', '')
    clan_id = event.get('clan_steamid', '')
    link = f"https://store.steampowered.com/news/app/{event.get('appid')}/view/{gid}"
    
    # 获取封面图
    img_src = event.get('jsondata', {}).get('image_url', '')
    if not img_src:
        # 备选图
        img_src = "https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/594650/capsule_617x353.jpg"
    else:
        img_src = f"https://shared.fastly.steamstatic.com/assets_c/{img_src}"

    return f"""
    <div class="swiper-slide cursor-pointer" onclick="window.open('{link}', '_blank')">
        <div class="relative h-full w-full overflow-hidden rounded-2xl border border-white/10 group">
            <img src="{img_src}" class="absolute inset-0 w-full h-full object-cover opacity-60 group-hover:scale-110 transition-transform duration-700">
            <div class="absolute inset-0 bg-gradient-to-t from-[#0b0e14] via-transparent to-transparent"></div>
            <div class="absolute bottom-0 p-6 w-full">
                <h2 class="text-xl font-bold text-white line-clamp-2 group-hover:text-blue-400 transition-colors">{title}</h2>
            </div>
        </div>
    </div>
    """

def update_web():
    # 39154431 是 Steam 官方公告的 ClanID
    featured_events = get_steam_news("39154431") # 获取精选/官方混合
    official_events = get_steam_news("4") # 获取 Steam 官方博客动态

    featured_html = "".join([format_slide(e) for e in featured_events])
    official_html = "".join([format_slide(e) for e in official_events])

    now_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    
    full_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Steam 实时情报站</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.css" />
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body {{ background: #05070a; color: white; font-family: sans-serif; }}
        .swiper {{ width: 100%; height: 300px; padding: 20px 0; }}
        .swiper-slide {{ width: 400px; }}
        .section-title {{ border-left: 4px solid #3b82f6; padding-left: 15px; margin: 40px 0 20px 0; font-weight: 900; font-style: italic; }}
    </style>
</head>
<body class="p-8">
    <div class="max-w-6xl mx-auto">
        <header class="flex justify-between items-center mb-10">
            <h1 class="text-4xl font-black italic tracking-tighter text-blue-500">STEAM INTELLIGENCE</h1>
            <span class="text-xs font-mono opacity-50 text-white">SYNC: {now_time}</span>
        </header>

        <h2 class="section-title text-2xl uppercase">Featured 精选内容</h2>
        <div class="swiper mySwiper">
            <div class="swiper-wrapper">{featured_html}</div>
            <div class="swiper-pagination"></div>
        </div>

        <h2 class="section-title text-2xl uppercase text-blue-400">Official 官方公告</h2>
        <div class="swiper mySwiper">
            <div class="swiper-wrapper">{official_html}</div>
            <div class="swiper-pagination"></div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.js"></script>
    <script>
        document.querySelectorAll('.mySwiper').forEach(el => {{
            new Swiper(el, {{
                effect: "coverflow",
                grabCursor: true,
                centeredSlides: true,
                slidesPerView: "auto",
                loop: true,
                coverflowEffect: {{ rotate: 30, stretch: 0, depth: 100, modifier: 1, slideShadows: true }},
                autoplay: {{ delay: 3000 + Math.random()*1000 }}
            }});
        }});
    </script>
</body>
</html>"""

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(full_html)

if __name__ == "__main__":
    update_web()
