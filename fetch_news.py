import requests
import datetime
import re

def get_latest_news(clan_id):
    # 使用 Steam 内部活动接口，这是目前最实时的数据源
    # clanid 39154431 为精选/官方混合，clanid 4 为 Steam 核心更新
    url = f"https://store.steampowered.com/events/ajaxgetadjacentevents/?appid=0&clanid={clan_id}&count=15&l=schinese"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        resp = requests.get(url, headers=headers, timeout=10).json()
        return resp.get('events', [])
    except:
        return []

def format_card(event, category_name):
    title = event.get('event_name', 'Steam News')
    # 提取时间戳并转换
    ts = event.get('rtime_last_modified', 0)
    date_str = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
    
    # 获取公告 ID 和 链接
    gid = event.get('announcement_body', {}).get('gid', '')
    link = f"https://store.steampowered.com/news/view/{gid}"
    
    # 强制匹配 2026 年最新大图
    img_src = event.get('jsondata', {}).get('image_url', '')
    if img_src:
        img_url = f"https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/0/events/{gid}/{img_src}"
    else:
        img_url = "https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/594650/capsule_617x353.jpg"

    return f"""
    <div class="swiper-slide cursor-pointer" onclick="window.open('{link}', '_blank')">
        <div class="relative h-full w-full overflow-hidden rounded-3xl border border-white/10 group bg-slate-800">
            <img src="{img_url}" class="absolute inset-0 w-full h-full object-cover opacity-50 group-hover:scale-105 transition-transform duration-500">
            <div class="absolute inset-0 bg-gradient-to-t from-[#05070a] via-transparent to-transparent"></div>
            <div class="absolute bottom-0 p-6 w-full">
                <div class="flex items-center gap-2 mb-2">
                    <span class="bg-blue-600 text-[10px] px-2 py-0.5 rounded font-bold italic">{category_name}</span>
                    <span class="text-[10px] text-gray-400">{date_str}</span>
                </div>
                <h2 class="text-xl font-bold text-white line-clamp-2">{title}</h2>
            </div>
        </div>
    </div>
    """

def update_web():
    # 抓取不同板块
    featured = get_latest_news("39154431") # 精选/推荐
    official = get_latest_news("4")        # 官方/技术
    
    featured_html = "".join([format_card(e, "精选") for e in featured])
    official_html = "".join([format_card(e, "官方") for e in official])

    now_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    
    full_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Steam & 行业实时动态</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.css" />
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body {{ background: #05070a; color: white; font-family: sans-serif; overflow-x: hidden; }}
        .swiper {{ width: 100%; height: 350px; padding: 20px 0; overflow: visible !important; }}
        .swiper-slide {{ width: 420px; transition: opacity 0.3s; opacity: 0.4; }}
        .swiper-slide-active {{ opacity: 1; }}
        .section-header {{ display: flex; align-items: center; gap: 1rem; margin-top: 50px; }}
        .section-header h2 {{ font-size: 1.8rem; font-weight: 900; font-style: italic; color: #3b82f6; }}
    </style>
</head>
<body class="p-4 md:p-12">
    <div class="max-w-7xl mx-auto">
        <header class="flex flex-col md:flex-row justify-between items-baseline border-b border-blue-900/30 pb-6">
            <h1 class="text-5xl font-black italic tracking-tighter bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-indigo-600">NEWS MONITOR</h1>
            <p class="text-xs font-mono text-blue-500 uppercase tracking-widest mt-2 md:mt-0">Update: {now_time}</p>
        </header>
