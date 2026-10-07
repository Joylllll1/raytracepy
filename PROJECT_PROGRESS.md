# RayTracePy 鸿蒙 PC 移植进度

状态统一使用：`未开始`、`进行中`、`阻塞`、`待审核`、`已完成`。

2026-10-07 更新：PR #1–#8 已合并，历史设备验证记录已归档。
本次重新打包并在 macOS 上核验，最新安装包的鸿蒙设备复测尚未完成；
解释器来源和关闭 JIT 的方案仍待老师确认。复测步骤见 `docs/harmonyos-pc/REVALIDATION.md`。
本地安装新 wheel 后，`tests/` 与 `scripts/tests/` 合计 82 passed、44 subtests passed；
包内 18 个 Python 文件与源码一致，CDF 功能验证通过，日志见 `artifacts/release/verification/`。

| 负责人 | 工作项 | 分支 | 截止节点 | 状态 | PR / 结果 |
|---|---|---|---|---|---|
| 1号（组长） | 基线、仓库管理、PR 审核、最终集成 | `port/harmonyos-pc` | 第 10 天 | 进行中 | PR #1–#8 已合并；交付包已更新，待最新包设备复测与验收口径确认 |
| 2号 | 参考环境、固定输入输出、自动化测试 | `feature/baseline-tests` | 第 2 / 8 天 | 已完成 | 参考基线、fixtures、自动化测试和历史设备数值对比已完成；2026-10-07 重新核验归档直方图数据逐字节一致，见 `docs/harmonyos-pc/REFERENCE_COMPARISON.md` |
| 3号 | 鸿蒙原生 Python 环境检查 | `feature/python-environment` | 第 3 天 | 已完成 | PR #3 已合并。环境在设备上实测通过（检测脚本 `RESULT: OK`；`NUMBA_DISABLE_JIT=1` 时测试 7 passed）。所用 CPython 3.10.15 系 Alpine Linux 构建、**非为鸿蒙编译**（原生执行、无模拟层），验收标准待老师裁定，见 `docs/harmonyos-pc/PYTHON_ENVIRONMENT.md` 与探测报告第十、十一节 |
| 4号 | 依赖兼容矩阵和安装脚本 | `feature/dependencies-fix` | 第 4 / 9 天 | 已完成 | PR #5 已合并。依赖清单（含全部传递依赖）、兼容矩阵与安装脚本完成；安装脚本已在干净 venv 上端到端验证（`artifacts/dependencies/harmonyos-pc/install-script-verification.log`） |
| 5号 | 源码兼容性和官方示例 | `feature/harmonyos-delivery` | 第 7 天 | 已完成 | PR #4、#5、#7 已合并；包含 JIT 环境变量守卫、SciPy 积分 API 与 NumPy 常量命名适配，算法未改；官方示例有历史设备运行记录 |
| 6号 | 打包、安装文档、报告和演示 | `feature/harmonyos-delivery` | 第 9 天 | 进行中 | 文档和演示材料已归档；2026-10-07 重建 wheel/sdist 并核验最新源码，待新包设备复测；历史全新 venv 测试为 7 passed |

## 第一周检查点

- [x] 创建 `port/harmonyos-pc` 集成分支；
- [x] 确定源码、版本、许可证和项目范围；
- [x] 2号提交参考环境版本、示例输入输出和运行日志；
- [x] 3号确认鸿蒙 PC 系统、CPU 架构、原生 CPython 和 pip
      （探测已完成：系统 HarmonyOS 6.1.0、架构 aarch64 已确认；
      设备**不存在为鸿蒙编译的 CPython**，现用解释器为 Alpine Linux 构建、
      在设备上原生执行；环境已实测通过，见 `docs/harmonyos-pc/PYTHON_ENVIRONMENT.md`
      与探测报告第十、十一节）；
- [x] 4号提交主要依赖的安装与导入结果；
- [x] 5号确认 Windows 专用 `.pyd` 是否影响正常运行；
- [x] 第 5 天完成“继续移植 / 申请调整范围”的阶段结论（结论：继续移植，不申请调整范围）。

## 第二周检查点

- [x] 至少一个官方示例在鸿蒙 PC 上完整运行；
- [x] 参考环境与鸿蒙 PC 的数值结果完成对比；
- [x] PR #1–#8 已合并到 `port/harmonyos-pc`；
- [x] 历史版本在全新 venv 完成安装、导入和冒烟测试（7 passed）；
- [x] 安装包、测试报告、移植报告、已知问题和演示材料齐全；
- [x] 更新安装包，纳入 PR #7 源码兼容修复；
- [ ] 在鸿蒙设备全新 venv 中复测最新 wheel，保存版本、包哈希、测试和示例日志；
- [ ] 确认解释器、JIT 和性能的验收要求，记录老师答复；
- [ ] 设备复测与验收口径确认后，记录最终交付 commit。

## PR 规则

1. 每位成员只在按“姓名 + 功能”命名的个人分支工作；已经创建的分支保持原名，不必重新命名；
2. PR 目标分支统一为 `port/harmonyos-pc`；
3. PR 必须写明修改内容、测试方法、运行结果和遗留问题；
4. 通过相关负责人交叉验证和组长审核后再合并；
5. `master` 保留上游基线，项目验收完成前不合并鸿蒙专属改动。

## 每日汇报格式

```text
负责人：
今日完成：
验证证据（commit / PR / 日志）：
当前阻塞：
明日计划：
```

## 交付信息

- 仓库：https://github.com/Joylllll1/raytracepy
- 集成分支：`port/harmonyos-pc`
- 最终交付 commit：`e516b5f`（最新安装包已于 2026-10-07 在鸿蒙设备复测通过，
  见 `docs/harmonyos-pc/REVALIDATION.md` 与 `artifacts/revalidation/harmonyos-pc/2026-10-07/`）
- 已合并 PR：#1 打包子包修复、#2 参考基线、#3 环境探测与就绪、#4 JIT 守卫、
  #5 示例 / 数值对比 / 依赖 / 打包 / 文档、#6 环境工具归档与收尾、#7 源码兼容修复、
  #8 Release 附件与已知问题说明
- 源码适配：`NUMBA_DISABLE_JIT` 守卫、SciPy 积分 API、NumPy 常量命名，算法未改
- 主要交付物：`docs/harmonyos-pc.md`、`PORTING_REPORT.md`、`SOURCE_COMPATIBILITY.md`、
  `docs/harmonyos-pc/`、`requirements-harmonyos.txt`、`artifacts/release/`、
  `artifacts/environment/harmonyos-pc/`、`artifacts/dependencies/harmonyos-pc/`、
  `scripts/`（含 `scripts/harmonyos/` 环境工具）
- 环境工具补充：18 个 Alpine 3.10.15 包（44 MB）见 Release 附件
  `ohos-python-tools-apks.tar.gz`，sha256
  `16141c85a9546d70b55ee0df9c1dd91ecab4534fe419af05ffea0149bea07033`
- 安装包与验证记录：`artifacts/release/README.md`、`artifacts/release/verification/`（macOS 本地）、
  `artifacts/revalidation/harmonyos-pc/2026-10-07/`（鸿蒙设备复测）
- 待办：解释器来源（原生执行 / 是否为鸿蒙编译）、关闭 JIT 的交付方式与性能要求待老师确认
