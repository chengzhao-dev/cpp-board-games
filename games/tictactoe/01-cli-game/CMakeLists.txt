#===------------------------------------------------------------------------===#
# CMakeLists.txt - 井字棋工程的构建定义
#
# 约定产物目录，并按井字棋动态库、主程序与测试三个组件组织构建。
#===------------------------------------------------------------------------===#

#===------------------------------------------------------------------------===#
# 工程声明
#===------------------------------------------------------------------------===#

# CMake 版本约束：保证本目录使用的命令可用。
cmake_minimum_required(VERSION 4.2)

# 项目名，只启用 C++ 语言。
project(tictactoe_01_cli_game LANGUAGES CXX)

# 导出编译数据库：clangd 从 build/compile_commands.json 读取真实编译参数。
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# libc++ 作用于本目录及子目录，包含随后拉取的 GoogleTest。
add_compile_options(-stdlib=libc++)
add_link_options(-stdlib=libc++)

#===------------------------------------------------------------------------===#
# 产物目录
#===------------------------------------------------------------------------===#

# 可执行文件归入 build/bin。
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin")
# 动态库归入 build/lib。
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/lib")
# 静态库归入 build/lib。
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/lib")

#===------------------------------------------------------------------------===#
# 测试
#===------------------------------------------------------------------------===#

# 开启 CTest：子目录注册的测试才能被 ctest 发现和运行。
enable_testing()

#===------------------------------------------------------------------------===#
# 组件
#===------------------------------------------------------------------------===#

# 三个组件目录各自带 CMakeLists.txt，按依赖顺序加入构建。
add_subdirectory(tictactoe)
add_subdirectory(apps)
add_subdirectory(tests)
