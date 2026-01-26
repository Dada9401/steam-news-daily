import feedparser
import datetime
import re

# --- 2026 Steam 官方年度活动数据库（严格对齐官方链接） ---
STEAM_EVENTS_2026 = [
    {"name": "棋盘游戏节", "start": "20260126", "end": "20260202", "type": "fest"},
    {"name": "打字节", "start": "20260205", "end": "20260209", "type": "spotlight"},
    {"name": "PvP 游戏节", "start": "20260209", "end": "20260216", "type": "fest"},
    {"name": "Steam 新品节 (2月版)", "start": "20260223", "end": "20260302", "type": "nextfest", "appid": "3985950"},
    {"name": "Steam 春季特卖", "start": "20260319", "end": "20260326", "type": "major"},
    # ... 其他活动保持一致
]

def get_steam_rss_data(url_type):
    # --- 核心升级：构建全维度新闻矩阵 ---
    sources = []
    
    if url_type == "featured":
        # 精选板块：抓取商店精选 + 所有活动聚合
        sources.append("https://store.steampowered.com/feeds/news/collection/featured/?l=schinese")
        sources.append("https://store.steampowered.com/feeds/news/collection/all/?l=schinese")
    else:
        # 官方博文板块：抓取官方社区组 + 针对新品节的专项扫描
        sources.append("https://steamcommunity.com/groups/steam/rss/?l=schinese")
        # 针对 2 月新品节的 AppID (3985950) 进行定向补盲抓取
        sources.append("https://store.steampowered.com/feeds/news/app/3985950/?l=schinese")
        # 备用：Steamworks 开发者公告（很多新品节通知发在这里）
        sources.append("https://store.steampowered.com/feeds/news/app/594650/?l=schinese")

    all_entries = []
    seen_links = set()

    for url in sources:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                if entry.link not in seen_links:
                    all_entries.append(entry)
                    seen_links.add(entry.link)
        except: continue

    # --- 增强版置顶逻辑 ---
    # 定义高价值关键词，哪怕发布时间较早，只要包含这些也会被置顶
    must_show_keywords = ["新品节", "Next Fest", "官方公告", "2026"]
    
    def get_rank_score(entry):
        score = 0
        title = entry.title
        # 如果是新品节公告，给予最高权重
        if any(kw in title for kw in ["新品节", "Next Fest"]):
            score += 2000 
        # 如果是路线图或大促预告，给予次高权重
        if any(kw in title for kw in ["路线图", "特卖", "新鮮出爐"]):
            score += 1000
        # 时间权重：越新的分数越高
        if hasattr(entry, 'published_parsed'):
            score += int(entry.published_parsed[0] * 100 + entry.published_parsed[1])
        return score

    all_entries.sort(key=get_rank_score, reverse=True)

    slides_html = ""
    for entry in all_entries[:12]:
        title, link = entry.title, entry.link
        content = entry.get('summary', '') or entry.get('description', '')
        # 尝试提取高质量图片，如果提取不到则使用新品节占位图
        img_match = re.search(r'<img [^>]*src="([^"]+)"', content)
        img_url = img_match.group(1) if img_match else "https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/3985950/capsule_617x353.jpg"
        
        # 样式标签
        is_nextfest = any(kw in title for kw in ["新品节", "Next Fest"])
        tag = ""
        if is_nextfest:
            tag = '<span class="bg-yellow-400 text-black text-[10px] px-2 py-1 rounded-sm font-black mr-2">OFFICIAL ALERT</span>'
        
        slides_html += f'''
        <div class="swiper-slide cursor-pointer" onclick="window.open('{link}', '_blank')">
            <div class="relative h-full w-full overflow-hidden rounded-[1.5rem] bg-slate-900 border {"border-yellow-400/40 shadow-[0_0_20px_rgba(250,204,21,0.2)]" if is_nextfest else "border-white/5"} group">
                <img src="{img_url}" class="absolute inset-0 w-full h-full object-cover opacity-50 transition-transform duration-1000 group-hover:scale-105">
                <div class="absolute inset-0 bg-gradient-to-t from-black via-transparent to-transparent"></div>
                <div class="absolute bottom-0 p-8 w-full">
                    <h2 class="text-xl font-black text-white leading-tight tracking-tight">{tag}{title}</h2>
                </div>
            </div>
        </div>'''
    return slides_html
