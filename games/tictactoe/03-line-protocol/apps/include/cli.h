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
#include "opponent.h"

namespace tictactoe {

/// 终端诊断与提示共用的程序名。
inline constexpr std::string_view kProgramName = "app";

/// 一次读取的结果。
enum class ReadResult : std::uint8_t {
  kOk = 0,     ///< 读到两个整数。
  kRetry = 1,  ///< 重试：本行不是两个整数，已丢掉。
  kEof = 2,    ///< 输入结束。
};

/// 一次人类落子的读入结果。
enum class HumanMove : std::uint8_t {
  kPlaced = 0,    ///< 落子已交给对局；坐标被拒绝时原因已报告。
  kRetry = 1,     ///< 本行不可用，重新读入。
  kInputEnd = 2,  ///< 输入结束，调用方退出。
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

/// 在每次打印棋盘后写一行 JSON 快照。
///
/// 快照包含版本、序号、九个棋盘格子、当前玩家、状态和胜者。这是应用层
/// 协议，不把 JSON 类型带进井字棋动态库。
///
/// @param out 接收快照的输出流。
/// @param game 要记录的对局。
void WriteSnapshot(std::ostream& out, const Game& game);

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

/// 读入一整行。
///
/// @param in 玩家输入流。
/// @param[out] line 接收整行内容（不含换行符）的字符串。
/// @returns 读到一行返回 true，输入结束返回 false。
bool ReadOwnedLine(std::istream& in, std::string& line);

/// 读入对局类型：1 双人，2 人机。
///
/// 其他整行重试，直到读到这两种或输入结束。
///
/// @param in 玩家输入流。
/// @param out 选择提示的输出流。
/// @param err 诊断输出流。
/// @param[out] against_cpu 选人机时置 true，选双人置 false。
/// @returns 读到有效选择返回 true，输入结束返回 false。
bool ReadMatchKind(std::istream& in, std::ostream& out, std::ostream& err, bool& against_cpu);

/// 读入电脑强度：1 随机，2 启发式，3 极小极大。
///
/// 其他整行重试，直到读到这三种或输入结束。
///
/// @param in 玩家输入流。
/// @param out 选择提示的输出流。
/// @param err 诊断输出流。
/// @param[out] strength 读到的强度。
/// @returns 读到有效选择返回 true，输入结束返回 false。
bool ReadStrength(std::istream& in, std::ostream& out, std::ostream& err, Strength& strength);

/// 读入一行行列坐标并尝试落子，被拒绝时报告原因。
///
/// 落子提示由调用方打印。
///
/// @param in 玩家输入流。
/// @param err 诊断输出流。
/// @param game 要落子的对局。
/// @returns 落子已处理返回 kPlaced，需要重试返回 kRetry，输入结束返回
/// kInputEnd。
HumanMove ReadHumanMove(std::istream& in, std::ostream& err, Game& game);

/// 打印、读入并落子，直到终局或输入结束。
///
/// 两名玩家都从输入读入。
///
/// @param in 玩家输入流。
/// @param out 棋盘、提示与 JSON 快照的输出流。
/// @param err 诊断输出流。
/// @returns 对局下完返回 0，输入结束返回 1。
int PlayToEnd(std::istream& in, std::ostream& out, std::ostream& err);

/// 打印、读入并落子，直到终局或输入结束。
///
/// 先手从输入读入，后手由对手产生 Move，再调用同一个 TryPlace。
///
/// @param in 玩家输入流。
/// @param out 棋盘、提示与 JSON 快照的输出流。
/// @param err 诊断输出流。
/// @param opponent 电脑对手的强度。
/// @returns 对局下完返回 0，输入结束返回 1。
int PlayToEnd(std::istream& in, std::ostream& out, std::ostream& err, Strength opponent);

/// 先读对局类型，选人机时再读强度，然后下到终局。
///
/// @param in 玩家输入流。
/// @param out 棋盘、提示与选择菜单的输出流。
/// @param err 诊断输出流。
/// @returns 对局下完返回 0，输入结束返回 1。
int RunMatch(std::istream& in, std::ostream& out, std::ostream& err);

}  // namespace tictactoe
