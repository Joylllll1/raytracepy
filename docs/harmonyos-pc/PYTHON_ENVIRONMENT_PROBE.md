# 鸿蒙原生 Python 环境探测报告

- 负责人：3号
- 日期：2026-09-25
- 状态：阻塞

## 一、结论

目标设备上**不存在可供本项目使用的原生 CPython 运行时**。

该结论包含两层：

1. 经系统化探测，未发现任何 Python 解释器、包管理器或构建工具链。剩余不确定性仅存在于应用沙箱不可访问的系统目录中。
2. 该设备上的终端运行于应用沙箱内，即使系统隐藏分区中存在 Python，沙箱也无法访问，对本项目不可用。此点已经证据确认，结论确定。

因此，**"无可用运行时"的判定成立**，不依赖未访问目录的探测结果。

## 二、设备信息

| 项目 | 值 |
|---|---|
| 型号名称 | HUAWEI MateBook Pro |
| 型号代码 | HAD-W32 |
| HarmonyOS 版本 | 6.1.0 |
| 软件版本 | 6.1.0.117 (SP68C00E100R13P3) |
| 处理器 | HUAWEI Kirin X90 |
| CPU 架构 | aarch64 |
| 运行内存 | 32 GB |
| 内核版本 | HongMeng Kernel 1.12.0 |
| API 版本 | 6.1.0(23) |
| OpenHarmony 版本 | OpenHarmony 6.1 |
| 系统服务版本 | 6.23.0.100 |
| 安全补丁标签 | 2026/05/01 |

（设备序列号已省略，不写入公开文档。）

要点说明：

- **内核为 HongMeng Kernel，不是 Linux 内核**，因此常见 POSIX 工具不保证存在。
- 芯片为 Kirin X90，架构 aarch64，与预期一致。

## 三、探测环境

| 项目 | 值 |
|---|---|
| 终端程序 | Alacritty（第三方应用，非系统终端） |
| Shell | /bin/sh |
| 用户 | USER=100（非 root） |
| 家目录 | /storage/Users/currentUser |
| 当前目录 | /storage/Users/currentUser/Desktop |
| PATH | /usr/local/bin:/data/app/bin:/data/service/hnp/bin:/usr/bin:/vendor/bin |

## 四、探测结果

### 1. 系统架构

```
$ uname -m
aarch64
```

与 Kirin X90 一致。

### 2. PATH 内各目录存在性

```
$ ls /usr/local/bin
ls: /usr/local/bin: No such file or directory

$ ls /vendor/bin
ls: /vendor/bin: No such file or directory

$ ls /data/app/bin
ls: /data/app/bin: No such file or directory

$ ls /data/service/hnp/bin
ls: /data/service/hnp/bin: No such file or directory

$ ls /usr/bin
（存在，共约 100 项，完整清单见附录）
```

PATH 中 5 个目录，仅 `/usr/bin` 真实存在。

### 3. /usr/bin 内容核查

完整清单中不含以下任何一项：

- `python`、`python2`、`python3`
- 任何 `python3.x` 形式
- `pip`、`pip3`

已核查的具体名称：awk, base64, basename, bunzip2, bzcmp, bzdiff, bzegrep, bzfgrep, bzgrep, bzip2, bzip2recover, bzmore, cal, cat, chmod, cksum, clear, cmp, comm, count, cp, cpio, crc32, curl, cut, date, dd, df, diff, dirname, dos2unix, du, echo, egrep, env, expand, expr, factor, false, fgrep, file, find, flock, fmt, free, ftpget, ftpput, getconf, getfattr, grep, gunzip, gzip, head, help, hexedit, hidumper, hilog, hiperf, hiprofiler_cmd, hisysevent, hitrace, hostname, iconv, ifconfig, iotop, ipcs, join, kill, killall, ln, loh, ls, lsattr, lsmod, mcookie, md5sum, mkdir, mkpasswd, mktemp, more, mount, mountpoint, mv, netcat, netstat, nl, nohup, nproc, od, openssl, param, paramshell, paste, patch, pgrep, pidof, ping, ping6, pkill, pr, printenv, printf, ps, pwd, pwdx, readahead, readlink, realpath, reboot, reset, rev, rm, rmdir, route, scp, sed, seq, setfattr, sftp, sh, sha1sum, sha256sum, sha384sum, sha512sum, shred, sleep, sort, split, ssh, ssh-keygen, stat, strings, sudo, sync, sysctl, tac, tail, tar, taskset, tee, telnet, test, time, timeout, timestamps, toe, top, touch, tr, traceroute, traceroute6, true, truncate, tsort, tty, uname, uniq, unix2dos, unlink, unzip, uptime, usleep, uudecode, uuencode, uuidgen, vi, view, vim, vmstat, watch, wc, wget, which, xargs, xxd, yes, zcat, zip, zsh

