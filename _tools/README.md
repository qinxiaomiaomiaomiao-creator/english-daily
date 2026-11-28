# 英语日课 · GitHub Pages 发布流程

线上地址（main 分支根目录，GitHub Pages 自动发布，推送后 1–2 分钟生效）：

- 秦心远：https://qinxiaomiaomiaomiao-creator.github.io/english-daily/xinyuan/
- 秦悠然：https://qinxiaomiaomiaomiao-creator.github.io/english-daily/youran/
- 选择页：https://qinxiaomiaomiaomiao-creator.github.io/english-daily/

## 规则（家长的要求）

「心远和悠然的英语日课」网页版只要有文件改动，就同时提交到这个仓库，
不用另外询问。两份页面始终从同一个最新的合并网页版生成，不要手工分别修改
`xinyuan/` 或 `youran/` 里的页面。

## 每次改完后的步骤

1. 连接仓库（每个会话第一次时）：
   `add_repo(owner="qinxiaomiaomiaomiao-creator", repo="english-daily", access="push")`，
   然后按返回的提示 clone（仓库约 40 MB，大部分是音频）。
2. 准备好最新的合并网页版文件夹 `SRC_DIR`（就是发布为 claude.ai 网页
   「心远和悠然的英语日课」的那个文件夹）：`index.html`（外壳：今日、抄写默写）、
   `lb.html`（听力营，外壳用 iframe 加载）、`assets/`（带哈希文件名的大文件：
   动画引擎 stage.*.js、听力营数据 lbdata.*.js、字体）和 `audio/*.mp3`。
3. 生成两份页面：
   ```bash
   python3 _tools/build.py SRC_DIR .
   ```
   脚本会改写 `xinyuan/`（index.html、lb.html）、`youran/`、`audio/`、`assets/`、
   `index.html`，其余不动。
   如果报 `expected exactly one ...`，说明源页面里被替换的那段代码变了：
   改 `_tools/build.py` 里对应的匹配串，不要跳过。
4. 检查（至少做到）：本地起一个 `python3 -m http.server`，按
   `/english-daily/xinyuan/` 的目录结构访问，两个页面都能显示名字和今日页，
   一个孩子页面写入的进度另一个看不到，`../audio/*.mp3`、`../assets/*` 返回 200。
5. 提交并推送：
   ```bash
   git add -A && git commit -m "<改了什么>" && git -c push.negotiate=true push origin main
   ```
6. 1–2 分钟后用 curl 确认三个线上地址返回 200，再告诉家长。

## 不能改的约定

- **进度按孩子分开**：两份页面在同一个域名下，所以 `build.py` 给所有
  localStorage 键加了 `xinyuan/`、`youran/` 前缀。源页面新增的存储只要走
  `localStorage.getItem/setItem/removeItem`，会自动带前缀；不要改用
  `localStorage[key]` 这种写法，否则两个孩子的进度会混在一起。
- **存储键名不要随意改**（如 `phonics_v1`、`lbcamp_v1`、`dx_v1`）：改了孩子
  的线上进度就会清零。确实要改时，在页面里写好从旧键迁移的代码。
- **地址不变**：不要改仓库名或 `xinyuan/`、`youran/` 目录名，孩子 iPad 主屏幕
  上的图标指向这些地址。
- 单个文件不超过 100 MB（GitHub 上限），音频保持放在 `audio/` 里单独的 mp3 文件。
- **不要再把子页面或大数据 base64 塞进一个 HTML**：那样每次打开都要整份下载、
  解码、解析，iPad 上打开很慢。大文件放 `assets/`，文件名带内容哈希，内容变了
  文件名就变，浏览器可以放心缓存。
- 自然拼读模块已去掉（2026-11-28），但 `phonics_v1` 记录保留在孩子 iPad 上，
  备份码里也带着；`audio/a8_*.mp3` 仍被抄写默写用来读单词，不要删。
