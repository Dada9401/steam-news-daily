import feedparser
import datetime
import re
import time
import random

# ==========================================
# 核心配置：2026 Steam 官方活动数据库
# ==========================================
STEAM_EVENTS_2026 = [
    {"name": "棋盘游戏节", "start": "20260126", "end": "20260202", "type": "fest"},
    {"name": "打字节 (焦点节)", "start": "20260205", "end": "20260209", "type": "spotlight"},
    {"name": "PvP 游戏节", "start": "20260209", "end": "20260216", "type": "fest"},
    {"name": "Steam 新品节 (2月版)", "start": "20260223", "end": "20260302", "type": "nextfest", "appid": "3985950"},
    {"name": "Steam 春季特卖", "start": "20260319", "end": "20260326", "type": "major"},
    {"name": "Steam 新品节 (6月版)", "start": "20260615", "end": "20260622", "type": "nextfest"},
    {"name": "Steam 夏季特卖", "start": "20260625", "end": "20260709", "type": "major"},
]

def generate_timeline_html():
    now = datetime.datetime.now()
    curr_int = int(now.strftime("%Y%m%d"))
    html = '<div class="flex flex-nowrap gap-4 overflow-x-auto pb-6 mb-10 no-scrollbar select-none">'
    upcoming = [e for e in STEAM_EVENTS_2026 if int(e['end']) >= curr_int][:8]
    for e in upcoming:
        active = int(e['start']) <= curr_int <= int(e['end'])
        color = {"major": "red-500", "nextfest": "emerald-500", "spotlight": "purple-500"}.get(e['type'], "blue-500")
        html += f'''
        <div class="flex-shrink-0 w-60 p-5 rounded-2xl bg-white/80 dark:bg-slate-900/40 backdrop-blur-xl border border-slate-200 dark:border-white/5 transition-all">
            <div class="flex justify-between items-center mb-3">
                <span class="text-[9px] font-black {'text-emerald-500 animate-pulse' if active else 'text-slate-400'} uppercase">{'● ACTIVE' if active else '○ PENDING'}</span>
                <span class="text-[10px] font-mono text-slate-400">{e['start'][4:6]}-{e['start'][6:]}</span>
            </div>
            <div class="text-sm font-bold text-slate-800 dark:text-slate-100 truncate mb-3">{e['name']}</div>
            <div class="h-1 w-full bg-slate-100 dark:bg-white/5 rounded-full overflow-hidden">
                <div class="h-full bg-{color} {'shadow-[0_0_8px] shadow-'+color if active else 'opacity-20'}" style="width: {'100%' if active else '20%'}"></div>
            </div>
        </div>'''
    return html + '</div>'

def get_steam_all_data():
    """
    统一抓取所有源，返回处理后的条目列表
    """
    urls = [
        "https://store.steampowered.com/feeds/news/collection/featured/?l=schinese",
        "https://store.steampowered.com/feeds/news/collection/steam/?l=schinese",
        "https://store.steampowered.com/feeds/news/group/39049601/?l=schinese",
        "https://store.steampowered.com/feeds/news/group/4145017/?l=schinese"
    ]
    entries = []
    seen_links = set()
    timestamp = int(time.time())
    for url in urls:
        try:
            feed = feedparser.parse(f"{url}&nocache={timestamp}&v={random.random()}")
            for e in feed.entries:
                if e.link not in seen_links:
                    entries.append(e)
                    seen_links.add(e.link)
        except: continue
    # 基础按时间排序
    entries.sort(key=lambda x: x.get('published_parsed', time.gmtime(0)), reverse=True)
    return entries

