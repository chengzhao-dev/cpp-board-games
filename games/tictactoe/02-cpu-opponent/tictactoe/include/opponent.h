//===------------------------------------------------------------------------------------------===//
// opponent.h - 电脑对手的落子选择。
//
// 只读当前对局并返回一次 Move。落子仍由调用方交给 Game::TryPlace。
//===------------------------------------------------------------------------------------------===//

#pragma once

#include <cstdint>
#include <vector>

#include "game.h"

namespace tictactoe {

/// 三种电脑对手的强度。
///
/// 随机只保证落在空棋盘格子上；启发式能赢就赢，否则挡住对方马上能赢的一步；
/// 极小极大按终局结果选择对当前玩家最有利的一步。
enum class Strength : std::uint8_t {
  kRandom = 0,
  kHeuristic = 1,
  kMinimax = 2,
};

/// 收集还没有棋子的棋盘格子。
///
/// @param game 只读的当前对局。
/// @returns 空棋盘格子坐标的列表，按行序排列。
[[nodiscard]] std::vector<CellPosition> EmptyCells(const Game& game);

/// 检查把这枚棋子放进这个棋盘格子后，是否能凑成三连。
///
/// @param game 只读的当前对局。
/// @param position 假设放入棋子的棋盘格子。
/// @param state 假设放入的棋盘格子状态。
/// @returns 放子后能凑成三连。
[[nodiscard]] bool CompletesLine(const Game& game, CellPosition position, CellState state);

/// 在空棋盘格子里等概率选一格。
///
/// 对局必须仍在进行，棋盘上至少还有一格空位。
///
/// @param game 只读的当前对局。
/// @returns 选出的一步落子。
Move RandomMove(const Game& game);

/// 能立刻取胜就取胜，否则挡住对方马上能赢的一步，再按中心、四角、四边选格。
///
/// 对局必须仍在进行。
///
/// @param game 只读的当前对局。
/// @returns 选出的一步落子。
Move HeuristicMove(const Game& game);

/// 由对局结果得到极小极大的得分：X 胜为 1，平局为 0，O 胜为 -1。
///
/// @param result 对局结果。
/// @returns 该结果对应的得分。
[[nodiscard]] int TerminalScore(GameResult result);

/// 极小极大搜索：X 取更大分数，O 取更小分数，alpha、beta
/// 剪掉不可能改变选择的分支。
///
/// @param game 只读的当前对局。
/// @param alpha 当前已知最好分数的下界。
/// @param beta 当前已知最好分数的上界。
/// @returns 双方都按最优应对时当前玩家能取得的得分。
[[nodiscard]] int Search(const Game& game, int alpha, int beta);

/// 对每个空棋盘格子搜索一次，留下对当前玩家更好的那一格。
///
/// 对局必须仍在进行。
///
/// @param game 只读的当前对局。
/// @returns 选出的一步落子。
Move MinimaxMove(const Game& game);

/// 为当前玩家选择一步落子。
///
/// 对局必须仍在进行。返回的坐标指向空棋盘格子，玩家是当前玩家。
///
/// @param game 只读的当前对局。
/// @param strength 电脑对手的强度。
/// @returns 选出的一步落子。
[[nodiscard]] Move ChooseMove(const Game& game, Strength strength);

}  // namespace tictactoe
