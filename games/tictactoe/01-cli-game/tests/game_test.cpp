//===----------------------------------------------------------------------===//
// game_test.cpp - 回合、拒绝落子与终局测试。
//
// 固定错人落子、三连、对角线和平局。
//===----------------------------------------------------------------------===//

#include "game.h"

#include <gtest/gtest.h>

#include <initializer_list>

#include "board.h"

namespace {

using tictactoe::CellPosition;
using tictactoe::CellState;
using tictactoe::Game;
using tictactoe::GameResult;
using tictactoe::PlaceResult;
using tictactoe::Player;

CellPosition At(int row, int col) {
  return {.row = row, .col = col};
}

// 按顺序落下这些坐标。调用方保证每步都应由当前玩家落子。
void Play(Game& game, std::initializer_list<CellPosition> moves) {
  for (const CellPosition position : moves) {
    ASSERT_EQ(
        game.Place({.position = position, .player = game.CurrentPlayer()}),
        PlaceResult::kPlaced);
  }
}

// 后手在先手之前落子会被拒绝，棋盘保持为空。
TEST(GameTest, RejectsWrongPlayer) {
  Game game;
  EXPECT_EQ(game.Place({.position = At(0, 0), .player = Player::kNought}),
            PlaceResult::kRejected);
  EXPECT_EQ(game.GetCellState(At(0, 0)), CellState::kEmpty);
  EXPECT_EQ(game.CurrentPlayer(), Player::kCross);
}

// 第一行三连时 X 获胜。
TEST(GameTest, RowWin) {
  Game game;
  Play(game, {At(0, 0), At(1, 0), At(0, 1), At(1, 1), At(0, 2)});
  EXPECT_EQ(game.GetResult(), GameResult::kCrossWin);
}

// 第一列三连时 X 获胜。
TEST(GameTest, ColumnWin) {
  Game game;
  Play(game, {At(0, 0), At(0, 1), At(1, 0), At(1, 1), At(2, 0)});
  EXPECT_EQ(game.GetResult(), GameResult::kCrossWin);
}

// 主对角线三连时 X 获胜。
TEST(GameTest, MainDiagonalWin) {
  Game game;
  Play(game, {At(0, 0), At(0, 1), At(1, 1), At(0, 2), At(2, 2)});
  EXPECT_EQ(game.GetResult(), GameResult::kCrossWin);
}

// 副对角线三连时 X 获胜。
TEST(GameTest, AntiDiagonalWin) {
  Game game;
  Play(game, {At(0, 2), At(0, 0), At(1, 1), At(1, 0), At(2, 0)});
  EXPECT_EQ(game.GetResult(), GameResult::kCrossWin);
}

// 下满且没有三连时为平局。
TEST(GameTest, DrawWhenBoardFillsWithoutThree) {
  Game game;
  Play(game, {At(0, 0), At(0, 1), At(0, 2), At(1, 2), At(1, 0), At(1, 1),
              At(2, 1), At(2, 0), At(2, 2)});
  EXPECT_EQ(game.GetResult(), GameResult::kDraw);
}

// 终局之后再落子会被拒绝。
TEST(GameTest, RejectsMoveAfterWin) {
  Game game;
  Play(game, {At(0, 0), At(1, 0), At(0, 1), At(1, 1), At(0, 2)});
  EXPECT_EQ(game.Place({.position = At(2, 2), .player = Player::kNought}),
            PlaceResult::kRejected);
  EXPECT_EQ(game.GetCellState(At(2, 2)), CellState::kEmpty);
  EXPECT_EQ(game.History().size(), 5U);
}

}  // namespace
