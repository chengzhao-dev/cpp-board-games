#===------------------------------------------------------------------------===#
# CMakeLists.txt - 规则库组件的构建定义
#
# 把规则核心编译成动态库 tic_tac_toe_core，供 CLI 与测试链接。
#===------------------------------------------------------------------------===#

#===------------------------------------------------------------------------===#
# 规则库目标
#===------------------------------------------------------------------------===#

# SHARED 生成动态库，产物经顶层规则归入 build/lib。
add_library(tic_tac_toe_core SHARED
  src/game_state.cpp
)

# C++20 随目标传播：链接本库的 CLI 与测试也按 C++20 编译。
target_compile_features(tic_tac_toe_core PUBLIC cxx_std_20)

# include/ 是公开接口目录，使用方按 tic_tac_toe/xxx.h 找到头文件。
target_include_directories(tic_tac_toe_core
  PUBLIC "${CMAKE_CURRENT_SOURCE_DIR}/include"
)
