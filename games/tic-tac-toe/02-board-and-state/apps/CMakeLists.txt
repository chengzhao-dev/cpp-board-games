#===------------------------------------------------------------------------===#
# CMakeLists.txt - 终端程序组件的构建定义
#
# 构建 CLI 可执行目标，链接规则库并约定动态库查找路径。
#===------------------------------------------------------------------------===#

#===------------------------------------------------------------------------===#
# CLI 目标
#===------------------------------------------------------------------------===#

# 源文件显式列出，新增文件在这里追加。
add_executable(tic_tac_toe_cli
  main.cpp
)

# C++20 来自规则库的传播要求，这里再显式声明一次，保持目标自描述。
target_compile_features(tic_tac_toe_cli PRIVATE cxx_std_20)

# 链接规则库动态库。
target_link_libraries(tic_tac_toe_cli PRIVATE tic_tac_toe_core)

# 把库查找位置写进可执行文件：从 build/bin 出发找到 build/lib。
set_target_properties(tic_tac_toe_cli PROPERTIES
  BUILD_RPATH "$ORIGIN/../lib"
)