def build_news_sections(all_entries):
    urgent_items = []
    feat_html = ""
    offi_html = ""
    
    # 截止日期识别关键词
    deadline_keywords = ["报名", "截止", "deadline", "apply", "registration", "registration closes"]
    
    # 1. 提取紧急截止内容 (Urgent Ticker)
    for e in all_entries[:30]: # 扫描最近30条
        text_to_scan = (e.title + e.get('summary', '')).lower()
        if any(k in text_to_scan for k in deadline_keywords):
            urgent_items.append(e)

    # 2. 生成精选资讯 (Featured - 游戏节置顶)
    def feat_sort(e):
        is_fest = any(k in e.title.lower() for k in ["游戏节", "festival", "fest", "新品节"])
        pub_time = time.mktime(e.get('published_parsed', time.gmtime(0)))
        return (1e10 if is_fest else 0) + pub_time
    
    feat_entries = sorted(all_entries[:20], key=feat_sort, reverse=True)
    for e in feat_entries[:10]:
        feat_html += render_slide(e, True)

    # 3. 生成官方公告
    offi_entries = [e for e in all_entries if any(k in e.title for k in ["公告", "Steam", "Update"])]
    for e in offi_entries[:10]:
        offi_html += render_slide(e, False)

    return feat_html, offi_html, urgent_items

def render_slide(e, allow_fest_logic):
    title, link = e.title, e.link
    content = e.get('summary', '') or e.get('description', '')
    img = re.search(r'<img [^>]*src="([^"]+)"', content)
    img_url = img.group(1) if img else "https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/3985950/capsule_617x353.jpg"
    pub_time = time.strftime("%m-%d %H:%M", e.published_parsed) if hasattr(e, 'published_parsed') else "RECENT"
    
    is_fest = any(k in title.lower() for k in ["游戏节", "festival", "fest"])
    fest_tag = '<span class="bg-emerald-500 text-white text-[9px] px-2 py-0.5 rounded mr-2">FESTIVAL</span>' if is_fest and allow_fest_logic else ""
    
    return f'''
    <div class="swiper-slide group cursor-pointer" onclick="window.open('{link}', '_blank')">
        <div class="relative h-[420px] w-full overflow-hidden rounded-[2.5rem] bg-white dark:bg-[#1a1f26] border { "border-emerald-500/50 shadow-[0_0_30px_rgba(16,185,129,0.2)]" if is_fest and allow_fest_logic else "border-slate-200 dark:border-white/5" } transition-all duration-500">
            <img src="{img_url}" class="absolute inset-0 w-full h-full object-cover opacity-90 dark:opacity-40 transition-transform duration-1000 group-hover:scale-110">
            <div class="absolute inset-0 bg-gradient-to-t from-slate-50 dark:from-[#05070a] via-transparent to-transparent"></div>
            <div class="absolute bottom-0 p-8 w-full">
                <div class="flex items-center gap-2 mb-3">
                    {fest_tag}
                    <span class="text-[10px] font-mono text-blue-600 dark:text-blue-400 font-bold uppercase tracking-widest">{pub_time}</span>
                </div>
                <h2 class="text-2xl font-black text-slate-900 dark:text-white line-clamp-2 leading-tight tracking-tighter italic">{title}</h2>
            </div>
        </div>
    </div>'''

