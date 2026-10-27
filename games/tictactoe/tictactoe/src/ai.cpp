/// @file ai.cpp
/// @brief 随机、启发式与极小极大三种选子实现。
///
/// 三种强度都只产生当前玩家的一次合法落子，不读取输入也不打印；
/// 随机源是线程局部变量，不同线程的对局不会争用同一台引擎。

#include "ai.h"

#include <algorithm>
#include <array>
#include <cstddef>
#include <memory>
#include <random>
#include <stdexcept>
#include <vector>

#include "board.h"
#include "game.h"

namespace tictactoe {

std::vector<CellPosition> CollectEmptyCells(const Game& game) {
  std::vector<CellPosition> cells;
  /// 返回顺序按行序；同一局面的候选格顺序一致，启发式与极小极大的平手规则才可复现。
  for (int row = 0; row < kBoardRows; ++row) {
    for (int col = 0; col < kBoardCols; ++col) {
      const CellPosition position = {.row = row, .col = col};
      if (game.GetCellType(position) == CellType::kEmpty) {
        cells.push_back(position);
      }
    }
  }
  return cells;
}

namespace {

/// 三种强度都要从非空候选里取一格；空列表说明对局状态与“进行中”不一致。
std::vector<CellPosition> EmptyCellsOrThrow(const Game& game) {
  std::vector<CellPosition> cells = CollectEmptyCells(game);
  if (cells.empty()) {
    throw std::logic_error{"EmptyCellsOrThrow: no empty cell left to place"};
  }
  return cells;
}

}  // namespace

std::unique_ptr<Ai> MakeAi(AiStrength strength) {
  switch (strength) {
    case AiStrength::kRandom:
      return std::make_unique<RandomAi>();
    case AiStrength::kHeuristic:
      return std::make_unique<HeuristicAi>();
    case AiStrength::kMinimax:
      return std::make_unique<MinimaxAi>();
  }
  /// 枚举已覆盖全部取值；这一行让编译器看到所有路径都有返回值。
  return std::make_unique<MinimaxAi>();
}

Ai::~Ai() = default;

Move RandomAi::Choose(const Game& game) const {
  if (game.GetResult() != GameResult::kInProgress) {
    throw std::logic_error{"Ai::Choose: game is already over"};
  }
  const std::vector<CellPosition> cells = EmptyCellsOrThrow(game);
  /// thread_local：每个线程各自推进随机序列。
  static thread_local std::mt19937 generator{std::random_device{}()};
  std::uniform_int_distribution<std::size_t> distribution(0, cells.size() - 1);
  return {.position = cells[distribution(generator)], .player = game.GetCurrentPlayer()};
}

Move HeuristicAi::Choose(const Game& game) const {
  if (game.GetResult() != GameResult::kInProgress) {
    throw std::logic_error{"Ai::Choose: game is already over"};
  }
  const Player current = game.GetCurrentPlayer();
  const CellType mine = PlayerToCellType(current);
  const CellType theirs = PlayerToCellType(PlayerToOpponent(current));
  const std::vector<CellPosition> cells = EmptyCellsOrThrow(game);
  /// 先找自己的胜手：错过必胜会让对方多走一步，后面的“挡”再准也没用。
  for (const CellPosition position : cells) {
    if (game.IsLineComplete(position, mine)) {
      return {.position = position, .player = game.GetCurrentPlayer()};
    }
  }
  /// 再看对手的胜手：自己不赢时必须挡，否则下一回合就输。
  for (const CellPosition position : cells) {
    if (game.IsLineComplete(position, theirs)) {
      return {.position = position, .player = game.GetCurrentPlayer()};
    }
  }
  /// 选格顺序：中心、四角、四边；空白格按这个次序取第一格。
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
    if (game.GetCellType(position) == CellType::kEmpty) {
      return {.position = position, .player = game.GetCurrentPlayer()};
    }
  }
  /// 九格全被占满时对局已经结束，上面的检查会先拦下；这里只保留一条不会取空的返回路径。
  return {.position = cells.front(), .player = game.GetCurrentPlayer()};
}

Move MinimaxAi::Choose(const Game& game) const {
  if (game.GetResult() != GameResult::kInProgress) {
    throw std::logic_error{"Ai::Choose: game is already over"};
  }
  /// X 是最大化方，O 是最小化方；分数只从 X 的视角定义（见 ScoreTerminal）。
  const bool maximize = game.GetCurrentPlayer() == Player::kCross;
  int best = maximize ? -2 : 2;
  const std::vector<CellPosition> cells = EmptyCellsOrThrow(game);
  CellPosition chosen = cells.front();
  for (const CellPosition position : cells) {
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

int MinimaxAi::ScoreTerminal(GameResult result) {
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
int MinimaxAi::Search(const Game& game, int alpha, int beta) {
  /// 终局直接返回分数：搜索到叶子才算完成，不在中途估算局面。
  if (game.GetResult() != GameResult::kInProgress) {
    return ScoreTerminal(game.GetResult());
  }

  const Player current = game.GetCurrentPlayer();
  const CellType mine = PlayerToCellType(current);
  const CellType theirs = PlayerToCellType(PlayerToOpponent(current));
  const std::vector<CellPosition> cells = CollectEmptyCells(game);

  /// 着法序：先试马上能赢的一步，再试必须挡住对方的一步，其余按行序。
  /// 把好棋排在前面，让 beta <= alpha 剪枝更早发生。
  std::vector<CellPosition> winning;
  std::vector<CellPosition> blocking;
  std::vector<CellPosition> rest;
  for (const CellPosition position : cells) {
    if (game.IsLineComplete(position, mine)) {
      winning.push_back(position);
    } else if (game.IsLineComplete(position, theirs)) {
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
      break;  // 剪枝：这一支后续再搜也不会改变上层选择。
    }
  }
  return best;
}

}  // namespace tictactoe
