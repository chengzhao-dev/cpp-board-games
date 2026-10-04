#===------------------------------------------------------------------------===#
# CMakeLists.txt - 井字棋动态库组件的构建定义
#
# 把井字棋规则核心编译成动态库 tictactoe，供主程序与测试链接。
#===------------------------------------------------------------------------===#

#===------------------------------------------------------------------------===#
# 井字棋动态库目标
#===------------------------------------------------------------------------===#

# SHARED 生成动态库，产物经顶层规则归入 build/lib。
add_library(tictactoe SHARED
  src/board.cpp
  src/game.cpp
)

# C++20 随目标传播：链接本库的主程序与测试也按 C++20 编译。
target_compile_features(tictactoe PUBLIC cxx_std_20)

# include/ 是公开接口目录：头文件直接放在该根下，使用方写裸文件名引号 include。
target_include_directories(tictactoe
  PUBLIC "${CMAKE_CURRENT_SOURCE_DIR}/include"
)

# 警告只加在本库，不传给 GoogleTest。
target_compile_options(tictactoe PRIVATE -Wall -Wextra -Werror)
