#!/usr/bin/env bash
#===------------------------------------------------------------------------===#
# build-and-run.sh - 工程一键验证脚本
#
# 依次完成：配置 → 编译 → 格式与静态检查 → 测试 → 运行。
# 在 WSL Ubuntu 中于本目录执行：./build-and-run.sh
#===------------------------------------------------------------------------===#

#===------------------------------------------------------------------------===#
# 严格模式与工作目录
#===------------------------------------------------------------------------===#
set -euo pipefail

cd "$(dirname "$0")"
readonly STAGE_ROOT="${PWD}"
readonly STAGE_BIN="${STAGE_ROOT}/build/bin"
readonly APP_NAME="app"

#===------------------------------------------------------------------------===#
# 输出辅助
#===------------------------------------------------------------------------===#

# 在 stdout 打印一步标题，前面空一行，和紧随的命令输出分开。
header() {
  printf '\n==> %s\n' "$*"
}

# 把错误写到 stderr，避免混进正常输出。
err() {
  printf '错误: %s\n' "$*" >&2
}

#===------------------------------------------------------------------------===#
# main：1 配置 → 2 编译 → 3 格式与静态检查 → 4 测试 → 5 运行
#===------------------------------------------------------------------------===#

# 失败时补充定位提示，并保留原命令的非零退出码。
trap 'err "构建流程失败，定位最靠近上方的失败命令后重试"' ERR

main() {
  header "1. 配置"

  # 用 Ninja 和 clang++ 配置 Debug，并写出 build/compile_commands.json。
  # 每次都重新配置，避免这些开关留在上一次的 CMake 缓存里。
  cmake -S . -B build -G Ninja \
    -DCMAKE_BUILD_TYPE=Debug \
    -DCMAKE_CXX_COMPILER=clang++ \
    -DCMAKE_EXPORT_COMPILE_COMMANDS=ON

  header "2. 编译"
  cmake --build build

  header "3. 格式与静态检查"

  # 排版检查：偏离 .clang-format 即失败；build/ 产物目录不参与。
  find . -path ./build -prune -o \( -name '*.cpp' -o -name '*.h' \) -print |
    xargs clang-format --dry-run --Werror

  # 静态检查：编译数据库由配置步骤生成，头文件警告经 header-filter 一并报告。
  find . -path ./build -prune -o -name '*.cpp' -print |
    xargs clang-tidy -p build --header-filter='.*' --warnings-as-errors='*'

  header "4. 测试"
  ctest --test-dir build --output-on-failure

  header "5. 运行"
  # 子 shell 进入产物目录执行，父脚本工作目录保持不变。
  (
    cd "${STAGE_BIN}"
    "./${APP_NAME}"
  )
}

main "$@"
