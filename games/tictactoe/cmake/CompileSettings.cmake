# CompileSettings
#
# 在一个目标上设置 C++ 语言标准与警告等级。
#
# 用 include(CompileSettings) 载入。两个函数都只改传入的目标，
# 不建全局变量，也不下载依赖。
include_guard(GLOBAL)

#-------------------------------------------------------------------------------
# 让一个目标使用指定的 C++ 标准。
#
# :param target: 已经存在的 CMake 目标。
# :param visibility: 取 PUBLIC、PRIVATE 或 INTERFACE。
# :param standard: 取 c++11、c++14、c++17、c++20 或 c++23。
function(CompileSettings_SetCxxStandard target visibility standard)
  if(NOT TARGET "${target}")
    message(FATAL_ERROR
      "CompileSettings_SetCxxStandard: target '${target}' does not exist")
  endif()

  if(NOT visibility MATCHES "^(PUBLIC|PRIVATE|INTERFACE)$")
    message(FATAL_ERROR
      "CompileSettings_SetCxxStandard: visibility must be "
      "PUBLIC, PRIVATE, or INTERFACE")
  endif()

  set(supported_standards c++11 c++14 c++17 c++20 c++23)
  if(NOT standard IN_LIST supported_standards)
    message(FATAL_ERROR
      "CompileSettings_SetCxxStandard: standard must be one of "
      "${supported_standards}")
  endif()

  # c++23 -> 23：两种声明使用同一个编号。
  string(SUBSTRING "${standard}" 3 -1 number)
  target_compile_features("${target}" "${visibility}" "cxx_std_${number}")
  set_target_properties("${target}" PROPERTIES
    CXX_STANDARD "${number}"
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
  )
endfunction()

#-------------------------------------------------------------------------------
# 给一个目标加上编译警告。
#
# 只改传入的目标。PRIVATE 不向使用方传播。
#
# :param target: 已经存在的 CMake 目标。
# :param visibility: 取 PRIVATE 或 INTERFACE。
# :keyword LEVEL: 可省略。取 basic、standard 或 strict；
#   省略时按 standard。
function(CompileSettings_SetWarnings target visibility)
  cmake_parse_arguments(PARSE_ARGV 2 arg "" "LEVEL" "")

  if(arg_UNPARSED_ARGUMENTS)
    message(FATAL_ERROR
      "CompileSettings_SetWarnings: unexpected arguments: "
      "${arg_UNPARSED_ARGUMENTS}")
  endif()

  if(NOT TARGET "${target}")
    message(FATAL_ERROR
      "CompileSettings_SetWarnings: target '${target}' does not exist")
  endif()

  if(NOT visibility MATCHES "^(PRIVATE|INTERFACE)$")
    message(FATAL_ERROR
      "CompileSettings_SetWarnings: visibility must be PRIVATE or INTERFACE")
  endif()

  if(NOT arg_LEVEL)
    set(arg_LEVEL standard)
  endif()

  if(MSVC)
    set(basic_warnings /W4)
    set(standard_warnings ${basic_warnings} /permissive- /WX)
    set(strict_warnings
      ${standard_warnings}
      /w14242 /w14254 /w14263 /w14265 /w14287 /w14296
      /w14311 /w14545 /w14546 /w14547 /w14549 /w14555
      /w14619 /w14640 /w14826
    )
  elseif(CMAKE_CXX_COMPILER_ID MATCHES "Clang|GNU")
    set(basic_warnings -Wall -Wextra)
    set(standard_warnings
      ${basic_warnings}
      -Werror              # 把告警当错误
      -Wshadow             # 变量遮蔽
      -Wold-style-cast     # C 风格转换
      -Wpedantic           # 非标准扩展
      -Wnon-virtual-dtor   # 有虚函数但析构非虚
      -Woverloaded-virtual
    )
    set(strict_warnings
      ${standard_warnings}
      -Wcast-align
      -Wcast-qual
      -Wconversion
      -Wsign-conversion
      -Wdouble-promotion
      -Wformat=2
      -Wimplicit-fallthrough
      -Wnull-dereference
      -Wundef
    )
  else()
    message(FATAL_ERROR
      "CompileSettings_SetWarnings: unsupported compiler "
      "'${CMAKE_CXX_COMPILER_ID}'")
  endif()

  if(arg_LEVEL STREQUAL "basic")
    set(warnings ${basic_warnings})
  elseif(arg_LEVEL STREQUAL "standard")
    set(warnings ${standard_warnings})
  elseif(arg_LEVEL STREQUAL "strict")
    set(warnings ${strict_warnings})
  else()
    message(FATAL_ERROR
      "CompileSettings_SetWarnings: LEVEL must be basic, standard, or strict")
  endif()

  target_compile_options("${target}" "${visibility}" ${warnings})
endfunction()
