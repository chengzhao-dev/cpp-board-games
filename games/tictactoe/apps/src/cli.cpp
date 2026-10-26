//===------------------------------------------------------------------------------------------===//
// cli.cpp - 终端程序的打印与读入。
//
// 按行列号打印棋盘，读入两个整数并落子，直到终局。
//===------------------------------------------------------------------------------------------===//

#include "cli.h"

#include <cstdint>
#include <expected>
#include <ios>
#include <istream>
#include <limits>
#include <memory>
#include <ostream>
#include <string>
#include <string_view>

#include "ai.h"
#include "board.h"
#include "game.h"

namespace tictactoe {

char CellSymbol(CellType cell_type) {
  switch (cell_type) {
    case CellType::kEmpty:
      return ' ';
    case CellType::kX:
      return 'X';
    case CellType::kO:
      return 'O';
  }
  return ' ';
}

std::string BoardToString(const Game& game) {
  // 列号写在表头、行号写在最左：玩家按“先看行号再看列号”的顺序数格子，
  // 与落子提示里的“行和列”同序，不必在脑子里交换。
  std::string board = "    0   1   2\n";
  const std::string rule = "  +---+---+---+\n";
  board += rule;
  for (int row = 0; row < kBoardRows; ++row) {
    board += std::to_string(row);
    board += " |";
    for (int col = 0; col < kBoardCols; ++col) {
      board += ' ';
      board += CellSymbol(game.GetCellType({.row = row, .col = col}));
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
  // 字段顺序与网页读取顺序一致，改动要同步书里的快照说明。
  out << R"({"version":1,"sequence":)" << game.GetHistory().size() << R"(,"cells":[)";
  for (int row = 0; row < kBoardRows; ++row) {
    for (int col = 0; col < kBoardCols; ++col) {
      if (row != 0 || col != 0) {
        out << ',';
      }
      const char symbol = CellSymbol(game.GetCellType({.row = row, .col = col}));
      out << '"' << symbol << '"';
    }
  }
  const char player = game.GetCurrentPlayer() == Player::kCross ? 'X' : 'O';
  const GameResult result = game.GetResult();
  std::string_view status = "in_progress";
  std::string_view winner;
  switch (result) {
    case GameResult::kCrossWin:
      status = "x_wins";
      winner = "X";
      break;
    case GameResult::kNoughtWin:
      status = "o_wins";
      winner = "O";
      break;
    case GameResult::kDraw:
      status = "draw";
      break;
    case GameResult::kInProgress:
      break;
  }
  out << R"(],"player":")" << player << R"(","status":")" << status << R"(","winner":")" << winner
      << R"("})" << '\n';
}

void Report(std::ostream& err, const std::string& message) {
  err << kProgramName << ": " << message << '\n';
}

std::expected<RowAndCol, ReadError> ReadRowAndCol(std::istream& in, std::ostream& err) {
  // 先按 64 位读，再判断能否收进 int：直接读 int 时溢出会让流失败，量级丢失，
  // 分不清写错了数还是写了字母。
  std::int64_t input_row = 0;
  std::int64_t input_col = 0;
  if (in >> input_row >> input_col) {
    if (input_row >= std::numeric_limits<int>::min() &&
        input_row <= std::numeric_limits<int>::max() &&
        input_col >= std::numeric_limits<int>::min() &&
        input_col <= std::numeric_limits<int>::max()) {
      // 一行只取两个整数；行尾余下的内容一起丢掉，下一轮从新行开始。
      in.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
      return RowAndCol{.row = static_cast<int>(input_row), .col = static_cast<int>(input_col)};
    }
    in.clear();
    in.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
    Report(err, "坐标超出可用范围");
    return std::unexpected(ReadError::kRetry);
  }
  if (in.eof()) {
    return std::unexpected(ReadError::kEof);
  }
  // 清掉失败位再丢整行：不丢的话下一次读会立刻再失败，同一行会被反复报告。
  in.clear();
  in.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
  Report(err, "请输入两个整数");
  return std::unexpected(ReadError::kRetry);
}

void ReportRejected(std::ostream& err, const Game& game, CellPosition position) {
  // 从最具体的原因往下排：同一坐标可能同时越界且没轮到，玩家先要知道该改哪一个。
  if (!Board::IsInRange(position)) {
    Report(err, "坐标超出棋盘");
    return;
  }
  if (game.GetCellType(position) != CellType::kEmpty) {
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

bool ReadAiStrength(std::istream& in, std::ostream& out, std::ostream& err, AiStrength& strength) {
  while (true) {
    out << "请选择难度（1 随机，2 启发式，3 极小极大）：" << std::flush;
    std::string line;
    if (!ReadOwnedLine(in, line)) {
      Report(err, "输入结束");
      return false;
    }
    if (line == "1") {
      strength = AiStrength::kRandom;
      return true;
    }
    if (line == "2") {
      strength = AiStrength::kHeuristic;
      return true;
    }
    if (line == "3") {
      strength = AiStrength::kMinimax;
      return true;
    }
    Report(err, "请输入 1、2 或 3");
  }
}

HumanMove ReadHumanMove(std::istream& in, std::ostream& err, Game& game) {
  const std::expected<RowAndCol, ReadError> input = ReadRowAndCol(in, err);
  if (!input) {
    return input.error() == ReadError::kEof ? HumanMove::kInputEnd : HumanMove::kRetry;
  }
  const CellPosition position{.row = input->row, .col = input->col};
  const PlaceResult result =
      game.TryPlace({.position = position, .player = game.GetCurrentPlayer()});
  if (result == PlaceResult::kRejected) {
    ReportRejected(err, game, position);
  }
  // 被拒也算这一轮读完：提示已经打印，主循环继续读下一行；kInputEnd 与 kRetry 只表示输入层状态。
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

int PlayToEnd(std::istream& in, std::ostream& out, std::ostream& err, AiStrength strength) {
  Game game;
  const std::unique_ptr<Ai> ai = MakeAi(strength);
  while (game.GetResult() == GameResult::kInProgress) {
    PrintGame(out, game);
    if (game.GetCurrentPlayer() == Player::kNought) {
      const PlaceResult placed = game.TryPlace(ai->Choose(game));
      if (placed == PlaceResult::kRejected) {
        // 电脑的落子被拒说明选格逻辑违背了 Game 的规则，重试只会死循环，直接结束并留报告。
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
  AiStrength strength = AiStrength::kMinimax;
  if (!ReadAiStrength(in, out, err, strength)) {
    return 1;
  }
  return PlayToEnd(in, out, err, strength);
}

}  // namespace tictactoe
