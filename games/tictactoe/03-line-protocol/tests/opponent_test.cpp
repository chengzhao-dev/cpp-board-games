//===------------------------------------------------------------------------------------------===//
// opponent_test.cpp - 电脑对手的落子选择。
//
// 核对能赢就赢、能挡就挡、优先序、空位清单顺序、终局得分，以及双方极小
// 极大开局成和。
//===------------------------------------------------------------------------------------------===//

#include "opponent.h"

#include <vector>

#include <gtest/gtest.h>

#include "board.h"
#include "game.h"
#include "test_support.h"

namespace {

using tictactoe::Board;
using tictactoe::CellPosition;
using tictactoe::CellState;
using tictactoe::ChooseMove;
using tictactoe::EmptyCells;
using tictactoe::Game;
using tictactoe::GameResult;
using tictactoe::PlaceResult;
using tictactoe::Strength;
using tictactoe::TerminalScore;
using tictactoe::testing::Play;

TEST(OpponentTest, MinimaxTakesTheWin) {
  Game game;
  Play(game,
       {{.row = 0, .col = 0}, {.row = 1, .col = 0}, {.row = 0, .col = 1}, {.row = 1, .col = 1}});
  const auto move = ChooseMove(game, Strength::kMinimax);
  EXPECT_EQ(move.position.row, 0);
  EXPECT_EQ(move.position.col, 2);
}

TEST(OpponentTest, MinimaxBlocksTheOpponent) {
  Game game;
  Play(game, {{.row = 0, .col = 0}, {.row = 1, .col = 0}, {.row = 0, .col = 1}});
  const auto move = ChooseMove(game, Strength::kMinimax);
  EXPECT_EQ(move.position.row, 0);
  EXPECT_EQ(move.position.col, 2);
}

TEST(OpponentTest, HeuristicTakesTheWin) {
  Game game;
  Play(game,
       {{.row = 0, .col = 0}, {.row = 1, .col = 0}, {.row = 0, .col = 1}, {.row = 1, .col = 1}});
  const auto move = ChooseMove(game, Strength::kHeuristic);
  EXPECT_EQ(move.position.row, 0);
  EXPECT_EQ(move.position.col, 2);
}

// 启发式在没有取胜机会时挡住对方马上能赢的一步。
TEST(OpponentTest, HeuristicBlocksTheOpponent) {
  Game game;
  Play(game, {{.row = 0, .col = 0}, {.row = 1, .col = 0}, {.row = 0, .col = 1}});
  const auto move = ChooseMove(game, Strength::kHeuristic);
  EXPECT_EQ(move.position.row, 0);
  EXPECT_EQ(move.position.col, 2);
}

// 没有取胜或封堵需求时先占中心。
TEST(OpponentTest, HeuristicPrefersCenterFirst) {
  const Game game;
  const auto move = ChooseMove(game, Strength::kHeuristic);
  EXPECT_EQ(move.position.row, 1);
  EXPECT_EQ(move.position.col, 1);
}

// 空位清单按行优先顺序给出。
TEST(OpponentTest, EmptyCellsListsRowMajor) {
  Game game;
  Play(game, {{.row = 0, .col = 0}});
  const std::vector<CellPosition> cells = EmptyCells(game);
  ASSERT_EQ(cells.size(), 8U);
  EXPECT_EQ(cells[0].row, 0);
  EXPECT_EQ(cells[0].col, 1);
  EXPECT_EQ(cells[1].row, 0);
  EXPECT_EQ(cells[1].col, 2);
  EXPECT_EQ(cells[2].row, 1);
  EXPECT_EQ(cells[2].col, 0);
  EXPECT_EQ(cells.back().row, 2);
  EXPECT_EQ(cells.back().col, 2);
}

// 得分只区分胜负与未分胜负。
TEST(OpponentTest, TerminalScoreMarksWinLossAndDraw) {
  EXPECT_EQ(TerminalScore(GameResult::kCrossWin), 1);
  EXPECT_EQ(TerminalScore(GameResult::kNoughtWin), -1);
  EXPECT_EQ(TerminalScore(GameResult::kDraw), 0);
  EXPECT_EQ(TerminalScore(GameResult::kInProgress), 0);
}

TEST(OpponentTest, RandomMoveIsLegal) {
  const Game game;
  const auto move = ChooseMove(game, Strength::kRandom);
  EXPECT_TRUE(Board::IsValidPosition(move.position));
  EXPECT_EQ(game.GetCellState(move.position), CellState::kEmpty);
  EXPECT_EQ(move.player, game.GetCurrentPlayer());
}

// 棋盘已经落子时随机落子仍指向空位。
TEST(OpponentTest, RandomMoveIsLegalOnPartlyFilledBoard) {
  Game game;
  Play(game, {{.row = 0, .col = 0}, {.row = 1, .col = 1}, {.row = 2, .col = 2}});
  const auto move = ChooseMove(game, Strength::kRandom);
  EXPECT_TRUE(Board::IsValidPosition(move.position));
  EXPECT_EQ(game.GetCellState(move.position), CellState::kEmpty);
  EXPECT_EQ(move.player, game.GetCurrentPlayer());
}

TEST(OpponentTest, MinimaxSelfPlayDraws) {
  Game game;
  while (game.GetResult() == GameResult::kInProgress) {
    const auto move = ChooseMove(game, Strength::kMinimax);
    ASSERT_EQ(game.TryPlace(move), PlaceResult::kPlaced);
  }
  EXPECT_EQ(game.GetResult(), GameResult::kDraw);
}

}  // namespace
