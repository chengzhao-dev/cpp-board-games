# 主程序的构建定义。
#
# 程序入口编成可执行文件 app，只链接井字棋动态库；终端循环与测试当前不参与构建。

#-------------------------------------------------------------------------------
# 主程序目标

# 程序入口只做装配，对局规则全部来自井字棋动态库。
add_executable(app
  src/main.cpp
)

# 要求可执行文件 app 使用 C++23。
CompileSettings_SetCxxStandard(app PRIVATE c++23)

set_target_properties(app PROPERTIES
  # 构建期从 build/bin 找到 build/lib 下的动态库。
  BUILD_RPATH "$ORIGIN/../lib"
)

# 链接井字棋动态库。
target_link_libraries(app PRIVATE tictactoe)

# 给可执行文件 app 施加标准警告等级。
CompileSettings_SetWarnings(app PRIVATE LEVEL standard)
