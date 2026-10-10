# 最新安装包设备复测（历史记录）

> **2026-10-10 更新**：本文描述的是**自建 Alpine Python 3.10 环境**下的安装包复测。
> 目标环境已切换为官方"鸿蒙化" CPython 3.12.9，当前复测记录见
> `artifacts/revalidation/harmonyos-pc/2026-10-07-ohos-runtime/` 与
> `PORTING_REPORT.md` 第五、六节。本文保留作为历史操作说明。

2026-10-07 的 wheel/sdist 已纳入 PR #7 的 SciPy/NumPy 修复。
构建与本地验证在 macOS / CPython 3.12 上执行；**鸿蒙设备复测已于 2026-10-07 完成**，
结果见下节，日志归档在 `artifacts/revalidation/harmonyos-pc/2026-10-07/`。
以下步骤保留为可重复的操作说明。

## 复测结果（2026-10-07，已完成）

设备：HUAWEI MateBook Pro（HAD-W32），HarmonyOS 6.1.0，aarch64；
commit `e516b5f`；CPython 3.10.15 / scipy 1.15.3 / numpy 1.26.4 / numba 0.61.2。

| 步骤 | 结果 |
|---|---|
| `sha256sum -c artifacts/release/SHA256SUMS` | wheel 与 sdist 均 OK |
| 全新 venv + `install_dependencies_harmonyos.py --skip-raytracepy` | 退出码 0 |
| 安装最新 wheel（`--force-reinstall --no-deps`） | 退出码 0 |
| 导入校验（位于新 venv 的 `site-packages`；`generate_cdf` 与解析解一致） | 通过 |
| `NUMBA_DISABLE_JIT=1 pytest -q tests/ scripts/tests/` | **82 passed, 44 subtests passed** |
| `scripts/check_environment.py` | `RESULT: OK_WITH_WARNINGS`（仅缺 `wheel` 构建工具，与运行无关） |
| 300 万光线参考负载（`--verify-repeat`） | hit_count 1923054；`histogram_sha256` **与 Windows 参考逐位一致**；62.19 s；`repeat_identical=True` |
| 官方示例 `examples/single/single_light.py` | 退出码 0，生成 `single_led.html` |

据此，`PROJECT_PROGRESS.md` 与 `PORTING_REPORT.md` 已更新；最终交付 commit 定为 `e516b5f`。
仍待老师确认的只有解释器来源、关闭 JIT 的交付方式与性能要求。


## 复测前记录

确认老师是否接受 Alpine 构建、在鸿蒙原生执行的解释器，以及关闭 Numba JIT
的交付方式；同时确认是否有性能指标。记录答复日期与原文，未收到答复前保持
“待确认”，不要将项目自设的数值容差写成老师确认的标准。

在已准备好 CPython 3.10.15 和环境工具的鸿蒙设备上使用最新仓库。
以下使用独立 venv；如目录已经存在，换一个新的目录名。历史
`artifacts/reference/` 和 `artifacts/environment/harmonyos-pc/` 保留不动。

```bash
cd <repo>
mkdir -p artifacts/revalidation/harmonyos-pc/2026-10-07
git rev-parse HEAD > artifacts/revalidation/harmonyos-pc/2026-10-07/commit.txt
git status --short > artifacts/revalidation/harmonyos-pc/2026-10-07/worktree.txt
sha256sum -c artifacts/release/SHA256SUMS
sha256sum artifacts/release/raytracepy-0.0.1-py3-none-any.whl \
  > artifacts/revalidation/harmonyos-pc/2026-10-07/wheel.sha256
python -m venv .venv-device-revalidation
source .venv-device-revalidation/bin/activate
```

记录设备型号、系统版本、解释器来源和 `python -V`；包哈希须与仓库清单一致。
全新 venv 验证以已有解释器为前提，不能据此声称裸设备从零安装已通过。

## 安装最新 wheel

