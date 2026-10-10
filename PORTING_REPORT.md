# RayTracePy 鸿蒙 PC 移植报告

- 项目：将 PyPI `raytracepy 0.0.1` 移植到鸿蒙 PC（HarmonyOS 6.1.0 / aarch64）
- 目标设备：HUAWEI MateBook Pro（HAD-W32），Kirin X90，32 GB，API 23
- 目标环境：**官方"鸿蒙化" CPython 3.12.9**（`ohos-aarch64`，`aarch64-unknown-linux-ohos`）
- 参考环境：Windows 10 AMD64 + CPython 3.10.21
- 设备证据：2026-09-26 / 09-28（历史环境）、**2026-10-10（官方鸿蒙运行时，当前结论）**
- 相关文档：`docs/harmonyos-pc.md`（安装使用）、
  `docs/harmonyos-pc/PYTHON_ENVIRONMENT.md`（环境）、
  `docs/harmonyos-pc/DEPENDENCY_MATRIX.md`（依赖矩阵）、
  `docs/harmonyos-pc/REFERENCE_COMPARISON.md`（数值对比）

## 一、结论

RayTracePy 0.0.1 可在鸿蒙 PC 上**安装、导入、运行测试与官方示例**。目标环境已切换为
**官方鸿蒙原生 CPython 3.12.9**，在该环境上：

- **numba JIT 正常工作**（此前在自建 Alpine 环境上的段错误不再出现）；
- 300 万光线参考负载的整数计数与直方图数据与 Windows 参考环境**逐位一致**
  （`histogram_sha256` 相同）；
- 官方示例退出码 0 并生成 HTML。

源码改动仅 3 处环境适配（见第四节），**算法未改**。此前"解释器非为鸿蒙编译""JIT 不可用"
两条已知问题**已随运行时切换而消除**。

## 二、完成标准对照

| # | 完成标准 | 状态 | 证据 |
|---|---|---|---|
| 1 | 在鸿蒙 PC 原生 Python 环境中成功安装 | ✅ | 官方鸿蒙化运行时（triple `aarch64-unknown-linux-ohos`）+ `.venv-ohos`，`pip install -e .` 成功 |
| 2 | `import raytracepy` 正常执行 | ✅ | `artifacts/revalidation/harmonyos-pc/2026-10-07-ohos-runtime/`，检测脚本 `RESULT: OK_WITH_WARNINGS`（仅缺构建工具） |
| 3 | 至少一个官方示例完整运行 | ✅ | `example-run/`：退出码 0，生成 `single_led.html`（169 KB） |
| 4 | 计算结果与参考环境在允许误差内一致 | ✅ | 300 万光线负载：命中数 1923054、`histogram_sha256` 与参考**逐位一致**、`repeat_identical=True` |
| 5 | 在全新环境中按文档可重新安装 | ✅ | 官方安装器 + 新建 venv + 固定依赖（`docs/harmonyos-pc.md` 第二节），2026-10-10 实测通过 |
| 6 | 测试、文档、安装包和已知问题齐全 | ✅ | `pytest -q tests/` 7 passed；wheel/sdist 在 `artifacts/release/`；文档与本节 |

## 三、环境

| 项目 | 值 |
|---|---|
| 运行时 | 官方鸿蒙化 CPython 3.12.9（`ohos-aarch64`，装于 `~/usr/local`），pip 26.2.1 |
| 包源 | 社区源 `pypi.cnb.cool/OpenHarmonyPCDeveloper/...`（安装器自动配置） |
| 依赖 | numpy 1.26.3 / scipy 1.15.3 / pandas 2.3.1 / numba 0.65.1 / llvmlite 0.47.0 / plotly 7.1.0 / datashader 0.19.1 |
| 测试 | pytest 9.1.1 / pytest-cov 7.1.0 |
| 应用形态（可选） | matplotlib 3.11.1 / tkinter 3.12.9.post1 |
| 运行方式 | **JIT 开启**（无需 `NUMBA_DISABLE_JIT`） |

详见 `docs/harmonyos-pc/PYTHON_ENVIRONMENT.md` 与 `requirements-harmonyos.txt`。

## 四、源码改动

1. `src/raytracepy/__init__.py`（PR #4）—— 尊重显式设置的 `NUMBA_DISABLE_JIT`
   （原先无条件覆盖）；默认行为不变。**在官方运行时上已非必需**，保留以便调试与对比。
2. `src/raytracepy/ref_data/utils_ref_data.py`（PR #7）—— 用
   `cumulative_trapezoid(..., initial=0)` 替换 SciPy 1.14 起移除的 `cumtrapz`。
3. `src/raytracepy/raytrace.py`（PR #7）—— `np.NaN` 改为 `np.nan`。

算法未改。

