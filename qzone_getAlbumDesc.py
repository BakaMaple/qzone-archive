from playwright.sync_api import sync_playwright
import os
import json
import time
import random

SAVE_DIR = "qzone_data"
os.makedirs(SAVE_DIR, exist_ok=True)

backup_data = {}

# =========================
# 读取所有 JSON（兼容多相册）
# =========================
for file in os.listdir(SAVE_DIR):
    if file.endswith(".json"):
        path = os.path.join(SAVE_DIR, file)
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            album_name = file.replace(".json", "")

            if album_name not in backup_data:
                backup_data[album_name] = {}

            for date, entries in data.items():
                if date not in backup_data[album_name]:
                    backup_data[album_name][date] = {}
                backup_data[album_name][date].update(entries)

        except Exception as e:
            print(f"读取 {file} 失败:", e)


# =========================
# 状态变量
# =========================
last_new_count = 0
no_new_count = 0
global_count = 0
in_photo_page = False
started = False


# =========================
# JSONP解析
# =========================
def extract_jsonp(text):
    s = text.find("(")
    e = text.rfind(")")
    if s == -1 or e == -1:
        return None
    return text[s + 1:e]


# =========================
# 保存（多相册独立文件）
# =========================
def save_all():
    if not backup_data:
        return

    for album_name, album_data in backup_data.items():
        safe = album_name.replace("/", "_").replace("\\", "_").replace(":", "_")
        path = os.path.join(SAVE_DIR, f"{safe}.json")

        with open(path, "w", encoding="utf-8") as f:
            json.dump(album_data, f, ensure_ascii=False, indent=2)

        total = sum(len(v) for v in album_data.values())
        print(f"\n已保存: {safe}.json，总条目: {total}")


# =========================
# XHR监听
# =========================
def handle_response(response):
    global last_new_count, in_photo_page, started

    url = response.url

    if "cgi_floatview_photo_list_v2" in url:
        in_photo_page = True
        started = True

    if "cgi_floatview_photo_list_v2" not in url:
        return

    try:
        text = response.text()
        json_text = extract_jsonp(text)
        if not json_text:
            return

        data = json.loads(json_text)
        photos = data.get("data", {}).get("photos", [])

        new_count = 0

        for p in photos:
            album = p.get("topicName") or "未知相册"
            if album == "说说相册":
                continue

            t = p.get("uploadTime")
            if not t:
                continue

            date = t[:10]
            hm = t[11:16]
            desc = (p.get("desc") or "").strip() or "[无描述图片]"

            if album not in backup_data:
                backup_data[album] = {}
            if date not in backup_data[album]:
                backup_data[album][date] = {}

            if hm in backup_data[album][date] and backup_data[album][date][hm] == desc:
                continue

            backup_data[album][date][hm] = desc
            new_count += 1

            if desc == "[无描述图片]":
                print("🐾 无描述图片")

            print("\n------------------")
            print("相册:", album)
            print("日期:", date)
            print("时间:", hm)
            print("描述:", desc[:80])

        last_new_count = new_count

        if new_count > 0:
            save_all()

    except Exception as e:
        print("解析失败:", e)


# =========================
# 主程序
# =========================
with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    page.on("response", handle_response)

    print("打开QQ空间...")
    page.goto("https://user.qzone.qq.com", timeout=180000, wait_until="load")

    print("\n👉 手动登录 → 进入相册 → 打开第一张图")

    print("\n等待进入照片页...")
    while not started:
        page.keyboard.press("ArrowRight")
        time.sleep(1.5)

    print("✅ 已进入照片页，开始抓取")

    NO_NEW_LIMIT = 100
    MAX_GLOBAL = 5000

    count = 0

    try:
        while True:
            page.keyboard.press("ArrowRight")
            count += 1
            global_count += 1

            print(f"\r自动下一张 ({count})", end="", flush=True)

            time.sleep(random.uniform(0.8, 2.4))

            if not started:
                continue

            if last_new_count == 0:
                no_new_count += 1
            else:
                no_new_count = 0

            if no_new_count >= NO_NEW_LIMIT:
                print("\n🛑 连续无新数据，停止")
                break

            if global_count >= MAX_GLOBAL:
                print("\n🛑 达到上限")
                break

    except KeyboardInterrupt:
        print("\n手动退出")

    finally:
        save_all()
        try:
            browser.close()
        except:
            pass
