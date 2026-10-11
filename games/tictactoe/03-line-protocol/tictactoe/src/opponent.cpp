//===------------------------------------------------------------------------------------------===//
// opponent.cpp - 随机、启发式与极小极大。
//
// 三种强度都只产生当前玩家的一次合法落子，不读取输入也不打印。
//===------------------------------------------------------------------------------------------===//

#include "opponent.h"

#include <algorithm>
#include <array>
#include <cassert>
#include <cstddef>
#include <random>
#include <vector>

#include "board.h"
#include "game.h"

namespace tictactoe {

std::vector<CellPosition> EmptyCells(const Game& game) {
  std::vector<CellPosition> cells;
  for (int row = 0; row < kRows; ++row) {
    for (int col = 0; col < kCols; ++col) {
      const CellPosition position = {.row = row, .col = col};
      if (game.GetCellState(position) == CellState::kEmpty) {
        cells.push_back(position);
      }
    }
  }
  return cells;
}

bool CompletesLine(const Game& game, CellPosition position, CellState state) {
  const auto has_state = [&](CellPosition probed) {
    if (probed.row == position.row && probed.col == position.col) {
      return true;  // 假设这一格已经放进 state。
    }
    return game.GetCellState(probed) == state;
  };
  const auto has_line = [&](CellPosition a, CellPosition b, CellPosition c) {
    const std::array<CellPosition, 3> line{a, b, c};
    return std::ranges::all_of(line, has_state);
  };

  for (int row = 0; row < kRows; ++row) {
    if (has_line({.row = row, .col = 0}, {.row = row, .col = 1}, {.row = row, .col = 2})) {
      return true;
    }
  }
  for (int col = 0; col < kCols; ++col) {
    if (has_line({.row = 0, .col = col}, {.row = 1, .col = col}, {.row = 2, .col = col})) {
      return true;
    }
  }

  return has_line({.row = 0, .col = 0}, {.row = 1, .col = 1}, {.row = 2, .col = 2}) ||
         has_line({.row = 0, .col = 2}, {.row = 1, .col = 1}, {.row = 2, .col = 0});
}

Move RandomMove(const Game& game) {
  assert(game.GetResult() == GameResult::kInProgress);
  const std::vector<CellPosition> cells = EmptyCells(game);
  static thread_local std::mt19937 generator{std::random_device{}()};
  std::uniform_int_distribution<std::size_t> distribution(0, cells.size() - 1);
  return {.position = cells[distribution(generator)], .player = game.GetCurrentPlayer()};
}

Move HeuristicMove(const Game& game) {
  assert(game.GetResult() == GameResult::kInProgress);
  const Player current = game.GetCurrentPlayer();
  const CellState mine = PlayerToCellState(current);
  const CellState theirs = current == Player::kCross ? CellState::kNought : CellState::kCross;
  const std::vector<CellPosition> cells = EmptyCells(game);
  for (const CellPosition position : cells) {
    if (CompletesLine(game, position, mine)) {
      return {.position = position, .player = game.GetCurrentPlayer()};
    }
  }
  for (const CellPosition position : cells) {
    if (CompletesLine(game, position, theirs)) {
      return {.position = position, .player = game.GetCurrentPlayer()};
    }
  }
  const std::array<CellPosition, 9> order = {{
      {.row = 1, .col = 1},
      {.row = 0, .col = 0},
      {.row = 0, .col = 2},
      {.row = 2, .col = 0},
      {.row = 2, .col = 2},
      {.row = 0, .col = 1},
      {.row = 1, .col = 0},
      {.row = 1, .col = 2},
      {.row = 2, .col = 1},
  }};
  for (const CellPosition position : order) {
    if (game.GetCellState(position) == CellState::kEmpty) {
      return {.position = position, .player = game.GetCurrentPlayer()};
    }
  }
  return {.position = cells.front(), .player = game.GetCurrentPlayer()};
}

int TerminalScore(GameResult result) {
  switch (result) {
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

// NOLINTNEXTLINE(misc-no-recursion)
int Search(const Game& game, int alpha, int beta) {
  if (game.GetResult() != GameResult::kInProgress) {
    return TerminalScore(game.GetResult());
  }

  const Player current = game.GetCurrentPlayer();
  const CellState mine = PlayerToCellState(current);
  const CellState theirs = current == Player::kCross ? CellState::kNought : CellState::kCross;
  const std::vector<CellPosition> cells = EmptyCells(game);

  // 着法序：先试马上能赢的一步，再试必须挡住对方的一步，其余按行序。
  // 把好棋排在前面，让下面的 beta <= alpha 剪枝更早发生。
  std::vector<CellPosition> winning;
  std::vector<CellPosition> blocking;
  std::vector<CellPosition> rest;
  for (const CellPosition position : cells) {
    if (CompletesLine(game, position, mine)) {
      winning.push_back(position);
    } else if (CompletesLine(game, position, theirs)) {
      blocking.push_back(position);
    } else {
      rest.push_back(position);
    }
  }
  std::vector<CellPosition> ordered;
  ordered.reserve(cells.size());
  ordered.insert(ordered.end(), winning.begin(), winning.end());
  ordered.insert(ordered.end(), blocking.begin(), blocking.end());
  ordered.insert(ordered.end(), rest.begin(), rest.end());

  const bool maximize = current == Player::kCross;
  int best = maximize ? -2 : 2;
  for (const CellPosition position : ordered) {
    Game next = game;
    const PlaceResult placed = next.TryPlace({.position = position, .player = current});
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
      break;  // 剪枝：这一支后续再搜也不会改变上层的选择。
    }
  }
  return best;
}

Move MinimaxMove(const Game& game) {
  assert(game.GetResult() == GameResult::kInProgress);
  const bool maximize = game.GetCurrentPlayer() == Player::kCross;
  int best = maximize ? -2 : 2;
  CellPosition chosen = EmptyCells(game).front();
  for (const CellPosition position : EmptyCells(game)) {
    Game next = game;
    const PlaceResult placed =
        next.TryPlace({.position = position, .player = game.GetCurrentPlayer()});
    if (placed != PlaceResult::kPlaced) {
      continue;
    }
    const int score = Search(next, -2, 2);
    const bool better = maximize ? score > best : score < best;
    if (better) {
      best = score;
      chosen = position;  // 严格更优才换格，同分保留先出现的格子。
    }
  }
  return {.position = chosen, .player = game.GetCurrentPlayer()};
}

Move ChooseMove(const Game& game, Strength strength) {
  // 入口先挡不满足前置条件的调用：对局已结束时棋盘已满，选格会越界。
  assert(game.GetResult() == GameResult::kInProgress);
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
