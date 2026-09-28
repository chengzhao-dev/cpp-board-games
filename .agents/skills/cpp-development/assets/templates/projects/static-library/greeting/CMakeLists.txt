# 构建 greeting 静态库。

# 构建静态库，并把 include/ 作为它的公开接口目录。
add_library(greeting STATIC src/greeting.cpp)
target_include_directories(greeting PUBLIC include)
target_compile_options(greeting PRIVATE -stdlib=libc++ -Wall -Wextra -Werror)
