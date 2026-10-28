/// @file testing-board.cpp
/// @brief Board 的行为测试。
///
/// 验证空棋盘、占格、非法坐标、不可覆盖写入、下满判定、清空与终局判定。

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
using tictactoe::PlaceCellResult;
using tictactoe::WinPreviewResult;

/// 新建棋盘的每个棋盘格子均为空。
TEST(BoardTest, InitialBoardIsEmpty) {
  const Board board;
  for (int row = 0; row < tictactoe::kBoardRows; ++row) {
    for (int col = 0; col < tictactoe::kBoardCols; ++col) {
      EXPECT_EQ(board.GetCellType({.row = row, .col = col}), CellType::kEmpty);
    }
  }
}

/// 坐标范围包含左上角和右下角。
TEST(BoardTest, ValidPositionIncludesBothCorners) {
  EXPECT_TRUE(Board::IsInRange({.row = 0, .col = 0}));
  EXPECT_TRUE(
      Board::IsInRange({.row = tictactoe::kBoardRows - 1, .col = tictactoe::kBoardCols - 1}));
}

/// 写入 X 后，中心棋盘格子保存 X。
TEST(BoardTest, PlaceCellWritesEmptyCell) {
  Board board;
  const CellPosition center{.row = 1, .col = 1};
  EXPECT_EQ(board.PlaceCell(center, CellType::kX), PlaceCellResult::kSuccess);
  EXPECT_EQ(board.GetCellType(center), CellType::kX);
}

/// `kEmpty` 类型不是一次有效写入。
TEST(BoardTest, PlaceCellRejectsEmptyType) {
  Board board;
  const CellPosition center{.row = 1, .col = 1};
  EXPECT_EQ(board.PlaceCell(center, CellType::kEmpty), PlaceCellResult::kEmptyCellType);
  EXPECT_EQ(board.GetCellType(center), CellType::kEmpty);
}

/// 已占用的棋盘格子不能被第二次写入。
TEST(BoardTest, PlaceCellRejectsOccupiedCell) {
  Board board;
  const CellPosition origin{.row = 0, .col = 0};
  ASSERT_EQ(board.PlaceCell(origin, CellType::kX), PlaceCellResult::kSuccess);
  EXPECT_EQ(board.PlaceCell(origin, CellType::kO), PlaceCellResult::kOccupied);
  EXPECT_EQ(board.GetCellType(origin), CellType::kX);
}

/// 负坐标和上界坐标都不能写入。
TEST(BoardTest, PlaceCellRejectsInvalidPosition) {
  Board board;
  EXPECT_EQ(board.PlaceCell({.row = -1, .col = 0}, CellType::kX), PlaceCellResult::kOutOfRange);
  EXPECT_EQ(board.PlaceCell({.row = 0, .col = -1}, CellType::kO), PlaceCellResult::kOutOfRange);
  EXPECT_EQ(board.PlaceCell({.row = tictactoe::kBoardRows, .col = 0}, CellType::kX),
            PlaceCellResult::kOutOfRange);
  EXPECT_EQ(board.PlaceCell({.row = 0, .col = tictactoe::kBoardCols}, CellType::kO),
            PlaceCellResult::kOutOfRange);
  EXPECT_EQ(board.GetCellType({.row = 0, .col = 0}), CellType::kEmpty);
}

/// 落子校验给出与 PlaceCell 相同的拒绝原因，且不改棋盘。
TEST(BoardTest, CheckPlaceableReportsReasonWithoutPlacing) {
  Board board;
  EXPECT_EQ(board.CheckPlaceable({.row = 0, .col = 0}, CellType::kX),
            PlaceCellResult::kSuccess);
  EXPECT_EQ(board.CheckPlaceable({.row = 3, .col = 0}, CellType::kX),
            PlaceCellResult::kOutOfRange);
  EXPECT_EQ(board.CheckPlaceable({.row = 0, .col = 0}, CellType::kEmpty),
            PlaceCellResult::kEmptyCellType);
  EXPECT_EQ(board.GetCellType({.row = 0, .col = 0}), CellType::kEmpty);
}

