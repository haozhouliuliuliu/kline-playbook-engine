#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""离线渲染江河 VISUAL 观察 V0.1：input JSON -> PNG + manifest JSON。

纯本地、离线：不发起任何网络请求，不调用任何模型/provider，不读取系统时钟
（as_of 一律来自输入 JSON），不写任何机器相关元数据。

输出原子性（F-ADV-02）：PNG 与 manifest 作为逻辑 artifact pair 原子落盘。
任一步失败（含 manifest / PNG 写失败、覆盖既有文件中途失败）都不会留下
貌似成功的裸 PNG / 裸 manifest / 新旧混合 pair；失败时清理本次临时文件，
且不删除调用前已存在的合法文件（除非已进入已验证的 replacement transaction）。

输入 JSON（字段名遵循 canonical ObservationBar）：

```json
{
  "product": "cu",
  "concrete_contract": "SHFE.cu2609",
  "as_of": "2026-08-23T10:00:00+08:00",
  "panels": [
    {
      "timeframe": "1m",
      "bars": [
        {
          "open_time": "2026-08-23T09:59:00+08:00",
          "close_time": "2026-08-23T10:00:00+08:00",
          "available_at": "2026-08-23T10:00:00+08:00",
          "open_price": "78200",
          "high_price": "78250",
          "low_price": "78180",
          "close_price": "78230",
          "volume": "1234",
          "is_closed": true
        }
      ]
    }
  ]
}
```