补充说明：

- 存在鸿蒙系统级工具：`hilog`、`hidumper`、`hitrace`、`hiperf`、`hisysevent`、`param`、`paramshell`。
- 存在网络与压缩工具：`curl`、`wget`、`ssh`、`scp`、`sftp`、`tar`、`zip`、`unzip`、`openssl`。
- **不存在任何 C 编译器或构建工具**：无 `cc`、`gcc`、`clang`、`cl`、`make`。

### 4. 包管理器

```
$ for c in apt apt-get dnf yum apk pacman rpm dpkg hpm pkgcmd brew; do command -v "$c"; done
（无输出）
```

11 种包管理器中，无一种存在。系统不提供任何软件安装手段。

### 5. 文件系统全盘搜索

```
$ find / -maxdepth 4 -name "*python*" 2>/dev/null
（无输出）

$ find /usr /storage -name "*python*" 2>/dev/null
（无输出）
```

在可访问的文件系统范围内，无任何名称含 `python` 的文件或目录。

### 6. /usr/lib 内容

```
$ ls /usr/lib
libcrypto.so.3  libncursesw.so.6  libssl.so.3  libtinfo.so.6  libz.so.1  libz.so.1.2.13
```

仅 6 个基础共享库，**无 libpython**。

### 7. 基础系统信息命令

```
$ id
zsh: command not found: id
```

连 `id` 这样的基础 coreutils 命令都不存在。

### 8. 运行环境判定（关键证据）

```
$ env
ALACRITTY_WINDOW_ID=window85_terminal0
HAP_DEBUGGABLE=false
XDG_CACHE_HOME=/data/storage/el2/base/haps/entry/files
XDG_CONFIG_HOME=/data/storage/el2/base/haps/entry/files
__LIBACE_ENTRY_POINT=59f6cc9a34
USER=100
HNP_PRIVATE_HOME=/data/app
HNP_PUBLIC_HOME=/data/service/hnp
...
```

判定依据：

- `XDG_CACHE_HOME` 与 `XDG_CONFIG_HOME` 指向 `/data/storage/el2/base/haps/entry/files`。`el2` 与 `haps`（Harmony Ability Package）为 OpenHarmony 应用沙箱路径特征。
- `__LIBACE_ENTRY_POINT` 表明进程运行在 ACE（ArkUI）运行时内。
- `HAP_DEBUGGABLE=false` 表明该应用包不可调试。
- `ALACRITTY_WINDOW_ID` 表明该终端为第三方应用 Alacritty，而非系统终端。
- `USER=100`，非 root。

**结论：所使用终端是运行在应用沙箱内的一个鸿蒙应用，不是系统 shell。**

这解释了以下权限受限现象：

```
$ ls /
ls: /: Permission denied

$ ls /bin
ls: /bin: Permission denied

$ ls /system
ls: /system: Permission denied

$ ls /data
ls: /data: Permission denied

$ ls -la /storage/Users/currentUser/appdata
ls: /storage/Users/currentUser/appdata: Operation not permitted
```

### 9. HNP 机制

```
$ command -v hnp
（无输出）
```

环境变量 `HNP_PUBLIC_HOME=/data/service/hnp` 存在，但该目录不存在。说明 HNP 机制在系统中存在，但当前未安装任何 HNP 包。

## 五、阻塞影响

本机既无 Python 运行时，也无包管理器和编译器，因此：

| 负责人 | 工作项 | 受影响情况 |
|---|---|---|
| 3号 | 鸿蒙 Python 环境 | 阻塞，无法完成环境搭建 |
| 4号 | 依赖验证（NumPy/SciPy/Numba 等） | 阻塞，无解释器可安装依赖 |
| 5号 | 源码适配与示例运行 | 阻塞，无法在本机运行 |
| 6号 | 打包与全新环境复测 | 阻塞，无法在本机安装验证 |

