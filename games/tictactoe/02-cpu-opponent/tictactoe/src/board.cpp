//===----------------------------------------------------------------------===//
// board.cpp - 棋盘格子的读写实现。
//
// 检查坐标边界，并保证已占用的格子不会被覆盖。
//===----------------------------------------------------------------------===//

#include "board.h"

#include <algorithm>
#include <cstddef>
#include <stdexcept>

namespace tictactoe {

// 行和列都必须落在棋盘范围内，任一越界即无效。
bool Board::IsValidPosition(CellPosition position) noexcept {
  return (position.row >= 0 && position.row < kRows) &&
         (position.col >= 0 && position.col < kCols);
}

// 坐标无效时抛出异常，而不是返回空格状态。
CellState Board::GetCellState(CellPosition position) const {
  if (!IsValidPosition(position)) {
    throw std::out_of_range("GetCellState: position is outside the board");
  }

  // 坐标已通过校验，.at() 作为第二道越界防线。
  return cells_.at(ToFlatIndex(position));
}

// 先校验后写入：任何失败都在改动棋盘前返回，拒绝时棋盘保持不变。
bool Board::PlacePiece(CellPosition position, CellState state) {
  if (!IsValidPosition(position) || state == CellState::kEmpty) {
    return false;  // 坐标无效或要写入的是空格，拒绝。
  }

  CellState& cell = cells_.at(ToFlatIndex(position));
  if (cell != CellState::kEmpty) {
    return false;  // 目标格子已被占用，拒绝覆盖。
  }

  cell = state;  // 校验全部通过，写入棋子。
  return true;
}

// 每个格子都有棋子时棋盘已满。
bool Board::IsFull() const noexcept {
  return std::ranges::all_of(
      cells_, [](CellState cell) { return cell != CellState::kEmpty; });
}

// 先跳过前面的整行，再加上列偏移，得到一维索引。
std::size_t Board::ToFlatIndex(CellPosition position) noexcept {
  return (static_cast<std::size_t>(position.row) * kCols) +
         static_cast<std::size_t>(position.col);
}

}  // namespace tictactoe
