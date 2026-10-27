/// @file game.h
/// @brief 定义井字棋的回合、落子请求与对局结果。
///
/// Game 记录轮到谁、这步能不能走、走完结果是什么。

#ifndef TICTACTOE_INCLUDE_GAME_H_
#define TICTACTOE_INCLUDE_GAME_H_

#include <cstdint>
#include <vector>

#include "board.h"

namespace tictactoe {

/// 对局玩家。
enum class Player : std::uint8_t {
  kCross = 0,   ///< 先手：使用 X 棋子。
  kNought = 1,  ///< 后手：使用 O 棋子。
};

/// 一次落子的处理结果。
enum class PlaceResult : std::uint8_t {
  kPlaced = 0,    ///< 落子成功。
  kRejected = 1,  ///< 落子被拒，棋盘不变。
};

/// 对局结果。
enum class GameResult : std::uint8_t {
  kInProgress = 0,  ///< 游戏进行中：还可以落子。
  kCrossWin = 1,    ///< X 获胜：达成三连。
  kNoughtWin = 2,   ///< O 获胜：达成三连。
  kDraw = 3,        ///< 平局：棋盘已满，双方都没有三连。
};

/// 一名玩家的一次落子。
struct Move {
  CellPosition position;
  Player player = Player::kCross;
};

/// 由对局玩家得到应写入的棋盘格子类型。
///
/// Player 是“谁在下”，CellType 是“棋盘上是什么”；转换都是 constexpr 纯函数。
///
/// Player::kCross 对应 CellType::kX。
constexpr CellType PlayerToCellType(Player player) {
  return player == Player::kCross ? CellType::kX : CellType::kO;
}

/// 由对局玩家得到对手。
///
/// Player::kCross 对应 Player::kNought。
constexpr Player PlayerToOpponent(Player player) {
  return player == Player::kCross ? Player::kNought : Player::kCross;
}

/// 由对局玩家得到该玩家获胜时的对局结果。
///
/// Player::kCross 对应 GameResult::kCrossWin。
constexpr GameResult PlayerToWinResult(Player player) {
  return player == Player::kCross ? GameResult::kCrossWin : GameResult::kNoughtWin;
}

/// 一局 X 先手、两名玩家轮流落子的井字棋对局，棋盘、轮次、结果与历史同步更新。
///
/// 落子成功时 TryPlace 同时改写这四项；对局结束后轮次停在最后一名玩家。
/// 历史停在最后一步。
class Game {
 public:
  /// 默认构造函数：得到一局空棋盘对局，轮到 X 落子。
  Game() = default;

  /// 获取当前落子玩家。
  [[nodiscard]] Player GetCurrentPlayer() const noexcept;

  /// 获取当前对局结果。
  [[nodiscard]] GameResult GetResult() const noexcept;

  /// 转发给 Board；坐标越界时抛出 std::out_of_range。
  ///
  /// @param position 行列坐标。
  /// @throws std::out_of_range 坐标不在棋盘范围内。
  [[nodiscard]] CellType GetCellType(CellPosition position) const;

  /// 检查在指定坐标放入给定棋子后，是否会形成三连。
  ///
  /// 只做推演，不改变对局；电脑落子用它判断“这一步能不能赢”。
  ///
  /// @param position 假设落子的行列坐标。
  /// @param cell_type 假设放入的棋盘格子类型。
  /// @return 放入后能形成三连返回 true；否则返回 false。
  [[nodiscard]] bool IsLineComplete(CellPosition position, CellType cell_type) const;

  /// 获取本局落子历史。
  ///
  /// 历史随落子增长，界面和测试都只读；调用方不要跨界面刷新缓存它。
  /// 先手第一步在最前，最近一步在末尾。
  [[nodiscard]] const std::vector<Move>& GetHistory() const noexcept;

  /// 尝试执行一次落子。
  ///
  /// 只有对局进行中、且落子玩家正是当前玩家时才继续，棋盘、轮次、历史一起更新。
  ///
  /// @param move 待执行的落子，玩家必须等于 GetCurrentPlayer()。
  /// @return 写入棋盘并换手时返回 kPlaced；
  /// 终局、玩家不符或棋盘拒绝落子时返回 kRejected。
  /// 三种情况都不改变棋盘、轮次和历史。
  [[nodiscard]] PlaceResult TryPlace(const Move& move);

 private:
  /// 判定落子后的对局结果。
  ///
  /// 只看刚落子的一方：它成线就判它胜，否则棋盘下满判平局，都没发生则对局继续。
  /// 做成 static 因为它只依赖传入的棋盘与玩家，测试可单独驱动。
  ///
  /// @param board 落子后的棋盘。
  /// @param player 刚落子的对局玩家。
  [[nodiscard]] static GameResult JudgeAfterPlace(const Board& board, Player player);

  /// 本局棋盘：开局是空棋盘。
  Board board_;
  /// 当前玩家：开局由 X 先手。
  Player current_player_ = Player::kCross;
  /// 对局结果：落子被拒时保持原值。
  GameResult result_ = GameResult::kInProgress;
  /// 落子历史：按落子次序保存。
  std::vector<Move> history_;
};

}  // namespace tictactoe

#endif  // TICTACTOE_INCLUDE_GAME_H_
