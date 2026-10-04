//===----------------------------------------------------------------------===//
// game.cpp - 回合、落子与终局判定。
//
// 只接受当前玩家的合法落子，并在三连或下满时结束对局。
//===----------------------------------------------------------------------===//

#include "game.h"

#include <algorithm>
#include <array>
#include <cstddef>
#include <vector>

#include "board.h"

namespace tictactoe {
namespace {

// 由行、列得到棋盘格子坐标。
constexpr CellPosition At(int row, int col) {
  return {.row = row, .col = col};
}

// 三行、三列和两条对角线。
constexpr std::array<std::array<CellPosition, 3>, 8> kLines = {{
    {{At(0, 0), At(0, 1), At(0, 2)}},
    {{At(1, 0), At(1, 1), At(1, 2)}},
    {{At(2, 0), At(2, 1), At(2, 2)}},
    {{At(0, 0), At(1, 0), At(2, 0)}},
    {{At(0, 1), At(1, 1), At(2, 1)}},
    {{At(0, 2), At(1, 2), At(2, 2)}},
    {{At(0, 0), At(1, 1), At(2, 2)}},
    {{At(0, 2), At(1, 1), At(2, 0)}},
}};

// 这条线上的三个棋盘格子是否都是同一状态。
bool LineFilled(const Board& board, CellState state,
                const std::array<CellPosition, 3>& line) {
  return std::ranges::all_of(line, [&](CellPosition cell) {
    return board.GetCellState(cell) == state;
  });
}

// 刚落子的玩家是否三连；否则在下满时平局。
GameResult ResultAfterMove(const Board& board, Player player) {
  const CellState state = CellStateFor(player);
  for (const std::array<CellPosition, 3>& line : kLines) {
    if (LineFilled(board, state, line)) {
      return player == Player::kCross ? GameResult::kCrossWin
                                      : GameResult::kNoughtWin;
    }
  }
  if (board.IsFull()) {
    return GameResult::kDraw;
  }
  return GameResult::kInProgress;
}

}  // namespace

Player Game::CurrentPlayer() const {
  return current_player_;
}

GameResult Game::GetResult() const {
  return result_;
}

CellState Game::GetCellState(CellPosition position) const {
  return board_.GetCellState(position);
}

// 接受一次落子：先校验轮次与棋盘，接受后判定终局并记录，未结束才轮换。
PlaceResult Game::Place(const Move& move) {
  if (result_ != GameResult::kInProgress || move.player != current_player_) {
    return PlaceResult::kRejected;  // 对局已结束或还没轮到该玩家。
  }

  if (!board_.PlacePiece(move.position, CellStateFor(move.player))) {
    return PlaceResult::kRejected;  // 棋盘拒绝落子，局面保持不变。
  }

  result_ = ResultAfterMove(board_, move.player);  // 接受后立即判定终局。
  history_.push_back(move);
  if (result_ == GameResult::kInProgress) {
    current_player_ =
        current_player_ == Player::kCross ? Player::kNought : Player::kCross;
  }
  return PlaceResult::kPlaced;
}

const std::vector<Move>& Game::History() const {
  return history_;
}

}  // namespace tictactoe
