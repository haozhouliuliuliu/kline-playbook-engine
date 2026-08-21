# Bilibili 交易员视频语料获取 V0.1

> 状态：CANDIDATE（真实枚举、最高画质验证、下载及恢复验证完成前不得标为 VERIFIED）

## 固定范围与安全边界

- UP URL：`https://space.bilibili.com/3546770449631285/video`
- UID：`3546770449631285`
- 输出目录：`%USERPROFILE%\Videos\kline-playbook-engine\bilibili\3546770449631285\`
- `Chrome bridge = REJECTED_FOR_THIS_ENVIRONMENT`；不会再读取 Chrome Profile 或 Cookie。
- 登录改为 Bilibili 网页二维码流程；二维码登录产生的 Bilibili 域 Cookie 仅在仓库外、临时 Netscape 文件中保存，供当前 yt-dlp 步骤读取后删除。
- 不打印、不记录、不提交 Cookie、SESSDATA、refresh token、Token 或浏览器配置；日志会对疑似敏感键值脱敏。
- 视频、字幕与元数据均在仓库外；仓库仅保存程序、测试和本证据记录。

## 实现语义

- 主枚举路径：yt-dlp 的 `BilibiliSpaceVideo`；按 BVID 去重并以报告总数交叉验证。未知总数或数量不相等即 `ENUMERATION_COMPLETE=NO`，失败闭合。
- 画质（Owner 批准修正）：`QUALITY_POLICY=SOURCE_BEST_PLUS_VISUAL_ADEQUACY`。下载认证会话实际返回的最高视频流与最佳音频流；1080p 为可接受基线。`support_formats` 中高于实际 DASH 的标签不单独证明存在相应源流，也不得造成假 FAIL；只有实际 DASH 返回更高流而程序错误选择较低流才 FAIL。
- 下载（待真实验证后启用）：最佳视频流 + 最佳音频流，ffmpeg 仅 mux/remux，不重编码；保留 info JSON、原生字幕、ffprobe 和 SHA256 证据，并以下载档案实现可恢复、不重复。
- 磁盘：估计总量超过可用空间 70% 时为 `DISK_CAPACITY_BLOCKED`，不开始全量下载。
- 媒体接口发生 412 后，第一次重试至少等待 10 分钟，之后指数退避并限制为单请求；二维码轮询保持约 3 秒一次。

## 当前实际运行结果

```text
YTDLP_VERSION=2026.08.19
FFMPEG_VERSION=9.0.1
COOKIE_MODE=QR_LOGIN_RUNTIME_ONLY_TEMPORARY_BILIBILI_DOMAIN_COOKIES_DELETED_AFTER_PILOT
ENUMERATION_METHOD=Bilibili:WBI_SPACE_API
UPLOADER_REPORTED_TOTAL=99
ENUMERATED_UNIQUE_BVIDS=99
ENUMERATION_COMPLETE=YES
QR_LOGIN=PASS
ACCOUNT_LOGIN_VERIFIED=YES
PILOT_BVID=BV1yxebzoERD
HIGHEST_SUPPORTED_RESOLUTION=8K_LABEL_NOT_SOURCE_PROOF
HIGHEST_DOWNLOADABLE_RESOLUTION=1080x1920
ACTUAL_BEST_RESOLUTION=1080x1920/30fps/AV1
QUALITY_VERIFICATION=PASS
PILOT_RESULT=PASS_FFPROBE_SHA256_AND_10_ORIGINAL_RESOLUTION_PNGS
FALLBACK_USED=YES_WBI_SPACE_API
CHROME_BRIDGE=REJECTED_FOR_THIS_ENVIRONMENT
CHROME_DPAPI_EXTRACTION=FAILED
QR_LOGIN_ROUTE=VERIFIED_FOR_PILOT
YTDLP=VERIFIED_FOR_PILOT
HTTP_412_STATUS=SEEN_BEFORE_QR_LOGIN;NOT_SEEN_ON_AUTHENTICATED_YTDLP_PILOT_DOWNLOAD
BILI23_DOWNLOADER=CANDIDATE_SOURCE_REVIEWED_ONLY
BILI23_REVIEW_PIN=v2.11.0/52977543839b8c6cbab473cd25d6b0d673649aff
PROJECT_BILIBILI_ACQUISITION_STATUS=CANDIDATE
```

## 已知限制

此版本绝不会把“当前页面没有更多项目”当作完整性证明。若 yt-dlp 遇到 352、412、登录、WBI 或分页不一致，运行必须停在失败闭合状态；在写入 VERIFIED 前需要补齐同一登录态下的 WBI Space API 差集审计与最高质量 DASH 验证。

2026-08-21 的真实运行已确认：Chrome 关闭后，`yt-dlp --cookies-from-browser chrome:Default`
仍被 Windows DPAPI/Chrome 应用绑定加密拒绝；Chrome bridge 也无法在该运行环境接管页面，故此路线正式停止。
无 Cookie 的 BilibiliSpaceVideo 请求则收到 HTTP 412。
WBI Space API 备用路径完整枚举到 99 个唯一 BVID，报告总数也是 99，且无重复。
Owner 于 2026-08-21 明确批准画质验收语义修正：不再把 `support_formats` 的 8K 标签与实际 DASH 最高 1080 流的差异判为失败；改为以认证会话实际可取得的最高媒体流为准，并在 pilot 下载后以 ffprobe 与原分辨率机械帧抽取确认完整性。

二维码登录路径已真实通过：二维码轮询的 `data.code=0` 后，`nav.isLogin=true`。
认证后的 yt-dlp 元数据请求可取得 1080x1920/30fps AVC 视频流；同一会话的项目最小 WBI playurl
验证显示 `support_formats` 的最高画质为 8K（quality 127），而实际 DASH 最高为 quality 80、1080x1920、
30fps、AVC，音频为 AAC。该历史记录在新 Owner 规则下不再是失败；需重新取得临时会话并执行 pilot 下载验收。

重新验证后的 pilot 实际下载为认证会话实际选择的 1080x1920/30fps AV1 + AAC，ffmpeg 仅完成无损 MP4 mux；ffprobe 成功，文件 SHA256 已记录，并从完整原始帧机械抽取 10 个不同时间点的 1080x1920 PNG。未对帧内交易含义作任何分析。基于 99 项 manifest 总时长和保守 10 Mbps 估计，完整语料约 75.85 GiB，而目标盘可用空间约 18.14 GiB，超过 70% 安全阈值，故全量下载状态为 `DISK_CAPACITY_BLOCKED`。

针对第二引擎候选，已在仓库外审查 Bili23-Downloader 稳定版 v2.11.0 的固定提交。
其二维码流程使用 `data.code`、同一 HTTP 会话及 buvid 初始化；其视频解析仍调用相同的
`/x/player/wbi/playurl` WBI 路由，参数为 `qn`、`fnver=0`、`fnval=4048`、`fourk=1`。
本次认证后的 yt-dlp 并未返回 412，故不安装、不运行 Bili23 GUI，也不把它标为 VERIFIED 或 ADOPTED。

临时 Netscape Cookie 文件只含 Bilibili 域 Cookie，pilot 完成后已删除；未导出、打印或提交任何 Cookie 值。二维码路线与 yt-dlp 仅对本次 pilot 标为 VERIFIED；全量获取尚未执行，项目整体仍为 CANDIDATE。
