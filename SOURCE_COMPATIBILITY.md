# RayTracePy 源码兼容性说明

## 鸿蒙 PC

RayTracePy 的主计算路径使用 Numba `@njit`。**在官方的鸿蒙化 CPython 3.12.9 运行时上，
JIT 工作正常**（2026-10-10 实测：冒烟仿真与 300 万光线参考负载均正常执行，结果与
Windows 基准逐位一致）。因此现在**不需要**关闭 JIT：

```sh
~/usr/local/bin/python3 -m venv .venv-ohos   # 官方鸿蒙化运行时
.venv-ohos/bin/python examples/single/single_light.py
```

早期（2026-09 ~ 10-07）在自建 Alpine 环境上曾出现"JIT 能编译但执行段错误"，
原因是那套环境经过 ELF 修补并挂了兼容 shim；换用官方运行时后该问题消失。

`raytracepy` 仍保留 PR #4 的守卫：不再覆盖用户显式设置的 `NUMBA_DISABLE_JIT`，
默认行为不变。这样在需要对比纯 Python 路径时仍可用
`NUMBA_DISABLE_JIT=1`（**已非必需**，仅用于调试/性能对比）。

仓库中的 `math_custom.cp310-win_amd64.pyd` 仅适用于 Windows x86-64，不能作为
鸿蒙 ARM 二进制直接复用。`compile/` 下现有的 pycc 示例也没有覆盖
`create_rays`/`trace_rays` 主路径，因此不能宣称它是现成的 JIT 替代后端。

## 依赖 API 兼容性

- SciPy 1.14 起移除了 `scipy.integrate.cumtrapz`，源码已改用
  `cumulative_trapezoid(..., initial=0)`，保持原有输出长度和初始值。
- NumPy 2.0 移除了 `np.NaN`，源码已改用 `np.nan`。
- 安装依赖将 NumPy 上限固定为 `<2.0`，作为当前移植环境的保守约束；后续若
  需要支持 NumPy 2.x，应再进行完整回归测试。

## 历史设备验证说明

以下为 PR #7 随附的设备验证说明，未附独立原始日志。
2026-10-07 本地重建包的验证另存于 `artifacts/release/verification/`；
最新包的鸿蒙设备完整复测尚未完成。

已在鸿蒙 PC 的项目虚拟环境（CPython 3.10.15 / scipy 1.15.3 / numpy 1.26.4 /
numba 0.61.2）实测：

| 项目 | 结果 |
|---|---|
| `import raytracepy.ref_data.utils_ref_data` | 修复前 `ImportError: cannot import name 'cumtrapz'`，修复后正常 |
| `generate_cdf()` | 正常（长度 11，`cdf[0]=0.0`，`cdf[-1]=1.0`） |
| `cumulative_trapezoid(..., initial=0)` 与旧 `cumtrapz` + `np.insert` 等价性 | **逐位一致**（最大差 0.0） |
| `NUMBA_DISABLE_JIT=1 pytest -q tests/` | 7 passed |

说明：

- `utils_ref_data` 目前只被 `ref_data/ground_glass_diffuser.py` 与
  `ref_data/led.py` 的 `local_run()` 辅助函数引用，不影响主仿真与示例路径；
  但作为包内模块，在 scipy ≥1.14 环境下导入即失败，属真实缺陷。
- 保留 `numpy<2.0` 上限作为当前验证范围的约束：源码仍使用 `np.trapz`
  （`ref_data/utils_ref_data.py`），且未完成 NumPy 2.x 回归；修复 `np.NaN`
  本身不能证明整个包已兼容 NumPy 2.x。
- `NUMBA_DISABLE_JIT` 守卫沿用 PR #4 已合并的实现，本次不重复改动
  `src/raytracepy/__init__.py`。

## 2026-10-07 本地新包验证

在 macOS arm64 / CPython 3.12.14 的独立 venv 安装重建 wheel，核心依赖使用
numpy 1.26.4、scipy 1.15.3、pandas 2.2.3、numba 0.61.2、llvmlite 0.44.0。
`generate_cdf(2*x)` 返回 11 点、初值 0、终值 1，并与解析解 `x**2` 在
`rtol=1e-14` / `atol=1e-15` 内一致。现有测试合计 82 passed、44 subtests passed。
wheel/sdist 的 18 个包内 Python 文件及已安装文件均与当前源码一致，
日志见 `artifacts/release/verification/`。这些结果不代替鸿蒙设备复测。
