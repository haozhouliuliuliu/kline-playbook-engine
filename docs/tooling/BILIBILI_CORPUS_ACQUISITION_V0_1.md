# Bilibili 交易员视频语料获取 V0.1

> 状态：CANDIDATE（真实枚举、最高画质验证、下载及恢复验证完成前不得标为 VERIFIED）

## 固定范围与安全边界

- UP URL：`https://space.bilibili.com/3546770449631285/video`
- UID：`3546770449631285`
- 输出目录：`%USERPROFILE%\Videos\kline-playbook-engine\bilibili\3546770449631285\`
- Chrome 登录态只由 `yt-dlp --cookies-from-browser chrome` 在本机运行时读取。
- 不导出、不打印、不记录、不提交 Cookie、SESSDATA、Token 或浏览器配置；日志会对疑似敏感键值脱敏。
- 视频、字幕与元数据均在仓库外；仓库仅保存程序、测试和本证据记录。

## 实现语义

- 主枚举路径：yt-dlp 的 `BilibiliSpaceVideo`；按 BVID 去重并以报告总数交叉验证。未知总数或数量不相等即 `ENUMERATION_COMPLETE=NO`，失败闭合。
- 画质：先获取 pilot 的格式，只有最高可下载视频流满足已知支持画质时才允许继续；不得静默降级。
- 下载（待真实验证后启用）：最佳视频流 + 最佳音频流，ffmpeg 仅 mux/remux，不重编码；保留 info JSON、原生字幕、ffprobe 和 SHA256 证据，并以下载档案实现可恢复、不重复。
- 磁盘：估计总量超过可用空间 70% 时为 `DISK_CAPACITY_BLOCKED`，不开始全量下载。

## 当前实际运行结果

```text
YTDLP_VERSION=2026.08.19
FFMPEG_VERSION=NOT_AVAILABLE_FOR_VERIFICATION
COOKIE_MODE=chrome_runtime_only_no_export
ENUMERATION_METHOD=Bilibili:WBI_SPACE_API
UPLOADER_REPORTED_TOTAL=99
ENUMERATED_UNIQUE_BVIDS=99
ENUMERATION_COMPLETE=YES
QUALITY_VERIFICATION=NOT_RUN
PILOT_RESULT=NOT_RUN
FALLBACK_USED=YES_WBI_SPACE_API
PROJECT_BILIBILI_ACQUISITION_STATUS=CANDIDATE
```

## 已知限制

此版本绝不会把“当前页面没有更多项目”当作完整性证明。若 yt-dlp 遇到 352、412、登录、WBI 或分页不一致，运行必须停在失败闭合状态；在写入 VERIFIED 前需要补齐同一登录态下的 WBI Space API 差集审计与最高质量 DASH 验证。

2026-08-21 的真实运行已确认：Chrome 关闭后，`yt-dlp --cookies-from-browser chrome:Default`
仍被 Windows DPAPI/Chrome 应用绑定加密拒绝；无 Cookie 的 BilibiliSpaceVideo 请求则收到 HTTP 412。
WBI Space API 备用路径完整枚举到 99 个唯一 BVID，报告总数也是 99，且无重复。
但 pilot 的媒体格式请求仍受 412 拦截，无法以该 Chrome 已登录账号验证最高可下载画质。
未导出、打印或持久化任何 Cookie 值，未下载媒体，因而不得标记 VERIFIED。
