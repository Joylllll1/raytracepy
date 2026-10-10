# 鸿蒙 PC 依赖兼容矩阵（4号）

- 日期：2026-09-26（1号 于 2026-09-28、2026-10-10 补充实测）
- 当前环境：**官方"鸿蒙化" CPython 3.12.9**（`ohos-aarch64`，`~/usr/local`）+ 项目 `.venv-ohos`
- 历史环境：自建 Alpine CPython 3.10.15（已不再使用，见 `PYTHON_ENVIRONMENT.md` 第六节）
- 证据：`artifacts/revalidation/harmonyos-pc/2026-10-07-ohos-runtime/`

## 一、兼容矩阵（2026-10-10 实测）

| 包 | 参考 | 当前目标 | 来源 | import | 状态 |
|---|---|---|---|---|---|
| numpy | 1.22.0 | 1.26.3 | 社区源 `cp312-ohos_aarch64` wheel | OK | 可用；固定 <2（源码仍用 `np.trapz`） |
| scipy | 1.10.0 | 1.15.3 | 社区源 wheel | OK | 可用（版本偏离） |
| pandas | 1.4.1 | 2.3.1 | 社区源 wheel | OK | 可用（版本偏离） |
| numba | 0.56.4 | 0.65.1 | 社区源 wheel | OK | **JIT 正常执行**（无需关闭） |
| llvmlite | 0.39.1 | 0.47.0 | 社区源 wheel | OK | 可用（随 numba） |
| plotly | 5.6.0 | 7.1.0 | 纯 Python | OK | 可用（官方示例已验证） |
| datashader | 0.13.0 | 0.19.1 | 纯 Python | OK | 可用（仅 `examples/` 使用，库本身不依赖） |
| matplotlib / tkinter | — | 3.11.1 / 3.12.9.post1 | 社区源 wheel | OK | 应用形态（GUI）可用 |
| pytest / pytest-cov | 9.1.1 / 7.1.0 | 同左 | 纯 Python | OK | 可用 |
| raytracepy | 0.0.1 | 源码树 / wheel | — | OK | 可用，**JIT 开启** |

钉版本：`requirements-harmonyos.txt`。
安装：`python scripts/install_dependencies_harmonyos.py`（或见 `docs/harmonyos-pc.md` 第二节）。

## 二、与历史（Alpine）环境的差异

| 项 | 历史环境 | 当前环境 |
|---|---|---|
| 解释器三元组 | `aarch64-alpine-linux-musl` | **`aarch64-unknown-linux-ohos`**（真鸿蒙原生） |
| numba / llvmlite | 本地修补的 `linux_aarch64` wheel | 社区源 `cp312-ohos_aarch64` wheel |
| JIT | 执行段错误，只能纯 Python | **正常执行** |
| 额外步骤 | 需 `fixall.py`（签名）+ `add_stlshim.py` | **不需要**（无 ELF 修补、无 shim） |
| 性能（300 万光线） | 67.5 s（纯 Python） | **33.4 s**（JIT；Windows 参考 22.33 s，差异主要来自硬件） |

## 三、依赖兼容性发现（2026-10-10，重要）

1. **必须 `--prefer-binary`**：pip 在"社区源 + 备用源（清华/PyPI）"间取最高版本，
   备用源的更新源码包会盖掉社区源的 ohos wheel（实测 matplotlib 3.11.2 sdist 顶掉
   3.11.1 wheel，随后因缺 meson 构建失败）。
2. **不要安装 dask**：
   - `datashader 0.16.x + dask 2023.3.0` 在 Python 3.12 上导入即报错（dask 过旧）；
   - 新版 dask（2026.x）需要 `pyarrow`；
   - `datashader 0.19.1` 已不依赖 dask，因此直接不装。
   - 社区源也提供 `pyarrow-25.x-ohos_aarch64` wheel，当前不需要。
3. **numpy < 2**：源码仍使用 NumPy 2 已改名的 `np.trapz`
   （`src/raytracepy/ref_data/utils_ref_data.py`）。
4. **plotly 7.1.0**：官方示例 `examples/single/single_light.py` 在其上正常运行
   （退出码 0，生成 HTML）。

## 四、Windows 专用产物

`src/raytracepy/compile/math_custom.cp310-win_amd64.pyd` 为 Windows/AMD64 二进制，
目标环境不可用；该目录未被任何代码引用，**不影响导入与运行**。

## 五、未决

| 问题 | 谁 |
|---|---|
| 应用形态与上架流程 | 1号 / 老师 |
| NumPy 2.x、新版 datashader 的完整回归 | 4号 |
