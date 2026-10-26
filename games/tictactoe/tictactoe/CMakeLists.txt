# 井字棋动态库的构建定义。
#
# 把棋盘、对局与电脑落子编成动态库 tictactoe，供主程序链接。

#-------------------------------------------------------------------------------
# 动态库目标

# 把三个源文件编成井字棋动态库。
add_library(tictactoe SHARED
  src/board.cpp
  src/game.cpp
  src/ai.cpp
)

# 要求井字棋动态库使用 C++23，标准随公共接口传播。
CompileSettings_SetCxxStandard(tictactoe PUBLIC c++23)

# 井字棋动态库和链接它的程序都使用 libc++；选项只挂在 target 上，不污染其他目标。
target_compile_options(tictactoe PUBLIC -stdlib=libc++)
target_link_options(tictactoe PUBLIC -stdlib=libc++)

# 把头文件目录公开给链接井字棋动态库的目标。
target_include_directories(tictactoe
  PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/include
)

# 给井字棋动态库施加标准警告等级。
CompileSettings_SetWarnings(tictactoe PRIVATE LEVEL standard)
