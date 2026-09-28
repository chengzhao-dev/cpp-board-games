//===----------------------------------------------------------------------===//
// game_state.cpp - GameState 的实现
//
// 只实现初始状态、格子查询、越界保护与占格写入；完整规则后续补全。
//===----------------------------------------------------------------------===//

#include "tic_tac_toe/game_state.h"

namespace tic_tac_toe {

GameState::GameState() {
  cells_.fill(Mark::kEmpty);
}

Mark GameState::MarkAt(Position position) const {
  return cells_[position.row * kCols + position.col];
}

ApplyResult GameState::Apply(Move move) {
  if (!IsValid(move.position)) {
    return ApplyResult::kRejected;
  }
  const int index = move.position.row * kCols + move.position.col;
  cells_[index] = MarkOf(move.player);
  return ApplyResult::kAccepted;
}

GameStatus GameState::Status() const {
  return GameStatus::kInProgress;
}

}  // namespace tic_tac_toe