def update_web():
    all_entries = get_steam_all_data()
    feat, offi, urgent = build_news_sections(all_entries)
    
    # 构造紧急轮条内容
    urgent_html = "".join([f'<a href="{e.link}" target="_blank" class="mx-8 hover:text-white transition-colors">⚠️ <span class="font-bold text-amber-500">[报名截止提醒]</span> {e.title}</a>' for e in urgent])
    if not urgent_html: urgent_html = "<span>目前没有检测到即将截止的报名项 // 持续监控中...</span>"

    template = f'''<!DOCTYPE html>
<html lang="zh-CN" class="dark">
<head>
    <meta charset="UTF-8">
    <title>STEAM INTEL NODE</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.css" />
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {{ darkMode: 'class' }}
        function toggleTheme() {{
            const isDark = document.documentElement.classList.toggle('dark');
            localStorage.setItem('steam_theme', isDark ? 'dark' : 'light');
        }}
    </script>
    <style>
        .no-scrollbar::-webkit-scrollbar {{ display: none; }}
        .swiper {{ width: 100%; height: 500px; padding: 20px 0 80px 0; overflow: visible !important; }}
        .swiper-slide {{ width: 550px; opacity: 0.1; transition: 0.8s cubic-bezier(0.2, 1, 0.3, 1); transform: scale(0.85); filter: blur(10px); }}
        .swiper-slide-active {{ opacity: 1; transform: scale(1); filter: blur(0); z-index: 20; }}
        @keyframes marquee {{ 0% {{ transform: translateX(0); }} 100% {{ transform: translateX(-50%); }} }}
        .animate-marquee {{ display: inline-flex; animation: marquee 40s linear infinite; }}
        body {{ transition: background-color 0.5s ease; }}
    </style>
</head>
<body class="bg-slate-50 dark:bg-[#05070a] text-slate-900 dark:text-slate-100 p-6 md:p-16 min-h-screen pb-32">
    <div class="max-w-[1500px] mx-auto">
        <header class="flex justify-between items-center mb-16">
            <div class="border-l-4 border-blue-600 pl-6">
                <h1 class="text-6xl font-black italic tracking-tighter uppercase text-slate-900 dark:text-white leading-none">Steam<span class="text-blue-600">Intel</span></h1>
                <p class="text-[10px] text-blue-500 font-mono mt-3 tracking-[0.5em] uppercase font-bold">2026 SURVEILLANCE NODE</p>
            </div>
            <button onclick="toggleTheme()" class="px-6 py-3 bg-white dark:bg-slate-900 rounded-xl shadow-lg border border-slate-200 dark:border-white/5 transition-all active:scale-95">
                <span class="text-xs font-black tracking-widest dark:hidden">DARK</span><span class="text-xs font-black tracking-widest hidden dark:inline text-blue-400">LIGHT</span>
            </button>
        </header>

        <section class="mb-20">
            <div class="flex items-center gap-4 mb-8 text-[10px] font-black uppercase text-blue-600 tracking-[0.3em]">
                <span>Roadmap</span><div class="h-px flex-1 bg-slate-200 dark:bg-white/10"></div>
            </div>
            {generate_timeline_html()}
        </section>

        <main class="space-y-24">
            <section>
                <h2 class="text-3xl font-black italic uppercase mb-8 tracking-tighter italic">Featured <span class="text-blue-600">精选资讯</span></h2>
                <div class="swiper mySwiper"><div class="swiper-wrapper">{feat}</div><div class="swiper-pagination"></div></div>
            </section>
            <section>
                <h2 class="text-3xl font-black italic uppercase mb-8 tracking-tighter italic text-blue-600">Official <span class="dark:text-white">官方公告</span></h2>
                <div class="swiper mySwiper"><div class="swiper-wrapper">{offi}</div><div class="swiper-pagination"></div></div>
            </section>
        </main>
    </div>

    <div class="fixed bottom-0 left-0 w-full h-14 bg-white/70 dark:bg-slate-900/80 backdrop-blur-2xl border-t border-slate-200 dark:border-white/10 flex items-center overflow-hidden z-[100]">
        <div class="bg-amber-500 text-white h-full flex items-center px-6 font-black text-xs z-10 shadow-xl tracking-tighter">URGENT</div>
        <div class="flex-1 overflow-hidden relative">
            <div class="animate-marquee whitespace-nowrap text-xs font-bold text-slate-600 dark:text-slate-400 py-2 uppercase tracking-wide">
                {urgent_html} {urgent_html}
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.js"></script>
    <script>
        if (localStorage.getItem('steam_theme') === 'light') document.documentElement.classList.remove('dark');
        document.querySelectorAll('.mySwiper').forEach(el => {{
            new Swiper(el, {{
                effect: "coverflow", centeredSlides: true, slidesPerView: "auto", loop: true,
                autoplay: {{ delay: 5000 }},
                coverflowEffect: {{ rotate: 0, stretch: 80, depth: 150, modifier: 1.5, slideShadows: false }},
                pagination: {{ el: el.querySelector('.swiper-pagination'), clickable: true }}
            }});
        }});
    </script>
</body>
</html>'''
    with open("index.html", "w", encoding="utf-8") as f: f.write(template)

if __name__ == "__main__":
    update_web()
    print("Dashboard Updated: Deadline Ticker Integrated.")
