# QZone Archive

在 QQ 空间彻底成为时代眼泪之前，把属于自己的互联网记忆保存下来。

 作者已成功备份了2011年以来的超过一万条说说和相册描述
## 功能

* 备份 QQ 空间说说
* 备份相册描述
* 支持断点续传
* 支持增量更新
* JSON 格式导出

## 环境要求

* Python 3.10+
* Playwright

安装依赖：

```bash
pip install playwright
playwright install
```


## 使用方法

### 备份说说

编辑 `qzone_getPost.py`：

```python
QQ = "你的QQ号"
```

运行：

```bash
python qzone_getPost.py
```

首次运行需要登录 QQ 空间，登录成功后会自动保存 Cookie。

程序会自动：

* 分页抓取说说
* 保存评论
* 保存转发内容
* 保存断点
* 导出 JSON


## 爬取结果示例
qzone_getPost.py
爬取转发原文、转评、评论区、时间戳

  {
    "time": "2021-07-08 21:34:50",
    "timestamp": 1625751290,
    "name": "Kaede",
    "content": "[转评] 我现在所在的陆行鸟大区红玉海服务器已经解除角色创建限制，列表有没有人来一起玩[em]e400932[/em] [转自] 可恶，为什么列表没人来玩ff14 来打副本，钓鱼，弹琴(听别人也行），逛rp店（role play角色扮演，中/重rp语擦，轻rp类似女仆咖啡厅） 当暖暖玩也好玩啊（） 还能结婚.jpg 总之来玩，哦摩西罗伊 [图片]",
    "comments": [
      "AsahiPrPr：明天",
      "Kaede → AsahiPrPr：差不多"
    ]
  }

qzone_getAlbumDesc.py
爬取相册描述

  "2026-05-26": {
    "18:53": "我还以为是个垃圾袋，差点踩上去，怎么是只猫"
  },
  "2026-05-25": {
    "21:48": "咖啡因",
    "16:48": "阿紫一。。。",
    "16:10": "舍友说晚上我的键盘吵，那换个新的\n闷了很多不扰民了\n旧的拿回家给老电脑用"
  }


  
输出文件：

```text
qzone_v6_backup.json
相册描述则将按相册分类各自保存为独立的 相册名.json 文件 

---

### 备份相册描述

运行：

```bash
python qzone_getAlbumDesc.py
```

然后：

1. 登录 QQ 空间
2. 打开相册
3. 打开任意一张照片

脚本会自动翻阅照片并保存描述。

输出目录：

```text
qzone_data/
├── 相册A.json
├── 相册B.json
└── ...
```

## 注意事项

* QQ 空间接口可能随时发生变化。
* 本项目仅用于个人数据备份与归档。
* Cookie 仅保存在本地，不会上传到任何服务器。
* 请勿用于未经授权的数据抓取。


---

# English

Archive your QQ Zone memories before they disappear forever.

Successfully archived over 10,000 posts from a QQ Zone account dating back to 2011.

## Features

* Backup QQ Zone posts
* Backup album descriptions
* Incremental updates
* Resume from checkpoints
* JSON export

## Requirements

* Python 3.10+
* Playwright

Install dependencies:

```bash
pip install playwright
playwright install
```

## Usage

### Backup Posts

Edit `qzone_getPost.py`:

```python
QQ = "Your QQ Number"
```

Run:

```bash
python qzone_getPost.py
```

The script will:

* Save login cookies locally
* Fetch posts page by page
* Save reposts and comments
* Resume from checkpoints
* Export all data as JSON


## Example Output

qzone_getPost.py
Reposted original text, repost comments, comment section, and timestamps

  {
    "time": "2021-07-08 21:34:50",
    "timestamp": 1625751290,
    "name": "Kaede",
    "content": "[转评] 我现在所在的陆行鸟大区红玉海服务器已经解除角色创建限制，列表有没有人来一起玩[em]e400932[/em] [转自] 可恶，为什么列表没人来玩ff14 来打副本，钓鱼，弹琴(听别人也行），逛rp店（role play角色扮演，中/重rp语擦，轻rp类似女仆咖啡厅） 当暖暖玩也好玩啊（） 还能结婚.jpg 总之来玩，哦摩西罗伊 [图片]",
    "comments": [
      "AsahiPrPr：明天傻屌",
      "Kaede → AsahiPrPr：差不多"
    ]
  }

qzone_getAlbumDesc.py
Album descriptions


  "2026-05-26": {
    "18:53": "我还以为是个垃圾袋，差点踩上去，怎么是只猫"
  },
  "2026-05-25": {
    "21:48": "咖啡因",
    "16:48": "阿紫一。。。",
    "16:10": "舍友说晚上我的键盘吵，那换个新的\n闷了很多不扰民了\n旧的拿回家给老电脑用"
  }

  
Output:

```text
qzone_v6_backup.json
```
Album descriptions are exported as individual JSON files grouped by album.

---

### Backup Album Descriptions

Run:

```bash
python qzone_getAlbumDesc.py
```

Then:

1. Log in to QQ Zone
2. Open Albums
3. Open the first photo

The script will automatically browse photos and save descriptions.

Output:

```text
qzone_data/
├── AlbumA.json
├── AlbumB.json
└── ...
```

## Notes

* QQ Zone APIs may change at any time.
* This project is intended for personal data backup and archival purposes only.
* Cookies are stored locally and are never uploaded anywhere.
* Please do not use this project for unauthorized data collection.

## License

MIT
