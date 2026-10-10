# 演示脚本（约 5 分钟）

面向验收演示，在鸿蒙 PC 目标设备上执行。命令均已在设备上实测
（2026-10-10，官方鸿蒙化 Python 运行时）。

## 准备

```bash
cd <repo>
# 目标环境（官方鸿蒙化 Python 3.12.9）
.venv-ohos/bin/python -V
```

## 1. 环境（30 秒）

```bash
.venv-ohos/bin/python -c "import raytracepy, numpy, numba; print(raytracepy.__file__, numpy.__version__, numba.__version__)"
.venv-ohos/bin/python -c "import sysconfig; print(sysconfig.get_platform(), sysconfig.get_config_var('HOST_GNU_TYPE'))"
```

预期：`ohos-aarch64 aarch64-unknown-linux-ohos`（鸿蒙原生运行时）。

## 2. 环境自检（30 秒）

```bash
.venv-ohos/bin/python scripts/check_environment.py
```

预期结尾：`RESULT : OK_WITH_WARNINGS`、`blockers : none`
（可能提示未装 `setuptools`/`wheel` 构建工具，与运行无关）。

## 3. 自动化测试（1 分钟）

```bash
.venv-ohos/bin/python -m pytest -q tests/ -o addopts=''
```

预期：`7 passed`。**JIT 开启即可**，不需要 `NUMBA_DISABLE_JIT`。

## 4. 运行官方示例（2 分钟）

```bash
mkdir -p /tmp/demo && cd /tmp/demo
<repo>/.venv-ohos/bin/python <repo>/examples/single/single_light.py
```

预期：打印光线数与命中统计，退出码 0，生成 `single_led.html`。
实测产物见 `artifacts/revalidation/harmonyos-pc/2026-10-07-ohos-runtime/example-run/`。

## 5. 数值一致性（30 秒）

展示 `docs/harmonyos-pc/REFERENCE_COMPARISON.md`：

- 300 万光线参考负载，`histogram_sha256` 与 Windows 参考**逐位相同**；
- 浮点统计量最大绝对差 1.8e-15（阈值 1e-6 / 1e-8）；
- 设备 33.4 s vs Windows 22.3 s（约 1.5 倍，主要是硬件）。

## 6. 已知问题（30 秒）

| 问题 | 现状 |
|---|---|
| RayTracePy 是库、无界面 | 若要求"上架应用"，需在库之上另做一个应用（待确认） |
| numpy 固定 <2 | 源码仍使用 `np.trapz`（NumPy 2 已改名） |
| datashader 仅 `examples/` 使用 | 已适配 0.19.1；**不要安装 dask** |

## 演示材料清单

| 材料 | 位置 |
|---|---|
| 环境自检输出 | `artifacts/revalidation/harmonyos-pc/2026-10-07-ohos-runtime/environment.log` |
| 测试证据 | `artifacts/revalidation/harmonyos-pc/2026-10-07-ohos-runtime/pytest.log` |
| 示例运行日志 / 产出 | `.../example-run/example-run.log`、`.../example-run/single_led.html` |
| 300 万光线对比 | `.../reference-comparison/single_light_run.log` |
| 数值对比报告 | `docs/harmonyos-pc/REFERENCE_COMPARISON.md` |
| 参考环境对照产物 | `artifacts/reference/windows-python310/single_light_report.html` |
