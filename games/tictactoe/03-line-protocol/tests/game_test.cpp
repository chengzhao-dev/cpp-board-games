//===------------------------------------------------------------------------------------------===//
// game_test.cpp - 回合、拒绝落子与终局测试。
//
// 固定错人落子、三连、对角线、平局、落子记录与拒绝分支。
//===------------------------------------------------------------------------------------------===//

#include "game.h"

#include <vector>

#include <gtest/gtest.h>

#include "board.h"
#include "test_support.h"

namespace {

using tictactoe::CellState;
using tictactoe::Game;
using tictactoe::GameResult;
using tictactoe::Move;
using tictactoe::PlaceResult;
using tictactoe::Player;
using tictactoe::testing::Play;

// 后手在先手之前落子会被拒绝，棋盘保持为空。
TEST(GameTest, RejectsWrongPlayer) {
  Game game;
  EXPECT_EQ(game.TryPlace({.position = {.row = 0, .col = 0}, .player = Player::kNought}),
            PlaceResult::kRejected);
  EXPECT_EQ(game.GetCellState({.row = 0, .col = 0}), CellState::kEmpty);
  EXPECT_EQ(game.GetCurrentPlayer(), Player::kCross);
}

// 第一行三连时 X 获胜。
TEST(GameTest, RowWin) {
  Game game;
  Play(game, {{.row = 0, .col = 0},
              {.row = 1, .col = 0},
              {.row = 0, .col = 1},
              {.row = 1, .col = 1},
              {.row = 0, .col = 2}});
  EXPECT_EQ(game.GetResult(), GameResult::kCrossWin);
}

// 第一列三连时 X 获胜。
TEST(GameTest, ColumnWin) {
  Game game;
  Play(game, {{.row = 0, .col = 0},
              {.row = 0, .col = 1},
              {.row = 1, .col = 0},
              {.row = 1, .col = 1},
              {.row = 2, .col = 0}});
  EXPECT_EQ(game.GetResult(), GameResult::kCrossWin);
}

// 主对角线三连时 X 获胜。
TEST(GameTest, MainDiagonalWin) {
  Game game;
  Play(game, {{.row = 0, .col = 0},
              {.row = 0, .col = 1},
              {.row = 1, .col = 1},
              {.row = 0, .col = 2},
              {.row = 2, .col = 2}});
  EXPECT_EQ(game.GetResult(), GameResult::kCrossWin);
}

// 副对角线三连时 X 获胜。
TEST(GameTest, AntiDiagonalWin) {
  Game game;
  Play(game, {{.row = 0, .col = 2},
              {.row = 0, .col = 0},
              {.row = 1, .col = 1},
              {.row = 1, .col = 0},
              {.row = 2, .col = 0}});
  EXPECT_EQ(game.GetResult(), GameResult::kCrossWin);
}

// 下满且没有三连时为平局。
TEST(GameTest, DrawWhenBoardFillsWithoutThree) {
  Game game;
  Play(game, {{.row = 0, .col = 0},
              {.row = 0, .col = 1},
              {.row = 0, .col = 2},
              {.row = 1, .col = 2},
              {.row = 1, .col = 0},
              {.row = 1, .col = 1},
              {.row = 2, .col = 1},
              {.row = 2, .col = 0},
              {.row = 2, .col = 2}});
  EXPECT_EQ(game.GetResult(), GameResult::kDraw);
}

// 末尾一行三连时 O 获胜。
TEST(GameTest, NoughtWinsWithLastRow) {
  Game game;
  Play(game, {{.row = 0, .col = 0},
              {.row = 2, .col = 0},
              {.row = 0, .col = 1},
              {.row = 2, .col = 1},
              {.row = 1, .col = 1},
              {.row = 2, .col = 2}});
  EXPECT_EQ(game.GetResult(), GameResult::kNoughtWin);
}

// 终局之后再落子会被拒绝。
TEST(GameTest, RejectsMoveAfterWin) {
  Game game;
  Play(game, {{.row = 0, .col = 0},
              {.row = 1, .col = 0},
              {.row = 0, .col = 1},
              {.row = 1, .col = 1},
              {.row = 0, .col = 2}});
  EXPECT_EQ(game.TryPlace({.position = {.row = 2, .col = 2}, .player = Player::kNought}),
            PlaceResult::kRejected);
  EXPECT_EQ(game.GetCellState({.row = 2, .col = 2}), CellState::kEmpty);
  EXPECT_EQ(game.GetHistory().size(), 5U);
}

// 已占用的棋盘格子不能再次落子，轮次保持不变。
TEST(GameTest, RejectsOccupiedCell) {
  Game game;
  Play(game, {{.row = 1, .col = 1}});
  EXPECT_EQ(game.TryPlace({.position = {.row = 1, .col = 1}, .player = Player::kNought}),
            PlaceResult::kRejected);
  EXPECT_EQ(game.GetCellState({.row = 1, .col = 1}), CellState::kCross);
  EXPECT_EQ(game.GetCurrentPlayer(), Player::kNought);
  EXPECT_EQ(game.GetHistory().size(), 1U);
}

// 出界坐标不能落子，棋盘与轮次都保持不变。
TEST(GameTest, RejectsPositionOutsideBoard) {
  Game game;
  EXPECT_EQ(game.TryPlace({.position = {.row = -1, .col = 0}, .player = Player::kCross}),
            PlaceResult::kRejected);
  EXPECT_EQ(
      game.TryPlace({.position = {.row = 0, .col = tictactoe::kCols}, .player = Player::kCross}),
      PlaceResult::kRejected);
  EXPECT_TRUE(game.GetHistory().empty());
  EXPECT_EQ(game.GetCurrentPlayer(), Player::kCross);
}

// 落子记录按发生顺序保存坐标与执行玩家。
TEST(GameTest, HistoryRecordsMovesInOrder) {
  Game game;
  Play(game, {{.row = 0, .col = 0}, {.row = 1, .col = 1}, {.row = 0, .col = 1}});
  const std::vector<Move>& history = game.GetHistory();
  ASSERT_EQ(history.size(), 3U);
  EXPECT_EQ(history[0].position.row, 0);
  EXPECT_EQ(history[0].position.col, 0);
  EXPECT_EQ(history[0].player, Player::kCross);
  EXPECT_EQ(history[1].position.row, 1);
  EXPECT_EQ(history[1].position.col, 1);
  EXPECT_EQ(history[1].player, Player::kNought);
  EXPECT_EQ(history[2].position.row, 0);
  EXPECT_EQ(history[2].position.col, 1);
  EXPECT_EQ(history[2].player, Player::kCross);
}

}  // namespace
