//===------------------------------------------------------------------------------------------===//
// game.h - 定义井字棋的对局流程和结果。
//
// 提供玩家、落子和 Game；棋盘格子的保存由 Board 负责。
//===------------------------------------------------------------------------------------------===//

#pragma once

#include <cstdint>
#include <vector>

#include "board.h"

namespace tictactoe {

/// 对局玩家。
enum class Player : std::uint8_t {
  kCross = 0,   ///< 先手：使用 X 棋子。
  kNought = 1,  ///< 后手：使用 O 棋子。
};

/// 一次落子的处理结果。
enum class PlaceResult : std::uint8_t {
  kPlaced = 0,    ///< 落子已写入。
  kRejected = 1,  ///< 落子被拒绝，局面保持不变。
};

/// 对局的结果。
enum class GameResult : std::uint8_t {
  kInProgress = 0,  ///< 游戏进行中：对局尚未结束，可继续落子。
  kCrossWin = 1,    ///< X 获胜：达成三连。
  kNoughtWin = 2,   ///< O 获胜：达成三连。
  kDraw = 3,        ///< 平局：棋盘已满且双方均未三连。
};

/// 一名玩家的一次落子。
struct Move {
  CellPosition position;           ///< 落子的行列坐标。
  Player player = Player::kCross;  ///< 执行落子的玩家。
};

/// 由对局玩家得到应写入的棋盘格子状态。
///
/// Player::kCross 对应 CellState::kCross。
constexpr CellState PlayerToCellState(Player player) {
  return player == Player::kCross ? CellState::kCross : CellState::kNought;
}

/// 一局井字棋对局（X 先手，两名玩家轮流落子）。
///
/// 提供获取棋盘格子状态与对局结果、执行落子和查看落子历史的功能。
class Game {
 public:
  /// 构造函数：创建空棋盘，轮到 X 落子。
  Game() = default;

  /// 获取当前落子玩家。
  [[nodiscard]] Player GetCurrentPlayer() const;

  /// 获取当前对局结果。
  [[nodiscard]] GameResult GetResult() const;

  /// 获取指定坐标处的棋盘格子状态。
  ///
  /// @param position 行列坐标。
  /// @throws std::out_of_range 坐标不在棋盘范围内。
  [[nodiscard]] CellState GetCellState(CellPosition position) const;

  /// 获取本局落子历史。
  ///
  /// 先手的第一步在最前，最近一步在最后。
  [[nodiscard]] const std::vector<Move>& GetHistory() const;

  /// 尝试执行一次落子。
  ///
  /// 落子合法时，把落子玩家的棋子写入棋盘并轮到另一名玩家。
  /// 对局已结束、落子的玩家不是当前玩家、坐标无效或目标棋盘格子已被占用时拒绝，
  /// 棋盘和轮次保持不变。
  ///
  /// @param move 待执行的落子。
  /// @returns 落子执行成功返回 kPlaced，被拒绝返回 kRejected。
  [[nodiscard]] PlaceResult TryPlace(const Move& move);

 private:
  /// 检查棋盘上是否已形成三连获胜线。
  ///
  /// @param board 被检查的棋盘。
  /// @param state 要比对的棋盘格子状态。
  /// @returns 任一行、任一列或任一条对角线上的三个棋盘格子都是 state。
  [[nodiscard]] static bool HasPlayerLine(const Board& board, CellState state);

  /// 判定落子后的对局结果。
  ///
  /// 刚落子的玩家获胜则判胜，否则棋盘下满判平局，都未发生则对局继续。
  ///
  /// @param board 落子后的棋盘。
  /// @param player 刚落子的对局玩家。
  [[nodiscard]] static GameResult ResultAfterMove(const Board& board, Player player);

  Board board_;                                  // 对局的棋盘。
  Player current_player_ = Player::kCross;       // 当前轮到的对局玩家，X 先手。
  GameResult result_ = GameResult::kInProgress;  // 当前对局结果。
  std::vector<Move> history_;                    // 本局落子历史。
};

}  // namespace tictactoe
