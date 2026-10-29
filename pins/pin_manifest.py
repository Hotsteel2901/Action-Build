#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 OnePlus 内核清单里三个源码仓的 revision 替换成固定 commit。

用法:
    pin_manifest.py <manifest.xml> <common_sha> <msm_sha> <devicetree_sha>

只改 revision 属性，不动 <remote>/<default>/<linkfile> 等结构，
因此上游以后往清单里加新 project 也能继续用。
"""
import re
import sys

TARGETS = (
    ("android_kernel_common_oneplus_sm8650", "common"),
    ("android_kernel_oneplus_sm8650", "msm-kernel"),
    ("android_kernel_modules_and_devicetree_oneplus_sm8650", "devicetree"),
)


def replace_once(text: str, name: str, sha: str) -> tuple[str, int]:
    """name 在 revision 之前（OnePlus 现行写法）"""
    pattern = re.compile(
        r'(<project\b[^>]*\bname="' + re.escape(name) + r'"[^>]*\brevision=")([^"]*)(")'
    )
    text, count = pattern.subn(lambda m: m.group(1) + sha + m.group(3), text, count=1)
    if count:
        return text, count
    # 兜底：万一将来属性顺序反了
    pattern = re.compile(
        r'(<project\b[^>]*\brevision=")([^"]*)("[^>]*\bname="' + re.escape(name) + r'")'
    )
    return pattern.subn(lambda m: m.group(1) + sha + m.group(3), text, count=1)


def main() -> int:
    if len(sys.argv) != 5:
        print("usage: pin_manifest.py <manifest.xml> <common_sha> <msm_sha> <dt_sha>")
        return 64

    path, common_sha, msm_sha, dt_sha = sys.argv[1:5]
    shas = {
        TARGETS[0][0]: common_sha,
        TARGETS[1][0]: msm_sha,
        TARGETS[2][0]: dt_sha,
    }

    with open(path, encoding="utf-8") as fh:
        text = fh.read()

    missing = []
    for name, label in TARGETS:
        text, count = replace_once(text, name, shas[name])
        print("  [%s] %s -> %s (matched=%d)" % (label, name, shas[name][:12], count))
        if count != 1:
            missing.append(name)

    if missing:
        print("ERROR: 以下 project 没能锚定: " + ", ".join(missing))
        return 2

    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
