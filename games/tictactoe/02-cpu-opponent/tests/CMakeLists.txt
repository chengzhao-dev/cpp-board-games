#===------------------------------------------------------------------------===#
# CMakeLists.txt - 测试组件的构建定义
#
# 引入 GoogleTest，构建棋盘与对局测试，并注册管道对局。
#===------------------------------------------------------------------------===#

#===------------------------------------------------------------------------===#
# 引入 GoogleTest
#===------------------------------------------------------------------------===#

# 引入 FetchContent 模块。
include(FetchContent)

# 首次配置时经 codeload 拉取源码包，与工程一起编译。
FetchContent_Declare(googletest
  URL https://codeload.github.com/google/googletest/tar.gz/refs/tags/v1.17.0
)
# GoogleTest 自己的警告不作为本工程失败条件。
set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)
FetchContent_MakeAvailable(googletest)

#===------------------------------------------------------------------------===#
# 测试目标
#===------------------------------------------------------------------------===#

# 源文件显式列出，新增文件在这里追加。
add_executable(tictactoe_test
  board_test.cpp
  game_test.cpp
  opponent_test.cpp
)

# 链接井字棋动态库与 GoogleTest 的 main 适配。
target_link_libraries(tictactoe_test
  PRIVATE
    tictactoe
    GTest::gtest_main
)

target_compile_features(tictactoe_test PRIVATE cxx_std_20)
target_compile_options(tictactoe_test PRIVATE -Wall -Wextra -Werror)

# 测试可执行文件同样从 build/bin 出发查找 build/lib 的动态库。
set_target_properties(tictactoe_test PROPERTIES
  BUILD_RPATH "$ORIGIN/../lib"
)

#===------------------------------------------------------------------------===#
# 注册测试
#===------------------------------------------------------------------------===#

# 把 app 与 tictactoe_test 注册给 CTest。opponent 是静态库，链进这两个目标。
add_test(NAME tictactoe_test COMMAND tictactoe_test)

# 用一局固定棋谱走完，stdout 必须出现胜者。
find_program(BASH_EXECUTABLE bash REQUIRED)
add_test(
  NAME tictactoe_scripted_match
  COMMAND ${BASH_EXECUTABLE} -c
          [[printf '%s\n' '1' '0 0' '1 0' '0 1' '1 1' '0 2' | "$1"]]
          bash $<TARGET_FILE:app>
)
set_tests_properties(tictactoe_scripted_match PROPERTIES
  PASS_REGULAR_EXPRESSION "X 获胜"
)

# 先选人机，再选启发式。棋谱只含先手，后手由对手产生。
add_test(
  NAME tictactoe_cpu_menu
  COMMAND ${BASH_EXECUTABLE} -c
          [[printf '%s\n' '2' '2' '0 0' '2 2' '2 0' '2 1' | "$1"]]
          bash $<TARGET_FILE:app>
)
set_tests_properties(tictactoe_cpu_menu PROPERTIES
  PASS_REGULAR_EXPRESSION "X 获胜"
)
