//===------------------------------------------------------------------------------------------===//
// cli.cpp - 终端对局的打印与读入。
//
// 按行列号打印棋盘，读入两个整数并落子，直到终局。
//===------------------------------------------------------------------------------------------===//

#include "cli.h"

#include <cstdint>
#include <ios>
#include <istream>
#include <limits>
#include <ostream>
#include <string>
#include <string_view>

#include "board.h"
#include "game.h"
#include "opponent.h"

namespace tictactoe {

char CellSymbol(CellState state) {
  switch (state) {
    case CellState::kEmpty:
      return ' ';
    case CellState::kCross:
      return 'X';
    case CellState::kNought:
      return 'O';
  }
  return ' ';
}

std::string BoardToString(const Game& game) {
  std::string board = "    0   1   2\n";
  const std::string rule = "  +---+---+---+\n";
  board += rule;
  for (int row = 0; row < kRows; ++row) {
    board += std::to_string(row);
    board += " |";
    for (int col = 0; col < kCols; ++col) {
      board += ' ';
      board += CellSymbol(game.GetCellState({.row = row, .col = col}));
      board += " |";
    }
    board += '\n';
    board += rule;
  }
  return board;
}

std::string GameResultToString(GameResult result) {
  switch (result) {
    case GameResult::kInProgress:
      return "游戏进行中";
    case GameResult::kDraw:
      return "平局";
    case GameResult::kCrossWin:
      return "X 获胜";
    case GameResult::kNoughtWin:
      return "O 获胜";
  }
  return "游戏进行中";
}

void PrintGame(std::ostream& out, const Game& game) {
  out << BoardToString(game) << "对局结果：" << GameResultToString(game.GetResult()) << '\n';
  WriteSnapshot(out, game);
}

void WriteSnapshot(std::ostream& out, const Game& game) {
  out << R"({"version":1,"sequence":)" << game.GetHistory().size() << R"(,"cells":[)";
  for (int row = 0; row < kRows; ++row) {
    for (int col = 0; col < kCols; ++col) {
      if (row != 0 || col != 0) {
        out << ',';
      }
      const char symbol = CellSymbol(game.GetCellState({.row = row, .col = col}));
      out << '"' << symbol << '"';
    }
  }
  const char player = game.GetCurrentPlayer() == Player::kCross ? 'X' : 'O';
  std::string_view status = "in_progress";
  switch (game.GetResult()) {
    case GameResult::kCrossWin:
      status = "x_wins";
      break;
    case GameResult::kNoughtWin:
      status = "o_wins";
      break;
    case GameResult::kDraw:
      status = "draw";
      break;
    case GameResult::kInProgress:
      status = "in_progress";
      break;
  }
  std::string_view winner;
  if (game.GetResult() == GameResult::kCrossWin) {
    winner = "X";
  } else if (game.GetResult() == GameResult::kNoughtWin) {
    winner = "O";
  }
  out << R"(],"player":")" << player << R"(","status":")" << status << R"(","winner":")" << winner
      << R"("})" << '\n';
}

void Report(std::ostream& err, const std::string& message) {
  err << kProgramName << ": " << message << '\n';
}

ReadResult ReadRowAndCol(std::istream& in, std::ostream& err, int& row, int& col) {
  std::int64_t input_row = 0;
  std::int64_t input_col = 0;
  if (in >> input_row >> input_col) {
    if (input_row >= std::numeric_limits<int>::min() &&
        input_row <= std::numeric_limits<int>::max() &&
        input_col >= std::numeric_limits<int>::min() &&
        input_col <= std::numeric_limits<int>::max()) {
      row = static_cast<int>(input_row);
      col = static_cast<int>(input_col);
      return ReadResult::kOk;
    }
    in.clear();
    in.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
    Report(err, "坐标超出可用范围");
    return ReadResult::kRetry;
  }
  if (in.eof()) {
    return ReadResult::kEof;
  }
  in.clear();
  in.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
  Report(err, "请输入两个整数");
  return ReadResult::kRetry;
}

void ReportRejected(std::ostream& err, const Game& game, CellPosition position) {
  if (!Board::IsValidPosition(position)) {
    Report(err, "坐标超出棋盘");
    return;
  }
  if (game.GetCellState(position) != CellState::kEmpty) {
    Report(err, "棋盘格子已被占用");
    return;
  }
  Report(err, "现在不能落子");
}

