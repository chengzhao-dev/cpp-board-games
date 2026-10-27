/// @file ai.h
/// @brief 电脑落子的接口与三种强度实现。
///
/// Ai 定义统一的选子接口，三种强度各是一个派生类；选子只读对局并返回一步 Move。

#ifndef TICTACTOE_INCLUDE_AI_H_
#define TICTACTOE_INCLUDE_AI_H_

#include <cstdint>
#include <memory>
#include <vector>

#include "board.h"
#include "game.h"

namespace tictactoe {

/// 电脑落子的强度。
enum class AiStrength : std::uint8_t {
  kRandom = 0,     ///< 随机落子。
  kHeuristic = 1,  ///< 能赢就赢，否则挡住对方。
  kMinimax = 2,    ///< 按终局结果选最优步。
};

/// 收集还没有棋子的棋盘格子。
///
/// @param game 只读的当前对局。
/// @return 空棋盘格子坐标的列表，按行序排列。
[[nodiscard]] std::vector<CellPosition> CollectEmptyCells(const Game& game);

class Ai;

/// 按强度造出对应的电脑落子对象。
///
/// @param strength 电脑落子的强度。
[[nodiscard]] std::unique_ptr<Ai> MakeAi(AiStrength strength);

/// 电脑落子的公共接口。
///
/// 创建后由调用方持有，通过 Choose 选择一步落子。
class Ai {
 public:
  /// 默认构造函数：得到不携带状态的电脑落子对象。
  Ai() = default;

  /// 拷贝与移动构造函数、赋值运算符：删除，由 MakeAi 返回的 unique_ptr 独占持有。
  Ai(const Ai&) = delete;
  Ai& operator=(const Ai&) = delete;
  Ai(Ai&&) = delete;
  Ai& operator=(Ai&&) = delete;

  /// 析构函数：保证通过接口指针正确删除派生类对象。
  virtual ~Ai();

  /// 为当前玩家选择一步落子。
  ///
  /// 对局必须仍在进行。返回的坐标指向空棋盘格子，玩家是当前玩家。
  ///
  /// @param game 只读的当前对局。
  /// @return 选出的一步落子。
  /// @throws std::logic_error 对局已经结束。
  [[nodiscard]] virtual Move Choose(const Game& game) const = 0;
};

/// 随机强度的电脑落子。
///
/// 只保证合法，用来对照另外两种强度：它下满一局就能验证对局流程和终局判定。
class RandomAi final : public Ai {
 public:
  /// 在空棋盘格子里等概率选一格。
  ///
  /// 对局必须仍在进行，棋盘上至少还有一格尚未落子。
  ///
  /// @param game 只读的当前对局。
  /// @return 选出的一步落子。
  /// @throws std::logic_error 对局已经结束。
  [[nodiscard]] Move Choose(const Game& game) const override;
};

/// 启发式强度的电脑落子。
///
/// 只看一步：先赢、再挡，然后按中心、四角、四边的次序选格。
/// 它是对照组，用来显示“不搜索整棵树也能下得像样”。
class HeuristicAi final : public Ai {
 public:
  /// 能立刻取胜就取胜，否则挡住对方马上能赢的一步，再按中心、四角、四边选格。
  ///
  /// 对局必须仍在进行。
  ///
  /// @param game 只读的当前对局。
  /// @return 选出的一步落子。
  /// @throws std::logic_error 对局已经结束。
  [[nodiscard]] Move Choose(const Game& game) const override;
};

/// 极小极大强度的电脑落子。
///
/// 对每个空棋盘格子都试落一子再递归搜索，配合 alpha-beta 剪枝；
/// 井字棋状态少，能在一局内算到终局，所以不会输。
class MinimaxAi final : public Ai {
 public:
  /// 对每个空棋盘格子搜索一次，留下对当前玩家更好的那一格。
  ///
  /// 对局必须仍在进行。
  ///
  /// @param game 只读的当前对局。
  /// @return 选出的一步落子。
  /// @throws std::logic_error 对局已经结束。
  [[nodiscard]] Move Choose(const Game& game) const override;

 private:
  /// 为终局结果打分：X 胜为 1，平局为 0，O 胜为 -1。
  ///
  /// @param result 对局结果。
  [[nodiscard]] static int ScoreTerminal(GameResult result);

  /// 极小极大搜索：X 取更大分数，O 取更小分数，alpha、beta 剪掉不可能的分支。
  ///
  /// @param game 只读的当前对局。
  /// @param alpha 当前已知最好分数的下界。
  /// @param beta 当前已知最好分数的上界。
  /// @return 双方都按最优应对时当前玩家能取得的得分。
  [[nodiscard]] static int Search(const Game& game, int alpha, int beta);
};

}  // namespace tictactoe

#endif  // TICTACTOE_INCLUDE_AI_H_
