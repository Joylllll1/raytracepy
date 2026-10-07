# 安装包与验证记录

2026-10-07 基于 `8c8f2ef` 的包源码重建，已纳入 PR #4 的 JIT 守卫和
PR #7 的 SciPy/NumPy 兼容修复。版本号保持 0.0.1；同名文件替换了旧包，
使用 `SHA256SUMS` 核对具体产物。

| 文件 | 内容 |
|---|---|
| `raytracepy-0.0.1-py3-none-any.whl` | 最新 wheel，包含全部 18 个包内 Python 文件 |
| `raytracepy-0.0.1.tar.gz` | 最新源码包；默认构建流程从该源码包生成 wheel |
| `SHA256SUMS` | 两个安装包的 SHA-256，从仓库根目录执行 `sha256sum -c artifacts/release/SHA256SUMS` |
| `verification/build.log` | 本地构建日志，退出码 0 |
| `verification/wheel-install.log` | 独立 venv 安装 wheel 的日志，退出码 0 |
| `verification/package-check.log` | 包内容、已安装文件、CDF 功能和历史直方图核验 |
| `verification/pytest.log` | 新 wheel 下的现有测试：82 passed、44 subtests passed |
| `verification/pip-check.log` | 本地依赖一致性检查，无缺失或冲突 |
| `verification/environment.json` | 本地平台、Python/依赖版本、源码哈希、产物哈希和验证范围 |
| `verification/installed-packages.txt` | 本地验证 venv 的包清单 |

本次验证环境为 macOS arm64 / CPython 3.12.14，运行时显式设置
`NUMBA_DISABLE_JIT=1`。核心计算依赖与设备记录同版，Python、平台二进制及部分
传递依赖不同，具体版本见 `verification/environment.json`。

安装后确认 `raytracepy.__file__` 位于独立 venv 的 `site-packages`，全部包内
Python 文件与源码一致；CDF 功能通过解析解检查。历史 Windows 与鸿蒙
直方图数据重新核验一致，但没有重新在鸿蒙设备执行仿真。

**最新包的鸿蒙设备复测待完成**；这些本地结果不代表设备验收已通过。
操作步骤见 `docs/harmonyos-pc/REVALIDATION.md`。解释器来源、关闭 JIT 的交付
方式和性能要求仍待老师确认。
