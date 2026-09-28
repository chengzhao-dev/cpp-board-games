//===----------------------------------------------------------------------===//
// value_types.h - 棋盘状态的值类型定义
//
// 集中声明位置、玩家、棋子、动作与结果的值类型，规则核心与调用方共用。
//===----------------------------------------------------------------------===//

#pragma once

namespace tic_tac_toe {

// 棋盘尺寸：行数与列数，都是 3。
inline constexpr int kRows = 3;
inline constexpr int kCols = 3;

// 对局的两名玩家。
enum class Player {
  kX,
  kO,
};

// 格子内容；kEmpty 表示空格。
enum class Mark {
  kEmpty,
  kX,
  kO,
};

// 终局结果；规则补全前固定返回 kInProgress。
enum class GameStatus {
  kInProgress,
  kDraw,
  kXWins,
  kOWins,
};

// 落子动作的处理结果；当前只区分接受与拒绝。
enum class ApplyResult {
  kAccepted,
  kRejected,
};

// 棋盘位置，行与列都从 0 开始，取值 0 到 2。
struct Position {
  int row;
  int col;
};

// 一次落子动作：把玩家的棋子放到指定位置。
struct Move {
  Position position;
  Player player;
};

// 判断位置是否落在 3×3 棋盘内。
constexpr bool IsValid(Position position) {
  return position.row >= 0 && position.row < kRows &&
         position.col >= 0 && position.col < kCols;
}

// 把玩家映射为它落下的棋子。
constexpr Mark MarkOf(Player player) {
  return player == Player::kX ? Mark::kX : Mark::kO;
}

}  // namespace tic_tac_toe