第 5 天决策门条件不满足。

补充说明：即使存在裸 Python 解释器，由于缺少 C 编译器与 `make`，numpy、scipy、numba 等依赖在 aarch64 鸿蒙平台上大概率无预编译 wheel，需从源码构建，当前工具链无法支持（numba 另需 LLVM，构建难度更高）。因此本机不具备完成移植所需的完整工具链。

## 六、未验证项

1. **开发者模式**：未开启、未验证。
   - 未验证原因：该设备为官方借用设备，需归还。开启开发者模式存在引入系统故障的风险，经评估后主动放弃。
   - 需说明：`HAP_DEBUGGABLE=false` 已表明当前沙箱应用不可调试；即便开启开发者模式，也不会新增 Python 运行时，仅可能提升对 `/system`、`/data` 目录的读取权限。
   - 该未验证项不影响主要结论，原因见第一节。

2. **华为是否以 HNP 形式提供 Python 运行时**：未确认。

3. **应用市场是否存在官方原生 Python 应用**：未确认。

## 七、交付物情况

| 计划交付物 | 状态 |
|---|---|
| `scripts/check_environment.py` | 已完成，已在 Windows + CPython 3.10.21 上验证通过 |
| 鸿蒙 PC Python 环境说明 | 以本报告替代，待组长确认 |
| 环境安装和验证日志 | 以本报告第四节的探测记录替代，待组长确认 |
| 可重复执行的环境准备步骤 | 无法产出，前提条件不成立 |

关于 `check_environment.py`：

- 该脚本为纯标准库实现，用于检测目标机是否具备运行 RayTracePy 的条件，输出文本报告和 JSON。
- 已在 Windows + CPython 3.10.21 上完成验证，覆盖依赖存在与缺失两种情形。
- **未能在目标设备上执行**，原因是设备不存在 Python 解释器。此事实本身构成一条证据。

## 八、待决事项

1. 是否向老师申请调整验收范围。
2. 上表中三项交付物的替代方案是否获批。
3. 3号后续任务如何重新分配（当前工作已完全阻塞）。
4. 是否通过官方渠道确认 HNP 形式的 Python 运行时或原生 Python 应用。

## 九、边界声明

依据项目分工文档，本人在确认无可用运行时后，未采取以下操作：

- 未安装非官方 Python 二进制。
- 未尝试开启 root 或规避系统权限。
- 未改用虚拟机、容器或兼容层方案。
- 未伪造任何设备端执行记录。

## 附录：/usr/bin 完整清单

```
awk           cp        file            hitrace   mount       printenv   sha1sum     telnet       uptime
base64        cpio      find            hostname  mountpoint  printf     sha256sum   test         usleep
basename      crc32     flock           iconv     mv          ps         sha384sum   time         uudecode
bunzip2       curl      fmt             ifconfig  netcat      pwd        sha512sum   timeout      uuencode
bzcmp         cut       free            iotop     netstat     pwdx       shred       timestamps   uuidgen
bzdiff        date      ftpget          ipcs      nl          readahead  sleep       toe          vi
bzegrep       dd        ftpput          join      nohup       readlink   sort        top          view
bzfgrep       df        getconf         kill      nproc       realpath   split       touch        vim
bzgrep        diff      getfattr        killall   od          reboot     ssh         tr           vmstat
bzip2         dirname   grep            ln        openssl     reset      ssh-keygen  traceroute   watch
bzip2recover  dos2unix  gunzip          loh       param       rev        stat        traceroute6  wc
bzmore        du        gzip            ls        paramshell  rm         strings     true         wget
cal           echo      head            lsattr    paste       rmdir      sudo        truncate     which
cat           egrep     help            lsmod     patch       route      sync        tsort        xargs
chmod         env       hexedit         mcookie   pgrep       scp        sysctl      tty          xxd
cksum         expand    hidumper        md5sum    pidof       sed        tac         uname        yes
clear         expr      hilog           mkdir     ping        seq        tail        uniq         zcat
cmp           factor    hiperf          mkpasswd  ping6       setfattr   tar         unix2dos     zip
comm          false     hiprofiler_cmd  mktemp    pkill       sftp       taskset     unlink       zsh
count         fgrep     hisysevent      more      pr          sh         tee         unzip
```
