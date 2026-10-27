/// @file board.cpp
/// @brief 棋盘格子的读写与三连、平局判定。
///
/// 写入只改目标棋盘格子；胜负判定与三连推演共用一张八条线表。

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

bool Board::IsGameOver() const {
  return IsWin() || IsDraw();
}

bool Board::IsWin() const {
  return GetWinner().has_value();
}

bool Board::IsDraw() const {
  return IsFull() && !IsWin();
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
  if (HasLine(CellType::kX)) {
    return CellType::kX;
  }
  if (HasLine(CellType::kO)) {
    return CellType::kO;
  }
  return std::nullopt;
}

bool Board::PlaceCell(CellPosition position, CellType cell_type) {
  /// 越界或写入空类型时直接拒绝，不碰数组。
  if (!IsInRange(position) || cell_type == CellType::kEmpty) {
    return false;
  }

  /// 已确认坐标在界内；目标棋盘格子已有棋子时同样不覆盖。
  CellType& cell = cells_.at(position.row).at(position.col);
  if (cell != CellType::kEmpty) {
    return false;
  }

  /// 越界、空类型与已占都已在赋值前返回，走到这里棋盘保持原样。
  cell = cell_type;
  return true;
}

void Board::Clear() noexcept {
  /// 整体赋回默认值，九个棋盘格子一起恢复为空。
  cells_ = {};
}

bool Board::IsLineComplete(CellPosition position, CellType cell_type) const {
  /// 拒绝条件与 PlaceCell 相同：越界、空类型、目标棋盘格子已有棋子。
  if (!IsInRange(position) || cell_type == CellType::kEmpty) {
    return false;
  }
  if (cells_.at(position.row).at(position.col) != CellType::kEmpty) {
    return false;
  }

  /// 候选坐标视为已放入该类型，其余棋盘格子照常读取。
  const auto matches = [&](CellPosition cell) {
    return cell == position || cells_.at(cell.row).at(cell.col) == cell_type;
  };

  /// 先找包含候选坐标的那条线，再确认整条线都匹配。
  return std::ranges::any_of(kLines, [&](const auto& line) {
    return std::ranges::find(line, position) != line.end() && std::ranges::all_of(line, matches);
  });
}

bool Board::HasLine(CellType cell_type) const {
  /// 逐格比较棋盘格子类型；不用编号求和，和相等不代表整条线都是同一种棋子。
  return std::ranges::any_of(kLines, [&](const auto& line) {
    return std::ranges::all_of(line, [&](CellPosition position) {
      return cells_.at(position.row).at(position.col) == cell_type;
    });
  });
}

}  // namespace tictactoe
