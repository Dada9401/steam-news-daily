import requests
import datetime
import re
import feedparser

def get_data(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    try:
        r = requests.get(url, headers=headers, timeout=15)
        return r
    except: return None

def update_web():
    # --- 1. 抓取行业简报 (GameSpot) ---
    ticker_text = "正在连接行业情报源..."
    try:
        industry_feed = feedparser.parse("https://www.gamespot.com/feeds/news/")
        if industry_feed.entries:
            briefs = [f"【{e.title}】" for e in industry_feed.entries[:10]]
            ticker_text = " • ".join(briefs)
    except: ticker_text = "行业简报暂时离线"

    # --- 2. 抓取 Steam 数据 ---
    def get_steam_slides(clan_id):
        # 增加随机参数绕过缓存
        api_url = f"https://store.steampowered.com/events/ajaxgetadjacentevents/?appid=0&clanid={clan_id}&count=10&l=schinese&t={datetime.datetime.now().timestamp()}"
        res = get_data(api_url)
        html = ""
        if res and res.status_code == 200:
            events = res.json().get('events', [])
            for e in events:
                gid = e.get('announcement_body', {}).get('gid', '')
                img = e.get('jsondata', {}).get('image_url', '')
                # 构建图片URL
                img_url = f"https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/0/events/{gid}/{img}" if img else "https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/594650/capsule_617x353.jpg"
                html += f"""
                <div class="swiper-slide cursor-pointer" onclick="window.open('https://store.steampowered.com/news/view/{gid}', '_blank')">
                    <div class="relative h-full w-full overflow-hidden rounded-3xl border border-white/10 bg-slate-900">
                        <img src="{img_url}" class="absolute inset-0 w-full h-full object-cover opacity-40">
                        <div class="absolute inset-0 bg-gradient-to-t from-[#05070a] to-transparent"></div>
                        <div class="absolute bottom-0 p-6 w-full"><h2 class="text-lg font-bold text-white line-clamp-2">{e.get('event_name')}</h2></div>
                    </div>
                </div>"""
        return html

    featured_html = get_steam_slides("39154431")
    official_html = get_steam_slides("4")

    # 如果没内容，放个占位符提示
    if not featured_html: featured_html = '<div class="text-gray-500">Steam 精选内容同步中...</div>'
    if not official_html: official_html = '<div class="text-gray-500">Steam 官方公告同步中...</div>'

    now_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # --- 3. 生成完整 HTML ---
    full_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Steam & 行业监控</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.css" />
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body {{ background: #020408; color: white; font-family: system-ui; overflow-x: hidden; padding-bottom: 80px; }}
        .swiper {{ width: 100%; height: 320px; padding: 20px 0; overflow: visible !important; }}
        .swiper-slide {{ width: 380px; opacity: 0.3; transition: 0.5s; transform: scale(0.8); }}
        .swiper-slide-active {{ opacity: 1; transform: scale(1); }}
        .ticker-wrap {{ position: fixed; bottom: 0; left: 0; width: 100%; background: #2563eb; color: white; padding: 12px 0; z-index: 100; }}
        .ticker {{ display: inline-block; white-space: nowrap; animation: scroll 80s linear infinite; }}
        @keyframes scroll {{ 0% {{ transform: translateX(100%); }} 100% {{ transform: translateX(-100%); }} }}
    </style>
</head>
<body class="p-6 md:p-12">
    <div class="max-w-7xl mx-auto">
        <h1 class="text