## 五、验证证据（2026-10-10，官方鸿蒙运行时）

| 验证项 | 命令 | 结果 |
|---|---|---|
| 环境检测 | `python scripts/check_environment.py` | `RESULT: OK_WITH_WARNINGS`（仅提示未装 `setuptools`/`wheel`）；`system: HarmonyOS` |
| 自动化测试 | `python -m pytest -q tests/ -o addopts=''` | **7 passed**（JIT 开启，17.2 s） |
| 官方示例 | `python examples/single/single_light.py` | 退出码 0，生成 `single_led.html` |
| 参考负载对比 | `python scripts/generate_reference_baseline.py --input tests/fixtures/single_light_reference_input.json --verify-repeat` | 命中数 1923054、sha256 与参考一致、**33.40 s**、`repeat_identical=True` |
| datashader 功能 | `ds.Canvas(...).points(...)` + `shade` | 通过（仅 `examples/` 使用） |

证据目录：`artifacts/revalidation/harmonyos-pc/2026-10-07-ohos-runtime/`
（`python.txt`、`installed-packages.txt`、`pytest.log`、`environment.log|json`、
`reference-comparison/`、`example-run/`）。

## 六、复测记录

### 6.1 官方鸿蒙运行时（2026-10-10，当前结论）

按 `docs/harmonyos-pc.md` 第二节执行：官方安装器 → 新建 `.venv-ohos` →
`pip install --prefer-binary <固定版本>` → `pip install -e .`。结果见第五节。
性能：Windows 参考 22.33 s，本设备 33.40 s（约 1.5 倍，差异主要来自硬件）。

### 6.2 历史环境（2026-09-26 ~ 10-07，已被取代）

自建 Alpine CPython 3.10.15 + ELF 修补 + 签名 + 2 个兼容 shim 的方案也曾完整跑通
（安装、导入、示例、7 项测试、全新 venv 复测），但 JIT 无法执行、只能纯 Python，
且解释器非为鸿蒙编译。该方案及其日志/工具已随仓库清理移除，
如需查阅可从 git 历史找回（清理前提交 `236e13f`）。

## 七、已知问题

| # | 问题 | 影响 | 处理 |
|---|---|---|---|
| 1 | **应用形态与上架未定**：RayTracePy 是库（无界面、无入口），上架对象必须是基于它的应用 | 影响最终验收形式 | 可用 GUI 工具链为 tkinter + matplotlib（社区源有 ohos wheel）；需老师确认"命令行工具 / 桌面应用"及上架方式 |
| 2 | NumPy 2.x 尚未回归 | 依赖固定 `numpy==1.26.3` | 源码仍使用 `np.trapz`（NumPy 2 已改名）；升级需完整回归 |
| 3 | datashader 仅 `examples/` 使用，库本身不依赖 | 4 个热图示例依赖它 | 已固定 `datashader==0.19.1`（不再需要 dask）；**不要安装 dask** |
| 4 | `scripts/check_environment.py` 的 `@njit` 探针只测简单函数 | 检测结论可能偏乐观 | 已记录；建议后续加强为跑一个极小仿真 |
| 5 | `scripts/generate_reference_baseline.py` 的 `--expected-output` 是**输出**参数，覆盖已存在文件时不提示 | 误指向参考基线会静默覆盖 | 使用前勿指向 `artifacts/reference/`；建议加 `--force` 保护并改名（未修） |
| 6 | `src/raytracepy/compile/math_custom.cp310-win_amd64.pyd` 为 Windows 专用 | 无 | 该目录未被任何代码引用，不影响导入与运行 |

## 八、交付物清单

| 交付物 | 位置 |
|---|---|
| 可安装包 | `artifacts/release/raytracepy-0.0.1-py3-none-any.whl`、`.tar.gz`（纯 Python，3.10–3.12 通用） |
| 安装与使用说明 | `docs/harmonyos-pc.md` |
| 移植报告与已知问题 | 本文件 |
| 环境说明与安装步骤 | `docs/harmonyos-pc/PYTHON_ENVIRONMENT.md` |
| 依赖清单与兼容矩阵 | `requirements-harmonyos.txt`、`docs/harmonyos-pc/DEPENDENCY_MATRIX.md` |
| 数值对比报告 | `docs/harmonyos-pc/REFERENCE_COMPARISON.md` |
| 环境检测脚本 / 安装脚本 | `scripts/check_environment.py`、`scripts/install_dependencies_harmonyos.py` |
| 自动化测试 | `tests/`（7 项）、`scripts/tests/`（75 项） |
| 当前环境实测证据 | `artifacts/revalidation/harmonyos-pc/2026-10-07-ohos-runtime/` |
| 源码兼容性说明 | `SOURCE_COMPATIBILITY.md` |
