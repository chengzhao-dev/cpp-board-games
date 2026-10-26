//===------------------------------------------------------------------------------------------===//
// cli.h - 终端程序的打印与读入。
//
// 声明终端显示、输入读入与对局循环。
//===------------------------------------------------------------------------------------------===//

#ifndef APPS_INCLUDE_CLI_H_
#define APPS_INCLUDE_CLI_H_

#include <cstdint>
#include <expected>
#include <iosfwd>
#include <string>
#include <string_view>

#include "ai.h"
#include "board.h"
#include "game.h"

namespace tictactoe {

/// 终端诊断与提示共用的程序名。
///
/// 诊断统一写成“程序名: 描述”；名字取可执行文件名，脚本按前缀就能把诊断和棋盘、快照分开。
inline constexpr std::string_view kProgramName = "app";

/// 读取行列时除成功外的两种结果。
enum class ReadError : std::uint8_t {
  kRetry = 0,  ///< 这一行无效，重新读。
  kEof = 1,    ///< 输入结束。
};

/// 读到的一对行列坐标。
struct RowAndCol {
  int row = 0;  ///< 可能为负数，合法性由落子入口判定。
  int col = 0;  ///< 可能越界，合法性由落子入口判定。
};

/// 一次人类落子的读入结果。
enum class HumanMove : std::uint8_t {
  kPlaced = 0,    ///< 这一行已处理，继续下一轮。
  kRetry = 1,     ///< 重新读一行。
  kInputEnd = 2,  ///< 输入结束。
};

/// 把棋盘格子类型转成单个显示字符：`' '`、`'X'`、`'O'`。
char CellSymbol(CellType cell_type);

/// 把对局棋盘转成待打印的多行文本。
std::string BoardToString(const Game& game);

/// 把终局结果转成中文结果短语。
std::string GameResultToString(GameResult result);

/// 按行列号打印棋盘，在末行写出终局结果，并在棋盘后追加一行 JSON 快照。
///
/// @param out 接收棋盘与状态的输出流。
/// @param game 要打印的对局。
void PrintGame(std::ostream& out, const Game& game);

/// 在每次打印棋盘后写一行 JSON 快照。
///
/// 快照包含版本、序号、九个棋盘格子、当前玩家、状态和胜者。这份 JSON
/// 由应用层读写，不把 JSON 类型带进井字棋动态库。
///
/// @param out 接收快照的输出流。
/// @param game 要记录的对局。
void WriteSnapshot(std::ostream& out, const Game& game);

/// 把诊断写到调用方给出的错误流。
///
/// 格式为“程序名: 描述”。
///
/// @param err 诊断输出流。
/// @param message 诊断内容。
void Report(std::ostream& err, const std::string& message);

/// 读取输入中的两个整数作为行列坐标。
///
/// 先按 64 位读入再收窄到 int：超出 int 的输入当成本行不可用。
/// 成功时消费整行；不是两个整数或超出可用范围时，清掉错误并丢掉本行，说明写到 err。
///
/// @param in 玩家输入流。
/// @param err 诊断输出流。
/// @return 成功时带行列坐标；需要重试返回 kRetry，输入结束返回 kEof。
std::expected<RowAndCol, ReadError> ReadRowAndCol(std::istream& in, std::ostream& err);

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
/// @return 读到一行返回 true，输入结束返回 false。
bool ReadOwnedLine(std::istream& in, std::string& line);

/// 读入对局类型：1 双人，2 人机。
///
/// 其他整行重试，直到读到这两种或输入结束。
///
/// @param in 玩家输入流。
/// @param out 选择提示的输出流。
/// @param err 诊断输出流。
/// @param[out] against_cpu 选人机时置 true，选双人置 false。
/// @return 读到有效选择返回 true，输入结束返回 false。
bool ReadMatchKind(std::istream& in, std::ostream& out, std::ostream& err, bool& against_cpu);

/// 读入电脑强度：1 随机，2 启发式，3 极小极大。
///
/// 其他整行重试，直到读到这三种或输入结束。
///
/// @param in 玩家输入流。
/// @param out 选择提示的输出流。
/// @param err 诊断输出流。
/// @param[out] strength 读到的强度。
/// @return 读到有效选择返回 true，输入结束返回 false。
bool ReadAiStrength(std::istream& in, std::ostream& out, std::ostream& err, AiStrength& strength);

/// 读入一行行列坐标并尝试落子，被拒绝时报告原因。
///
/// 落子提示由调用方打印：同一段读入既服务双人模式也服务人机模式，提示文案留在一处。
///
/// @param in 玩家输入流。
/// @param err 诊断输出流。
/// @param game 要落子的对局。
/// @return 落子已处理返回 kPlaced，需要重试返回 kRetry，输入结束返回 kInputEnd。
HumanMove ReadHumanMove(std::istream& in, std::ostream& err, Game& game);

/// 打印、读入并落子，直到终局或输入结束。
///
/// 两名玩家都从输入读入。
///
/// @param in 玩家输入流。
/// @param out 棋盘、提示与 JSON 快照的输出流。
/// @param err 诊断输出流。
/// @return 对局下完返回 0，输入结束返回 1。
int PlayToEnd(std::istream& in, std::ostream& out, std::ostream& err);

/// 打印、读入并落子，直到终局或输入结束。
///
/// 先手从输入读入，后手由电脑产生 Move，再调用同一个 TryPlace：
/// 两条路径共用同一处落子判定，人机模式不会绕过规则检查。
///
/// @param in 玩家输入流。
/// @param out 棋盘、提示与 JSON 快照的输出流。
/// @param err 诊断输出流。
/// @param strength 电脑落子的强度。
/// @return 对局下完返回 0，输入结束返回 1。
int PlayToEnd(std::istream& in, std::ostream& out, std::ostream& err, AiStrength strength);

/// 先读对局类型，选人机时再读强度，然后下到终局。
///
/// 菜单只在前两步出现：对局开始后每一轮由 PlayToEnd 自己打印，入口函数不重复提示。
///
/// @param in 玩家输入流。
/// @param out 棋盘、提示与选择菜单的输出流。
/// @param err 诊断输出流。
/// @return 对局下完返回 0，输入结束返回 1。
int RunMatch(std::istream& in, std::ostream& out, std::ostream& err);

}  // namespace tictactoe

#endif  // APPS_INCLUDE_CLI_H_
