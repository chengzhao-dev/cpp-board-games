/// @file board.h
/// @brief 定义井字棋棋盘、格子坐标与格子类型。
///
/// 棋盘保存九个棋盘格子的状态，提供查询、落子与清空棋盘。

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
///
/// @param lhs 左操作数。
/// @param rhs 右操作数。
/// @return 行与列都相同返回 true；否则返回 false。
[[nodiscard]] constexpr bool operator==(CellPosition lhs, CellPosition rhs) noexcept {
  return lhs.row == rhs.row && lhs.col == rhs.col;
}

/// 落子结果，用于区分落子时的情况。
enum class PlaceCellResult : std::uint8_t {
  kSuccess = 0,        ///< 落子成功。
  kOutOfRange = 1,     ///< 坐标越界。
  kEmptyCellType = 2,  ///< 传入空棋盘格子类型，非法参数。
  kOccupied = 3,       ///< 目标已有棋子，落子失败。
};

/// 落子推演结果。
enum class WinPreviewResult : std::uint8_t {
  kWouldWin = 0,     ///< 在候选位置落子会形成完整线。
  kWouldNotWin = 1,  ///< 落子合法，但不会成线。
  kInvalidPlace = 2,  ///< 该位置本身不可落子，见 CheckPlaceable。
};

/// 井字棋棋盘。
class Board {
 public:
  /// 构造空棋盘：九个棋盘格子都是 kEmpty。
  Board() noexcept;

  /// 检查坐标是否落在棋盘下标区间内。
  ///
  /// 行的有效区间是 [0, kBoardRows)，列的有效区间是 [0, kBoardCols)。
  /// 只判断几何边界，不检查格子是否为空、对局是否已经结束。
  ///
  /// @param position 待检查的坐标。
  /// @return 行和列都在区间内返回 true；任一越界返回 false。
  [[nodiscard]] static bool IsInRange(CellPosition position) noexcept;

  /// 检查指定坐标上的棋盘格子是否为空。
  ///
  /// 越界返回 false。本函数只看格子上有没有棋子，不判断对局是否结束。
  /// 对局因一方成线而提前结束时，棋盘上尚未落满的空格仍是空的；
  /// 只有下满且没有赢家的平局才会没有空格。
  ///
  /// @param position 待检查的坐标。
  /// @return 坐标在棋盘内且该格子为空时返回 true；越界或已有棋子时返回 false。
  [[nodiscard]] bool IsCellEmpty(CellPosition position) const;

  /// 检查棋盘是否已满。
  ///
  /// @return 九个棋盘格子都不为空时返回 true；否则返回 false。
  [[nodiscard]] bool IsFull() const noexcept;

  /// 合法坐标返回该棋盘格子的类型；越界时抛出 std::out_of_range。
  ///
  /// @param position 行列坐标。
  /// @return 该坐标上的棋盘格子类型。
  /// @throws std::out_of_range 坐标不在棋盘范围内。
  [[nodiscard]] CellType GetCellType(CellPosition position) const;

  /// 获取形成三连的棋盘格子类型。
  ///
  /// 按 kX、kO 的次序检查，先手优先；同一棋盘不会让双方同时成线。
  /// 次序一致只为结果可复现。
  ///
  /// @return 有赢家时返回形成三连的棋盘格子类型；没有三连时返回 std::nullopt。
  [[nodiscard]] std::optional<CellType> GetWinner() const;

  /// 检查一次落子是否合法，不修改棋盘。
  ///
  /// 依次检查坐标、棋子类型与目标格子占用情况；任一项不通过就返回对应结果。
  ///
  /// @param position 目标行列坐标。
  /// @param cell_type 要放置的棋盘格子类型。
  /// @return 可以落子返回 kSuccess；否则返回对应的拒绝原因。
  [[nodiscard]] PlaceCellResult CheckPlaceable(CellPosition position, CellType cell_type) const;

  /// 在指定坐标放置棋子。
  ///
  /// @param position 目标行列坐标。
  /// @param cell_type 要放置的棋盘格子类型，必须是 kX 或 kO。
  /// @return 落子成功返回 kSuccess；越界、空类型或目标已有棋子时返回对应枚举，棋盘不变。
  [[nodiscard]] PlaceCellResult PlaceCell(CellPosition position, CellType cell_type);

  /// 清空棋盘：每个棋盘格子恢复为 kEmpty。
  void Clear() noexcept;

  /// 推演在指定坐标放入给定棋子后是否会形成三连，不修改棋盘。
  ///
  /// 先按 CheckPlaceable 判断这一手能否落子：不能落子时返回 kInvalidPlace；
  /// 能落子时只在推演中放下这一子，再检查它所在的线是否整条同色。
  ///
  /// @param position 假设落子的行列坐标。
  /// @param cell_type 假设放入的棋盘格子类型。
  /// @return 不可落子返回 kInvalidPlace；落子后成线返回 kWouldWin；否则返回 kWouldNotWin。
  [[nodiscard]] WinPreviewResult PreviewWin(CellPosition position, CellType cell_type) const;

 private:
  /// 检查一种棋盘格子类型是否已经三连。
  ///
  /// @param cell_type 要检查的棋盘格子类型。
  /// @return 任一行、任一列或任一条对角线都是该类型时返回 true；否则返回 false。
  [[nodiscard]] bool HasLine(CellType cell_type) const;

  /// 棋盘格子数组：外层下标是行，内层下标是列，每个元素表示一个棋盘格子的类型。
  std::array<std::array<CellType, kBoardCols>, kBoardRows> cells_{};
};

}  // namespace tictactoe

#endif  // TICTACTOE_INCLUDE_BOARD_H_