// 这一整行要留到比较结束，所以放进 std::string，不借用输入缓冲。
bool ReadOwnedLine(std::istream& in, std::string& line) {
  if (!std::getline(in, line)) {
    return false;
  }
  if (!line.empty() && line.back() == '\r') {
    line.pop_back();
  }
  return true;
}

bool ReadMatchKind(std::istream& in, std::ostream& out, std::ostream& err, bool& against_cpu) {
  while (true) {
    out << "请选择对局（1 双人，2 人机）：" << std::flush;
    std::string line;
    if (!ReadOwnedLine(in, line)) {
      Report(err, "输入结束");
      return false;
    }
    if (line == "1") {
      against_cpu = false;
      return true;
    }
    if (line == "2") {
      against_cpu = true;
      return true;
    }
    Report(err, "请输入 1 或 2");
  }
}

bool ReadStrength(std::istream& in, std::ostream& out, std::ostream& err, Strength& strength) {
  while (true) {
    out << "请选择难度（1 随机，2 启发式，3 极小极大）：" << std::flush;
    std::string line;
    if (!ReadOwnedLine(in, line)) {
      Report(err, "输入结束");
      return false;
    }
    if (line == "1") {
      strength = Strength::kRandom;
      return true;
    }
    if (line == "2") {
      strength = Strength::kHeuristic;
      return true;
    }
    if (line == "3") {
      strength = Strength::kMinimax;
      return true;
    }
    Report(err, "请输入 1、2 或 3");
  }
}

HumanMove ReadHumanMove(std::istream& in, std::ostream& err, Game& game) {
  int row = 0;
  int col = 0;
  const ReadResult read = ReadRowAndCol(in, err, row, col);
  if (read == ReadResult::kEof) {
    return HumanMove::kInputEnd;
  }
  if (read == ReadResult::kRetry) {
    return HumanMove::kRetry;
  }
  const CellPosition position{.row = row, .col = col};
  const PlaceResult result =
      game.TryPlace({.position = position, .player = game.GetCurrentPlayer()});
  if (result == PlaceResult::kRejected) {
    ReportRejected(err, game, position);
  }
  return HumanMove::kPlaced;
}

int PlayToEnd(std::istream& in, std::ostream& out, std::ostream& err) {
  Game game;
  while (game.GetResult() == GameResult::kInProgress) {
    PrintGame(out, game);
    const char mark = game.GetCurrentPlayer() == Player::kCross ? 'X' : 'O';
    out << "轮到 " << mark << "。请输入行和列（0 到 2）：" << std::flush;
    const HumanMove move = ReadHumanMove(in, err, game);
    if (move == HumanMove::kInputEnd) {
      Report(err, "输入结束");
      return 1;
    }
  }
  PrintGame(out, game);
  return 0;
}

int PlayToEnd(std::istream& in, std::ostream& out, std::ostream& err, Strength opponent) {
  Game game;
  while (game.GetResult() == GameResult::kInProgress) {
    PrintGame(out, game);
    if (game.GetCurrentPlayer() == Player::kNought) {
      const PlaceResult placed = game.TryPlace(ChooseMove(game, opponent));
      if (placed == PlaceResult::kRejected) {
        Report(err, "现在不能落子");
        return 1;
      }
      continue;
    }
    const char mark = 'X';
    out << "轮到 " << mark << "。请输入行和列（0 到 2）：" << std::flush;
    if (ReadHumanMove(in, err, game) == HumanMove::kInputEnd) {
      Report(err, "输入结束");
      return 1;
    }
  }
  PrintGame(out, game);
  return 0;
}

int RunMatch(std::istream& in, std::ostream& out, std::ostream& err) {
  bool against_cpu = false;
  if (!ReadMatchKind(in, out, err, against_cpu)) {
    return 1;
  }
  if (!against_cpu) {
    return PlayToEnd(in, out, err);
  }
  Strength strength = Strength::kMinimax;
  if (!ReadStrength(in, out, err, strength)) {
    return 1;
  }
  return PlayToEnd(in, out, err, strength);
}

}  // namespace tictactoe
