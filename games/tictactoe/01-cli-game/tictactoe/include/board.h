//===----------------------------------------------------------------------===//
// board.h - 定义井字棋棋盘及其格子状态。
//
// 提供棋盘尺寸、格子坐标、格子状态和放置棋子的功能。
//===----------------------------------------------------------------------===//

#pragma once

#include <array>
#include <cstddef>
#include <cstdint>

namespace tictactoe {

/// 棋盘的行数。
inline constexpr int kRows = 3;
/// 棋盘的列数。
inline constexpr int kCols = 3;
/// 棋盘包含的格子总数。
inline constexpr int kCellCount = kRows * kCols;

/// 棋盘格子的状态。
enum class CellState : std::uint8_t {
  kEmpty = 0,   ///< 空格。
  kCross = 1,   ///< X 棋子。
  kNought = 2,  ///< O 棋子。
};

/// 表示棋盘格子的行列坐标。
///
/// 行和列从 0 开始，默认构造的坐标是 (0, 0)。
struct CellPosition {
  int row = 0;  ///< 行坐标。
  int col = 0;  ///< 列坐标。
};

/// 表示井字棋的棋盘。
///
/// 提供读取格子状态、放置棋子和检查棋盘是否已满的功能。
///
/// 棋盘为 3 行 3 列。
class Board {
 public:
  /// 检查坐标是否在棋盘范围内。
  ///
  /// @param position 待检查的行列坐标。
  /// @return 坐标在棋盘内返回 true，否则返回 false。
  [[nodiscard]] static bool IsValidPosition(CellPosition position) noexcept;

  /// 构造函数：创建一个所有格子均为空的棋盘。
  Board() = default;

  /// 获取指定坐标处的格子状态。
  ///
  /// @param position 行列坐标。
  /// @return 该坐标处的棋盘格子状态。
  /// @throw std::out_of_range 坐标不在棋盘范围内。
  [[nodiscard]] CellState GetCellState(CellPosition position) const;

  /// 在指定坐标放置棋子。
  ///
  /// 坐标无效、要写入的是空格或目标格子已有棋子时放置失败，棋盘保持不变。
  ///
  /// @param position 目标行列坐标。
  /// @param state 要放置的棋盘格子状态。
  /// @return 放置成功返回 true，否则返回 false。
  [[nodiscard]] bool PlacePiece(CellPosition position, CellState state);

  /// 检查棋盘是否已满。
  [[nodiscard]] bool IsFull() const noexcept;

 private:
  /// 将二维坐标转换为一维索引。
  ///
  /// @param position 已通过 IsValidPosition 检查的行列坐标。
  /// @return 转换得到的一维索引。
  [[nodiscard]] static std::size_t ToFlatIndex(CellPosition position) noexcept;

  // 棋盘格子的存储数组，按行依次存放。
  std::array<CellState, static_cast<std::size_t>(kCellCount)> cells_{};
};

}  // namespace tictactoe
