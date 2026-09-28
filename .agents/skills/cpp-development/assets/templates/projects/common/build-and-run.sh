#!/usr/bin/env bash
# 配置、构建并运行当前 CMake 项目。

# 任一命令失败时立即停止。
set -euo pipefail

cd "$(dirname "$0")"

printf '\n==> 配置\n\n'
cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=Debug -DCMAKE_CXX_COMPILER=clang++

printf '\n==> 构建\n\n'
cmake --build build

printf '\n==> 运行\n\n'
./build/bin/app
