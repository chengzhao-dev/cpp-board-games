//===------------------------------------------------------------------------------------------===//
// cli.h - 终端对局的打印与读入。
//
// 声明终端显示、输入读入与对局循环；不进入井字棋动态库。
//===------------------------------------------------------------------------------------------===//

#pragma once

#include <cstdint>
#include <iosfwd>
#include <string>
#include <string_view>

#include "board.h"
#include "game.h"

namespace tictactoe {

/// 终端诊断与提示共用的程序名。
inline constexpr std::string_view kProgramName = "app";

/// 一次读取的结果。
enum class ReadResult : std::uint8_t {
  kOk = 0,     ///< 读到两个整数。
  kRetry = 1,  ///< 重试：本行不是两个整数，已丢掉。
  kEof = 2,    ///< 输入结束。
};

/// 把棋盘格子状态转成单个显示字符，空棋盘格子显示为空位。
char CellSymbol(CellState state);

/// 把对局的棋盘转成待打印的多行文本。
std::string BoardToString(const Game& game);

/// 把终局结果转成中文结果短语。
std::string GameResultToString(GameResult result);

/// 按行列号打印棋盘，并在末行写出终局结果。
///
/// @param out 接收棋盘与状态的输出流。
/// @param game 要打印的对局。
void PrintGame(std::ostream& out, const Game& game);

/// 把诊断写到调用方给出的错误流。
///
/// 格式为「程序名: 描述」。
///
/// @param err 诊断输出流。
/// @param message 诊断内容。
void Report(std::ostream& err, const std::string& message);

/// 读取输入中的两个整数作为行列坐标。
///
/// 不是两个整数或超出可用范围时，清掉错误并丢掉本行，说明写到 err。
///
/// @param in 玩家输入流。
/// @param err 诊断输出流。
/// @param[out] row 读到的行坐标。
/// @param[out] col 读到的列坐标。
/// @returns 读到两个整数返回 kOk，需要重试返回 kRetry，输入结束返回 kEof。
ReadResult ReadRowAndCol(std::istream& in, std::ostream& err, int& row, int& col);

/// 说明一次落子被拒绝的原因。
///
/// 棋盘在 TryPlace 拒绝后保持原样。
///
/// @param err 诊断输出流。
/// @param game 刚被拒绝落子的对局。
/// @param position 被拒绝的行列坐标。
void ReportRejected(std::ostream& err, const Game& game, CellPosition position);

/// 打印、读入并落子，直到终局或输入结束。
///
/// 两名玩家都从输入读入。
///
/// @param in 玩家输入流。
/// @param out 棋盘与提示的输出流。
/// @param err 诊断输出流。
/// @returns 对局下完返回 0，输入结束返回 1。
int PlayToEnd(std::istream& in, std::ostream& out, std::ostream& err);

}  // namespace tictactoe
