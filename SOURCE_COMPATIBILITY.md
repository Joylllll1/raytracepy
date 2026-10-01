# RayTracePy 源码兼容性说明

## 鸿蒙 PC

RayTracePy 的主计算路径使用 Numba `@njit`。在当前鸿蒙 PC 环境中，Numba
可以导入并完成编译，但执行生成的 JIT 代码会导致段错误。因此运行示例或
测试前需要显式选择纯 Python 路径：

```sh
NUMBA_DISABLE_JIT=1 python examples/single/single_light.py
```

`raytracepy` 保留上游默认行为（未设置变量时启用 JIT），但不再覆盖用户显式
设置的 `NUMBA_DISABLE_JIT`。这使得同一份源码可以在支持 JIT 的平台上保持加速，
并在当前鸿蒙环境中安全运行。根据设备侧验证，300 万条光线的官方示例在回退
模式下可以完成，结果与 Windows 基准一致；JIT 本身仍属于平台限制，尚未适配。

仓库中的 `math_custom.cp310-win_amd64.pyd` 仅适用于 Windows x86-64，不能作为
鸿蒙 ARM 二进制直接复用。`compile/` 下现有的 pycc 示例也没有覆盖
`create_rays`/`trace_rays` 主路径，因此不能宣称它是现成的 JIT 替代后端。

## 依赖 API 兼容性

- SciPy 1.14 起移除了 `scipy.integrate.cumtrapz`，源码已改用
  `cumulative_trapezoid(..., initial=0)`，保持原有输出长度和初始值。
- NumPy 2.0 移除了 `np.NaN`，源码已改用 `np.nan`。
- 安装依赖将 NumPy 上限固定为 `<2.0`，作为当前移植环境的保守约束；后续若
  需要支持 NumPy 2.x，应再进行完整回归测试。

## 验证

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
- 保留 `numpy<2.0` 上限的原因：源码仍使用 NumPy 2.0 已改名的 `np.trapz`
  （`ref_data/utils_ref_data.py`），因此即使 `np.NaN` 已修正，仍建议暂时封顶。
- `NUMBA_DISABLE_JIT` 守卫沿用 PR #4 已合并的实现，本次不重复改动
  `src/raytracepy/__init__.py`。

