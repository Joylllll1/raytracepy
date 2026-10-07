# 鸿蒙 PC Python 环境准备工具（归档）

本目录归档目标设备 Python 环境的准备工具，使环境**可复现**。
环境的版本矩阵与步骤说明见 `docs/harmonyos-pc/PYTHON_ENVIRONMENT.md` 第三节。

## 已归档内容

| 路径 | 说明 |
|---|---|
| `tools/setup_py310.sh` | 主流程：解压 Alpine 包 → 替换 libffi → 平台补丁 → patchelf → 签名 |
| `tools/fixcompat.py` | 接入 musl 兼容层（本内核缺失的 libc 符号） |
| `tools/fixwheels.py` | 修复 wheel 安装的扩展（libc soname、libpython 链接、代码签名） |
| `tools/fixall.py` | 依次执行 fixwheels → fixcompat → fixwheels |
| `tools/signall.py` | 对目录下所有 ELF 逐个签名 |
| `tools/add_stlshim.py` + `tools/stlshim.cpp` | 给 numba 的 4 个扩展与 pillow 的 libzstd 挂 stl/musl 兼容 shim |
| `tools/lib/libstlshim.so`<br>`tools/lib/libmusl_compat.so` | 上面两个 shim 的**运行时依赖**（`add_stlshim.py` / `fixcompat.py` 从脚本同级的 `lib/` 读取） |
| `wheels/llvmlite-0.44.0-cp310-cp310-linux_aarch64.whl`<br>`wheels/numba-0.61.2-cp310-cp310-linux_aarch64.whl` | 设备专用 wheel；PyPI 无 musllinux 版，且无法由 apk 重新生成（需 LLVM 15 源码构建） |
| `toolchain-manifest.txt` | 上述文件的完整 sha256，可用 `sha256sum -c` 校验 |

## 未归档

| 项 | 原因 |
|---|---|
| `selfsign.py` | **第三方工具**：[hqzing/ohos-selfsign](https://github.com/hqzing/ohos-selfsign)，0BSD。运行 `setup_py310.sh` / `signall.py` / `add_stlshim.py` 前需自行取得并放入 `tools/`（期望 sha256 前 16 位：`7df6eb1ca6b00a3f`） |
| `pyapks/*.apk`（18 个，44 MB） | 未放入 Git；已记录为 Release 附件 `ohos-python-tools-apks.tar.gz`，sha256 `16141c85a9546d70b55ee0df9c1dd91ecab4534fe419af05ffea0149bea07033`；清单见 `toolchain-manifest.txt` |
| `build/`（140 MB） | llvmlite 源码构建树，复现环境不需要 |
| harmonybrew 的 `libffi.so.8.5.0` | 用于替换 Alpine 的 3.4.4（后者在本内核上 `ffi_closure_alloc()` 返回 NULL）；从设备上的 harmonybrew 取得 |

## 有历史验证记录的端到端流程

2026-09-26 / 28 在已有解释器的设备上新建干净 venv，依赖安装与后处理通过
（结果见 `PORTING_REPORT.md` 第六节）。历史日志使用设备原有工具目录；
切换到仓库内工具、裸设备解释器重建和最新安装包仍需验证。

```bash
export PIP_INDEX_URL=https://pypi.org/simple
python -m venv .venv-fresh
SP=.venv-fresh/lib/python3.10/site-packages
H=scripts/harmonyos                       # 本目录

pip install numpy==1.26.4
pip install "$H"/wheels/llvmlite-0.44.0-cp310-cp310-linux_aarch64.whl \
            "$H"/wheels/numba-0.61.2-cp310-cp310-linux_aarch64.whl
pip install -r requirements-harmonyos.txt

python "$H"/tools/fixall.py "$SP"        # ELF 元数据 + musl 兼容 + 代码签名
python "$H"/tools/add_stlshim.py "$SP"   # numba 的 4 个扩展链接 stl shim

pip install -e .                          # 或 artifacts/release/*.whl
NUMBA_DISABLE_JIT=1 pytest -q tests/      # 期望 7 passed
```

> 更省事的方式：直接运行 `scripts/install_dependencies_harmonyos.py`
> （内部按上述顺序执行，并自动完成第 4、5 步）。

## 运行时依赖

shim 通过 RPATH 被扩展引用，因此 `tools/lib/` 下的两个 `.so` 必须保留：

| 提供 | 缺失后果 |
|---|---|
| `libstlshim.so` | numba 导入失败（缺 `_ZNSt20bad_array_new_lengthC1Ev`） |
| `libmusl_compat.so` | pillow 等扩展导入失败（缺 `qsort_r` 等 libc 符号） |
| `libstdc++.so.6`（`~/.local/alpine-llvm15/usr/lib`） | numba 导入失败 |

现有设备环境的 RUNPATH 指向 `~/.local/ohos-python-tools/lib`；若改用本目录的
`tools/lib`，重新运行一次 `add_stlshim.py` / `fixcompat.py` 即可把路径指向仓库内副本。

## 待办

1. 在新设备验证 Release 附件与归档工具能否从零重建解释器，并保存日志。
2. （可选）补一份端到端脚本：调用 `setup_py310.sh` 重建解释器 + 建 venv + 装依赖，
   使其能在完全干净的设备上一键复现。
3. 第三方 `selfsign.py` 若决定随仓库分发，需保留其版权与 0BSD 许可证声明。

## 校验

```bash
cd scripts/harmonyos
sha256sum -c toolchain-manifest.txt
```
