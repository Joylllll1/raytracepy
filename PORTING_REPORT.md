# RayTracePy 鸿蒙 PC 移植报告

- 项目：将 PyPI `raytracepy 0.0.1` 移植到鸿蒙 PC（HarmonyOS 6.1.0 / aarch64）
- 目标设备：HUAWEI MateBook Pro（HAD-W32），Kirin X90，32 GB，API 23
- 参考环境：Windows 10 AMD64 + CPython 3.10.21
- 设备证据日期：2026-09-26 / 2026-09-28；交付更新：2026-10-07
- 相关文档：`docs/harmonyos-pc.md`（安装使用）、
  `docs/harmonyos-pc/PYTHON_ENVIRONMENT.md`（环境）、
  `docs/harmonyos-pc/DEPENDENCY_MATRIX.md`（依赖矩阵）、
  `docs/harmonyos-pc/REFERENCE_COMPARISON.md`（数值对比）

## 一、结论

历史设备记录显示，RayTracePy 0.0.1 在关闭 JIT 后可在鸿蒙 PC 上
**安装、导入并运行官方示例**。固定输入下的整数计数和直方图数据与参考环境
逐位一致，浮点统计最大差约 1.9e-17，符合仓库设定的数值容差。

源码已包含 JIT 环境变量守卫和 SciPy/NumPy API 兼容修复，算法未改。
2026-10-07 重新构建 wheel/sdist，核验包内源码并在 macOS 上验证；
最新安装包尚未在鸿蒙设备上复测，不能将历史结果视为当前交付包的完整验证。
解释器来源、关闭 JIT 和性能是否满足验收要求仍待老师确认。

本次本地验证结果：安装新 wheel 后，`tests/` 与 `scripts/tests/` 合计
82 passed、44 subtests passed；wheel/sdist 中 18 个包内 Python 文件与源码
逐字节一致，`generate_cdf(2*x)` 与解析解 `x**2` 一致。详见
`artifacts/release/verification/pytest.log` 与 `package-check.log`。

## 二、完成标准对照

| # | 完成标准 | 状态 | 证据 |
|---|---|---|---|
| 1 | 在鸿蒙 PC 原生 Python 环境中成功安装 | 历史通过；口径待确认 | 原生执行但非为鸿蒙编译；历史环境检测 `RESULT: OK`，新包待复测 |
| 2 | `import raytracepy` 正常执行 | 历史通过；新包待复测 | 检测脚本与历史全新 venv 日志；本次 macOS 验证见 `artifacts/release/verification/` |
| 3 | 至少一个官方示例完整运行 | 历史通过；新包待复测 | `example-run/` 保存运行输出和 HTML；该日志未记录 commit 与退出码 |
| 4 | 计算结果与参考环境在允许误差内一致 | 历史通过；新包待复测 | 300 万光线整数计数与直方图一致，浮点最大差 1.9e-17；目标日志对应 `16761de` |
| 5 | 在全新环境中按文档可重新安装 | 历史 venv 通过；新包待复测 | 历史依赖安装、wheel 导入、冒烟仿真与 7 项测试通过，见第六节；不包含裸设备解释器重建验证 |
| 6 | 测试、文档、安装包和已知问题齐全 | 已更新；待设备复测归档 | 最新 wheel/sdist 与本地验证记录在 `artifacts/release/`；复测步骤见 `REVALIDATION.md` |

## 三、环境

| 项目 | 值 |
|---|---|
| Python | CPython 3.10.15（aarch64 / musl），项目 `.venv` |
| 依赖 | numpy 1.26.4 / scipy 1.15.3 / pandas 2.2.3 / numba 0.61.2 / llvmlite 0.44.0(LLVM 15.0.7) / plotly 5.6.0 / datashader 0.16.3 |
| 测试 | pytest 9.1.1 / pytest-cov 7.1.0 |
| 工具链 | clang 15.0.4 / make / cmake / ninja（`/data/service/hnp/bin`） |
| 运行方式 | 关闭 numba JIT（`NUMBA_DISABLE_JIT=1`） |

详见 `docs/harmonyos-pc/PYTHON_ENVIRONMENT.md` 与 `requirements-harmonyos.txt`。

## 四、源码改动

1. `src/raytracepy/__init__.py`（PR #4）—— 原先无条件执行
   `numba.config.DISABLE_JIT = False`，会覆盖 numba 自己读取的 `NUMBA_DISABLE_JIT`
   环境变量。改为仅在未显式设置该变量时才强制开启 JIT；**默认行为不变**。
2. `src/raytracepy/ref_data/utils_ref_data.py`（PR #7）—— 用
   `cumulative_trapezoid(..., initial=0)` 替换已移除的 `cumtrapz` 与补零操作。
