#!/usr/bin/env bash
#===------------------------------------------------------------------------------------------===#
# running-build.sh - 井字棋工程的构建、测试与运行入口
#
# 依次完成：配置与编译、CTest、运行主程序。Debug 一轮，构建目录为 build/。
# 在 WSL Ubuntu 中于本目录执行：./running-build.sh
#===------------------------------------------------------------------------------------------===#

set -euo pipefail

cd "$(dirname "$0")"

# 打印步骤标题
header() {
  printf '\n==> %s\n' "$*"
}

main() {
  header "1. 配置与编译"

  cmake -S . -B build -G Ninja \
    -DCMAKE_BUILD_TYPE=Debug \
    -DCMAKE_CXX_COMPILER=clang++

  cmake --build build

  header "2. 测试"

  ctest --test-dir build --output-on-failure

  header "3. 运行"

  ./build/bin/app
}

main "$@"
