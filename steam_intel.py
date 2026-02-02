import feedparser
import datetime
import re
import time
import random

# ==========================================
# 1. 核心数据库
# ==========================================
STEAM_EVENTS_2026 = [
    {"name": "棋盘游戏节", "start": "20260126", "end": "20260202", "type": "fest", "url": "https://store.steampowered.com/category/tabletop"},
    {"name": "再来一局游戏节 (Tiny Roguelikes)", "start": "20260130", "end": "20260206", "type": "fest", "url": "https://store.steampowered.com/developer/rogueduck/sale/TinyRoguelikes2026"},
    {"name": "打字节 (焦点节)", "start": "20260205", "end": "20260209", "type": "spotlight", "url": "https://store.steampowered.com/category/typing"},
    {"name": "PvP 游戏节", "start": "20260209", "end": "20260216", "type": "fest", "url": "https://store.steampowered.com/category/pvp"},
    {"name": "Steam 新品节 (2月版)", "start": "20260223", "end": "20260302", "type": "nextfest", "url": "https://store.steampowered.com/sale/nextfest"},
]

def generate_timeline_html():
    now = datetime.datetime.now()
    curr_int = int(now.strftime("%Y%m%d"))
    # 补全：显示所有未过期的官方活动
    upcoming = [e for e in sorted(STEAM_EVENTS_2026, key=lambda x: x['start']) if int(e['end']) >= curr_int]
    
    html = '<div class="flex flex-nowrap gap-4 overflow-x-auto pb-6 mb-10 no-scrollbar select-none">'
    for e in upcoming:
        active = int(e['start']) <= curr_int <= int(e['end'])
        color = "emerald-500" if active else "blue-600"
        html += f'''
        <div class="flex-shrink-0 w-64 p-6 rounded-3xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-white/5 shadow-sm">
            <div class="flex justify-between items-center mb-4">
                <span class="text-[10px] font-black {'text-emerald-500 animate-pulse' if active else 'text-slate-400'} uppercase">{'● ACTIVE' if active else '○ PENDING'}</span>
                <span class="text-[10px] font-mono text-slate-400">{e['start'][4:6]}/{e['start'][6:]}</span>
            </div>
            <div class="text-base font-bold truncate mb-4 dark:text-white">{e['name']}</div>
            <div class="h-1.5 w-full bg-slate-100 dark:bg-white/5 rounded-full overflow-hidden">
                <div class="h-full bg-{color}" style="width: {'100%' if active else '20%'}"></div>
            </div>
        </div>'''
    return html + '</div>'

def generate_active_ticker():
    now = datetime.datetime.now()
    curr_int = int(now.strftime("%Y%m%d"))
    contents = []
    # 逻辑：必须是已开展的活动
    for e in STEAM_EVENTS_2026:
        if int(e['start']) <= curr_int <= int(e['end']):
            url = e.get('url', '#')
            contents.append(f"<span>🔥 正在开展: {e['name']}</span> | <a href='{url}' target='_blank' class='text-yellow-400 font-bold hover:underline px-2 relative z-[9999]'>[进入会场]</a>")
    if not contents: return ""
    ticker_text = " ——— ".join(contents)
    return f'''
    <div id="ticker-bar" class="fixed bottom-0 left-0 w-full bg-blue-900 text-white py-4 z-[9000] overflow-hidden whitespace-nowrap border-t border-white/20 shadow-2xl">
        <div class="inline-block animate-marquee px-4">
            <span class="font-bold italic text-sm uppercase">{ticker_text} ——— {ticker_text}</span>
        </div>
    </div>'''

