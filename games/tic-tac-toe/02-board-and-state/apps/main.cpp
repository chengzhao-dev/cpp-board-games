//===----------------------------------------------------------------------===//
// main.cpp - 棋盘状态程序的入口
//
// 构造初始状态并打印棋盘，验证 CLI 能链接规则库动态库并运行。
//===----------------------------------------------------------------------===//

#include <iostream>

#include "tic_tac_toe/game_state.h"
#include "tic_tac_toe/value_types.h"

namespace {

// 把格子内容转成棋盘字符：空格显示为点。
char CellSymbol(tic_tac_toe::Mark mark) {
  switch (mark) {
    case tic_tac_toe::Mark::kEmpty:
      return '.';
    case tic_tac_toe::Mark::kX:
      return 'X';
    case tic_tac_toe::Mark::kO:
      return 'O';
  }
  return '.';
}

}  // namespace

int main() {
  tic_tac_toe::GameState state;
  std::cout << "井字棋初始棋盘：\n";
  for (int row = 0; row < tic_tac_toe::kRows; ++row) {
    for (int col = 0; col < tic_tac_toe::kCols; ++col) {
      if (col > 0) {
        std::cout << ' ';
      }
      std::cout << CellSymbol(state.MarkAt({row, col}));
    }
    std::cout << '\n';
  }
  std::cout << "状态：进行中\n";
  return 0;
}
