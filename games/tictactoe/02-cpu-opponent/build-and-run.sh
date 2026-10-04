#!/usr/bin/env bash
#===------------------------------------------------------------------------===#
# build-and-run.sh - 井字棋工程的一键验证脚本
#
# 依次完成：配置 → 编译 → 格式与静态检查 → 测试 → 运行。
# 测试与运行步骤用临时 LD_LIBRARY_PATH 加固动态库查找，不改动系统配置。
# 在 WSL Ubuntu 中于本目录执行：./build-and-run.sh
#===------------------------------------------------------------------------===#

#===------------------------------------------------------------------------===#
# 严格模式与工作目录
#===------------------------------------------------------------------------===#
set -euo pipefail

cd "$(dirname "$0")"
readonly STAGE_ROOT="${PWD}"
readonly STAGE_LIB="${STAGE_ROOT}/build/lib"
readonly STAGE_BIN="${STAGE_ROOT}/build/bin"
readonly APP_NAME="app"

#===------------------------------------------------------------------------===#
# 输出辅助
#===------------------------------------------------------------------------===#

# 在 stdout 打印一步标题，前面空一行，和紧随的命令输出分开。
header() {
  printf '\n==> %s\n' "$*"
}

# 把错误写到 stderr，避免混进管道对局的正常输出。
err() {
  printf '错误: %s\n' "$*" >&2
}

#===------------------------------------------------------------------------===#
# 阶段库加固
#===------------------------------------------------------------------------===#

# 只包住单条命令的库查找路径：主路径是可执行文件内的 RPATH，这里仅加固。
# 变量展开保留调用者已有的 LD_LIBRARY_PATH，命令结束即失效。
run_with_stage_libs() {
  env LD_LIBRARY_PATH="${STAGE_LIB}${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}" "$@"
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

  # 只检查本目录头文件；排除 FetchContent 的 GoogleTest，告警即失败。
  # 不把 clang-tidy 挂进 CMAKE_CXX_CLANG_TIDY，避免扫到测试框架源码。
  readonly PROJECT_HEADER_FILTER="^${STAGE_ROOT}/(tictactoe/include|apps|tests)/"
  clang-tidy -p build \
    --header-filter="${PROJECT_HEADER_FILTER}" \
    --exclude-header-filter='(^|/)build/_deps/' \
    --warnings-as-errors='*' \
    tictactoe/src/board.cpp \
    tictactoe/src/game.cpp \
    tictactoe/src/opponent.cpp \
    apps/src/main.cpp \
    apps/src/cli.cpp \
    tests/board_test.cpp \
    tests/game_test.cpp \
    tests/opponent_test.cpp

  header "4. 测试"
  run_with_stage_libs ctest --test-dir build --output-on-failure

  header "5. 运行"
  # 管道喂入一局会由 X 取胜的棋谱，避免脚本停在读入。
  local output
  output="$(
    cd "${STAGE_BIN}"
    printf '%s\n' '1' '0 0' '1 0' '0 1' '1 1' '0 2' |
      run_with_stage_libs "./${APP_NAME}"
  )"
  printf '%s\n' "${output}"
  if [[ "${output}" != *"X 获胜"* ]]; then
    err "管道对局没有打印 X 获胜"
    exit 1
  fi
}

main "$@"
