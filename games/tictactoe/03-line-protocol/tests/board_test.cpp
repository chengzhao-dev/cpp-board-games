//===----------------------------------------------------------------------===//
// board_test.cpp - Board 的行为测试。
//
// 验证空棋盘、占格、非法坐标和不可覆盖写入。
//===----------------------------------------------------------------------===//

#include "board.h"

#include <gtest/gtest.h>

#include <stdexcept>

namespace {

using tictactoe::Board;
using tictactoe::CellPosition;
using tictactoe::CellState;

// 新建棋盘的每个格子均为空。
TEST(BoardTest, InitialBoardIsEmpty) {
  const Board board;
  for (int row = 0; row < tictactoe::kRows; ++row) {
    for (int col = 0; col < tictactoe::kCols; ++col) {
      EXPECT_EQ(board.GetCellState({.row = row, .col = col}),
                CellState::kEmpty);
    }
  }
}

// 坐标范围包含左上角和右下角。
TEST(BoardTest, ValidPositionIncludesBothCorners) {
  EXPECT_TRUE(Board::IsValidPosition({.row = 0, .col = 0}));
  EXPECT_TRUE(Board::IsValidPosition(
      {.row = tictactoe::kRows - 1, .col = tictactoe::kCols - 1}));
}

// 空格写入后保存对应状态。
TEST(BoardTest, PlacePieceWritesEmptyCell) {
  Board board;
  const CellPosition center{.row = 1, .col = 1};
  EXPECT_TRUE(board.PlacePiece(center, CellState::kCross));
  EXPECT_EQ(board.GetCellState(center), CellState::kCross);
}

// 空状态不是一次有效落子。
TEST(BoardTest, PlacePieceRejectsEmptyState) {
  Board board;
  const CellPosition center{.row = 1, .col = 1};
  EXPECT_FALSE(board.PlacePiece(center, CellState::kEmpty));
  EXPECT_EQ(board.GetCellState(center), CellState::kEmpty);
}

// 已占用的格子不能被第二次写入。
TEST(BoardTest, PlacePieceRejectsOccupiedCell) {
  Board board;
  const CellPosition origin{.row = 0, .col = 0};
  ASSERT_TRUE(board.PlacePiece(origin, CellState::kCross));
  EXPECT_FALSE(board.PlacePiece(origin, CellState::kNought));
  EXPECT_EQ(board.GetCellState(origin), CellState::kCross);
}

// 负坐标和上界坐标都不能写入。
TEST(BoardTest, PlacePieceRejectsInvalidPosition) {
  Board board;
  EXPECT_FALSE(board.PlacePiece({.row = -1, .col = 0}, CellState::kCross));
  EXPECT_FALSE(board.PlacePiece({.row = 0, .col = -1}, CellState::kNought));
  EXPECT_FALSE(
      board.PlacePiece({.row = tictactoe::kRows, .col = 0}, CellState::kCross));
  EXPECT_FALSE(board.PlacePiece({.row = 0, .col = tictactoe::kCols},
                                CellState::kNought));
  EXPECT_EQ(board.GetCellState({.row = 0, .col = 0}), CellState::kEmpty);
}

// 非法坐标不能用于读取格子状态。
TEST(BoardTest, GetCellStateThrowsForInvalidPosition) {
  const Board board;
  EXPECT_THROW((void)board.GetCellState({.row = -1, .col = 0}),
               std::out_of_range);
  EXPECT_THROW((void)board.GetCellState({.row = 0, .col = -1}),
               std::out_of_range);
  EXPECT_THROW((void)board.GetCellState({.row = tictactoe::kRows, .col = 0}),
               std::out_of_range);
  EXPECT_THROW((void)board.GetCellState({.row = 0, .col = tictactoe::kCols}),
               std::out_of_range);
}

}  // namespace
