#------------------------------------------------------------------------------#
# CMakeLists.txt - 棋盘测试的构建定义
#
# 引入固定版本的 GoogleTest，构建只覆盖 Board 的测试目标。
#------------------------------------------------------------------------------#

#------------------------------------------------------------------------------#
# 引入 GoogleTest
#------------------------------------------------------------------------------#

include(FetchContent)

# 固定版本，避免每次配置漂移。
FetchContent_Declare(
  googletest
  URL https://github.com/google/googletest/archive/refs/tags/v1.15.2.tar.gz
  DOWNLOAD_EXTRACT_TIMESTAMP TRUE
)

# 只构建测试需要的那一部分。
set(INSTALL_GTEST OFF CACHE BOOL "" FORCE)
set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)
FetchContent_MakeAvailable(googletest)

# GoogleTest 与测试目标必须和主库使用同一套标准库：gtest 若按 libstdc++ 编译，
# 测试按 libc++ 链接时会出现一批 std:: 符号未定义。只改导入的可执行/库目标，
# 留下全局编译选项会污染本工程自己的目标。
if(CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  foreach(gtest_target gtest gtest_main gmock gmock_main)
    if(TARGET ${gtest_target})
      target_compile_options(${gtest_target} PRIVATE -stdlib=libc++)
      target_link_options(${gtest_target} PRIVATE -stdlib=libc++)
    endif()
  endforeach()
endif()

#------------------------------------------------------------------------------#
# 测试目标
#------------------------------------------------------------------------------#

add_executable(tictactoe_test
  testing-board.cpp
)

CompileSettings_SetCxxStandard(tictactoe_test PRIVATE c++23)

target_link_libraries(tictactoe_test
  PRIVATE
    tictactoe
    GTest::gtest_main
)

CompileSettings_SetWarnings(tictactoe_test PRIVATE LEVEL standard)

set_target_properties(tictactoe_test PROPERTIES
  BUILD_RPATH "$ORIGIN/../lib"
)

#------------------------------------------------------------------------------#
# 注册测试
#------------------------------------------------------------------------------#

include(GoogleTest)
gtest_discover_tests(tictactoe_test
  DISCOVERY_TIMEOUT 30
  PROPERTIES
    LABELS "unit"
    TIMEOUT 10
)
