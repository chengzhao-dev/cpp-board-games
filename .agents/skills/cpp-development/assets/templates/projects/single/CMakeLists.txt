# 构建 {{CMAKE_PROJECT_NAME}} 可执行目标。
cmake_minimum_required(VERSION 3.31)
project({{CMAKE_PROJECT_NAME}} LANGUAGES CXX)

# 使用 C++20，并把可执行文件统一输出到 build/bin。
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)

# 生成编译数据库，记录每个源文件的实际编译参数。
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# 创建 app 可执行目标。
add_executable(app main.cpp)

# 使用 libc++，并启用常用警告。
target_compile_options(app PRIVATE -stdlib=libc++ -Wall -Wextra -Werror)
target_link_options(app PRIVATE -stdlib=libc++)