def get_news_content(mode, exclude_links):
    """
    核心抓取函数：
    mode='featured' -> 游戏节优先 + 日期倒序
    mode='official' -> 纯日期倒序 + 必须保底10条
    """
    url = "https://store.steampowered.com/feeds/news/collection/steam/?l=schinese" if mode == "official" else "https://store.steampowered.com/feeds/news/collection/featured/?l=schinese"
    
    try:
        # 增加抓取量以备筛选
        feed = feedparser.parse(f"{url}&v={random.random()}")
        all_entries = feed.entries
    except: return ""

    # 排序算法
    def get_sort_score(e):
        pub_time = time.mktime(e.get('published_parsed', time.gmtime(0)))
        if mode == "featured":
            is_fest = any(k in e.title.lower() for k in ["游戏节", "festival", "fest", "roguelike", "sale"])
            # 权重：游戏节赋予一个超大的基数，确保凌驾于所有日期之上
            priority = 1 if is_fest else 0
            return (priority, pub_time)
        else:
            # 官方板块仅按时间排
            return (0, pub_time)

    # 执行排序：先按优先级排，再按时间排
    all_entries.sort(key=get_sort_score, reverse=True)

    final_list = []
    for e in all_entries:
        if e.link not in exclude_links:
            final_list.append(e)
            exclude_links.add(e.link)
        if len(final_list) >= 10: break

    # 如果官方公告依然不足10条（极端情况），回填一些哪怕重复的
    if mode == "official" and len(final_list) < 10:
        for e in all_entries:
            if e not in final_list:
                final_list.append(e)
            if len(final_list) >= 10: break

    html_slides = ""
    for e in final_list:
        content = e.get('summary', '') or e.get('description', '')
        img = re.search(r'<img [^>]*src="([^"]+)"', content)
        img_url = img.group(1) if img else "https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/3985950/capsule_617x353.jpg"
        is_fest = any(k in e.title.lower() for k in ["游戏节", "festival", "fest", "roguelike"])
        glow = "ring-4 ring-emerald-500 shadow-[0_0_30px_rgba(16,185,129,0.5)]" if (is_fest and mode == "featured") else ""
        
        html_slides += f'''
        <div class="swiper-slide cursor-pointer" onclick="window.open('{e.link}', '_blank')">
            <div class="relative h-[440px] w-full overflow-hidden rounded-[2.5rem] bg-[#1a1f26] border border-white/5 transition-all {glow}">
                <img src="{img_url}" class="absolute inset-0 w-full h-full object-cover opacity-80 transition-transform duration-1000 group-hover:scale-110">
                <div class="absolute inset-0 bg-gradient-to-t from-black via-transparent to-transparent"></div>
                <div class="absolute bottom-0 p-8 w-full text-white">
                    <div class="flex items-center gap-3 mb-3">
                        { "<span class='bg-emerald-500 text-white text-[9px] px-2 py-1 rounded italic font-black animate-pulse'>FESTIVAL</span>" if is_fest else "" }
                        <span class="font-mono text-[10px] text-blue-400 font-bold tracking-widest uppercase">{time.strftime("%m-%d %H:%M", e.published_parsed)}</span>
                    </div>
                    <h2 class="text-2xl font-black line-clamp-2 italic leading-tight uppercase">{e.title}</h2>
                </div>
            </div>
        </div>'''
    return html_slides

# ==========================================
# 静态 HTML 模板逻辑 (集成记忆主题脚本)
# ==========================================
RAW_TEMPLATE = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>STEAM INTEL CENTER</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.css" />
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        // 【核心修复：主题记忆】在页面渲染前执行，绝不默认黑色
        (function() {
            const savedTheme = localStorage.getItem('steam_theme') || 'light';
            if (savedTheme === 'dark') {
                document.documentElement.classList.add('dark');
            } else {
                document.documentElement.classList.remove('dark');
            }
        })();

        tailwind.config = {
            darkMode: 'class',
            theme: { extend: { animation: { 'marquee': 'marquee 40s linear infinite' }, keyframes: { marquee: { '0%': { transform: 'translateX(0%)' }, '100%': { transform: 'translateX(-50%)' } } } } }
        }

        function toggleTheme() {
            const isDark = document.documentElement.classList.toggle('dark');
            localStorage.setItem('steam_theme', isDark ? 'dark' : 'light');
        }
    </script>
    <style>
        .no-scrollbar::-webkit-scrollbar { display: none; }
        .swiper { width: 100%; height: 540px; padding: 20px 0 100px 0; overflow: visible !important; }
        .swiper-slide { width: 580px; opacity: 0.15; transition: 0.8s; transform: scale(0.8); filter: blur(4px); }
        .swiper-slide-active { opacity: 1; transform: scale(1); filter: blur(0); z-index: 20; }
        #ticker-bar a { pointer-events: auto !important; position: relative; z-index: 10001; }
    </style>
