#===------------------------------------------------------------------------===#
# CMakeLists.txt - 测试组件的构建定义
#
# 引入 GoogleTest，构建状态测试并注册到 CTest。
#===------------------------------------------------------------------------===#

#===------------------------------------------------------------------------===#
# 引入 GoogleTest
#===------------------------------------------------------------------------===#

# 首次配置时经 codeload 拉取源码包，与工程一起编译。
include(FetchContent)
FetchContent_Declare(googletest
  URL https://codeload.github.com/google/googletest/tar.gz/refs/tags/v1.17.0
)
FetchContent_MakeAvailable(googletest)

#===------------------------------------------------------------------------===#
# 测试目标
#===------------------------------------------------------------------------===#

# 测试可执行文件链接规则库与 GoogleTest 的 main 适配。
add_executable(tic_tac_toe_game_state_test
  game_state_test.cpp
)
target_link_libraries(tic_tac_toe_game_state_test
  PRIVATE
    tic_tac_toe_core
    GTest::gtest_main
)

# 测试可执行文件同样从 build/bin 出发查找 build/lib 的动态库。
set_target_properties(tic_tac_toe_game_state_test PROPERTIES
  BUILD_RPATH "$ORIGIN/../lib"
)

#===------------------------------------------------------------------------===#
# 注册测试
#===------------------------------------------------------------------------===#

# 把测试注册给 CTest，由一键脚本统一运行。
add_test(NAME tic_tac_toe_game_state_test
  COMMAND tic_tac_toe_game_state_test
)
