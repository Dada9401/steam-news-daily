import feedparser
import datetime

def update_web():
    # 1. 抓取 Steam 新闻
    feed = feedparser.parse("https://store.steampowered.com/feeds/news.xml")
    if not feed.entries:
        print("未抓取到新闻")
        return

    # 2. 准备新闻幻灯片 HTML 片段
    slides_html = ""
    for entry in feed.entries[:10]:
        pub_date = entry.published[:16] if 'published' in entry else "LIVE"
        slides_html += f"""
        <div class="swiper-slide cursor-pointer" onclick="window.open('{entry.link}', '_blank')">
            <div class="flex flex-col h-full">
                <div class="mb-4">
                    <span class="bg-blue-600 text-[10px] px-2 py-1 rounded font-bold italic text-white tracking-widest">TOP NEWS</span>
                </div>
                <h2 class="text-3xl md:text-4xl font-black mb-8 leading-tight hover:text-blue-400 transition-colors">{entry.title}</h2>
                <div class="mt-auto pt-6 border-t border-white/10 flex justify-between items-center text-slate-500 font-mono text-sm">
                    <span>{pub_date}</span>
                    <span class="text-blue-400 font-bold tracking-widest uppercase">Click to view Details →</span>
                </div>
            </div>
        </div>
        """

    # 3. 直接定义一整个完整的 HTML 字符串
    now_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Steam News Monitor</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.css" />
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body {{ background-color: #0b0
