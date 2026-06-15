import json
import random
import re
import time
from pathlib import Path

from playwright.sync_api import sync_playwright
empty_count=0
# ============================================
# 配置
# ============================================

QQ = ""
#Fill your QQ number here
COOKIE_FILE = "qzone_login.json"

OUTPUT_FILE = "qzone_v6_backup.json"

CHECKPOINT_FILE = "checkpoint.json"

# ============================================
# GTK
# ============================================

def getGTK(skey):

    hashes = 5381

    for c in skey:

        hashes += (hashes << 5) + ord(c)

    return hashes & 0x7fffffff


# ============================================
# 清理文本
# ============================================

def clean_text(text):

    if not text:
        return ""

    text = (
        text
        .replace("\n", " ")
        .replace("\r", " ")
        .replace("\t", " ")
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ============================================
# 保存
# ============================================

def save_data(data):

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2
        )


def save_checkpoint(pos, last_ts):

    checkpoint = {
        "pos": pos,
        "timestamp": last_ts
    }

    with open(
        CHECKPOINT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            checkpoint,
            f,
            ensure_ascii=False,
            indent=2
        )


# ============================================
# 真人行为模拟
# ============================================

def human_action(page, qq):

    action = random.choice([
        "scroll",
        "homepage",
        "album",
        "wait"
    ])

    try:

        # ====================================
        # 滚动
        # ====================================

        if action == "scroll":

            print("\n模拟滚动页面")

            page.mouse.wheel(
                0,
                random.randint(500, 2000)
            )

        # ====================================
        # 回主页
        # ====================================

        elif action == "homepage":

            print("\n返回空间主页")

            page.goto(
                f"https://user.qzone.qq.com/{qq}"
            )

        # ====================================
        # 打开相册
        # ====================================

        elif action == "album":

            print("\n随机查看相册")

            page.goto(
                f"https://user.qzone.qq.com/{qq}/311"
            )

        # ====================================
        # 发呆
        # ====================================

        else:

            print("\n随机发呆")

        # ====================================
        # 停留
        # ====================================

        stay = (
            10 +
            random.random() * 40
        )

        print(
            f"停留 {stay:.1f} 秒"
        )

        time.sleep(stay)

    except Exception as e:

        print(
            "真人行为失败:",
            e
        )


# ============================================
# 主程序
# ============================================

