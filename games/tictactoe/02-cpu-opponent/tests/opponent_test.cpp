//===----------------------------------------------------------------------===//
// opponent_test.cpp - 电脑对手的落子选择。
//
// 核对能赢就赢、能挡就挡，以及双方极小极大开局成和。
//===----------------------------------------------------------------------===//

#include "opponent.h"

#include <gtest/gtest.h>

#include <initializer_list>

#include "board.h"
#include "game.h"

namespace {

using tictactoe::Board;
using tictactoe::CellPosition;
using tictactoe::ChooseMove;
using tictactoe::Game;
using tictactoe::GameResult;
using tictactoe::PlaceResult;
using tictactoe::Strength;

CellPosition At(int row, int col) {
  return {.row = row, .col = col};
}

void Play(Game& game, std::initializer_list<CellPosition> moves) {
  for (const CellPosition position : moves) {
    ASSERT_EQ(
        game.Place({.position = position, .player = game.CurrentPlayer()}),
        PlaceResult::kPlaced);
  }
}

TEST(OpponentTest, MinimaxTakesTheWin) {
  Game game;
  Play(game, {At(0, 0), At(1, 0), At(0, 1), At(1, 1)});
  const auto move = ChooseMove(game, Strength::kMinimax);
  EXPECT_EQ(move.position.row, 0);
  EXPECT_EQ(move.position.col, 2);
}

TEST(OpponentTest, MinimaxBlocksTheOpponent) {
  Game game;
  Play(game, {At(0, 0), At(1, 0), At(0, 1)});
  const auto move = ChooseMove(game, Strength::kMinimax);
  EXPECT_EQ(move.position.row, 0);
  EXPECT_EQ(move.position.col, 2);
}

TEST(OpponentTest, HeuristicTakesTheWin) {
  Game game;
  Play(game, {At(0, 0), At(1, 0), At(0, 1), At(1, 1)});
  const auto move = ChooseMove(game, Strength::kHeuristic);
  EXPECT_EQ(move.position.row, 0);
  EXPECT_EQ(move.position.col, 2);
}

TEST(OpponentTest, RandomMoveIsLegal) {
  const Game game;
  const auto move = ChooseMove(game, Strength::kRandom);
  EXPECT_TRUE(Board::IsValidPosition(move.position));
  EXPECT_EQ(game.GetCellState(move.position), tictactoe::CellState::kEmpty);
  EXPECT_EQ(move.player, game.CurrentPlayer());
}

TEST(OpponentTest, MinimaxSelfPlayDraws) {
  Game game;
  while (game.GetResult() == GameResult::kInProgress) {
    const auto move = ChooseMove(game, Strength::kMinimax);
    ASSERT_EQ(game.Place(move), PlaceResult::kPlaced);
  }
  EXPECT_EQ(game.GetResult(), GameResult::kDraw);
}

}  // namespace
