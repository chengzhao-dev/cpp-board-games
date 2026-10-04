#===------------------------------------------------------------------------===#
# CMakeLists.txt - 终端程序组件的构建定义
#
# 构建 app 可执行目标，链接井字棋动态库并约定查找路径。
#===------------------------------------------------------------------------===#

#===------------------------------------------------------------------------===#
# 主程序目标
#===------------------------------------------------------------------------===#

# 源文件显式列出，新增文件在这里追加；全部 .cpp 在 src/。
add_executable(app
  src/main.cpp
  src/cli.cpp
)

# apps/include 仅 PRIVATE：展示头只服务终端展示，不放规则逻辑。
target_include_directories(app PRIVATE
  "${CMAKE_CURRENT_SOURCE_DIR}/include"
)

# C++20 随井字棋动态库传播，这里再显式声明一次，保持目标自描述。
target_compile_features(app PRIVATE cxx_std_20)

# 链接井字棋动态库 tictactoe。
target_link_libraries(app PRIVATE tictactoe)

# 警告只加在本程序。
target_compile_options(app PRIVATE -Wall -Wextra -Werror)

# 把库查找位置写进可执行文件：从 build/bin 出发找到 build/lib。
set_target_properties(app PROPERTIES
  BUILD_RPATH "$ORIGIN/../lib"
)
