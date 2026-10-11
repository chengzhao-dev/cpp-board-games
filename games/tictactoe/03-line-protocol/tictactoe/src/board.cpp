//===------------------------------------------------------------------------------------------===//
// board.cpp - 棋盘格子的读写实现。
//
// 检查坐标边界，并保证已占用的棋盘格子不会被覆盖。
//===------------------------------------------------------------------------------------------===//

#include "board.h"

#include <algorithm>
#include <cstddef>
#include <stdexcept>

namespace tictactoe {

bool Board::IsValidPosition(CellPosition position) noexcept {
  return (position.row >= 0 && position.row < kRows) && (position.col >= 0 && position.col < kCols);
}

CellState Board::GetCellState(CellPosition position) const {
  if (!IsValidPosition(position)) {
    throw std::out_of_range("GetCellState: position is outside the board");
  }

  return cells_.at(ToFlatIndex(position));
}

bool Board::PlacePiece(CellPosition position, CellState state) {
  if (!IsValidPosition(position) || state == CellState::kEmpty) {
    return false;  // 坐标无效或要写入的是空格，拒绝。
  }

  CellState& stored = cells_.at(ToFlatIndex(position));
  if (stored != CellState::kEmpty) {
    return false;  // 目标棋盘格子已被占用，拒绝覆盖。
  }

  stored = state;  // 校验全部通过，写入棋子。
  return true;
}

bool Board::IsFull() const noexcept {
  return std::ranges::all_of(cells_, [](CellState state) { return state != CellState::kEmpty; });
}

std::size_t Board::ToFlatIndex(CellPosition position) noexcept {
  return (static_cast<std::size_t>(position.row) * kCols) + static_cast<std::size_t>(position.col);
}

}  // namespace tictactoe
