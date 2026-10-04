//===----------------------------------------------------------------------===//
// opponent.h - 电脑对手的落子选择。
//
// 只读当前对局并返回一次 Move。落子仍由调用方交给 Game::Place。
//===----------------------------------------------------------------------===//

#pragma once

#include <cstdint>

#include "game.h"

namespace tictactoe {

/// 三种电脑对手的强度。
///
/// 随机只保证落在空格子上；启发式能赢就赢，否则挡住对方马上能赢的一步；
/// 极小极大按终局结果选择对当前玩家最有利的一步。
enum class Strength : std::uint8_t {
  kRandom = 0,
  kHeuristic = 1,
  kMinimax = 2,
};

/// 为当前玩家选择一步落子。
///
/// 对局必须仍在进行。返回的坐标是空棋盘格子，玩家是当前玩家。
[[nodiscard]] Move ChooseMove(const Game& game, Strength strength);

}  // namespace tictactoe
