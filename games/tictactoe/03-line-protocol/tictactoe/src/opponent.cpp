//===----------------------------------------------------------------------===//
// opponent.cpp - 随机、启发式与极小极大。
//
// 三种强度都只产生当前玩家的一次合法落子，不读取输入也不打印。
//===----------------------------------------------------------------------===//

#include "opponent.h"

#include <algorithm>
#include <array>
#include <cstddef>
#include <random>
#include <vector>

#include "board.h"
#include "game.h"

namespace tictactoe {
namespace {

constexpr CellPosition At(int row, int col) {
  return {.row = row, .col = col};
}

// 收集还没有棋子的棋盘格子。
std::vector<CellPosition> EmptyCells(const Game& game) {
  std::vector<CellPosition> cells;
  for (int row = 0; row < kRows; ++row) {
    for (int col = 0; col < kCols; ++col) {
      const CellPosition position = At(row, col);
      if (game.GetCellState(position) == CellState::kEmpty) {
        cells.push_back(position);
      }
    }
  }
  return cells;
}

// 假设把这枚棋子放进这个格子，看是否能凑成三连。
bool CompletesLine(const Game& game, CellPosition cell, CellState state) {
  const auto filled = [&](int row, int col) {
    if (row == cell.row && col == cell.col) {
      return true;
    }
    return game.GetCellState(At(row, col)) == state;
  };
  if (filled(cell.row, 0) && filled(cell.row, 1) && filled(cell.row, 2)) {
    return true;
  }
  if (filled(0, cell.col) && filled(1, cell.col) && filled(2, cell.col)) {
    return true;
  }
  if (cell.row == cell.col && filled(0, 0) && filled(1, 1) && filled(2, 2)) {
    return true;
  }
  return (cell.row + cell.col) == 2 && filled(0, 2) && filled(1, 1) &&
         filled(2, 0);
}

// 在空棋盘格子里等概率选一格。调用时棋盘上至少还有一格空位。
Move RandomMove(const Game& game) {
  const std::vector<CellPosition> cells = EmptyCells(game);
  std::mt19937 generator{std::random_device{}()};
  std::uniform_int_distribution<std::size_t> distribution(0, cells.size() - 1);
  return {.position = cells[distribution(generator)],
          .player = game.CurrentPlayer()};
}

// 能立刻取胜就取胜，否则挡住对方马上能赢的一步，再按中心、四角、四边。
Move HeuristicMove(const Game& game) {
  const CellState mine = CellStateFor(game.CurrentPlayer());
  const CellState theirs = game.CurrentPlayer() == Player::kCross
                               ? CellState::kNought
                               : CellState::kCross;
  const std::vector<CellPosition> cells = EmptyCells(game);
  for (const CellPosition cell : cells) {
    if (CompletesLine(game, cell, mine)) {
      return {.position = cell, .player = game.CurrentPlayer()};
    }
  }
  for (const CellPosition cell : cells) {
    if (CompletesLine(game, cell, theirs)) {
      return {.position = cell, .player = game.CurrentPlayer()};
    }
  }
  const std::array<CellPosition, 9> order = {
      At(1, 1), At(0, 0), At(0, 2), At(2, 0), At(2, 2),
      At(0, 1), At(1, 0), At(1, 2), At(2, 1),
  };
  for (const CellPosition cell : order) {
    if (game.GetCellState(cell) == CellState::kEmpty) {
      return {.position = cell, .player = game.CurrentPlayer()};
    }
  }
  return {.position = cells.front(), .player = game.CurrentPlayer()};
}

// 终局得分：X 胜为 1，平局为 0，O 胜为 -1。
int TerminalScore(GameResult status) {
  switch (status) {
    case GameResult::kCrossWin:
      return 1;
    case GameResult::kNoughtWin:
      return -1;
    case GameResult::kDraw:
    case GameResult::kInProgress:
      return 0;
  }
  return 0;
}

// X 取更大分数，O 取更小分数。alpha、beta 剪掉不可能改变选择的分支。
// NOLINTNEXTLINE(misc-no-recursion)
int Search(const Game& game, int alpha, int beta) {
  if (game.GetResult() != GameResult::kInProgress) {
    return TerminalScore(game.GetResult());
  }

  const bool maximize = game.CurrentPlayer() == Player::kCross;
  int best = maximize ? -2 : 2;
  for (const CellPosition cell : EmptyCells(game)) {
    Game next = game;
    const PlaceResult placed =
        next.Place({.position = cell, .player = game.CurrentPlayer()});
    if (placed != PlaceResult::kPlaced) {
      continue;
    }
    const int score = Search(next, alpha, beta);
    if (maximize) {
      best = std::max(score, best);
      alpha = std::max(best, alpha);
    } else {
      best = std::min(score, best);
      beta = std::min(best, beta);
    }
    if (beta <= alpha) {
      break;
    }
  }
  return best;
}

// 对每个空棋盘格子搜索一次，留下对当前玩家更好的那一格。
Move MinimaxMove(const Game& game) {
  const bool maximize = game.CurrentPlayer() == Player::kCross;
  int best = maximize ? -2 : 2;
  CellPosition chosen = EmptyCells(game).front();
  for (const CellPosition cell : EmptyCells(game)) {
    Game next = game;
    const PlaceResult placed =
        next.Place({.position = cell, .player = game.CurrentPlayer()});
    if (placed != PlaceResult::kPlaced) {
      continue;
    }
    const int score = Search(next, -2, 2);
    const bool better = maximize ? score > best : score < best;
    if (better) {
      best = score;
      chosen = cell;
    }
  }
  return {.position = chosen, .player = game.CurrentPlayer()};
}

}  // namespace

// 按强度选择对应的选法。
Move ChooseMove(const Game& game, Strength strength) {
  switch (strength) {
    case Strength::kRandom:
      return RandomMove(game);
    case Strength::kHeuristic:
      return HeuristicMove(game);
    case Strength::kMinimax:
      return MinimaxMove(game);
  }
  return MinimaxMove(game);
}

}  // namespace tictactoe
