//===----------------------------------------------------------------------===//
// cli.h - 终端对局的打印与读入。
//
// 声明按行列号打印和对局循环；不进入井字棋动态库。
//===----------------------------------------------------------------------===//

#pragma once

#include <iosfwd>

#include "game.h"
#include "opponent.h"

namespace tictactoe {

// 按行列号打印棋盘，并在末行写出终局结果。
void PrintGame(std::ostream& out, const Game& game);

// 打印、读入并落子，直到终局或输入结束。
// 下完返回 0；输入结束返回 1。两名玩家都从输入读入。
int PlayToEnd(std::istream& in, std::ostream& out, std::ostream& err);

// 先手从输入读入，后手由对手产生 Move，再调用同一个 Place。
int PlayToEnd(std::istream& in, std::ostream& out, std::ostream& err,
              Strength opponent);

// 先读对局种类。选人机时再读难度，然后下到终局。
// 下完返回 0；输入结束返回 1。
int RunMatch(std::istream& in, std::ostream& out, std::ostream& err);

}  // namespace tictactoe
