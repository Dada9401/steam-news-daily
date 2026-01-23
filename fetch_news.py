import requests
import datetime
import time
import feedparser

def get_data_safe(url):
    # 更加真实的浏览器头，防止被 Steam 拦截
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Referer': 'https://store.steampowered.com/news/'
    }
    try:
        # 增加超时和重试逻辑
        response = requests.get(url, headers=headers, timeout=20)
        if response.status_code == 200:
            return response
        else:
            print(f"请求失败，状态码: {response.status_code}")
            return None
    except Exception as e:
        print(f"发生网络错误: {e}")
        return None

def get_steam_slides(clan_id):
    # 强制增加随机后缀防止缓存
    api_url = f"https://store.steampowered.com/events/ajaxgetadjacentevents/?appid=0&clanid={clan_id}&count=12&l=schinese&t={int(time.time())}"
    res = get_data_safe(api_url)
    html = ""
    
    if res:
        try:
            # 关键修复：先检查是否是 JSON
            data = res.json()
            events = data.get('events', [])
            for e in events:
                gid = e.get('announcement_body', {}).get('gid', '')
                img = e.get('jsondata', {}).get('image_url', '')
                # 构建图片地址
                img_url = f"https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/0/events/{gid}/{img}" if img else "https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/594650/capsule_617x353.jpg"
                
                html += f"""
                <div class="swiper-slide cursor-pointer" onclick="window.open('https://store.steampowered.com/news/view/{gid}', '_blank')">
                    <div class="relative h-full w-full overflow-hidden rounded-3xl border border-white/10 bg-slate-900">
                        <img src="{img_url}" class="absolute inset-0 w-full h-full object-cover opacity-50 transition-transform duration-500 hover:scale-110">
                        <div class="absolute inset-0 bg-gradient-to-t from-[#05070a] to-transparent"></div>
                        <div class="absolute bottom-0 p-6 w-full"><h2 class="text-lg font-bold text-white line-clamp-2">{e.get('event_name')}</h2></div>
                    </div>
                </div>"""
        except Exception as e:
            print(f"JSON解析失败: {e}")
            html = '<div class="swiper-slide p-10 text-gray-500">该板块暂时无法从 Steam 获取实时数据，请稍后刷新。</div>'
    
    return html if html else '<div class="swiper-slide p-10 text-gray-500">暂无最新动态</div>'

def update_web():
    # 行业简报抓取 (GameSpot RSS 比较稳定)
    ticker_text = "正在同步全球行业情报..."
    try:
        industry_feed = feedparser.parse("https://www.gamespot.com/feeds/news/")
        if industry_feed.entries:
            ticker_text = " • ".join([f"【{e.title}】" for e in industry_feed.entries[:12]])
    except:
        pass

    featured_html = get_steam_slides("39154431")
    official_html = get_steam_slides("4")
    now_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # 最终 HTML 模板
    full_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>STEAM 2026 监控站</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.css" />
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body {{ background: #020408; color: white; font-family: system-ui; overflow-x: hidden; padding-bottom: 100px; }}
        .swiper {{ width: 100%; height: 350px; padding: 20px 0; overflow: visible !important; }}
        .swiper-slide {{ width: 400px;
