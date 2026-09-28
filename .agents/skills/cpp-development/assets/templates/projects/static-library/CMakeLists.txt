# 构建 {{CMAKE_PROJECT_NAME}} 工程：根 main.cpp 使用 greeting/ 提供的静态库。
cmake_minimum_required(VERSION 3.31)
project({{CMAKE_PROJECT_NAME}} LANGUAGES CXX)

# 使用 C++20，并把可执行文件和库分别输出到 build/bin 与 build/lib。
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)

# 生成编译数据库，记录每个源文件的实际编译参数。
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# 加载 greeting/CMakeLists.txt 中的静态库目标。
add_subdirectory(greeting)

# 创建 app 可执行目标，并在链接阶段使用 greeting 静态库。
add_executable(app main.cpp)
target_link_libraries(app PRIVATE greeting)
target_compile_options(app PRIVATE -stdlib=libc++ -Wall -Wextra -Werror)
target_link_options(app PRIVATE -stdlib=libc++)
