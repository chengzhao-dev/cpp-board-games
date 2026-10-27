/// @file main.cpp
/// @brief 井字棋动态库的进程入口。
///
/// 当前只做一次最小调用：创建一局、落一子并打印结果。

#include <exception>
#include <iostream>

#include "game.h"

int main() {
  try {
    tictactoe::Game game;
    const tictactoe::Move opening_move{
        .position = {.row = 0, .col = 0},
        .player = game.GetCurrentPlayer(),
    };

    if (game.TryPlace(opening_move) != tictactoe::PlaceResult::kPlaced) {
      std::cerr << "井字棋动态库调用失败\n";
      return 1;
    }

    std::cout << "井字棋动态库调用成功：已落子 " << game.GetHistory().size() << " 手\n";
    return 0;
  } catch (const std::exception& error) {
    std::cerr << "井字棋动态库调用失败：" << error.what() << '\n';
    return 1;
  }
}
