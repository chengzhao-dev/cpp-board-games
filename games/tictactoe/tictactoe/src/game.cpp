//===------------------------------------------------------------------------------------------===//
// game.cpp - 回合推进、落子校验与终局判定。
//
// 一次合法落子依次改写棋盘、结果、历史和轮次；被拒的落子不留下任何痕迹。
//===------------------------------------------------------------------------------------------===//

#include "game.h"

#include <cstddef>
#include <vector>

#include "board.h"

namespace tictactoe {

Player Game::GetCurrentPlayer() const noexcept {
  return current_player_;
}

GameResult Game::GetResult() const noexcept {
  return result_;
}

CellType Game::GetCellType(CellPosition position) const {
  return board_.GetCellType(position);
}

bool Game::IsLineComplete(CellPosition position, CellType cell_type) const {
  return board_.IsLineComplete(position, cell_type);
}

const std::vector<Move>& Game::GetHistory() const noexcept {
  return history_;
}

PlaceResult Game::TryPlace(const Move& move) {
  // 先看对局状态和轮次，再碰棋盘：被拒的落子不应改写任何成员。
  if (result_ != GameResult::kInProgress || move.player != current_player_) {
    return PlaceResult::kRejected;
  }

  const CellType cell_type = PlayerToCellType(move.player);
  // 历史最多九手；在改棋盘前一次留够容量，push_back 不会在棋盘已改后分配失败。
  history_.reserve(static_cast<std::size_t>(kBoardRows) * static_cast<std::size_t>(kBoardCols));
  if (!board_.PlaceCell(move.position, cell_type)) {
    return PlaceResult::kRejected;
  }

  // 棋盘已经写好，后面三步按依赖顺序更新：先判结果，再记历史，最后换手。
  result_ = JudgeAfterPlace(board_, move.player);
  history_.push_back(move);
  if (result_ == GameResult::kInProgress) {
    // 终局后不换手：current_player_ 停在落最后一子的人，界面靠它显示胜负归属。
    current_player_ = PlayerToOpponent(current_player_);
  }
  return PlaceResult::kPlaced;
}

GameResult Game::JudgeAfterPlace(const Board& board, Player player) {
  // 次序不能反：先判胜再判满，否则最后一子同时成线和填满棋盘时会被误判成平局。
  const auto winner = board.GetWinner();
  if (winner.has_value() && *winner == PlayerToCellType(player)) {
    return PlayerToWinResult(player);
  }
  if (board.IsFull()) {
    return GameResult::kDraw;
  }
  return GameResult::kInProgress;
}

}  // namespace tictactoe