3. `src/raytracepy/raytrace.py`（PR #7）—— `np.NaN` 改为 `np.nan`。

算法未改。PR #7 的设备验证说明见 `SOURCE_COMPATIBILITY.md`；
该说明未附独立原始日志。本次重建包纳入以上全部修改。

## 五、验证证据

下表为历史设备记录。本次本地构建与验证另存于 `artifacts/release/verification/`。
环境检测记录对应 `0712367`，300 万光线对比记录对应 `16761de`，
均不是本次更新基于的 `8c8f2ef`。

| 验证项 | 命令 | 结果 |
|---|---|---|
| 环境检测 | `python scripts/check_environment.py` | `RESULT: OK`，无阻塞、无警告 |
| 自动化测试 | `NUMBA_DISABLE_JIT=1 pytest -q tests/` | 7 passed |
| 官方示例 | `NUMBA_DISABLE_JIT=1 python examples/single/single_light.py` | 保存统计输出与 HTML；原始日志未记录退出码，末尾自动打开 HTML 报 `start: not found` |
| 参考负载对比 | `NUMBA_DISABLE_JIT=1 python scripts/generate_reference_baseline.py --input tests/fixtures/single_light_reference_input.json --verify-repeat` | 整数计数与直方图一致（sha256 相同），浮点统计在容差内 |
| 全新环境复测 | 见第六节 | 通过 |

证据文件均在 `artifacts/environment/harmonyos-pc/`：
`check_environment.log`、`environment.json`、`pytest-evidence.log`、
`example-run/`、`reference-comparison/`。

## 六、历史全新 venv 复测（通过；新包待复测）

以下记录使用 PR #7 之前的安装包。本次更换了 `artifacts/release/` 中的包，
保留旧日志作为历史证据；不能据此认定新包已经在设备上通过。

在一台已装好解释器的设备上新建空 venv，严格按 `docs/harmonyos-pc.md` 方式 A 执行：

```bash
export PIP_INDEX_URL=https://pypi.org/simple
python -m venv .venv-fresh
W=~/.local/ohos-python-tools/wheels ; T=~/.local/ohos-python-tools
SP=.venv-fresh/lib/python3.10/site-packages

pip install numpy==1.26.4
pip install "$W/llvmlite-0.44.0-cp310-cp310-linux_aarch64.whl" \
            "$W/numba-0.61.2-cp310-cp310-linux_aarch64.whl"
pip install -r requirements-harmonyos.txt
$T/fixall.py "$SP"          # ELF 元数据 + musl 兼容 + 代码签名
$T/add_stlshim.py "$SP"     # numba 的 4 个扩展链接 stl shim
pip install artifacts/release/raytracepy-0.0.1-py3-none-any.whl
```

结果（原始日志见 `artifacts/environment/harmonyos-pc/fresh-env-install.log`，
后处理日志见同目录 `fresh-env-fixall.log`、`fresh-env-stlshim.log`）：

| 步骤 | 结果 |
|---|---|
| 依赖安装（含固定传递依赖） | 成功 |
| `fixall.py` | 修补 236 个 ELF，失败 0（含签名） |
| `add_stlshim.py` | 为 numba 的 4 个扩展链接 shim |
| `import raytracepy` + 全部依赖 | 成功（numpy 1.26.4 / numba 0.61.2 / llvmlite 0.44.0 / scipy 1.15.3 / pandas 2.2.3） |
| 10000 光线冒烟仿真 | 成功（hits = 6432） |
| `pytest -q tests/`（在全新 venv 中） | **7 passed** |

复测中发现并已写入文档的三个必要步骤：固定传递依赖（否则 `dask` 新版会要求
`pyarrow`）、安装后必须签名（否则 `.so` 加载报 `Permission denied`）、
numba 扩展必须链接 stl shim（否则报 `symbol not found`）。

## 七、已知问题

