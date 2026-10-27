/// @file board.h
/// @brief 定义井字棋棋盘、格子坐标与格子类型。
///
/// 棋盘保存九个棋盘格子的状态，提供只读查询、落子与清空棋盘。

#ifndef TICTACTOE_INCLUDE_BOARD_H_
#define TICTACTOE_INCLUDE_BOARD_H_

#include <array>
#include <cstdint>
#include <optional>

namespace tictactoe {

/// 棋盘行数。
inline constexpr int kBoardRows = 3;
/// 棋盘列数。
inline constexpr int kBoardCols = 3;

/// 棋盘格子类型。
enum class CellType : std::uint8_t {
  kEmpty = 0,  ///< 空格子。
  kX = 1,      ///< X 标记。
  kO = 2,      ///< O 标记。
};

/// 棋盘格子坐标。
struct CellPosition {
  int row = 0;  ///< 行坐标，0 表示最上面一行。
  int col = 0;  ///< 列坐标，0 表示最左边一列。
};

/// 检查两个棋盘格子坐标的行与列是否都相同。
[[nodiscard]] constexpr bool operator==(CellPosition lhs, CellPosition rhs) noexcept {
  return lhs.row == rhs.row && lhs.col == rhs.col;
}

/// 井字棋棋盘。
class Board {
 public:
  /// 检查坐标是否落在棋盘下标区间内。
  ///
  /// 行的有效区间是 [0, kBoardRows)，列的有效区间是 [0, kBoardCols)。
  /// 只判断几何边界，不检查格子是否为空、对局是否已经结束。
  ///
  /// @param position 待检查的坐标。
  /// @return 行和列都在区间内返回 true；任一越界返回 false。
  [[nodiscard]] static bool IsInRange(CellPosition position) noexcept;

  /// 默认构造函数：得到空棋盘，每个棋盘格子都是 kEmpty。
  Board() = default;

  /// 检查指定坐标上的棋盘格子是否为空。
  ///
  /// 越界返回 false。不判断对局是否结束：终局后空格仍在，本函数只按格子上有没有棋子返回。
  ///
  /// @param position 待检查的坐标。
  /// @return 坐标在棋盘内且该棋盘格子为空时返回 true；越界或该棋盘格子已有棋子时返回 false。
  [[nodiscard]] bool IsCellEmpty(CellPosition position) const;

  /// 检查棋盘是否已满。
  [[nodiscard]] bool IsFull() const noexcept;

  /// 检查棋盘是否已有赢家或已经平局。
  [[nodiscard]] bool IsGameOver() const;

  /// 检查棋盘是否已有赢家。
  [[nodiscard]] bool IsWin() const;

  /// 检查棋盘是否已满且没有赢家。
  [[nodiscard]] bool IsDraw() const;

  /// 合法坐标返回该棋盘格子的类型；越界时抛出 std::out_of_range。
  ///
  /// @param position 行列坐标。
  /// @throws std::out_of_range 坐标不在棋盘范围内。
  [[nodiscard]] CellType GetCellType(CellPosition position) const;

  /// 获取形成三连的棋盘格子类型。
  ///
  /// 按 kX、kO 的次序检查，先手优先；同一棋盘不会让双方同时成线，次序一致只为结果可复现。
  ///
  /// @return 有赢家时返回形成三连的棋盘格子类型；没有三连时返回 std::nullopt。
  [[nodiscard]] std::optional<CellType> GetWinner() const;

  /// 在指定坐标放置棋子。
  ///
  /// 越界、已占或要写空棋盘格子都返回 false。
  ///
  /// @param position 目标行列坐标。
  /// @param cell_type 要放置的棋盘格子类型，必须是 kX 或 kO。
  /// @return 放置成功返回 true；坐标越界、要写的是空棋盘格子或目标已有棋子时返回 false，棋盘不变。
  [[nodiscard]] bool PlaceCell(CellPosition position, CellType cell_type);

  /// 清空棋盘：每个棋盘格子恢复为 kEmpty。
  void Clear() noexcept;

  /// 检查在指定坐标放入给定棋子后，是否会形成三连。
  ///
  /// 落子被拒时返回 false；否则返回落子后是否成线，原棋盘不变。
  ///
  /// @param position 假设落子的行列坐标。
  /// @param cell_type 假设放入的棋盘格子类型。
  /// @return 放入后能形成三连返回 true；否则返回 false。
  [[nodiscard]] bool IsLineComplete(CellPosition position, CellType cell_type) const;

 private:
  /// 检查一种棋盘格子类型是否已经三连。
  ///
  /// @param cell_type 要检查的棋盘格子类型。
  /// @return 任一行、任一列或任一条对角线都是该类型时返回 true；否则返回 false。
  [[nodiscard]] bool HasLine(CellType cell_type) const;

  /// 棋盘格子数组：外层下标是行，内层下标是列。
  std::array<std::array<CellType, kBoardCols>, kBoardRows> cells_{};
};

}  // namespace tictactoe

#endif  // TICTACTOE_INCLUDE_BOARD_H_
