#!/storage/Users/currentUser/.harmonybrew/bin/bash
# Build a working CPython 3.10 (musl/aarch64) for OpenHarmony from Alpine packages.
#
# Why this exists: the python-build-standalone musl build statically links a
# libffi whose ffi_closure_alloc() returns NULL on the OpenHarmony kernel, so
# ctypes callbacks (and therefore numba) cannot work. Alpine's Python links
# libffi dynamically, so we can swap in a libffi that does work.
#
# Steps: extract -> patchelf fixes -> libffi swap -> platform patches -> sign.
set -u

D=/storage/Users/currentUser/.local/alpine-py310
TOOLS=/storage/Users/currentUser/.local/ohos-python-tools
APKS=/storage/Users/currentUser/.local/ohos-python-tools/pyapks
HB=/storage/Users/currentUser/.harmonybrew
LOADER=$TOOLS/ld-musl-aarch64.so.1

mkdir -p "$TOOLS"
# selfsign.py 已随工具目录分发
# fixenv.py 不再需要（EXT_SUFFIX 本已是 -gnu）
if [ ! -f "$TOOLS/selfsign.py" ]; then echo "缺少 selfsign.py"; exit 1; fi
SIGN="python3 $TOOLS/selfsign.py"

# 1) a signed copy of the musl loader: executing it directly is denied by the
#    kernel unless it carries a .codesign section, but pip/setuptools/packaging
#    all shell out to it to detect the musl version.
if [ ! -f "$LOADER" ]; then
    cp /lib/ld-musl-aarch64.so.1 "$LOADER"
    chmod 755 "$LOADER"
    $SIGN "$LOADER" --force
fi

# 2) extract the Alpine package set
echo "== 解压 Alpine 包 =="
rm -rf "$D"; mkdir -p "$D"
for f in "$APKS"/*.apk; do tar xzf "$f" -C "$D" 2>/dev/null || true; done

# 3) libffi: Alpine 3.4.4 fails to allocate closures here; use 3.8.0
echo "== 替换 libffi (3.4.4 -> 3.8.0) =="
rm -f "$D/usr/lib/libffi.so.8.1.2"
cp "$HB/lib/libffi.so.8.5.0" "$D/usr/lib/libffi.so.8.1.2"

# 4) make the interpreter look like a normal Linux/musl host so that pip
#    produces musllinux wheel tags (mirrors what harmonybrew does at build time)
echo "== 平台补丁 =="
python3 - "$D" <<'PYEOF'
import sys
root = sys.argv[1]
p = f"{root}/usr/lib/python3.10/sysconfig.py"
s = open(p).read()
old = "def get_platform():"
assert s.count(old) == 1, s.count(old)
open(p, "w").write(s.replace(old, 'def get_platform():\n    return "linux-aarch64"', 1))
p = f"{root}/usr/lib/python3.10/platform.py"
s = open(p).read()
old = "def system():"
assert s.count(old) == 1, s.count(old)
open(p, "w").write(s.replace(old, 'def system():\n    return "Linux"', 1))
print("   sysconfig.get_platform -> linux-aarch64, platform.system -> Linux")
PYEOF

# 5) patchelf pass over every ELF
echo "== ELF 修补 =="
LIBDIR="$D/usr/lib"
n=0
while read -r f; do
    [ -L "$f" ] && continue
    [ "$(head -c4 "$f" 2>/dev/null | od -An -tx1 | tr -d ' \n')" = "7f454c46" ] || continue
    chmod 644 "$f" 2>/dev/null
    patchelf --set-rpath "$LIBDIR" "$f" 2>/dev/null || true
    # the host loader's SONAME is libc.so, not libc.musl-aarch64.so.1; leaving
    # the Alpine name makes musl load a second copy of libc
    patchelf --replace-needed libc.musl-aarch64.so.1 libc.so "$f" 2>/dev/null || true
    # extension modules only list libc, but need libpython's symbols
    case "$f" in
        */lib-dynload/*.so) patchelf --add-needed libpython3.10.so.1.0 "$f" 2>/dev/null || true ;;
    esac
    # point the interpreter at the signed loader copy
    case "$f" in
        */bin/python3.10) patchelf --set-interpreter "$LOADER" "$f" 2>/dev/null || true ;;
    esac
    chmod 755 "$f" 2>/dev/null
    n=$((n+1))
done < <(find "$D" -type f)
echo "   处理 $n 个 ELF"

# 6) sign every ELF: OpenHarmony enforces fs-verity code signing
echo "== 签名 =="
n=0
while read -r f; do
    [ -L "$f" ] && continue
    [ "$(head -c4 "$f" 2>/dev/null | od -An -tx1 | tr -d ' \n')" = "7f454c46" ] || continue
    $SIGN "$f" --force >/dev/null 2>&1 && n=$((n+1))
done < <(find "$D" -type f)
echo "   已签名 $n 个"

echo "== 完成: $D =="