/// 非法坐标不能用于读取棋盘格子类型。
TEST(BoardTest, GetCellTypeThrowsForInvalidPosition) {
  const Board board;
  EXPECT_THROW((void)board.GetCellType({.row = -1, .col = 0}), std::out_of_range);
  EXPECT_THROW((void)board.GetCellType({.row = 0, .col = -1}), std::out_of_range);
  EXPECT_THROW((void)board.GetCellType({.row = tictactoe::kBoardRows, .col = 0}),
               std::out_of_range);
  EXPECT_THROW((void)board.GetCellType({.row = 0, .col = tictactoe::kBoardCols}),
               std::out_of_range);
}

/// 非法坐标抛出的异常文案带函数名和行列值。
TEST(BoardTest, GetCellTypeErrorMessageIncludesPosition) {
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

/// 每落一子之前棋盘都未满，九个棋盘格子全部落子后才为满。
TEST(BoardTest, IsFullOnlyAfterEveryCellPlaced) {
  Board board;
  for (int row = 0; row < tictactoe::kBoardRows; ++row) {
    for (int col = 0; col < tictactoe::kBoardCols; ++col) {
      EXPECT_FALSE(board.IsFull());
      ASSERT_EQ(board.PlaceCell({.row = row, .col = col}, CellType::kX),
                PlaceCellResult::kSuccess);
    }
  }
  EXPECT_TRUE(board.IsFull());
}

/// 开局棋盘没有赢家。
TEST(BoardTest, GetWinnerHasNoValueOnNewBoard) {
  const Board board;
  EXPECT_FALSE(board.GetWinner().has_value());
}

/// 一行 kX 时 GetWinner 返回 kX。
TEST(BoardTest, GetWinnerReturnsXForTopRow) {
  Board board;
  for (int col = 0; col < tictactoe::kBoardCols; ++col) {
    ASSERT_EQ(board.PlaceCell({.row = 0, .col = col}, CellType::kX), PlaceCellResult::kSuccess);
  }
  ASSERT_TRUE(board.GetWinner().has_value());
  EXPECT_EQ(*board.GetWinner(), CellType::kX);
}

/// 下满且没有三连时棋盘已满、没有赢家；平局由对局层判定。
TEST(BoardTest, FullBoardWithoutWinnerHasNoWinner) {
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
    ASSERT_EQ(board.PlaceCell({.row = row, .col = col}, fills.at(index)),
              PlaceCellResult::kSuccess);
  }
  EXPECT_TRUE(board.IsFull());
  EXPECT_FALSE(board.GetWinner().has_value());
}

/// 假设在空角补上 X 后，第一行三连；PreviewWin 对 X 为 kWouldWin，棋盘保持不变。
TEST(BoardTest, PreviewWinProbesWithoutPlacing) {
  Board board;
  ASSERT_EQ(board.PlaceCell({.row = 0, .col = 0}, CellType::kX), PlaceCellResult::kSuccess);
  ASSERT_EQ(board.PlaceCell({.row = 0, .col = 1}, CellType::kX), PlaceCellResult::kSuccess);
  const CellPosition empty_corner{.row = 0, .col = 2};
  EXPECT_EQ(board.PreviewWin(empty_corner, CellType::kX), WinPreviewResult::kWouldWin);
  EXPECT_EQ(board.PreviewWin(empty_corner, CellType::kO), WinPreviewResult::kWouldNotWin);
  EXPECT_EQ(board.PreviewWin({.row = 0, .col = 0}, CellType::kX),
            WinPreviewResult::kInvalidPlace);
  EXPECT_EQ(board.GetCellType(empty_corner), CellType::kEmpty);
  EXPECT_FALSE(board.GetWinner().has_value());
}

/// 清空棋盘后九个棋盘格子恢复为空，终局查询回到开局，同一格可以再次写入。
TEST(BoardTest, ClearRestoresEmptyBoard) {
  Board board;
  ASSERT_EQ(board.PlaceCell({.row = 0, .col = 0}, CellType::kX), PlaceCellResult::kSuccess);
  ASSERT_EQ(board.PlaceCell({.row = 0, .col = 1}, CellType::kX), PlaceCellResult::kSuccess);
  ASSERT_EQ(board.PlaceCell({.row = 0, .col = 2}, CellType::kX), PlaceCellResult::kSuccess);
  ASSERT_TRUE(board.GetWinner().has_value());

  board.Clear();

  EXPECT_FALSE(board.GetWinner().has_value());
  EXPECT_FALSE(board.IsFull());
  EXPECT_EQ(board.PlaceCell({.row = 0, .col = 0}, CellType::kO), PlaceCellResult::kSuccess);
}

}  // namespace