| # | 问题 | 影响 | 处理 |
|---|---|---|---|
| 1 | **numba JIT 产物无法执行**：JIT 能编译，执行时段错误（`src/raytracepy/raytrace.py:175`） | 必须用纯 Python 路径；历史对比耗时约为参考的 3.0 倍，包含硬件差异 | 已提供源码守卫使 `NUMBA_DISABLE_JIT=1` 生效；固定负载数值在容差内。JIT 与性能验收要求待老师确认 |
| 2 | 解释器**原生执行但非为鸿蒙编译**（Alpine musl 二进制 + ELF 修补 + 2 个兼容 shim） | 口径问题 | 建议按"原生执行"判定；严格口径需延长周期 |
| 3 | 环境准备工具来源：自研脚本已归档；`selfsign.py` 为第三方（hqzing/ohos-selfsign，0BSD）；18 个 Alpine apk（44 MB）未入库 | 裸设备从零复现需要这些材料 | 自研脚本、`tools/lib` 的 shim、设备专用 wheel 已归档到 `scripts/harmonyos/`；`selfsign.py` 需自行获取（清单记有校验和）；apk 见 Release 附件 |
| 4 | pip 全局索引指向 `https://pypi.cnb.cool/OpenHarmonyPCDeveloper/pypi/...`，其中没有 numpy 等包 | 按文档直接 `pip install` 会失败 | 安装时指定官方索引或本地 wheelhouse（如 `PIP_INDEX_URL=https://pypi.org/simple`） |
| 5 | NumPy 2.x 尚未完整回归 | 当前验证范围与依赖清单固定为 numpy 1.26.4；不能声称 NumPy 2.x 已受支持 | `np.NaN` 已由 PR #7 修正为 `np.nan`；源码仍使用 `np.trapz`，保留 `numpy<2.0` 上限，后续升级需完整验证 |
| 6 | `src/raytracepy/compile/math_custom.cp310-win_amd64.pyd` 为 Windows 专用 | 无 | 该目录未被任何代码引用，不影响导入与运行 |
| 7 | `scripts/check_environment.py` 的 `@njit` 探针只测简单函数，包自身 JIT 崩溃时仍报 OK | 检测结论可能偏乐观 | 已在探测报告第十一节注明；建议后续加强探针 |
| 8 | 已安装扩展的 `RUNPATH` 指向 `~/.local/alpine-llvm15/usr/lib`（libstdc++）与 `~/.local/ohos-python-tools/lib`（libstlshim / libmusl_compat） | 这些目录缺失时 numba 无法导入 | `lib/` 下的两个 shim 已归档到 `scripts/harmonyos/tools/lib/`；如要让扩展指向仓库内副本，重跑 `add_stlshim.py` / `fixcompat.py` 即可 |
| 9 | 传递依赖必须固定 | 不固定 `dask` 时新版会引入 `pyarrow` 依赖导致 datashader 导入失败 | 已在 `requirements-harmonyos.txt` 固定全部传递依赖 |
| 10 | `scripts/generate_reference_baseline.py` 的 `--expected-output` 是**输出**参数，覆盖已存在文件时不提示 | 误指向参考基线会静默覆盖，之后跨平台对比变成循环论证 | 使用前勿指向 `artifacts/reference/`；建议后续加 `--force` 保护并改名（未修，已记录） |
| 11 | 最新安装包尚无鸿蒙设备复测记录 | 历史日志不能证明当前交付包已全部通过 | 按 `docs/harmonyos-pc/REVALIDATION.md` 在全新 venv 安装 wheel，保存包哈希、版本与运行日志 |

## 八、交付物清单

| 交付物 | 位置 |
|---|---|
| 可安装包 | `artifacts/release/raytracepy-0.0.1-py3-none-any.whl`、`artifacts/release/raytracepy-0.0.1.tar.gz`（构建产物默认写在 `dist/`） |
| 安装与使用说明 | `docs/harmonyos-pc.md` |
| 移植报告与已知问题 | 本文件 |
| 环境说明与准备步骤 | `docs/harmonyos-pc/PYTHON_ENVIRONMENT.md` |
| 依赖清单与兼容矩阵 | `requirements-harmonyos.txt`、`docs/harmonyos-pc/DEPENDENCY_MATRIX.md` |
| 数值对比报告 | `docs/harmonyos-pc/REFERENCE_COMPARISON.md` |
| 环境检测脚本 | `scripts/check_environment.py` |
| 自动化测试 | `tests/`（7 项）、`scripts/tests/`（75 项） |
| 实测证据与日志 | `artifacts/environment/harmonyos-pc/` |
| 示例产出 | `artifacts/environment/harmonyos-pc/example-run/single_led.html` |
| 源码兼容性说明 | `SOURCE_COMPATIBILITY.md` |
| 最新包本地验证与设备复测步骤 | `artifacts/release/README.md`、`artifacts/release/verification/`、`docs/harmonyos-pc/REVALIDATION.md` |
| 环境工具（解释器重建） | `scripts/harmonyos/`（自研脚本 + `tools/lib` 的 shim + 设备专用 wheel）；18 个 Alpine 3.10.15 包见 Release 附件 `ohos-python-tools-apks.tar.gz`，sha256 `16141c85a9546d70b55ee0df9c1dd91ecab4534fe419af05ffea0149bea07033` |
