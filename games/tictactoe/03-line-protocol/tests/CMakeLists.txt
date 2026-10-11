#===--------------------------------------------------------------------------------------------===#
# CMakeLists.txt - 测试组件的构建定义
#
# 引入 GoogleTest，构建棋盘与对局测试，并注册管道对局。
#===--------------------------------------------------------------------------------------------===#

#===--------------------------------------------------------------------------------------------===#
# 引入 GoogleTest
#===--------------------------------------------------------------------------------------------===#

# 引入 FetchContent 模块。
include(FetchContent)

# 首次配置时经 codeload 拉取源码包，与工程一起编译。
# URL_HASH 固定下载内容：标签指向的包被替换时配置立即失败。
FetchContent_Declare(googletest
  URL https://codeload.github.com/google/googletest/tar.gz/refs/tags/v1.17.0
  URL_HASH SHA256=65fab701d9829d38cb77c14acdc431d2108bfdbf8979e40eb8ae567edf10b27c
)
# GoogleTest 自己的警告不作为本工程失败条件。
set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)
FetchContent_MakeAvailable(googletest)

#===--------------------------------------------------------------------------------------------===#
# 测试目标
#===--------------------------------------------------------------------------------------------===#

# 源文件显式列出，新增文件在这里追加。
add_executable(tictactoe_test
  board_test.cpp
  cli_test.cpp
  game_test.cpp
  opponent_test.cpp
)

# 链接井字棋动态库、CLI 静态库与 GoogleTest 的 main 适配。
target_link_libraries(tictactoe_test
  PRIVATE
    tictactoe
    tictactoe_cli
    GTest::gtest_main
)

target_compile_features(tictactoe_test PRIVATE cxx_std_20)
target_compile_options(tictactoe_test PRIVATE -Wall -Wextra -Werror -Wold-style-cast -Wshadow)

# 测试可执行文件同样从 build/bin 出发查找 build/lib 的动态库。
set_target_properties(tictactoe_test PROPERTIES
  BUILD_RPATH "$ORIGIN/../lib"
)

#===--------------------------------------------------------------------------------------------===#
# 注册测试
#===--------------------------------------------------------------------------------------------===#

# 把 app 与 tictactoe_test 注册给 CTest。opponent 与棋盘、对局规则编译进同一个 tictactoe 动态库。
add_test(NAME tictactoe_test COMMAND tictactoe_test)

# 用一局固定棋谱走完，stdout 必须出现完整的对局结果行。
find_program(BASH_EXECUTABLE bash REQUIRED)
add_test(
  NAME tictactoe_scripted_match
  COMMAND ${BASH_EXECUTABLE} -c
          [[printf '%s\n' '1' '0 0' '1 0' '0 1' '1 1' '0 2' | "$1"]]
          bash $<TARGET_FILE:app>
)
set_tests_properties(tictactoe_scripted_match PROPERTIES
  PASS_REGULAR_EXPRESSION "对局结果：X 获胜"
)

# 先选人机，再选启发式。棋谱只含先手，后手由对手产生。
add_test(
  NAME tictactoe_cpu_menu
  COMMAND ${BASH_EXECUTABLE} -c
          [[printf '%s\n' '2' '2' '0 0' '2 2' '2 0' '2 1' | "$1"]]
          bash $<TARGET_FILE:app>
)
set_tests_properties(tictactoe_cpu_menu PROPERTIES
  PASS_REGULAR_EXPRESSION "对局结果：X 获胜"
)

add_test(
  NAME tictactoe_snapshot_line
  COMMAND ${BASH_EXECUTABLE} -c
          [[printf '%s\n' '1' '0 0' '1 0' '0 1' '1 1' '0 2' | "$1"]]
          bash $<TARGET_FILE:app>
)
# 快照行锁定开头按行优先排列的九个棋盘格子、终局状态与胜者。
set_tests_properties(tictactoe_snapshot_line PROPERTIES
  PASS_REGULAR_EXPRESSION [["cells":\["X","X","X","O","O".*"status":"x_wins","winner":"X"]]
)

# 每一步打印后恰有一行快照，sequence 从 0 递增到终局。
add_test(
  NAME tictactoe_snapshot_sequence
  COMMAND ${BASH_EXECUTABLE} -c
          [[out=$(printf '%s\n' '1' '0 0' '1 0' '0 1' '1 1' '0 2' | "$1")
          test "$(printf '%s\n' "$out" | grep -c '"version":1')" = 6
          test "$(printf '%s\n' "$out" | grep -o '"sequence":[0-9]*' | tr '\n' ' ')" = '"sequence":0 "sequence":1 "sequence":2 "sequence":3 "sequence":4 "sequence":5 ']]
          bash $<TARGET_FILE:app>
)

# 平局终局写出 status 为 draw、winner 为空的快照。
add_test(
  NAME tictactoe_snapshot_draw
  COMMAND ${BASH_EXECUTABLE} -c
          [[printf '%s\n' '1' '0 0' '0 1' '0 2' '1 2' '1 0' '1 1' '2 1' '2 0' '2 2' | "$1"]]
          bash $<TARGET_FILE:app>
)
set_tests_properties(tictactoe_snapshot_draw PROPERTIES
  PASS_REGULAR_EXPRESSION [["status":"draw","winner":""]]
)