退出码：0 = 成功；1 = 输入或渲染校验失败。
"""
from __future__ import annotations

import argparse
from datetime import datetime
import json
import os
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.jianghe_ai_trader import ObservationBar
from src.jianghe_visual_renderer import (
    JiangheVisualRenderer,
    RENDERER_VERSION,
    VisualObservationSpec,
    VisualPanel,
)


def _aware_datetime(value: object, field_name: str) -> datetime:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field_name} 必须是 ISO8601 字符串")
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        raise ValueError(f"{field_name} 不是合法 ISO8601 时间: {value!r}") from None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{field_name} 必须带时区: {value!r}")
    return parsed


def load_spec(payload: object) -> VisualObservationSpec:
    if not isinstance(payload, dict):
        raise ValueError("输入 JSON 顶层必须是对象")
    product = payload.get("product")
    concrete_contract = payload.get("concrete_contract")
    if not isinstance(product, str) or not product:
        raise ValueError("product 不能为空")
    if not isinstance(concrete_contract, str) or not concrete_contract:
        raise ValueError("concrete_contract 不能为空")
    as_of = _aware_datetime(payload.get("as_of"), "as_of")
    raw_panels = payload.get("panels")
    if not isinstance(raw_panels, list) or not raw_panels:
        raise ValueError("panels 必须是非空数组")
    panels: list[VisualPanel] = []
    for index, raw_panel in enumerate(raw_panels):
        if not isinstance(raw_panel, dict):
            raise ValueError(f"panels[{index}] 必须是对象")
        timeframe = raw_panel.get("timeframe")
        if not isinstance(timeframe, str) or not timeframe:
            raise ValueError(f"panels[{index}].timeframe 不能为空")
        raw_bars = raw_panel.get("bars")
        if not isinstance(raw_bars, list) or not raw_bars:
            raise ValueError(f"panels[{index}].bars 必须是非空数组")
        bars: list[ObservationBar] = []
        for bar_index, raw_bar in enumerate(raw_bars):
            where = f"panels[{index}].bars[{bar_index}]"
            if not isinstance(raw_bar, dict):
                raise ValueError(f"{where} 必须是对象")
            is_closed = raw_bar.get("is_closed")
            if not isinstance(is_closed, bool):
                raise ValueError(f"{where}.is_closed 必须是布尔值")
            bars.append(ObservationBar(
                timeframe=timeframe,
                open_time=_aware_datetime(raw_bar.get("open_time"), f"{where}.open_time"),
                close_time=_aware_datetime(raw_bar.get("close_time"), f"{where}.close_time"),
                available_at=_aware_datetime(raw_bar.get("available_at"), f"{where}.available_at"),
                open_price=str(raw_bar.get("open_price", "")),
                high_price=str(raw_bar.get("high_price", "")),
                low_price=str(raw_bar.get("low_price", "")),
                close_price=str(raw_bar.get("close_price", "")),
                volume=str(raw_bar.get("volume", "")),
                is_closed=is_closed,
            ))
        panels.append(VisualPanel(timeframe=timeframe, bars=tuple(bars)))
    return VisualObservationSpec(
        product=product,
        concrete_contract=concrete_contract,
        as_of=as_of,
        panels=tuple(panels),
    )


def _temp_sibling(target: Path) -> Path:
    """在与 target 同目录创建唯一临时文件（OS temp primitive；名字不进产物 identity）。"""
    fd, name = tempfile.mkstemp(prefix=f".{target.name}.partial-", dir=str(target.parent))
    os.close(fd)
    return Path(name)


def _quiet_remove(path: Path) -> None:
    try:
        path.unlink()
    except OSError:
        pass


def _atomic_pair_write(
    png_path: Path,
    png_bytes: bytes,
    manifest_path: Path,
    manifest_text: str,
) -> None:
    """把 (PNG, manifest) 作为逻辑 artifact pair 原子落盘（F-ADV-02）。

    策略：
    1. 先在与 target 同目录写两个完整临时文件（flush + fsync + close）；
    2. 备份既有 target（进入已验证的 replacement transaction）；
    3. 用 os.replace 安装新 pair（同卷原子替换，Windows-safe）；
    4. 任一步失败：回滚已安装的新产物、恢复既有备份、清理本次临时文件；
       不遗留貌似成功的裸 PNG / 裸 manifest / 新旧混合 pair；
    5. 不删除调用前就存在的合法文件（除非已进入上述 transaction）；
    6. 临时文件名不进入 PNG / manifest identity。
    """
    for target in (png_path, manifest_path):
        if target.is_dir():
            raise IsADirectoryError(f"输出路径是目录，拒绝覆盖: {target}")

    png_tmp: Path | None = None
    manifest_tmp: Path | None = None
    installed: list[Path] = []
    backups: list[tuple[Path, Path | None]] = []
    try:
        png_tmp = _temp_sibling(png_path)
        manifest_tmp = _temp_sibling(manifest_path)

        with open(png_tmp, "wb") as fh:
            fh.write(png_bytes)
            fh.flush()
            os.fsync(fh.fileno())
        with open(manifest_tmp, "wb") as fh:
            fh.write(manifest_text.encode("utf-8"))
            fh.flush()
            os.fsync(fh.fileno())

        for target in (png_path, manifest_path):
            if target.exists() or target.is_symlink():
                backup = _temp_sibling(target)
                os.replace(target, backup)
                backups.append((target, backup))
            else:
                backups.append((target, None))

        os.replace(png_tmp, png_path)
        installed.append(png_path)
        os.replace(manifest_tmp, manifest_path)
        installed.append(manifest_path)
    except BaseException:
        for target in installed:
            _quiet_remove(target)
        for target, backup in backups:
            if backup is not None:
                try:
                    os.replace(backup, target)
                except OSError:
                    pass
        if png_tmp is not None:
            _quiet_remove(png_tmp)
        if manifest_tmp is not None:
            _quiet_remove(manifest_tmp)
        raise
    else:
        for _, backup in backups:
            if backup is not None:
                _quiet_remove(backup)
        if png_tmp is not None:
            _quiet_remove(png_tmp)
        if manifest_tmp is not None:
            _quiet_remove(manifest_tmp)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="离线渲染江河 VISUAL 观察 V0.1（PNG + manifest；无网络、无模型调用）"
    )
    parser.add_argument("--input", required=True, help="观察输入 JSON 路径")
    parser.add_argument("--png-out", required=True, help="输出 PNG 路径")
    parser.add_argument("--manifest-out", required=True, help="输出 manifest JSON 路径")
    args = parser.parse_args(argv)

    try:
        payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
        spec = load_spec(payload)
        artifact = JiangheVisualRenderer().render(spec)
        png_path = Path(args.png_out)
        manifest_path = Path(args.manifest_out)
        _atomic_pair_write(
            png_path,
            artifact.png_bytes,
            manifest_path,
            artifact.manifest_json() + "\n",
        )
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(f"renderer_version={RENDERER_VERSION}")
    print(f"png={png_path} sha256={artifact.png_sha256}")
    print(f"manifest={manifest_path}")
    print(f"renderer_config_identity={artifact.renderer_config_identity}")
    print(f"input_observation_identity={artifact.input_observation_identity}")
    print(f"visual_artifact_identity={artifact.visual_artifact_identity}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
