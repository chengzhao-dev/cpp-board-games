//===------------------------------------------------------------------------------------------===//
// game.cpp - 回合、落子与终局判定。
//
// 只允许当前玩家落合法棋子，并在棋盘出现获胜线或下满时结束对局。
//===------------------------------------------------------------------------------------------===//

#include "game.h"

#include <algorithm>
#include <array>
#include <vector>

#include "board.h"

namespace tictactoe {

Player Game::GetCurrentPlayer() const {
  return current_player_;
}

GameResult Game::GetResult() const {
  return result_;
}

CellState Game::GetCellState(CellPosition position) const {
  return board_.GetCellState(position);
}

const std::vector<Move>& Game::GetHistory() const {
  return history_;
}

PlaceResult Game::TryPlace(const Move& move) {
  if (result_ != GameResult::kInProgress || move.player != current_player_) {
    return PlaceResult::kRejected;  // 对局已结束，或落子的玩家不是当前玩家。
  }

  const CellState state = PlayerToCellState(move.player);
  if (!board_.PlacePiece(move.position, state)) {
    return PlaceResult::kRejected;  // 棋盘拒绝落子，局面保持不变。
  }

  result_ = ResultAfterMove(board_, move.player);  // 落子写入后立即判定终局。
  history_.push_back(move);                        // 成功写入才记录落子历史。
  if (result_ == GameResult::kInProgress) {
    // 对局未结束才把轮次交给另一名玩家。
    current_player_ = current_player_ == Player::kCross ? Player::kNought : Player::kCross;
  }
  return PlaceResult::kPlaced;
}

bool Game::HasPlayerLine(const Board& board, CellState state) {
  const auto has_state = [&](CellPosition position) {
    return board.GetCellState(position) == state;
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

GameResult Game::ResultAfterMove(const Board& board, Player player) {
  if (HasPlayerLine(board, PlayerToCellState(player))) {
    // 刚落子的玩家已连成线，先判胜负。
    return player == Player::kCross ? GameResult::kCrossWin : GameResult::kNoughtWin;
  }
  if (board.IsFull()) {
    return GameResult::kDraw;  // 未分胜负且棋盘已满，判平局。
  }
  return GameResult::kInProgress;  // 仍可继续落子。
}

}  // namespace tictactoe
