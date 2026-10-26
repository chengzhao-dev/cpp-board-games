//===------------------------------------------------------------------------------------------===//
// testing-board.cpp - Board 的行为测试。
//
// 验证空棋盘、占格、非法坐标、不可覆盖写入、下满判定、清空与终局判定。
//===------------------------------------------------------------------------------------------===//

#include <array>
#include <cstddef>
#include <stdexcept>
#include <string>

#include <gtest/gtest.h>

#include "board.h"

namespace {

using tictactoe::Board;
using tictactoe::CellPosition;
using tictactoe::CellType;

// 新建棋盘的每个棋盘格子均为空。
TEST(BoardTest, InitialBoardIsEmpty) {
  const Board board;
  for (int row = 0; row < tictactoe::kBoardRows; ++row) {
    for (int col = 0; col < tictactoe::kBoardCols; ++col) {
      EXPECT_EQ(board.GetCellType({.row = row, .col = col}), CellType::kEmpty);
    }
  }
}

// 坐标范围包含左上角和右下角。
TEST(BoardTest, ValidPositionIncludesBothCorners) {
  EXPECT_TRUE(Board::IsInRange({.row = 0, .col = 0}));
  EXPECT_TRUE(
      Board::IsInRange({.row = tictactoe::kBoardRows - 1, .col = tictactoe::kBoardCols - 1}));
}

// 写入 X 后，中心棋盘格子保存 X。
TEST(BoardTest, PlaceCellWritesEmptyCell) {
  Board board;
  const CellPosition center{.row = 1, .col = 1};
  EXPECT_TRUE(board.PlaceCell(center, CellType::kX));
  EXPECT_EQ(board.GetCellType(center), CellType::kX);
}

// `kEmpty` 类型不是一次有效写入。
TEST(BoardTest, PlaceCellRejectsEmptyType) {
  Board board;
  const CellPosition center{.row = 1, .col = 1};
  EXPECT_FALSE(board.PlaceCell(center, CellType::kEmpty));
  EXPECT_EQ(board.GetCellType(center), CellType::kEmpty);
}

// 已占用的棋盘格子不能被第二次写入。
TEST(BoardTest, PlaceCellRejectsOccupiedCell) {
  Board board;
  const CellPosition origin{.row = 0, .col = 0};
  ASSERT_TRUE(board.PlaceCell(origin, CellType::kX));
  EXPECT_FALSE(board.PlaceCell(origin, CellType::kO));
  EXPECT_EQ(board.GetCellType(origin), CellType::kX);
}

// 负坐标和上界坐标都不能写入。
TEST(BoardTest, PlaceCellRejectsInvalidPosition) {
  Board board;
  EXPECT_FALSE(board.PlaceCell({.row = -1, .col = 0}, CellType::kX));
  EXPECT_FALSE(board.PlaceCell({.row = 0, .col = -1}, CellType::kO));
  EXPECT_FALSE(board.PlaceCell({.row = tictactoe::kBoardRows, .col = 0}, CellType::kX));
  EXPECT_FALSE(board.PlaceCell({.row = 0, .col = tictactoe::kBoardCols}, CellType::kO));
  EXPECT_EQ(board.GetCellType({.row = 0, .col = 0}), CellType::kEmpty);
}

// 非法坐标不能用于读取棋盘格子类型。
TEST(BoardTest, GetCellTypeThrowsForInvalidPosition) {
  const Board board;
  EXPECT_THROW((void)board.GetCellType({.row = -1, .col = 0}), std::out_of_range);
  EXPECT_THROW((void)board.GetCellType({.row = 0, .col = -1}), std::out_of_range);
  EXPECT_THROW((void)board.GetCellType({.row = tictactoe::kBoardRows, .col = 0}),
               std::out_of_range);
  EXPECT_THROW((void)board.GetCellType({.row = 0, .col = tictactoe::kBoardCols}),
               std::out_of_range);
}

// 非法坐标抛出的异常文案带函数名和行列值。
TEST(BoardTest, GetCellTypeWhatTextForInvalidPosition) {
  const Board board;
  try {
    (void)board.GetCellType({.row = -1, .col = 0});
    FAIL() << "坐标不在棋盘范围内时应抛出 std::out_of_range";
  } catch (const std::out_of_range& error) {
    const std::string message = error.what();
    EXPECT_NE(message.find("Board::GetCellType:"), std::string::npos);
    EXPECT_NE(message.find("row=-1"), std::string::npos);
    EXPECT_NE(message.find("col=0"), std::string::npos);
  }
}

// 每落一子之前棋盘都未满，九个棋盘格子全部落子后才为满。
TEST(BoardTest, IsFullOnlyAfterEveryCellPlaced) {
  Board board;
  for (int row = 0; row < tictactoe::kBoardRows; ++row) {
    for (int col = 0; col < tictactoe::kBoardCols; ++col) {
      EXPECT_FALSE(board.IsFull());
      ASSERT_TRUE(board.PlaceCell({.row = row, .col = col}, CellType::kX));
    }
  }
  EXPECT_TRUE(board.IsFull());
}

// 开局棋盘没有赢家。
TEST(BoardTest, GetWinnerHasNoValueOnNewBoard) {
  const Board board;
  EXPECT_FALSE(board.GetWinner().has_value());
  EXPECT_FALSE(board.IsWin());
  EXPECT_FALSE(board.IsGameOver());
}

// 一行 kX 时 GetWinner 返回 kX。
TEST(BoardTest, GetWinnerReturnsXForTopRow) {
  Board board;
  for (int col = 0; col < tictactoe::kBoardCols; ++col) {
    ASSERT_TRUE(board.PlaceCell({.row = 0, .col = col}, CellType::kX));
  }
  ASSERT_TRUE(board.GetWinner().has_value());
  EXPECT_EQ(*board.GetWinner(), CellType::kX);
  EXPECT_TRUE(board.IsWin());
  EXPECT_TRUE(board.IsGameOver());
  EXPECT_FALSE(board.IsDraw());
}

// 下满且没有三连时 IsDraw 为真。
TEST(BoardTest, IsDrawWhenFullWithoutWinner) {
  Board board;
  const std::array<CellType, static_cast<size_t>(tictactoe::kBoardRows * tictactoe::kBoardCols)>
      fills = {{
          CellType::kX,
          CellType::kX,
          CellType::kO,  // 第一行。
          CellType::kO,
          CellType::kO,
          CellType::kX,  // 第二行。
          CellType::kX,
          CellType::kO,
          CellType::kX,  // 第三行。
      }};
  for (int index = 0; index < tictactoe::kBoardRows * tictactoe::kBoardCols; ++index) {
    const int row = index / tictactoe::kBoardCols;
    const int col = index % tictactoe::kBoardCols;
    ASSERT_TRUE(board.PlaceCell({.row = row, .col = col}, fills.at(index)));
  }
  EXPECT_TRUE(board.IsFull());
  EXPECT_FALSE(board.GetWinner().has_value());
  EXPECT_TRUE(board.IsDraw());
}

// 假设在空角补上 X 后，第一行三连；IsLineComplete 对 X 为真、对 O 为假，棋盘保持不变。
TEST(BoardTest, IsLineCompleteProbesWithoutPlacing) {
  Board board;
  ASSERT_TRUE(board.PlaceCell({.row = 0, .col = 0}, CellType::kX));
  ASSERT_TRUE(board.PlaceCell({.row = 0, .col = 1}, CellType::kX));
  const CellPosition empty_corner{.row = 0, .col = 2};
  EXPECT_TRUE(board.IsLineComplete(empty_corner, CellType::kX));
  EXPECT_FALSE(board.IsLineComplete(empty_corner, CellType::kO));
  EXPECT_FALSE(board.IsLineComplete({.row = 0, .col = 0}, CellType::kX));
  EXPECT_EQ(board.GetCellType(empty_corner), CellType::kEmpty);
  EXPECT_FALSE(board.GetWinner().has_value());
}

// 清空棋盘后九个棋盘格子恢复为空，终局查询回到开局，同一格可以再次写入。
TEST(BoardTest, ClearRestoresEmptyBoard) {
  Board board;
  ASSERT_TRUE(board.PlaceCell({.row = 0, .col = 0}, CellType::kX));
  ASSERT_TRUE(board.PlaceCell({.row = 0, .col = 1}, CellType::kX));
  ASSERT_TRUE(board.PlaceCell({.row = 0, .col = 2}, CellType::kX));
  ASSERT_TRUE(board.IsWin());

  board.Clear();

  EXPECT_FALSE(board.GetWinner().has_value());
  EXPECT_FALSE(board.IsFull());
  EXPECT_FALSE(board.IsGameOver());
  EXPECT_TRUE(board.PlaceCell({.row = 0, .col = 0}, CellType::kO));
}

}  // namespace
