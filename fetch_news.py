import feedparser
import datetime
import re

# --- 2026 Steam 官方全年度活动数据库（完全对齐官方公告） ---
STEAM_EVENTS_2026 = [
    # 上半年
    {"name": "推理节", "start": "20260112", "end": "20260119", "type": "fest"},
    {"name": "棋盘游戏节", "start": "20260126", "end": "20260202", "type": "fest"},
    {"name": "打字节 (焦点游戏节)", "start": "20260205", "end": "20260209", "type": "spotlight"},
    {"name": "玩家对战 (PvP) 节", "start": "20260209", "end": "20260216", "type": "fest"},
    {"name": "马儿节 (焦点游戏节)", "start": "20260219", "end": "20260223", "type": "spotlight"},
    {"name": "Steam 新品节 (2月版)", "start": "20260223", "end": "20260302", "type": "nextfest"},
    {"name": "塔防节", "start": "20260309", "end": "20260316", "type": "fest"},
    {"name": "Steam 春季特卖 (大促)", "start": "20260319", "end": "20260326", "type": "major"},
    {"name": "房屋与家园节", "start": "20260330", "end": "20260407", "type": "fest"},
    {"name": "隐藏物件节 (焦点游戏节)", "start": "20260409", "end": "20260413", "type": "spotlight"},
    {"name": "中世纪节", "start": "20260420", "end": "20260427", "type": "fest"},
    {"name": "牌组制作节", "start": "20260504", "end": "20260511", "type": "fest"},
    {"name": "海洋节", "start": "20260518", "end": "20260525", "type": "fest"},
    # 下半年 (基于你提供的官方链接 493837645658461607)
    {"name": "弹幕射击节", "start": "20260608", "end": "20260615", "type": "fest"},
    {"name": "Steam 新品节 (6月版)", "start": "20260615", "end": "20260622", "type": "nextfest"},
    {"name": "Steam 夏季特卖", "start": "20260625", "end": "20260709", "type": "major"},
    {"name": "社会演绎节", "start": "20260713", "end": "20260716", "type": "fest"},
    {"name": "列车节", "start": "20260720", "end": "20260727", "type": "fest"},
    {"name": "赛博朋克节", "start": "20260803", "end": "20260810", "type": "fest"},
    {"name": "生存工匠节 (PvE)", "start": "20260831", "end": "20260907", "type": "fest"},
    {"name": "Steam 秋季特卖", "start": "20261001", "end": "20261008", "type": "major"},
    {"name": "Steam 新品节 (10月版)", "start": "20261019", "end": "20261026", "type": "nextfest"},
    {"name": "万圣节尖叫祭 V", "start": "20261026", "end": "20261102", "type": "fest"},
    {"name": "Steam 冬季特卖", "start": "20261217", "end": "20270104", "type": "major"},
]

def generate_timeline_html():
    now = datetime.datetime.now()
    current_date_int = int(now.strftime("%Y%m%d"))
    html = '<div class="flex flex-nowrap gap-4 overflow-x-auto pb-6 mb-10 no-scrollbar select-none">'
    
    # 筛选未结束的最近 8 个活动
    upcoming = [e for e in STEAM_EVENTS_2026 if int(e['end']) >= current_date_int][:8]
    
    for event in upcoming:
        is_active = int(event['start']) <= current_date_int <= int(event['end'])
        color_map = {"major": "red-500", "nextfest": "yellow-400", "spotlight": "purple-400", "fest": "blue-400"}
        theme = color_map.get(event['type'], "blue-400")
        if is_active: theme = "green-400"

        start_m, start_d = event['start'][4:6], event['start'][6:]
        end_m, end_d = event['end'][4:6], event['end'][6:]
        
        status_icon = "● LIVE" if is_active else "○ AIMING"
        
        html += f'''
        <div class="flex-shrink-0 w-60 p-4 rounded-2xl bg-slate-900/40 border border-white/5 backdrop-blur-xl transition-all hover:border-{theme}/40">
            <div class="flex justify-between items-center mb-2">
                <span class="text-[9px] font-black text-{theme} tracking-widest">{status_icon}</span>
                <span class="text-[10px] font-mono text-gray-500">{start_m}/{start_d} - {end_m}/{end_d}</span>
            </div>
            <div class="text-sm font-bold text-white truncate mb-3">{event['name']}</div>
            <div class="h-1 w-full bg-white/5 rounded-full overflow-hidden">
                <div class="h-full bg-{theme} {'animate-pulse shadow-[0_0_8px_#4ade80]' if is_active else 'opacity-20'}" style="width: {'100%' if is_active else '10%'}"></div>
            </div>
        </div>'''
    html += '</div>'
    return html

def get_steam_rss_data(url_type):
    channel = "steam" if url_type == "steam" else "featured"
    rss_url = f"https://store.steampowered.com/feeds/news/collection/{channel}/?l=schinese"
    slides_html = ""
    try:
        feed = feedparser.parse(rss_url)
        # 针对官方频道，确保“新品节/Next Fest”这类大公告在前面
        entries = feed.entries
        if url_type == "steam":
            entries.sort(key=lambda e: any(kw in e.title for kw in ["新品节", "Next Fest", "大促", "公告"]), reverse=True)

        for entry in entries[:10]:
            title, link = entry.title, entry.link
            content = entry.get('summary', '') or entry.get('description', '')
            img_match = re.search(r'<img [^>]*src="([^"]+)"', content)
            img_url = img_match.group(1) if img_match else "https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/594650/capsule_617x353.jpg"
            
            tag = ""
            if "新品节" in title or "Next Fest" in title:
                tag = '<span class="bg-yellow-500 text-black text-[9px] px-1.5 py-0.5 rounded font-black mr-2">NEXT FEST</span>'
            elif "特卖" in title or "Sale" in title:
                tag = '<span class="bg-red-600 text-white text-[9px] px-1.5 py-0.5 rounded font-black mr-2">MAJOR SALE</span>'

            slides_html += f'''
            <div class="swiper-slide cursor-pointer" onclick="window.open('{link}', '_blank')">
                <div class="relative h-full w-full overflow-hidden rounded-[2.5rem] bg-slate-900 border border-white/5 group shadow-2xl">
                    <img src="{img_url}" class="absolute inset-0 w-full h-full object-cover opacity-50 transition-transform duration-1000 group-hover:scale-105">
                    <div class="absolute inset-0 bg-gradient-to-t from-[#020408] via-transparent to-transparent"></div>
                    <div class="absolute bottom-0 p-8 w-full">
                        <h2 class="text-2xl font-bold text-white leading-tight">{tag}{title}</h2>
                    </div>
                </div>
            </div>'''
        return slides_html
    except: return ""

