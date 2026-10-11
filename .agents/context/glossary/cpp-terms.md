---
kb_id: "bg-cpp-chinese-terms-v1"
title: "C++ 中文术语全表"
domain: "cpp-teaching"
subdomain: "glossary"
tags: [terminology, chinese, cppreference, access-specifier, translation]
level_range: [0, 5]
dependencies: ["bg-comment-style-v1", "bg-terminology-v1"]
created: "2026-10-08"
updated: "2026-10-08"
chunk_strategy: "semantic_heading"
estimated_tokens: 3600
---

# C++ 中文术语全表

本文件是两仓写 C++ 中文正文与注释时**唯一**的术语权威：井字棋正文、代码注释、agent 文档凡点名 C++ 概念，一律按下表用词。读者侧的禁用摘录在 `bg-terminology-v1`，正反对照在 `bg-chinese-style-cases-v1`，注释用词在 `bg-comment-style-v1`；本文件不复制这三处的条文。

权威依据优先：[zh.cppreference 双语术语表](https://zh.cppreference.com/bilingual_glossary)、[访问说明符](https://zh.cppreference.com/cpp/language/access)、Microsoft Learn 中文「成员访问控制」、常见教材（learncpp 中译等）。本仓不把整份双语表搬进仓库，只收录井字棋正文与注释会碰到的词，加上作者写中文时容易写错的主流词。未收录词需要时查 cppreference，再按同一原则补进下表。

## 总原则

1. 关键字、标准库类型名用行内代码写原文（`` `public:` ``、`` `std::array` ``、`` `true` ``），中文只作说明，不替代源码词。
2. 一个概念全书一个中文称呼；自造比喻（「公开段」「私有段」「公共头」）一律禁用。
3. 读者正文仍「不讲语言课」：能写「谁调用、写在哪个文件、如何验证」就不展开语法定义；必须点名时用本表。

## A. 访问控制

| 源码 / 英文 | 本仓中文 | 禁用 |
| --- | --- | --- |
| access specifier | 访问说明符 | — |
| access control | 访问控制 | — |
| `public:` 成员 | **公开成员** | 公开段；公共成员；公有段 |
| `private:` 成员 | **私有成员** | 私有段 |
| `protected:` 成员 | **受保护成员** | 保护段；保护用（小众） |
| 指类里那一截声明 | 写 `` `public:` `` / `` `private:` `` 下（或之后） | 「…段」 |

改写口诀：不要说「公开段下面还有私有段」→ 说「入口在 `` `public:` `` 下；数据成员在 `` `private:` `` 下」。

## B. 类与成员

| 英文 / 源码 | 本仓中文 | 禁用或备注 |
| --- | --- | --- |
| class / struct / union | 类 / 结构体 / 联合体 | 正文可写 `` `class Game` `` |
| member | 成员 | — |
| member function | 成员函数 | 不用「方法」作主称呼 |
| data member / non-static data member | 数据成员 / 非静态数据成员 | 优于「成员变量」作主称呼 |
| static member | 静态成员 | — |
| constructor / destructor | 构造函数 / 析构函数 | — |
| default constructor | 默认构造函数 | 头内 `` `= default` `` 可直写 |
| copy / move | 拷贝 / 移动 | 拷贝构造、移动赋值等 |
| friend | 友元 | 少用；需要时写 `` `friend` `` |
| this | `` `this` `` | 不译「这个指针」撑句 |
| encapsulation（口语） | 写可观察边界（外界碰不到…） | 空泛「封装」单字 |

## C. 声明、定义与文件

| 英文 / 源码 | 本仓中文 | 禁用或备注 |
| --- | --- | --- |
| declaration / definition | 声明 / 定义 | 细则见 `bg-terminology-v1`；正文不贴「是声明/是定义」标签 |
| function prototype | （禁用） | 改「函数声明 / 成员函数声明」 |
| header file / source file | 头文件 / 源文件 | — |
| 库对外头文件 | 库对外头文件 | 禁用「公共头」「公开头文件」 |
| translation unit | 翻译单元 | agent 内部可用；读者正文少用 |
| include | `` `#include` `` / 包含 | 不写「引入头」含混说法 |
| ODR | 单一定义规则；或写具体后果 | 读者正文尽量避免缩写 |

## D. 类型、对象与值类别

| 英文 / 源码 | 本仓中文 | 备注 |
| --- | --- | --- |
| type / object / value | 类型 / 对象 / 值 | — |
| variable | 变量 | — |
| constant / constexpr 常量 | 常量；源码写 `` `constexpr` `` / `` `inline constexpr` `` | 不堆「编译期常量表达式」长定语 |
| enumeration / enumerator | 枚举 / 枚举项 | — |
| scoped enumeration / `enum class` | 有作用域枚举；正文优先 `` `enum class` `` | 不单称「枚举类」不带源码 |
| unscoped enum | 无作用域枚举 | 本仓领域枚举用 `enum class` |
| underlying type | 底层类型 | agent / 风格知识可用 |
| alias / `using` | 别名 / 别名声明 | — |
| cv-qualification | cv 限定 | 读者少用；写 `` `const` `` |
| lvalue / rvalue | 左值 / 右值 | 读者正文尽量不展开 |
| parameter / argument | 形参 / 实参 | 与 cppreference 一致 |

## E. 指针、引用与生命周期

| 英文 / 源码 | 本仓中文 | 备注 |
| --- | --- | --- |
| pointer / reference | 指针 / 引用 | — |
| null pointer / `nullptr` | 空指针；字面量 `` `nullptr` `` | — |
| dangling | 悬空 | 注释可用 |
| smart pointer | 智能指针 | — |
| `unique_ptr` / `shared_ptr` / `weak_ptr` | 保留类型名行内代码；可注「独占 / 共享 / 弱引用」 | 本仓井字棋当前少用 |
| new / delete | `` `new` `` / `` `delete` `` | 教学上本仓优先标准库容器 |
| RAII（口语） | 写「对象析构时释放资源」类事实 | 读者正文慎用缩写 |

## F. 函数、重载与异常

| 英文 / 源码 | 本仓中文 | 备注 |
| --- | --- | --- |
| function / free function | 函数 / 自由函数（命名空间作用域） | 对比成员函数 |
| overload / overload resolution | 重载 / 重载决议 | — |
| override / final | 覆盖；写 `` `override` `` / `` `final` `` | 「重写」易与 overload 混，本仓用「覆盖」 |
| virtual function | 虚函数 | 井字棋当前不用则不硬塞 |
| return type / return value | 返回类型 / 返回值 | — |
| exception / throw / catch | 异常 / 抛出 / 捕获 | 消息格式见 `bg-exception-message-format-v1` |
| `noexcept` | 行内代码保留 | — |
| `[[nodiscard]]` | 行内代码保留 | 旁白不解释成语言课 |

## G. 继承与多态（预留）

| 英文 / 源码 | 本仓中文 |
| --- | --- |
| inheritance | 继承 |
| base class / derived class | 基类 / 派生类 |
| public / protected / private inheritance | 公开 / 受保护 / 私有继承 |
| abstract class / pure virtual | 抽象类 / 纯虚函数 |
| interface（口语） | 对外入口 / 公开成员；或点名函数——不用空泛「接口」单字撑句 |

## H. 模板与泛型（预留）

| 英文 / 源码 | 本仓中文 |
| --- | --- |
| template / class template / function template | 模板 / 类模板 / 函数模板 |
| template parameter / argument | 模板形参 / 模板实参 |
| specialization / instantiation | 特化 / 实例化 |
| concept（C++20） | 概念；写 `` `concept` `` |

## I. 标准库与本仓已用设施

| 英文 / 源码 | 本仓中文 | 备注 |
| --- | --- | --- |
| standard library | 标准库 | — |
| container | 容器 | — |
| `std::array` / `std::vector` / `std::string` | 行内代码类型名 | 首次可一句白话（固定长度数组 / 动态数组 / 字符串） |
| iterator / algorithm | 迭代器 / 算法 | 读者少展开 |
| `std::uint8_t` 等 | 行内代码类型名 | — |
| `std::out_of_range` | 行内代码异常类型名 | — |
| namespace `std` | `` `std` `` 命名空间 | — |

## J. 编译与构建相关中文

| 英文 | 本仓中文 | 权威落点 |
| --- | --- | --- |
| configure / build / test / run | 配置 / 编译 / 测试 / 运行 | `bg-terminology-v1` |
| target | 构建目标 | `bg-cmake-conventions-v1` |
| static / shared library | 静态库 / 动态库 | 本仓称「井字棋动态库」 |
| link | 链接 | — |
| compile_commands.json | 保留文件名 | — |

## K. 布尔与字面量

| 写法 | 本仓 |
| --- | --- |
| `true` / `false` / `nullptr` | 行内代码原样；禁止「返回真 / 假」 |
| 布尔值（概念） | 可用中文「布尔值」 |

## 使用规则

- 读者正文（`content/**`）的禁用行由 `bg-terminology-v1` 摘录并硬闸；`.agents` 文档与代码注释同样遵守本表，注释侧不再另立词表。
- 新增术语时：先在 cppreference 双语表确认通行译法 → 按上表格式补行 → 同步 `bg-terminology-v1` 禁用行（若读者侧需要）→ 在 `bg-chinese-style-cases-v1` 补正反对照（若有好的案例）。

## 来源

- [zh.cppreference 双语术语表](https://zh.cppreference.com/bilingual_glossary)
- [访问说明符](https://zh.cppreference.com/cpp/language/access)
- [Microsoft Learn：成员访问控制（C++）](https://learn.microsoft.com/zh-cn/cpp/cpp/member-access-control-cpp)
- [阮一峰《中文技术文档写作规范》](https://github.com/ruanyf/document-style-guide)
- [华为《中文技术文档写作风格指南》](https://zh-style-guide.readthedocs.io)