使用设备已有的 `~/.local/ohos-python-tools/`（含签名工具、wheel 和 shim），
按既有安装脚本准备依赖。安装脚本必须带 `--skip-raytracepy`，防止装成源码版本。
以下日志由 shell 重定向保存；每条命令执行后检查退出码，非 0 时停止并排查。

```bash
python scripts/install_dependencies_harmonyos.py --skip-raytracepy \
  > artifacts/revalidation/harmonyos-pc/2026-10-07/dependencies.log 2>&1
echo $?
python -m pip install --force-reinstall --no-deps \
  artifacts/release/raytracepy-0.0.1-py3-none-any.whl \
  > artifacts/revalidation/harmonyos-pc/2026-10-07/wheel-install.log 2>&1
echo $?
python -m pip freeze > artifacts/revalidation/harmonyos-pc/2026-10-07/installed-packages.txt
NUMBA_DISABLE_JIT=1 python -c 'import raytracepy, numba; from raytracepy.ref_data.utils_ref_data import generate_cdf; import numpy as np; from pathlib import Path; import sys; p=Path(raytracepy.__file__).resolve(); assert p.is_relative_to(Path(sys.prefix).resolve()) and "site-packages" in p.parts, p; assert numba.config.DISABLE_JIT; x,cdf=generate_cdf(lambda x: np.ones_like(x)); assert len(cdf)==11 and cdf[0]==0 and np.isclose(cdf[-1],1); print("wheel import and CDF OK:",p)' \
  > artifacts/revalidation/harmonyos-pc/2026-10-07/wheel-import.log 2>&1
echo $?
```

`raytracepy.__file__` 须位于新 venv 的 `site-packages`，以确认测试的是安装包。
同一版本号 0.0.1 已重新构建，使用包哈希区分旧包与新包。

## 测试与完整负载

```bash
NUMBA_DISABLE_JIT=1 python -m pytest -q tests/ scripts/tests/ -o addopts='' \
  > artifacts/revalidation/harmonyos-pc/2026-10-07/pytest.log 2>&1
echo $?
python scripts/check_environment.py \
  --output artifacts/revalidation/harmonyos-pc/2026-10-07/environment.json \
  > artifacts/revalidation/harmonyos-pc/2026-10-07/environment.log 2>&1
echo $?
NUMBA_DISABLE_JIT=1 python scripts/generate_reference_baseline.py \
  --input tests/fixtures/single_light_reference_input.json \
  --output-dir artifacts/revalidation/harmonyos-pc/2026-10-07/reference-comparison \
  --verify-repeat
echo $?
```

对比新生成的 `single_light_metrics.json` 和 Windows 参考：整数计数与直方图哈希
应一致，浮点统计按仓库的 `rtol=1e-6` / `atol=1e-8` 核验。
`--expected-output` 是输出参数，不能指向已有参考文件。
环境检测的简单 JIT 探针通过，不能作为包自身 JIT 可用的证明。

另在新建的输出目录运行官方示例，保存标准输出、标准错误、退出码与 HTML：

```bash
RAYTRACEPY_REPO="$PWD"
mkdir -p artifacts/revalidation/harmonyos-pc/2026-10-07/example-run
cd artifacts/revalidation/harmonyos-pc/2026-10-07/example-run
NUMBA_DISABLE_JIT=1 python "$RAYTRACEPY_REPO/examples/single/single_light.py" > example-run.log 2>&1
echo $? > exit-code.txt
```

核验退出码为 0，`single_led.html` 已生成且可打开。末尾 `start: not found`
来自自动打开 HTML 的 Windows 命令；它不等于仿真失败，但仍需检查输出文件。

## 完成后归档

将上述版本、包哈希、日志、数值对比和 HTML 归档；在 `PROJECT_PROGRESS.md`
勾选最新包复测完成，在 `PORTING_REPORT.md` 写明设备、日期和实际结果。
记录老师确认的验收要求后，再确定最终交付 commit。
