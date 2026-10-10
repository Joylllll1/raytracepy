# 鸿蒙 PC 安装与使用说明

RayTracePy 0.0.1 在鸿蒙 PC（HarmonyOS 6.1.0 / aarch64，HUAWEI MateBook Pro HAD-W32）
上的安装、验证与使用方式。

**2026-10-10 更新**：目标环境已切换为**官方"鸿蒙化" CPython 3.12.9**
（OpenHarmony PC Developer 社区发布，目标三元组 `aarch64-unknown-linux-ohos`）。
在该环境上已实测：安装、导入、pytest 7 项全过、官方示例跑通、300 万光线参考负载
与 Windows 参考逐位一致，**numba JIT 正常工作**。

- 环境说明与安装细节：`docs/harmonyos-pc/PYTHON_ENVIRONMENT.md`
- 依赖清单与兼容矩阵：`requirements-harmonyos.txt`、`docs/harmonyos-pc/DEPENDENCY_MATRIX.md`
- 实测证据：`artifacts/revalidation/harmonyos-pc/2026-10-07-ohos-runtime/`
- 参考环境：Windows AMD64 + CPython 3.10.21（见 `docs/testing/REFERENCE_BASELINE.md`）

## 一、环境要求

| 项目 | 要求 |
|---|---|
| 系统 | HarmonyOS 6.1.0（API 23），aarch64，HongMeng Kernel 1.12.0 |
| Python | **官方鸿蒙化 CPython 3.12.9**（`ohos-aarch64`，装于 `~/usr/local`） |
| pip 源 | 社区源 `pypi.cnb.cool`（安装器自动配置） |
| numpy | 固定 **< 2.0**（源码仍使用 `np.trapz`），推荐 1.26.3 |
| 其它依赖 | 见 `requirements-harmonyos.txt` |

## 二、安装

```bash
# 1) 官方鸿蒙化 Python 运行时（装到 ~/usr/local，自动配置 pip 社区源）
curl -fsSL https://gitcode.com/OpenHarmonyPCDeveloper/cmd-pkgs/releases/download/pkgs/install-python.sh | sh -s -- 3.12.9

# 2) 新建独立 venv
cd <repo>
~/usr/local/bin/python3 -m venv .venv-ohos

# 3) 安装依赖（必须 --prefer-binary，且固定版本）
.venv-ohos/bin/python -m pip install --prefer-binary \
  numpy==1.26.3 scipy==1.15.3 pandas==2.3.1 numba==0.65.1 llvmlite==0.47.0 \
  plotly==7.1.0 datashader==0.19.1 pytest==9.1.1 pytest-cov==7.1.0

# 4) 安装本项目（源码可编辑安装，或安装 artifacts/release/ 里的 wheel）
.venv-ohos/bin/python -m pip install -e .
```

也可以一条命令：`scripts/install_dependencies_harmonyos.py`。

**为什么必须 `--prefer-binary`**：pip 会在"社区源 + 备用源"间取最高版本，备用源更新的
源码包会盖掉社区源的 ohos wheel（实测 matplotlib 会因此构建失败）。

## 三、验证安装

```bash
cd <repo>
.venv-ohos/bin/python scripts/check_environment.py     # 期望 RESULT: OK（可能提示缺 setuptools/wheel）
.venv-ohos/bin/python -m pytest -q tests/ -o addopts=''  # 期望 7 passed
```

与旧环境不同：**不再需要 `NUMBA_DISABLE_JIT=1`**，JIT 正常工作。

## 四、运行官方示例

```bash
cd <任意输出目录>
<repo>/.venv-ohos/bin/python <repo>/examples/single/single_light.py
```

2026-10-10 实测：退出码 0，生成 `single_led.html`（169 KB）。

## 五、常见问题

| 现象 | 原因 | 处理 |
|---|---|---|
| 依赖装成了源码包并构建失败 | 备用源的高版本 sdist 盖过社区源 wheel | 加 `--prefer-binary`，并固定版本 |
| `import datashader` 报错 | 装了 dask | **不要装 dask**；`datashader 0.19.1` 已不依赖它（旧版 0.16.x 与新 dask 不兼容） |
| `AttributeError: np.trapz` | 装了 numpy 2.x | 固定 `numpy==1.26.3` |
| 末尾出现 `start: not found` | 示例用 Windows 命令自动打开 HTML | 可忽略，HTML 已生成 |
| 想跑纯 Python 路径 | 调试/对比用 | `NUMBA_DISABLE_JIT=1` 仍然有效（源码守卫保留） |

## 六、应用形态与上架（进行中）

需要说明：**RayTracePy 本身是 Python 库**（无界面、无入口），无法直接"上架"，
上架的必须是基于它的**应用**。老师的方向是"上架并可正常使用"。

- 可用的 GUI 工具链（社区源有鸿蒙原生 wheel）：**tkinter 3.12.9.post1 + matplotlib 3.11.1**；
  PySide/PyQt 在社区源里**没有**鸿蒙 wheel。
- 待定：应用形态（命令行工具 / 桌面小工具）与上架流程，确认后按
  《开源应用上架指南》执行。

## 七、相关文档

| 文档 | 内容 |
|---|---|
| `docs/harmonyos-pc/PYTHON_ENVIRONMENT.md` | 环境说明、安装步骤、版本矩阵、踩坑记录 |
| `docs/harmonyos-pc/DEPENDENCY_MATRIX.md` | 依赖兼容矩阵 |
| `docs/harmonyos-pc/REFERENCE_COMPARISON.md` | 参考环境与目标环境的数值对比 |
| `docs/harmonyos-pc/REVALIDATION.md` | 安装包设备复测步骤与结果 |
| `PORTING_REPORT.md` | 移植报告与已知问题 |
| `SOURCE_COMPATIBILITY.md` | 源码兼容性说明 |

> 历史环境（2026-09-25 ~ 10-07 使用的自建 Alpine CPython 3.10 + ELF 修补 + shim 方案）
> 已被官方运行时取代，说明见 `PYTHON_ENVIRONMENT.md` 第六节；`scripts/harmonyos/`
> 中的相关工具保留作历史记录，新环境不再需要。
