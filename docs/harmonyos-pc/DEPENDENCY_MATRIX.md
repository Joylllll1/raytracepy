# 鸿蒙 PC 依赖兼容矩阵（4号）

- 日期：2026-09-26｜分支：`feature/dependencies`
- 环境：CPython 3.10.15（`~/.local/alpine-py310`）+ 项目 `.venv`
- 证据：组长设备实测；未改 raytracepy 源码。换解释器须重测。

## 兼容矩阵

| 包 | 参考 | 设备 | import | 状态 |
|---|---|---|---|---|
| numpy | 1.22.0 | 1.26.4 | OK | 可用（版本偏离） |
| scipy | 1.10.0 | 1.15.3 | OK | 可用（版本偏离） |
| pandas | 1.4.1 | 2.2.3 | OK | 可用（版本偏离） |
| numba | 0.56.4 | 0.61.2 | OK | **不可用(JIT)** |
| llvmlite | 0.39.1 | 0.44.0 | OK | 可用（随 numba） |
| plotly | 5.6.0 | 5.6.0 | OK | 可选（可视化） |
| datashader | 0.13.0 | 0.16.3 | OK | 可选（可视化） |
| pytest / pytest-cov | 9.1.1 / 7.1.0 | 同左 | OK | 可用 |
| raytracepy | 0.0.1 | 源码树 | OK | 可用（需关 JIT；回退归 5号） |

钉版本：`requirements-harmonyos.txt`。安装：`python scripts/install_dependencies_harmonyos.py`。

## numba JIT

import / 编译 OK，**执行段错误**（多版本已复现）。规避归 **5号**（`njit` → 恒等装饰器）。关 JIT 后数值与 Windows 参考一致，约 2.9× 慢。

## 端到端（关 JIT）

7 passed；`single_light.py` 300 万光线跑通；设备 64.07 s / Windows 22.33 s；哈希逐位相同。

## 未决

| 问题 | 谁 |
|---|---|
| JIT 回退 / 是否必须修 | 5号 / 老师 |
| Alpine-py310 是否算原生验收 | 老师 |
| 接受设备栈偏离参考版本 | 组长 |

未解决项详见 `artifacts/dependencies/harmonyos-pc/ISSUES.md`。