</head>
<body class="bg-slate-50 dark:bg-[#0b0e14] text-slate-900 dark:text-slate-100 p-6 md:p-16 min-h-screen pb-40 transition-colors duration-500">
    <div class="max-w-[1500px] mx-auto">
        <header class="flex flex-col md:flex-row justify-between items-center mb-16 gap-8">
            <div class="text-center md:text-left">
                <h1 class="text-7xl font-black italic tracking-tighter uppercase leading-none">Steam<span class="text-blue-600">Intel</span></h1>
                <p class="text-[11px] text-blue-600 font-mono mt-4 tracking-[0.5em] uppercase font-bold opacity-80">Sector Monitoring // @@TIME@@</p>
            </div>
            <button onclick="toggleTheme()" class="px-8 py-4 bg-white dark:bg-slate-800 rounded-2xl shadow-xl border border-slate-200 dark:border-white/10 font-bold text-xs hover:scale-105 transition-all">SWITCH COLOR THEME</button>
        </header>

        <section class="mb-24">
            <div class="flex items-center gap-4 mb-10">
                <span class="px-4 py-1 bg-blue-600 text-white text-[10px] font-black rounded-full uppercase italic">Official Roadmap</span>
                <div class="h-px flex-1 bg-slate-200 dark:bg-white/10"></div>
            </div>
            @@TIMELINE@@
        </section>

        <main class="space-y-40">
            <section>
                <h2 class="text-5xl font-black italic uppercase mb-10 tracking-tighter italic">Featured <span class="text-blue-600">精选资讯</span></h2>
                <div class="swiper mySwiper"><div class="swiper-wrapper">@@FEAT@@</div><div class="swiper-pagination"></div></div>
            </section>
            
            <section class="py-20 px-8 md:px-12 rounded-[4rem] border border-slate-200 dark:border-white/5 bg-slate-100/50 dark:bg-white/5 shadow-inner">
                <h2 class="text-5xl font-black italic uppercase mb-10 tracking-tighter text-blue-600 italic">Official <span class="dark:text-white">官方公告</span></h2>
                <div class="swiper mySwiper"><div class="swiper-wrapper">@@OFFI@@</div><div class="swiper-pagination"></div></div>
            </section>
        </main>
    </div>
    @@TICKER@@
    <script src="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.js"></script>
    <script>
        document.querySelectorAll('.mySwiper').forEach(el => {
            new Swiper(el, {
                effect: "coverflow", centeredSlides: true, slidesPerView: "auto", loop: true,
                autoplay: { delay: 6000, disableOnInteraction: false },
                coverflowEffect: { rotate: 0, stretch: 80, depth: 150, modifier: 1.2, slideShadows: false },
                pagination: { el: el.querySelector('.swiper-pagination'), clickable: true }
            });
        });
    </script>
</body>
</html>'''

def update_web():
    now_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    exclude = set()
    # 逻辑修改：严格按照 Featured -> Official 顺序抓取并去重
    feat_content = get_news_content("featured", exclude)
    offi_content = get_news_content("official", exclude)
    timeline_content = generate_timeline_html()
    ticker_content = generate_active_ticker()

    output = RAW_TEMPLATE.replace("@@TIME@@", now_time).replace("@@TIMELINE@@", timeline_content).replace("@@FEAT@@", feat_content).replace("@@OFFI@@", offi_content).replace("@@TICKER@@", ticker_content)

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(output)

if __name__ == "__main__":
    update_web()
    print("Build Complete: Hard 10-item limit and Multi-level sort active.")
