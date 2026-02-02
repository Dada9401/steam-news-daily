import feedparser
import datetime
import re
import time
import random

# ==========================================
# 1. 核心数据库：Steam 官方活动
# ==========================================
STEAM_EVENTS_2026 = [
    {"name": "棋盘游戏节", "start": "20260126", "end": "20260202", "type": "fest", "url": "https://store.steampowered.com/category/tabletop"},
    {"name": "再来一局游戏节 (Tiny Roguelikes)", "start": "20260130", "end": "20260206", "type": "fest", "url": "https://store.steampowered.com/developer/rogueduck/sale/TinyRoguelikes2026"},
    {"name": "打字节 (焦点节)", "start": "20260205", "end": "20260209", "type": "spotlight", "url": "https://store.steampowered.com/category/typing"},
    {"name": "PvP 游戏节", "start": "20260209", "end": "20260216", "type": "fest", "url": "https://store.steampowered.com/category/pvp"},
    {"name": "Steam 新品节 (2月版)", "start": "20260223", "end": "20260302", "type": "nextfest", "url": "https://store.steampowered.com/sale/nextfest"},
    {"name": "Steam 春季特卖", "start": "20260319", "end": "20260326", "type": "major", "url": "https://store.steampowered.com/sale/springsale"},
]

THIRD_PARTY_EVENTS = [
    {"name": "GDS GameDev Summit", "start": "20260203", "end": "20260205", "url": "https://gamedevsummit.com/"},
    {"name": "GDC 2026", "start": "20260309", "end": "20260313", "url": "https://gdconf.com/"},
]

def generate_timeline_html():
    now = datetime.datetime.now()
    curr_int = int(now.strftime("%Y%m%d"))
    upcoming = [e for e in sorted(STEAM_EVENTS_2026, key=lambda x: x['start']) if int(e['end']) >= curr_int]
    html = '<div class="flex flex-nowrap gap-4 overflow-x-auto pb-6 mb-10 no-scrollbar select-none">'
    for e in upcoming:
        active = int(e['start']) <= curr_int <= int(e['end'])
        color = "emerald-500" if active else "blue-600"
        html += f'''
        <div class="flex-shrink-0 w-64 p-6 rounded-3xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-white/5 shadow-sm">
            <div class="flex justify-between items-center mb-4">
                <span class="text-[10px] font-black {'text-emerald-500 animate-pulse' if active else 'text-slate-400'}">{'● ACTIVE' if active else '○ PENDING'}</span>
                <span class="text-[10px] font-mono text-slate-400">{e['start'][4:6]}/{e['start'][6:]}</span>
            </div>
            <div class="text-base font-bold truncate mb-4">{e['name']}</div>
            <div class="h-1.5 w-full bg-slate-100 dark:bg-white/5 rounded-full overflow-hidden">
                <div class="h-full bg-{color}" style="width: {'100%' if active else '20%'}"></div>
            </div>
        </div>'''
    return html + '</div>'

def generate_active_ticker():
    now = datetime.datetime.now()
    curr_int = int(now.strftime("%Y%m%d"))
    contents = []
    for e in STEAM_EVENTS_2026 + THIRD_PARTY_EVENTS:
        if int(e['start']) <= curr_int <= int(e['end']):
            url = e.get('url', '#')
            contents.append(f"<span>🔥 正在开展: {e['name']}</span> | <a href='{url}' target='_blank' class='text-yellow-400 font-bold hover:underline px-2'>[进入会场]</a>")
    if not contents: return ""
    ticker_text = " ——— ".join(contents)
    return f'''<div id="ticker-bar" class="fixed bottom-0 left-0 w-full bg-blue-900 text-white py-4 z-[9999] overflow-hidden whitespace-nowrap border-t border-white/20 shadow-2xl">
        <div class="inline-block animate-marquee px-4"><span class="font-bold italic text-sm uppercase">{ticker_text} ——— {ticker_text}</span></div>
    </div>'''

def get_news_data(exclude_links, mode):
    # 扩大抓取范围以确保去重后仍有10条
    url = "https://store.steampowered.com/feeds/news/collection/steam/?l=schinese" if mode == "official" else "https://store.steampowered.com/feeds/news/collection/featured/?l=schinese"
    try:
        feed = feedparser.parse(f"{url}&v={random.random()}")
        entries = feed.entries
    except: return ""

    # 逻辑：精选提权，官方纯时间
    def sort_logic(e):
        t = time.mktime(e.get('published_parsed', time.gmtime(0)))
        if mode == "featured":
            is_fest = any(k in e.title.lower() for k in ["游戏节", "festival", "fest", "roguelike", "sale"])
            return t + (10**10 if is_fest else 0)
        return t

    entries.sort(key=sort_logic, reverse=True)
    
    # 筛选不重复的条目
    final_list = []
    for e in entries:
        if e.link not in exclude_links:
            final_list.append(e)
            exclude_links.add(e.link)
        if len(final_list) == 10: break # 强行保底10条

    html_slides = ""
    for e in final_list:
        content = e.get('summary', '') or e.get('description', '')
        img = re.search(r'<img [^>]*src="([^"]+)"', content)
        img_url = img.group(1) if img else "https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/3985950/capsule_617x353.jpg"
        is_fest = any(k in e.title.lower() for k in ["游戏节", "festival", "fest"])
        glow = "ring-4 ring-emerald-500 shadow-[0_0_30px_rgba(16,185,129,0.5)]" if (is_fest and mode == "featured") else ""
        
        html_slides += f'''
        <div class="swiper-slide cursor-pointer" onclick="window.open('{e.link}', '_blank')">
            <div class="relative h-[440px] w-full overflow-hidden rounded-[2.5rem] bg-[#1a1f26] border border-white/5 transition-all {glow}">
                <img src="{img_url}" class="absolute inset-0 w-full h-full object-cover opacity-80 transition-transform duration-1000 group-hover:scale-110">
                <div class="absolute inset-0 bg-gradient-to-t from-black via-transparent to-transparent"></div>
                <div class="absolute bottom-0 p-8 w-full text-white">
                    <div class="flex items-center gap-3 mb-3">
                        { "<span class='bg-emerald-500 text-white text-[9px] px-2 py-1 rounded italic font-black'>FESTIVAL</span>" if is_fest else "" }
                        <span class="font-mono text-[10px] text-blue-400 font-bold uppercase">{time.strftime("%m-%d %H:%M", e.published_parsed)}</span>
                    </div>
                    <h2 class="text-2xl font-black line-clamp-2 italic leading-tight uppercase">{e.title}</h2>
                </div>
            </div>
        </div>'''
    return html_slides

def update_web():
    now_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    exclude = set()
    # 先拿精选，再拿官方，确保官方拿满10条
    feat = get_news_data(exclude, "featured")
    offi = get_news_data(exclude, "official")
    timeline = generate_timeline_html()
    ticker = generate_active_ticker()

    with open("template.html", "r", encoding="utf-8") as f:
        tmpl = f.read()

    output = tmpl.replace("@@NOW_TIME@@", now_time).replace("@@TIMELINE@@", timeline).replace("@@FEAT_HTML@@", feat).replace("@@OFFI_HTML@@", offi).replace("@@TICKER@@", ticker)

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(output)

if __name__ == "__main__":
    update_web()