with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=False
    )

    # ========================================
    # context
    # ========================================

    if Path(COOKIE_FILE).exists():

        context = browser.new_context(
            storage_state=COOKIE_FILE
        )

    else:

        context = browser.new_context()

    page = context.new_page()

    page.goto(
        f"https://user.qzone.qq.com/{QQ}"
    )

    # ========================================
    # 登录
    # ========================================

    if not Path(COOKIE_FILE).exists():

        input("登录完成后按回车...")

        context.storage_state(
            path=COOKIE_FILE
        )

        print("Cookie已保存")

    else:

        print("已加载Cookie")

    # ========================================
    # GTK
    # ========================================

    cookies = context.cookies()

    cookie_dict = {}

    for c in cookies:

        cookie_dict[
            c["name"]
        ] = c["value"]

    GTK = getGTK(
        cookie_dict["p_skey"]
    )

    print("GTK =", GTK)

    input(
        "\n确认QQ空间主页已打开后按回车开始抓取..."
    )

    # ========================================
    # 加载历史数据
    # ========================================

    all_data = []

    seen = set()

    pos = 0

    last_ts = 0

    # ========================================
    # 限流计数
    # ========================================

    rate_limit_count = 0

    if Path(OUTPUT_FILE).exists():

        with open(
            OUTPUT_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            try:

                all_data = json.load(f)

                for item in all_data:

                    seen.add(
                        item["timestamp"]
                    )

                print(
                    f"已加载 {len(all_data)} 条历史数据"
                )

            except:

                all_data = []

    # ========================================
    # 断点
    # ========================================

    if Path(CHECKPOINT_FILE).exists():

        with open(
            CHECKPOINT_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            cp = json.load(f)

            pos = cp.get(
                "pos",
                0
            )

            last_ts = cp.get(
                "timestamp",
                0
            )

        print(
            f"已恢复断点 pos={pos}"
        )

    # ========================================
    # 开始抓取
    # ========================================

    while True:

        print(
            f"\n========== pos={pos} =========="
        )

        url = (
            "https://user.qzone.qq.com/proxy/domain/"
            "taotao.qq.com/cgi-bin/"
            "emotion_cgi_msglist_v6"
        )

        params = {
            "uin": QQ,
            "ftype": 0,
            "sort": 0,
            "pos": pos,
            "num": 20,
            "replynum": 20,
            "g_tk": GTK,
            "callback": "_preloadCallback",
            "code_version": 1,
            "format": "jsonp",
            "need_private_comment": 1,
        }

        # ====================================
        # 浏览器 fetch
        # ====================================

        result = page.evaluate(
            """
            async ({url, params}) => {

                const qs = new URLSearchParams(
                    params
                ).toString()

                const resp = await fetch(
                    `${url}?${qs}`,
                    {
                        credentials: "include"
                    }
                )

                return await resp.text()
            }
            """,
            {
                "url": url,
                "params": params
            }
        )

        # ====================================
        # JSONP
        # ====================================

        json_start = result.find("(")

        json_end = result.rfind(")")

        json_text = result[
            json_start + 1:
            json_end
        ]

        data = json.loads(json_text)

        code = data.get("code")

        message = data.get(
            "message",
            ""
        )

        print(
            f"code = {code} | message = {message}"
        )

        # ====================================
        # 错误处理
        # ====================================

        if code != 0:

            print("\n接口异常")

            print(
                f"code = {code}"
            )

            print(
                f"message = {message}"
            )

            # ====================================
            # 限流
            # ====================================

            if code in [-3000, -10000]:

                rate_limit_count += 1

                print(
                    f"\n触发限流 x{rate_limit_count}"
                )

                # ====================================
                # 指数退避
                # ====================================

                base = min(
                    1800,
                    240 * (1.8 ** rate_limit_count)
                )

                wait_time = (
                    base * (
                        0.7 +
                        random.random() * 0.6
                    )
                )

                print(
                    f"等待 {wait_time / 60:.1f} 分钟后重试..."
                )

                # ====================================
                # 模拟真人离开
                # ====================================

                try:

                    human_action(
                        page,
                        QQ
                    )

                except:
                    pass

                time.sleep(wait_time)

                continue

            # ====================================
            # 其它错误
            # ====================================

            else:

                break

        # ====================================
        # 成功后恢复
        # ====================================

        rate_limit_count = 0

        msglist = data.get(
            "msglist"
        )or[]

        print(
            f"本次获取 {len(msglist)} 条"
        )

        if not msglist:
            empty_count += 1

            print(f"空列表次数: {empty_count}")

            if empty_count >= 20:
                print(f"连续{empty_count}次空列表，停止抓取")
                break

            wait_time = random.uniform(20, 40)
            print(f"等待 {wait_time:.1f} 秒后重试...")
            time.sleep(wait_time)

            continue

            # 有数据就清零
        empty_count = 0

        new_count = 0

        # ====================================
        # 遍历动态
        # ====================================

        for item in msglist:

            ts = item.get(
                "created_time",
                0
            )

            # 已存在
            if ts in seen:

                continue

            seen.add(ts)

            last_ts = ts

            # =================================
            # 正文
            # =================================

            content = clean_text(
                item.get(
                    "content",
                    ""
                )
            )

            # =================================
            # 转发
            # =================================

            rt_con = item.get(
                "rt_con"
            )

            if rt_con:

                rt_content = clean_text(
                    rt_con.get(
                        "content",
                        ""
                    )
                )

                # 转评
                if content:

                    content = (
                        f"[转评] {content} "
                        f"[转自] {rt_content}"
                    )

                # 纯转发
                else:

                    content = (
                        f"[转自] {rt_content}"
                    )

            # =================================
            # 图片
            # =================================

            has_pic = bool(
                item.get("pic")
            )

            if has_pic:

                if content:

                    content += " [图片]"

                else:

                    content = "[图片]"

            # =================================
            # 视频
            # =================================

            has_video = bool(
                item.get("video")
            )

            if has_video:

                if content:

                    content += " [视频]"

                else:

                    content = "[视频]"

            # =================================
            # 评论
            # =================================

            comments = []

            for c in item.get(
                "commentlist",
                []
            ):

                # =============================
                # 一级评论
                # =============================

                name = clean_text(
                    c.get("nickname")
                    or c.get("name", "")
                )

                text = clean_text(
                    c.get("content", "")
                )

                if text:

                    comments.append(
                        f"{name}：{text}"
                    )

                # =============================
                # 楼中楼
                # =============================

                for sub in c.get(
                    "list_3",
                    []
                ):

                    sub_name = clean_text(
                        sub.get("nickname")
                        or sub.get("name", "")
                    )

                    sub_text = clean_text(
                        sub.get("content", "")
                    )

                    # =========================
                    # 提取被回复者
                    # =========================

                    reply_match = re.search(
                        r'nick:([^,}]+)',
                        sub_text
                    )

                    reply_to = ""

                    if reply_match:

                        reply_to = clean_text(
                            reply_match.group(1)
                        )

                        # 去掉 @{...}
                        sub_text = re.sub(
                            r'@\{.*?\}',
                            '',
                            sub_text
                        ).strip()

                    # =========================
                    # 输出
                    # =========================

                    if reply_to:

                        comments.append(
                            f"{sub_name} → {reply_to}：{sub_text}"
                        )

                    else:

                        comments.append(
                            f"{sub_name}：{sub_text}"
                        )

            # =================================
            # 时间
            # =================================

            dt = time.strftime(
                "%Y-%m-%d %H:%M:%S",
                time.localtime(ts)
            )

            # =================================
            # 保存结构
            # =================================

            feed = {
                "time": dt,
                "timestamp": ts,
                "name": item.get(
                    "nickname"
                ) or item.get(
                    "name",
                    ""
                ),
                "content": content,
                "comments": comments
            }

            all_data.append(feed)

            new_count += 1

            print(
                dt,
                content[:120]
            )

        # ====================================
        # 保存
        # ====================================

        save_data(all_data)

        save_checkpoint(
            pos,
            last_ts
        )

        print(
            f"新增 {new_count} 条"
        )

        print(
            f"当前总动态: {len(all_data)}"
        )

        # ====================================
        # 下一页
        # ====================================

        pos += len(msglist)

        # ====================================
        # 真人行为
        # ====================================

        if random.random() < 0.35:

            human_action(
                page,
                QQ
            )

        # ====================================
        # 随机长休息
        # ====================================

        if random.random() < 0.15:

            long_sleep = (
                180 +
                random.random() * 600
            )

            print(
                f"\n随机长休息 {long_sleep / 60:.1f} 分钟"
            )

            time.sleep(long_sleep)

        # ====================================
        # 普通等待
        # ====================================

        sleep_time = (
            20 +
            random.random() * 40
        )

        print(
            f"等待 {sleep_time:.1f} 秒..."
        )

        time.sleep(
            sleep_time
        )

    print("\n抓取完成")

    input(
        "\n按回车关闭浏览器..."
    )

    browser.close()