def update_web():
    now_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    timeline_html = generate_timeline_html()
    featured_html = get_steam_rss_data("featured")
    official_html = get_steam_rss_data("steam")

    template = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>STEAM INTEL 2026</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.css" />
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background: #020408; color: white; font-family: 'Inter', system-ui, sans-serif; overflow-x: hidden; padding-bottom: 100px; }
        .no-scrollbar::-webkit-scrollbar { display: none; }
        .swiper { width: 100%; height: 420px; padding: 20px 0 80px 0; overflow: visible !important; }
        .swiper-slide { width: 480px; opacity: 0.2; transition: 0.6s cubic-bezier(0.22, 1, 0.36, 1); transform: scale(0.85); filter: blur(2px); }
        .swiper-slide-active { opacity: 1; transform: scale(1); filter: blur(0); }
        .swiper-pagination-bullet { background: rgba(255,255,255,0.2); width: 8px; height: 8px; transition: 0.4s; }
        .swiper-pagination-bullet-active { background: #3b82f6; width: 32px; border-radius: 4px; box-shadow: 0 0 20px rgba(59,130,246,0.6); }
        .ticker-wrap { position: fixed; bottom: 0; left: 0; width: 100%; background: #2563eb; color: white; padding: 12px 0; z-index: 100; font-size: 13px; letter-spacing: 1px; }
        .ticker { display: inline-block; white-space: nowrap; animation: scroll 100s linear infinite; font-weight: 800; }
        @keyframes scroll { 0% { transform: translateX(100%); } 100% { transform: translateX(-100%); } }
    </style>
</head>
<body class="px-6 py-10 md:px-12">
    <div class="max-w-[1400px] mx-auto">
        <header class="flex flex-col md:flex-row justify-between items-start md:items-end mb-12 border-l-4 border-blue-600 pl-6">
            <div>
                <h1 class="text-6xl font-black italic tracking-tighter uppercase leading-none text-white">Console 2.0</h1>
                <p class="text-[10px] text-blue-500 font-mono mt-3 tracking-[0.5em]">2026 OFFICIAL ROADMAP SYNC // {now_time}</p>
            </div>
        </header>

        <section class="mb-16">
            <div class="text-[10px] font-black text-gray-500 uppercase tracking-widest mb-6 flex items-center gap-3">
                <span class="w-2 h-2 bg-blue-600 rounded-full animate-ping"></span> Official Mission Control / 官方日程
            </div>
            {timeline_html}
        </section>

        <main class="space-y-20">
            <section>
                <div class="flex items-center gap-6 mb-4">
                    <h2 class="text-2xl font-black uppercase italic tracking-widest text-white">Featured</h2>
                    <div class="h-[1px] flex-1 bg-white/10"></div>
                </div>
                <div class="swiper mySwiper">
                    <div class="swiper-wrapper">{featured_html}</div>
                    <div class="swiper-pagination"></div>
                </div>
            </section>

            <section>
                <div class="flex items-center gap-6 mb-4">
                    <h2 class="text-2xl font-black uppercase italic tracking-widest text-blue-500">Official News</h2>
                    <div class="h-[1px] flex-1 bg-blue-500/20"></div>
                </div>
                <div class="swiper mySwiper">
                    <div class="swiper-wrapper">{official_html}</div>
                    <div class="swiper-pagination"></div>
                </div>
            </section>
        </main>
    </div>

    <div class="ticker-wrap"><div class="ticker">DATA STREAM: OFFICIAL STEAMWORKS 2026 ROADMAP DETECTED... ALL SYSTEMS OPERATIONAL... NO DATA LOSS DETECTED...</div></div>

    <script src="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.js"></script>
    <script>
        document.querySelectorAll('.mySwiper').forEach(el => {
            const swiper = new Swiper(el, {
                effect: "coverflow", centeredSlides: true, slidesPerView: "auto", loop: true,
                autoplay: { delay: 4500, disableOnInteraction: false },
                coverflowEffect: { rotate: 5, stretch: 50, depth: 100, modifier: 1, slideShadows: false },
                pagination: { el: el.querySelector('.swiper-pagination'), clickable: true }
            });
            el.addEventListener('mouseover', function(e) {
                if (e.target.classList.contains('swiper-pagination-bullet')) {
                    const bullets = Array.from(el.querySelectorAll('.swiper-pagination-bullet'));
                    swiper.slideToLoop(bullets.indexOf(e.target));
                }
            });
        });
    </script>
</body>
</html>'''

    full_html = template.replace("{now_time}", now_time)\
                        .replace("{featured_html}", featured_html)\
                        .replace("{official_html}", official_html)\
                        .replace("{timeline_html}", timeline_html)

    with open("index.html", "w", encoding="utf-8") as f: f.write(full_html)

if __name__ == "__main__":
    update_web()
