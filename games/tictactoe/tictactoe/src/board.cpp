/// @file board.cpp
/// @brief 棋盘格子的读写与三连、平局判定。
///
/// 写入只改目标棋盘格子；胜负判定与推演共用一张八条线表。

#include "board.h"

#include <algorithm>
#include <array>
#include <format>
#include <ranges>
#include <stdexcept>

namespace tictactoe {

/// 八条线的坐标表：三行、三列、两条对角线。
constexpr std::array<std::array<CellPosition, 3>, 8> kLines{{
    {{{.row = 0, .col = 0}, {.row = 0, .col = 1}, {.row = 0, .col = 2}}},  // 行 0
    {{{.row = 1, .col = 0}, {.row = 1, .col = 1}, {.row = 1, .col = 2}}},  // 行 1
    {{{.row = 2, .col = 0}, {.row = 2, .col = 1}, {.row = 2, .col = 2}}},  // 行 2
    {{{.row = 0, .col = 0}, {.row = 1, .col = 0}, {.row = 2, .col = 0}}},  // 列 0
    {{{.row = 0, .col = 1}, {.row = 1, .col = 1}, {.row = 2, .col = 1}}},  // 列 1
    {{{.row = 0, .col = 2}, {.row = 1, .col = 2}, {.row = 2, .col = 2}}},  // 列 2
    {{{.row = 0, .col = 0}, {.row = 1, .col = 1}, {.row = 2, .col = 2}}},  // 对角线
    {{{.row = 0, .col = 2}, {.row = 1, .col = 1}, {.row = 2, .col = 0}}},  // 反对角线
}};

Board::Board() noexcept {
  Clear();
}

bool Board::IsInRange(CellPosition position) noexcept {
  return (position.row >= 0 && position.row < kBoardRows) &&
         (position.col >= 0 && position.col < kBoardCols);
}

bool Board::IsCellEmpty(CellPosition position) const {
  if (!IsInRange(position)) {
    return false;
  }

  return cells_.at(position.row).at(position.col) == CellType::kEmpty;
}

bool Board::IsFull() const noexcept {
  return std::ranges::none_of(cells_ | std::views::join,
                              [](CellType cell_type) { return cell_type == CellType::kEmpty; });
}

CellType Board::GetCellType(CellPosition position) const {
  if (!IsInRange(position)) {
    throw std::out_of_range{std::format(
        "Board::GetCellType: board position is out of range (row={}, col={}); board is {}x{}",
        position.row, position.col, kBoardRows, kBoardCols)};
  }

  return cells_.at(position.row).at(position.col);
}

std::optional<CellType> Board::GetWinner() const {
  // 先查 X：X 先手，双方不可能同时成线，命中即可返回。
  if (HasLine(CellType::kX)) {
    return CellType::kX;
  }

  // X 没有成线时再查 O，此时 O 成线也不可能是双方同时成线。
  if (HasLine(CellType::kO)) {
    return CellType::kO;
  }

  return std::nullopt;
}

PlaceCellResult Board::CheckPlaceable(CellPosition position, CellType cell_type) const {
  // 坐标越界时棋盘外没有格子可写，直接拒绝。
  if (!IsInRange(position)) {
    return PlaceCellResult::kOutOfRange;
  }

  // 空类型表示“没有棋子”，不能作为一次落子写进棋盘。
  if (cell_type == CellType::kEmpty) {
    return PlaceCellResult::kEmptyCellType;
  }

  // 目标格已经有棋子时不能覆盖，否则会改掉已有对局。
  if (!IsCellEmpty(position)) {
    return PlaceCellResult::kOccupied;
  }

  return PlaceCellResult::kSuccess;
}

PlaceCellResult Board::PlaceCell(CellPosition position, CellType cell_type) {
  // 先只做校验，保证被拒的落子不会改动棋盘。
  const PlaceCellResult check = CheckPlaceable(position, cell_type);
  if (check != PlaceCellResult::kSuccess) {
    return check;
  }

  // 校验已通过，写入不会失败。
  cells_.at(position.row).at(position.col) = cell_type;
  return PlaceCellResult::kSuccess;
}

void Board::Clear() noexcept {
  std::ranges::fill(cells_ | std::views::join, CellType::kEmpty);
}

WinPreviewResult Board::PreviewWin(CellPosition position, CellType cell_type) const {
  // 先复用落子校验：不可落子的位置不进入成线推演。
  if (CheckPlaceable(position, cell_type) != PlaceCellResult::kSuccess) {
    return WinPreviewResult::kInvalidPlace;
  }

  // 候选坐标视为已放入该类型，其余棋盘格子照常读取。
  const auto matches = [&](CellPosition cell) {
    return cell == position || cells_.at(cell.row).at(cell.col) == cell_type;
  };

  // 只检查包含候选坐标的那条线：其他线不受这一手影响。
  const bool completes = std::ranges::any_of(kLines, [&](const auto& line) {
    return std::ranges::find(line, position) != line.end() && std::ranges::all_of(line, matches);
  });
  return completes ? WinPreviewResult::kWouldWin : WinPreviewResult::kWouldNotWin;
}

bool Board::HasLine(CellType cell_type) const {
  // 逐格比较棋盘格子类型；不用编号求和，和相等不代表整条线都是同一种棋子。
  return std::ranges::any_of(kLines, [&](const auto& line) {
    return std::ranges::all_of(line, [&](CellPosition position) {
      return cells_.at(position.row).at(position.col) == cell_type;
    });
  });
}

}  // namespace tictactoe
