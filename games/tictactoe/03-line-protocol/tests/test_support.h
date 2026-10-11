//===------------------------------------------------------------------------------------------===//
// test_support.h - 测试共用的落子助手。
//
// 按顺序执行一组已知合法的落子，供对局测试与对手测试复用。
//===------------------------------------------------------------------------------------------===//

#pragma once

#include <initializer_list>

#include <gtest/gtest.h>

#include "game.h"

namespace tictactoe::testing {

// 按顺序落下这些坐标。调用方保证每步都应由当前玩家落子。
inline void Play(Game& game, std::initializer_list<CellPosition> moves) {
  for (const CellPosition position : moves) {
    ASSERT_EQ(game.TryPlace({.position = position, .player = game.GetCurrentPlayer()}),
              PlaceResult::kPlaced);
  }
}

}  // namespace tictactoe::testing
