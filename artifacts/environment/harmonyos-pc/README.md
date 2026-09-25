# 目标设备环境探测证据

本目录保存 3号 对鸿蒙 PC 目标设备的环境探测证据。

## 文件

| 文件 | 说明 |
|---|---|
| `device_probe.log` | 在设备终端逐条执行命令的原始输出记录 |

## 采集信息

| 项目 | 值 |
|---|---|
| 采集人 | 3号 |
| 采集日期 | 2026-09-25 |
| 采集设备 | HUAWEI MateBook Pro（HAD-W32），HarmonyOS 6.1.0，aarch64 |
| 采集方式 | 设备自带终端（第三方应用 Alacritty）手动执行 |
| 采集内容 | 系统架构、PATH、Python / pip、编译工具、包管理器、文件系统、运行环境 |

设备序列号未记录在案。

## 结论

设备上不存在可供本项目使用的原生 CPython 运行时。完整分析见
`docs/harmonyos-pc/PYTHON_ENVIRONMENT_PROBE.md`。

## `scripts/check_environment.py` 的验证情况

该脚本由 3号 编写，为纯标准库实现。

已验证：

- 在 Windows AMD64 + CPython 3.13.13（未安装任何依赖）上运行，判定为
  `BLOCKED`，正确报告全部必需依赖缺失，并识别出 Windows 专用产物
  `math_custom.cp310-win_amd64.pyd`，退出码为 1。
- 在 Windows AMD64 + CPython 3.10.21（安装 `requirements-reference.txt`
  依赖）上运行，判定为 `OK_WITH_WARNINGS`，无阻塞项，`raytracepy` 可从
  `src/` 源码树成功导入。
- 输出的 JSON 键与 `artifacts/reference/windows-python310/environment.json`
  保持一致。

未能在目标设备上执行，原因是设备不存在 Python 解释器，详见
`device_probe.log` 第 [13] 节。该事实本身作为一条证据保留。
