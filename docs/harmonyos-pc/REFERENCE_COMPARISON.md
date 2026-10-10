# 参考环境与目标环境数值对比

- 负责人：2号（由 1号 在目标设备实测执行）
- 日期：2026-09-26 首版；**2026-10-10 更新为官方鸿蒙运行时**
- 负载：`tests/fixtures/single_light_reference_input.json`
  （`examples/single/single_light.py` 的完整 300 万光线工作量，`seed=20260920`）
- 参考结果：`artifacts/reference/windows-python310/`
- 目标结果：`artifacts/revalidation/harmonyos-pc/2026-10-07-ohos-runtime/reference-comparison/`

## 一、两个环境

| | 参考环境 | 目标环境 |
|---|---|---|
| 系统 | Windows 10（AMD64） | HarmonyOS 6.1.0（aarch64，HAD-W32） |
| Python | CPython 3.10.21 | **官方鸿蒙化 CPython 3.12.9**（`ohos-aarch64`） |
| numpy / numba | 1.22.0 / 0.56.4 | 1.26.3 / 0.65.1 |
| numba JIT | 开启 | **开启**（官方运行时上 JIT 正常） |
| 执行命令 | 见 `docs/testing/REFERENCE_BASELINE.md` | `python scripts/generate_reference_baseline.py --input tests/fixtures/single_light_reference_input.json --output-dir <dev> --verify-repeat` |

## 二、结果对比

| 指标 | 参考（Windows，JIT 开） | 目标（鸿蒙，JIT 开） | 判定 |
|---|---|---|---|
| total_rays | 3,000,000 | 3,000,000 | 一致 |
| hit_count | 1,923,054 | 1,923,054 | 一致 |
| miss_count | 1,076,946 | 1,076,946 | 一致 |
| hit_rate | 0.641018 | 0.641018 | 一致 |
| histogram_shape | [99, 99] | [99, 99] | 一致 |
| histogram_sum | 1,923,054 | 1,923,054 | 一致 |
| **histogram_sha256** | `bacd25e6…d0cc677` | `bacd25e6…d0cc677` | **逐位一致** |
| 直方图 min/1%/5%/10%/mean/std/90%/95%/99%/max | 见 metrics | 同左 | 一致 |
| hit_coordinate_max | 见 metrics | 同左 | 一致 |
| 运行耗时 | 22.33 s | **33.40 s** | 1.50 倍（主要是硬件差异） |
| repeat_identical（同环境重复运行） | True | True | 一致 |

## 三、浮点字段差异

逐字段比对后，**8 个浮点字段存在末位差异**（JIT 与参考的求和顺序不同）：

| 字段 | 参考 | 目标 | 绝对差 |
|---|---|---|---|
| hit_coordinate_mean[0] | 0.0007782921386433898 | 0.0007782921386433935 | 3.7e-18 |
| hit_coordinate_mean[1] | 0.004137619690995617 | 0.004137619690995643 | 2.6e-17 |
| hit_coordinate_mean[2] | 3.7e-21 | −3.0e-20 | 3.3e-20（两值均≈0） |
| hit_coordinate_min[0] | −9.999990942736803 | −9.999990942736805 | 1.8e-15 |
| hit_coordinate_min[1] | −9.99999811080813 | −9.999998110808132 | 1.8e-15 |
| hit_coordinate_std[0] | 4.073943230668654 | 4.073943230668653 | 8.9e-16 |
| hit_coordinate_std[1] | 4.074552095925623 | 4.074552095925624 | 8.9e-16 |
| hit_coordinate_std[2] | 1.2879190611469105e-16 | 1.2906870730497057e-16 | 2.8e-19（两值均≈0） |

其余字段（含整数计数、直方图全部统计量与哈希）**完全相同**。
最大绝对差 1.8e-15，相对差约 1.8e-16。

阈值对照：仓库自设的跨环境容差为 `rtol=1e-6` / `atol=1e-8`
（见 metrics 中的 `comparison_policy`），本次实测**远优于阈值**。

## 四、结论

1. 目标环境的计算结果与参考环境**一致**：整数计数与直方图哈希逐位相同，
   浮点统计量差异在 1e-15 量级，远优于仓库设定的数值容差。
2. 官方鸿蒙运行时上 **JIT 正常工作**，耗时 33.40 s（参考 22.33 s，约 1.5 倍，
   差异主要来自硬件）。历史 Alpine 环境只能跑纯 Python 路径，同样负载需 67.53 s。
3. 同环境重复运行结果一致（`repeat_identical=True`），可用于后续回归。

> 历史记录（自建 Alpine 环境、纯 Python 路径）的对比数据已在仓库清理时移除，
> 如需查阅可从 git 历史找回（清理前提交见 `PORTING_REPORT.md`）。
