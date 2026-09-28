---
name: testing
description: 组织 C++、Python 和文档的分层验证；规划测试或验收范围时使用
metadata:
  short-description: 分层测试与验收
---

# Skill: testing

承载 C++、Python 与文档的分层验证流程。

## 适用场景

- 规划规则测试、CLI smoke test 或验证范围。
- 判断某次改动需要跑哪些验证。
- **不适用**：实现测试代码本身（转 `cpp-development`）、文档写法（转 `writing-quarto`）。

## 任务路由

| 任务 | 读取 |
| --- | --- |
| 改动后圈定验证范围 | `references/verification-matrix.md` |
| 游戏 STAR 中测试步骤职责与报错记录落点 | `.agents/knowledge/agent-workspace/planning/engineering-storyline.md` |
| 验收边界与完成定义（读者视角，需要完整语义时） | `content/tic-tac-toe/06-cli-and-acceptance.qmd` |

## P0 硬约束

1. C++ 规则测试直接链接游戏库，不通过 CLI 覆盖所有逻辑。
2. CTest 由各阶段维护：测试注册在各阶段 `CMakeLists.txt`，通过该阶段 `build-and-run.sh` 运行；根目录不构建，不做根级统一发现。
3. CLI 测试只验证最小流程和输入输出。
4. Python 测试验证脚本、JSON 协议和子进程边界。
5. 修改共享代码时扩大到所有受影响游戏。
6. 需要时增加 AddressSanitizer、UndefinedBehaviorSanitizer 和 Windows CI。

## 完成判据

- [ ] 验证范围与改动范围匹配，CTest 全部通过。
- [ ] 文档中的验收描述与实际可执行验证一致。
