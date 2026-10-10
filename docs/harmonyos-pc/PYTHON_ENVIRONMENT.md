# 鸿蒙 PC Python 环境说明

- 整理：1号（在目标设备上实测）
- 日期：2026-10-07 首版（Alpine 方案）；**2026-10-10 更新：改用官方鸿蒙化运行时**
- 设备：HUAWEI MateBook Pro（HAD-W32），HarmonyOS 6.1.0，API 23，aarch64，32 GB
- 相关文档：`docs/harmonyos-pc.md`（安装使用）、`DEPENDENCY_MATRIX.md`（依赖矩阵）、
  `../../artifacts/revalidation/harmonyos-pc/2026-10-07-ohos-runtime/`（实测证据）

## 一、结论

目标环境已切换为**官方"鸿蒙化" CPython 3.12.9**（OpenHarmony PC Developer 社区发布），
为鸿蒙原生构建：

| 项目 | 值 |
|---|---|
| 平台标识 | `ohos-aarch64` |
| 目标三元组 | `aarch64-unknown-linux-ohos` |
| 扩展后缀 | `.cpython-312-aarch64-linux-ohos.so` |
| 安装位置 | `~/usr/local`（自带 pip，自动配置社区源） |

实测结论：**raytracepy 可正常安装、导入、跑测试与官方示例，numba JIT 正常工作**，
计算结果与 Windows 参考环境逐位一致。此前在自建 Alpine 环境上出现的 JIT 段错误、
需要 ELF 修补/签名/shim 等问题**均已消失**。

## 二、安装（已实测）

```bash
# 1) 安装官方运行时（默认装到 ~/usr/local，并自动配置社区 pip 源）
curl -fsSL https://gitcode.com/OpenHarmonyPCDeveloper/cmd-pkgs/releases/download/pkgs/install-python.sh | sh -s -- 3.12.9

# 2) 建独立 venv（不要复用旧的 Alpine venv）
cd <repo>
~/usr/local/bin/python3 -m venv .venv-ohos

# 3) 安装依赖：必须加 --prefer-binary，并固定版本
.venv-ohos/bin/python -m pip install --prefer-binary \
  numpy==1.26.3 scipy==1.15.3 pandas==2.3.1 numba==0.65.1 llvmlite==0.47.0 \
  plotly==7.1.0 datashader==0.19.1 pytest==9.1.1 pytest-cov==7.1.0

# 4) 安装本项目
.venv-ohos/bin/python -m pip install -e .
```

也可以直接运行 `python scripts/install_dependencies_harmonyos.py`（内部按上述顺序执行）。

## 三、版本矩阵（实测）

| 组件 | 版本 | 来源 |
|---|---|---|
| Python | 3.12.9（ohos-aarch64） | 社区官方安装器 |
| pip | 26.2.1 | 安装器自带 |
| numpy | 1.26.3 | 社区源 `cp312-ohos_aarch64` wheel |
| scipy | 1.15.3 | 社区源 wheel |
| pandas | 2.3.1 | 社区源 wheel |
| numba | 0.65.1 | 社区源 wheel |
| llvmlite | 0.47.0 | 社区源 wheel |
| plotly | 7.1.0 | 纯 Python |
| datashader | 0.19.1 | 纯 Python（**不再依赖 dask**） |
| matplotlib / tkinter | 3.11.1 / 3.12.9.post1 | 社区源 wheel（应用形态用） |
| pytest / pytest-cov | 9.1.1 / 7.1.0 | 纯 Python |

## 四、验证结果（2026-10-10 实测）

| 项目 | 结果 |
|---|---|
| JIT | ✅ 正常执行（`numba.config.DISABLE_JIT = 0`，冒烟仿真结果与预期 sha256 逐位一致） |
| 自动化测试 | `pytest -q tests/` → **7 passed**（JIT 开启） |
| 300 万光线参考负载 | hit_count 1923054、`histogram_sha256` **与 Windows 参考逐位一致**、**33.40 s**、`repeat_identical=True` |
| 官方示例 | `examples/single/single_light.py` 退出码 0，生成 `single_led.html`（169 KB） |
| 环境检测 | `RESULT: OK_WITH_WARNINGS`（仅提示未装 `setuptools`/`wheel` 构建工具） |
| 性能对比 | Windows 参考 22.33 s；本设备 33.40 s（约 1.5 倍，差异主要来自硬件） |

## 五、安装时踩过的坑（重要）

1. **必须 `--prefer-binary`**：pip 会在"社区源 + 备用源（清华/PyPI）"之间取最高版本，
   备用源的新源码包会顶掉社区源的 ohos wheel（实测 matplotlib 3.11.2 sdist 顶掉 3.11.1 wheel，
   随后因缺 meson 构建失败）。
2. **不要装 dask**：
   - `datashader 0.16.x + dask 2023.3.0` 在 Python 3.12 上导入即报错（dask 太旧）；
   - 新版 dask（2026.x）又需要 `pyarrow`；
   - `datashader 0.19.1` 已不再依赖 dask，因此直接不装 dask 即可（社区源也有
     `pyarrow-25.x-ohos_aarch64` wheel，但当前不需要）。
3. **numpy 必须 <2**：源码仍使用 NumPy 2 已改名的 `np.trapz`
   （`ref_data/utils_ref_data.py`）。

## 六、历史环境（已不再使用）

2026-09-25 ~ 10-07 期间使用过一套自建方案：Alpine 3.10.15 的 CPython 3.10.15 +
`patchelf` 修补 + ELF 签名 + 两个兼容 shim + 设备专用 numba/llvmlite wheel
（工具归档在 `scripts/harmonyos/`，apk 见 Release 附件）。该方案能跑通，但：

- 解释器不是为鸿蒙编译的（`aarch64-alpine-linux-musl`）；
- numba JIT 执行段错误，只能跑纯 Python 路径（约 3 倍耗时）。

**该方案已被官方鸿蒙化运行时取代**，`scripts/harmonyos/` 中的工具保留作历史记录，
新环境不再需要。

## 七、待办

- 应用形态与上架流程（老师要求"上架可正常使用"，见 `docs/harmonyos-pc.md`）；
- 是否需要支持 NumPy 2.x / 新版 datashader 的完整回归。
