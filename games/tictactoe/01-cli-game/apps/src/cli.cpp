//===----------------------------------------------------------------------===//
// cli.cpp - 终端对局的打印与读入。
//
// 按行列号打印棋盘，读入两个整数并落子，直到终局。
//===----------------------------------------------------------------------===//

#include "cli.h"

#include <cstddef>
#include <cstdint>
#include <ios>
#include <istream>
#include <limits>
#include <ostream>
#include <string>

#include "board.h"
#include "game.h"

namespace tictactoe {
namespace {

constexpr const char* kProgramName = "app";

// 把诊断写到调用方给出的错误流。格式为「程序名: 描述」。
void Report(std::ostream& err, const std::string& message) {
  err << kProgramName << ": " << message << '\n';
}

// 把棋盘格子状态转成单个显示字符：空棋盘格子显示为空位。
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

// 列号对准格子中心，行号写在左边框左侧。
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

// 把终局结果转成中文状态行。
std::string StatusToString(GameResult status) {
  switch (status) {
    case GameResult::kInProgress:
      return "进行中";
    case GameResult::kDraw:
      return "平局";
    case GameResult::kCrossWin:
      return "X 获胜";
    case GameResult::kNoughtWin:
      return "O 获胜";
  }
  return "进行中";
}

// 一次读取的结果：得到两个整数、需要重试，或输入已经结束。
enum class ReadResult : std::uint8_t {
  kOk = 0,     // 读到两个整数。
  kRetry = 1,  // 本行不是两个整数，已丢掉，需要重试。
  kEof = 2,    // 输入结束。
};

// 从输入读两个整数。非数字时清掉错误并丢掉本行，说明写到 err。
ReadResult ReadRowAndCol(std::istream& in, std::ostream& err, int& row,
                         int& col) {
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

// 拒绝时说明原因。棋盘在 Place 失败后保持原样。
void ReportRejected(std::ostream& err, const Game& game,
                    CellPosition position) {
  if (!Board::IsValidPosition(position)) {
    Report(err, "坐标超出棋盘");
    return;
  }
  if (game.GetCellState(position) != CellState::kEmpty) {
    Report(err, "该棋盘格子已占用");
    return;
  }
  Report(err, "现在不能落子");
}

}  // namespace

void PrintGame(std::ostream& out, const Game& game) {
  out << BoardToString(game) << "状态：" << StatusToString(game.GetResult())
      << '\n';
}

int PlayToEnd(std::istream& in, std::ostream& out, std::ostream& err) {
  Game game;
  while (game.GetResult() == GameResult::kInProgress) {
    PrintGame(out, game);
    const char mark = game.CurrentPlayer() == Player::kCross ? 'X' : 'O';
    out << "轮到 " << mark << "。请输入行和列（0 到 2）：";
    int row = 0;
    int col = 0;
    const ReadResult read = ReadRowAndCol(in, err, row, col);
    if (read == ReadResult::kEof) {
      Report(err, "输入结束");
      return 1;
    }
    if (read == ReadResult::kRetry) {
      continue;
    }
    const CellPosition position{.row = row, .col = col};
    const PlaceResult result =
        game.Place({.position = position, .player = game.CurrentPlayer()});
    if (result == PlaceResult::kRejected) {
      ReportRejected(err, game, position);
    }
  }
  PrintGame(out, game);
  return 0;
}

}  // namespace tictactoe
