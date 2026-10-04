//===----------------------------------------------------------------------===//
// game.h - 定义井字棋的对局流程和结果。
//
// 提供玩家、落子和 Game；棋盘格子的保存由 Board 负责。
//===----------------------------------------------------------------------===//

#pragma once

#include <cstdint>
#include <vector>

#include "board.h"

namespace tictactoe {

/// 对局中的玩家。
enum class Player : std::uint8_t {
  kCross = 0,
  kNought = 1,
};

/// 一次落子的处理结果。
enum class PlaceResult : std::uint8_t {
  kPlaced = 0,    ///< 落子已接受。
  kRejected = 1,  ///< 落子被拒绝，局面保持不变。
};

/// 对局的当前结果。
enum class GameResult : std::uint8_t {
  kInProgress = 0,  ///< 对局可以继续落子。
  kCrossWin = 1,    ///< X 获胜：达成三连。
  kNoughtWin = 2,   ///< O 获胜：达成三连。
  kDraw = 3,        ///< 平局：棋盘已满且双方均未三连。
};

/// 表示一名玩家的一次落子。
struct Move {
  CellPosition position;
  Player player = Player::kCross;
};

/// 由对局玩家得到应写入的棋盘格子状态。
///
/// @param player 对局玩家。
/// @return 该玩家应写入的棋盘格子状态。
constexpr CellState CellStateFor(Player player) {
  return player == Player::kCross ? CellState::kCross : CellState::kNought;
}

/// 管理轮次、落子记录和对局结果。
class Game {
 public:
  /// 构造函数：创建空棋盘，轮到 X 落子。
  Game() = default;

  /// 返回当前应当落子的玩家。
  [[nodiscard]] Player CurrentPlayer() const;

  /// 获取当前对局结果。
  [[nodiscard]] GameResult GetResult() const;

  /// 获取指定坐标处的格子状态。
  ///
  /// @param position 行列坐标。
  /// @return 该坐标处的棋盘格子状态。
  /// @throw std::out_of_range 坐标不在棋盘范围内。
  [[nodiscard]] CellState GetCellState(CellPosition position) const;

  /// 尝试接受一次落子。
  ///
  /// 玩家、坐标或格子不符合规则时拒绝，局面保持不变。
  ///
  /// @param move 待执行的落子。
  /// @return 接受时返回 kPlaced，拒绝时返回 kRejected。
  [[nodiscard]] PlaceResult Place(const Move& move);

  /// 返回已接受的落子，顺序与发生顺序相同。
  [[nodiscard]] const std::vector<Move>& History() const;

 private:
  Board board_;
  Player current_player_ = Player::kCross;
  GameResult result_ = GameResult::kInProgress;
  std::vector<Move> history_;
};

}  // namespace tictactoe
