import feedparser
import datetime
import re

def update_web():
    feed = feedparser.parse("https://store.steampowered.com/feeds/news.xml")
    if not feed.entries: return

    news_html = '<div id="news-container" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">\n'
    
    for entry in feed.entries[:12]: # 增加到12条，3列布局更整齐
        # 简化时间显示
        raw_date = entry.published if 'published' in entry else "Recent"
        clean_date = raw_date[:16] 

        news_html += f"""
        <div class="glass-card p-8 rounded-2xl flex flex-col justify-between">
            <div>
                <div class="flex justify-between items-start mb-6">
                    <span class="text-[10px] px-2 py-1 bg-blue-500/20 text-blue-300 rounded-md font-bold uppercase tracking-widest">News</span>
                    <span class="text-slate-500 text-[10px] font-mono">{clean_date}</span>
                </div>
                <h2 class="text-xl font-bold leading-tight mb-4 text-white group-hover:text-blue-400">{entry.title}</h2>
            </div>
            <div class="mt-6">
                <a href="{entry.link}" target="_blank" class="inline-flex items-center text-sm font-bold text-blue-400 hover:text-blue-300 transition-colors">
                    READ REPORT
                    <svg class="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3"></path></svg>
                </a>
            </div>
        </div>
        """
    news_html += '\n        </div>'

    with open("index.html", "r", encoding="utf-8") as f:
        content = f.read()

    pattern = r".*?"
    replacement = f"\n        {news_html}\n        "
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    now_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    new_content = re.sub(r"更新时间：.*?</p>", f"更新时间：{now_time}</p>", new_content) # 兼容旧代码
    new_content = re.sub(r'id="update-time".*?</p>', f'id="update-time" class="text-xs uppercase tracking-[0.3em] text-blue-400 font-semibold">Last Intelligence Sync: {now_time}</p>', new_content)

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(new_content)

if __name__ == "__main__":
    update_web()
