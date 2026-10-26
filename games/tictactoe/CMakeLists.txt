# 井字棋工程的构建定义。
#
# 约定产物目录；当前构建井字棋动态库、主程序与棋盘测试。
# cmake/ 放编译设置助手，供各目标复用。

#-------------------------------------------------------------------------------
# 工程声明

# 声明本工程至少使用 CMake 3.20。
cmake_minimum_required(VERSION 3.20)

# 声明工程名、版本和语言。
project(tictactoe VERSION 1.0.0 LANGUAGES CXX)

#-------------------------------------------------------------------------------
# 构建助手

# 把本目录下的 cmake 加入模块搜索路径。
list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/cmake")
# 引入通用 C++ 标准与警告助手。
include(CompileSettings)

#-------------------------------------------------------------------------------
# 工程选项

# 导出编译数据库。
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# 让 CTest 接管测试目标。
enable_testing()

# 静态库输出到构建目录下的 lib。
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)
# 动态库输出到构建目录下的 lib。
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)
# 可执行文件输出到构建目录下的 bin。
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)

#-------------------------------------------------------------------------------
# 工程组件

# 纳入井字棋动态库。
add_subdirectory(tictactoe)
# 纳入主程序。
add_subdirectory(apps)
# 纳入棋盘测试。
add_subdirectory(tests)
