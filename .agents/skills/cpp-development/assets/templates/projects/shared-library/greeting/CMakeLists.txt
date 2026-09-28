# 构建 greeting 动态库。

# 构建动态库，并把 include/ 作为它的公开接口目录。
add_library(greeting SHARED src/greeting.cpp)
target_include_directories(greeting PUBLIC include)
target_compile_options(greeting PRIVATE -stdlib=libc++ -Wall -Wextra -Werror)
target_link_options(greeting PRIVATE -stdlib=libc++)
