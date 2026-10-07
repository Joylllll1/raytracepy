# 鸿蒙 PC 安装与使用说明

RayTracePy 0.0.1 在鸿蒙 PC（HarmonyOS 6.1.0 / aarch64，HUAWEI MateBook Pro HAD-W32）
上的安装、验证与使用方式。2026-09-26 / 28 的设备记录显示，历史版本在关闭 JIT
后完成安装、导入、官方示例和测试。2026-10-07 重建的安装包已纳入 PR #7，
最新包的设备复测尚未完成，步骤见 `docs/harmonyos-pc/REVALIDATION.md`。

- 目标环境版本矩阵与可重复准备步骤：`docs/harmonyos-pc/PYTHON_ENVIRONMENT.md`
- 依赖清单与兼容矩阵：`requirements-harmonyos.txt`、`docs/harmonyos-pc/DEPENDENCY_MATRIX.md`
- 实测证据：`artifacts/environment/harmonyos-pc/`
- 参考环境：Windows AMD64 + CPython 3.10.21（见 `docs/testing/REFERENCE_BASELINE.md`）

## 一、环境要求

| 项目 | 要求 |
|---|---|
| 系统 | HarmonyOS 6.1.0（API 23），aarch64，HongMeng Kernel 1.12.0 |
| Python | CPython 3.10.x（目标环境用 3.10.15，aarch64/musl） |
| numpy | 按当前验证范围固定为 **< 2.0**，推荐 1.26.4；`np.NaN` 已修复，但仍使用 `np.trapz`，尚未完成 NumPy 2.x 回归 |
| 其它依赖 | 见 `requirements-harmonyos.txt` |
| 工具链 | clang 15.0.4 / make / cmake / ninja（`/data/service/hnp/bin`） |

## 二、安装

### 方式 A：源码安装（含后处理）

以下依赖安装和后处理顺序有历史干净 venv 验证记录；其中第 6 步的旧记录使用
wheel 安装（见 `PORTING_REPORT.md` 第六节）。最新源码安装仍需设备复测。

```bash
cd <repo>
python -m venv .venv-fresh && source .venv-fresh/bin/activate
export PIP_INDEX_URL=https://pypi.org/simple     # 见"常见问题"
W=~/.local/ohos-python-tools/wheels
T=~/.local/ohos-python-tools
SP=.venv-fresh/lib/python3.10/site-packages

# 1) numpy
pip install numpy==1.26.4

# 2) 设备专用 wheel（PyPI 无 musllinux 版；必须先于其它依赖安装）
pip install "$W/llvmlite-0.44.0-cp310-cp310-linux_aarch64.whl" \
            "$W/numba-0.61.2-cp310-cp310-linux_aarch64.whl"

# 3) 其余依赖（含全部传递依赖，已固定版本）
pip install -r requirements-harmonyos.txt

# 4) 后处理：ELF 元数据 + musl 兼容 + 代码签名
$T/fixall.py "$SP"

# 5) 后处理：给 numba 的 4 个扩展链接 stl shim
$T/add_stlshim.py "$SP"

# 6) 本项目
pip install -e .
```

**第 4、5 步不可省略**：OpenHarmony 要求 ELF 带 `.codesign` 段才能 `dlopen`，
未签名的扩展会报 `Permission denied`；numba 的扩展还缺一个 libstdc++ 符号，
需要 shim，否则报 `symbol not found: _ZNSt20bad_array_new_lengthC1Ev`。

### 方式 B：wheel 安装

本次交付的安装包已放在 `artifacts/release/`（构建时默认写到 `dist/`）：

```bash
python -m pip install --force-reinstall --no-deps artifacts/release/raytracepy-0.0.1-py3-none-any.whl
```

wheel 的 tag 为 `py3-none-any`（与上游 PyPI 发布一致）。
依赖仍需按方式 A 的第 1–5 步安装，之后才能导入。
项目版本号仍为 0.0.1，因此升级旧包时使用 `--force-reinstall`；`--no-deps`
保留已经按鸿蒙清单安装的依赖。包的校验和与本地验证记录见 `artifacts/release/README.md`。

## 三、验证安装

```bash
cd <repo>
source .venv-fresh/bin/activate       # 或实际使用的虚拟环境
python scripts/check_environment.py     # 期望：RESULT: OK
NUMBA_DISABLE_JIT=1 pytest -q tests/    # 期望：7 passed
```

## 四、运行官方示例

```bash
cd <任意输出目录>
NUMBA_DISABLE_JIT=1 python <repo>/examples/single/single_light.py
```

示例会运行 300 万光线的仿真、打印统计信息并生成 `single_led.html`。
实测输出与耗时见 `artifacts/environment/harmonyos-pc/example-run/`。

## 五、常见问题

| 现象 | 原因 | 处理 |
|---|---|---|
| 运行时报 `Segmentation fault` | 设备上 numba JIT 执行编译产物会崩溃 | 加 `NUMBA_DISABLE_JIT=1`（需 `fix/numba-disable-jit-override` 的源码守卫） |
| `ImportError: cannot import name 'cumtrapz'` 或 `AttributeError: np.NaN` | 使用了 PR #7 修复前的旧包 | 重装 2026-10-07 更新的 wheel；依赖仍按清单固定 |
| `pip` 装不上 numba / llvmlite | PyPI 无 musllinux wheel | 用设备专用 wheel，见 `PYTHON_ENVIRONMENT.md` 第三节 |
| `No matching distribution found for numpy` 等 | pip 全局索引指向 OpenHarmony 开发者镜像，其中没有这些包 | `export PIP_INDEX_URL=https://pypi.org/simple` 后重试 |
| `ImportError: ... Permission denied` 加载 `.so` | 扩展没有 `.codesign` 段，OpenHarmony 拒绝 `dlopen` | 运行 `fixall.py <site-packages>`（含签名） |
| `symbol not found: _ZNSt20bad_array_new_lengthC1Ev` | numba 的 clang 编译扩展缺 libstdc++ 符号 | 运行 `add_stlshim.py <site-packages>` |
| `ModuleNotFoundError: No module named 'pyarrow'` | 未固定 dask 版本，新版 `dask.dataframe` 需要 pyarrow | 按 `requirements-harmonyos.txt` 固定 `dask==2023.3.0` |
| 末尾出现 `start: not found` | 示例通过 Windows 的 `start` 命令打开 HTML，鸿蒙不提供该命令 | 检查 HTML 已生成后手动打开 |
| 运行明显比参考环境慢 | 历史目标运行关闭 JIT，且两端硬件不同 | 300 万光线约 67.53 s vs 22.33 s（3.02 倍）；整数计数和直方图一致，浮点差在容差内 |

## 六、相关文档

| 文档 | 内容 |
|---|---|
| `docs/harmonyos-pc/PYTHON_ENVIRONMENT.md` | 目标环境说明、版本矩阵、可重复准备步骤 |
| `docs/harmonyos-pc/DEPENDENCY_MATRIX.md` | 依赖兼容矩阵 |
| `docs/harmonyos-pc/PYTHON_ENVIRONMENT_PROBE.md` | 环境探测报告与实测结果 |
| `docs/harmonyos-pc/REFERENCE_COMPARISON.md` | 参考环境与目标环境的数值对比 |
| `PORTING_REPORT.md` | 移植报告与已知问题 |
| `docs/harmonyos-pc/REVALIDATION.md` | 最新 wheel 的设备复测与验收确认待办 |
| `docs/testing/REFERENCE_BASELINE.md` | 参考环境基线与测试说明 |
