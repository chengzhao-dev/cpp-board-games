//===----------------------------------------------------------------------===//
// game_state_test.cpp - GameState 的行为测试
//
// 用 GoogleTest 固定初始状态、落子写入、越界拒绝与终局结果的行为。
//===----------------------------------------------------------------------===//

#include "tic_tac_toe/game_state.h"

#include <gtest/gtest.h>

#include "tic_tac_toe/value_types.h"

namespace {

using tic_tac_toe::ApplyResult;
using tic_tac_toe::GameState;
using tic_tac_toe::GameStatus;
using tic_tac_toe::Mark;
using tic_tac_toe::Move;
using tic_tac_toe::Player;

// 初始状态的 9 个格子全部为空。
TEST(GameStateTest, InitialBoardIsEmpty) {
  GameState state;
  for (int row = 0; row < tic_tac_toe::kRows; ++row) {
    for (int col = 0; col < tic_tac_toe::kCols; ++col) {
      EXPECT_EQ(state.MarkAt({row, col}), Mark::kEmpty);
    }
  }
}

// 合法落子返回 kAccepted，并把目标格子标记为落子玩家的棋子。
TEST(GameStateTest, ApplyMarksTargetCell) {
  GameState state;
  const Move move{{1, 1}, Player::kX};
  EXPECT_EQ(state.Apply(move), ApplyResult::kAccepted);
  EXPECT_EQ(state.MarkAt(move.position), Mark::kX);
}

// 越界位置返回 kRejected，棋盘保持不变。
TEST(GameStateTest, ApplyRejectsOutOfBoundsPosition) {
  GameState state;
  const Move out_of_row{{tic_tac_toe::kRows, 0}, Player::kX};
  const Move out_of_col{{0, -1}, Player::kO};
  EXPECT_EQ(state.Apply(out_of_row), ApplyResult::kRejected);
  EXPECT_EQ(state.Apply(out_of_col), ApplyResult::kRejected);
  EXPECT_EQ(state.MarkAt({0, 0}), Mark::kEmpty);
}

// 完整规则补全前，终局结果不随落子变化，固定返回进行中。
TEST(GameStateTest, StatusStaysInProgress) {
  GameState state;
  ASSERT_EQ(state.Apply({{0, 0}, Player::kX}), ApplyResult::kAccepted);
  EXPECT_EQ(state.Status(), GameStatus::kInProgress);
}

}  // namespace
