#===--------------------------------------------------------------------------------------------===#
# CMakeLists.txt - 终端程序组件的构建定义
#
# 把 CLI 实现编成静态库，供 app 与测试链接；app 只留 main。
#===--------------------------------------------------------------------------------------------===#

#===--------------------------------------------------------------------------------------------===#
# CLI 静态库目标
#===--------------------------------------------------------------------------------------------===#

# CLI 实现编成库：app 与 tictactoe_test 链接同一份，测试不再重复编 cli.cpp。
add_library(tictactoe_cli STATIC
  src/cli.cpp
)

# apps/include 是 cli 组件接口根，PUBLIC 让链接方直接取到 cli.h。
target_include_directories(tictactoe_cli PUBLIC
  "${CMAKE_CURRENT_SOURCE_DIR}/include"
)

target_compile_features(tictactoe_cli PUBLIC cxx_std_20)
target_link_libraries(tictactoe_cli PUBLIC tictactoe)

# 警告只加在本库。
target_compile_options(tictactoe_cli PRIVATE -Wall -Wextra -Werror -Wold-style-cast -Wshadow)

#===--------------------------------------------------------------------------------------------===#
# 主程序目标
#===--------------------------------------------------------------------------------------------===#

# 源文件显式列出，新增文件在这里追加；全部 .cpp 在 src/。
add_executable(app
  src/main.cpp
)

# C++20 随 cli 库传播，这里再显式声明一次，保持目标自描述。
target_compile_features(app PRIVATE cxx_std_20)

# 链接 CLI 静态库；井字棋动态库经它传递，不再单独列出。
target_link_libraries(app PRIVATE tictactoe_cli)

# 警告只加在本程序。
target_compile_options(app PRIVATE -Wall -Wextra -Werror -Wold-style-cast -Wshadow)

# 把库查找位置写进可执行文件：从 build/bin 出发找到 build/lib。
set_target_properties(app PROPERTIES
  BUILD_RPATH "$ORIGIN/../lib"
)
