//===----------------------------------------------------------------------===//
// game_state.h - 棋盘状态的规则接口
//
// 声明 GameState 的查询、落子与结果接口；完整规则判断留待后续补全。
//===----------------------------------------------------------------------===//

#pragma once

#include <array>

#include "tic_tac_toe/value_types.h"

namespace tic_tac_toe {

// 3×3 棋盘的状态：查询格子、提交落子并报告终局结果。
class GameState {
 public:
  // 初始状态：全部格子为空。
  GameState();

  // 查询格子内容；position 必须合法。
  Mark MarkAt(Position position) const;

  // 落子：越界拒绝并保持棋盘不变，合法位置写入棋子。
  ApplyResult Apply(Move move);

  // 终局结果：完整规则补全前固定返回进行中。
  GameStatus Status() const;

 private:
  // 按行优先顺序存放 9 个格子。
  std::array<Mark, kRows * kCols> cells_;
};

}  // namespace tic_tac_toe
