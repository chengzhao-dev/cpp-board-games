//===------------------------------------------------------------------------------------------===//
// cli_test.cpp - 终端读入、菜单与对局循环的测试。
//
// 用字符串流注入输入：越界行与非整数行都被丢弃，菜单非法输入重试，
// 输入结束返回 1，人机对局的后手由对手产生。
//===------------------------------------------------------------------------------------------===//

#include "cli.h"

#include <sstream>
#include <string>

#include <gtest/gtest.h>

#include "opponent.h"

namespace {

using tictactoe::PlayToEnd;
using tictactoe::ReadMatchKind;
using tictactoe::ReadResult;
using tictactoe::ReadRowAndCol;
using tictactoe::ReadStrength;
using tictactoe::RunMatch;
using tictactoe::Strength;

// 超出 int 范围的一行整行丢弃，下一行仍从行首读。
TEST(CliTest, ReadRowAndColDropsOutOfRangeLine) {
  std::istringstream in("5000000000 1 2\n3 4\n");
  std::ostringstream err;
  int row = 0;
  int col = 0;
  EXPECT_EQ(ReadRowAndCol(in, err, row, col), ReadResult::kRetry);
  EXPECT_EQ(err.str(), "app: 坐标超出可用范围\n");
  EXPECT_EQ(ReadRowAndCol(in, err, row, col), ReadResult::kOk);
  EXPECT_EQ(row, 3);
  EXPECT_EQ(col, 4);
}

// 不是两个整数的一行整行丢弃，并提示重新输入。
TEST(CliTest, ReadRowAndColDropsNonIntegerLine) {
  std::istringstream in("a b\n1 2\n");
  std::ostringstream err;
  int row = 0;
  int col = 0;
  EXPECT_EQ(ReadRowAndCol(in, err, row, col), ReadResult::kRetry);
  EXPECT_EQ(err.str(), "app: 请输入两个整数\n");
  EXPECT_EQ(ReadRowAndCol(in, err, row, col), ReadResult::kOk);
  EXPECT_EQ(row, 1);
  EXPECT_EQ(col, 2);
}

// 输入已经结束时报告 kEof。
TEST(CliTest, ReadRowAndColReportsEof) {
  std::istringstream in("");
  std::ostringstream err;
  int row = 0;
  int col = 0;
  EXPECT_EQ(ReadRowAndCol(in, err, row, col), ReadResult::kEof);
}

// 菜单非法输入重试，读到 2 时进入人机。
TEST(CliTest, ReadMatchKindRetriesInvalidInput) {
  std::istringstream in("7\n2\n");
  std::ostringstream out;
  std::ostringstream err;
  bool against_cpu = false;
  EXPECT_TRUE(ReadMatchKind(in, out, err, against_cpu));
  EXPECT_TRUE(against_cpu);
  EXPECT_NE(err.str().find("请输入 1 或 2"), std::string::npos);
}

// 菜单处输入结束返回 false 并报告输入结束。
TEST(CliTest, ReadMatchKindReportsInputEnd) {
  std::istringstream in("\n");
  std::ostringstream out;
  std::ostringstream err;
  bool against_cpu = true;
  EXPECT_FALSE(ReadMatchKind(in, out, err, against_cpu));
  EXPECT_NE(err.str().find("输入结束"), std::string::npos);
}

// 难度菜单读到 3 时选极小极大。
TEST(CliTest, ReadStrengthAcceptsMinimax) {
  std::istringstream in("4\n3\n");
  std::ostringstream out;
  std::ostringstream err;
  Strength strength = Strength::kRandom;
  EXPECT_TRUE(ReadStrength(in, out, err, strength));
  EXPECT_EQ(strength, Strength::kMinimax);
  EXPECT_NE(err.str().find("请输入 1、2 或 3"), std::string::npos);
}

// 双人分支从菜单进入后走完一整局。
TEST(CliTest, RunMatchPlaysDoublePlayerMatch) {
  std::istringstream in("1\n0 0\n1 0\n0 1\n1 1\n0 2\n");
  std::ostringstream out;
  std::ostringstream err;
  EXPECT_EQ(RunMatch(in, out, err), 0);
  EXPECT_NE(out.str().find("对局结果：X 获胜"), std::string::npos);
}

// 人机分支在菜单后由对手落子，先手输入结束时返回 1。
TEST(CliTest, RunMatchPlaysCpuMatchUntilInputEnds) {
  std::istringstream in("2\n3\n0 0\n");
  std::ostringstream out;
  std::ostringstream err;
  EXPECT_EQ(RunMatch(in, out, err), 1);
  EXPECT_NE(out.str().find("对局结果："), std::string::npos);
  EXPECT_NE(out.str().find('O'), std::string::npos);
  EXPECT_NE(err.str().find("输入结束"), std::string::npos);
}

// 菜单处输入结束返回 1。
TEST(CliTest, RunMatchReturnsOneWhenMenuEnds) {
  std::istringstream in("");
  std::ostringstream out;
  std::ostringstream err;
  EXPECT_EQ(RunMatch(in, out, err), 1);
  EXPECT_NE(err.str().find("输入结束"), std::string::npos);
}

// 双人重载直接读坐标，被拒绝的坐标按原因提示。
TEST(CliTest, PlayToEndReportsRejectionAndContinues) {
  std::istringstream in("0 0\n9 9\n0 0\n1 0\n0 1\n1 1\n0 2\n");
  std::ostringstream out;
  std::ostringstream err;
  EXPECT_EQ(PlayToEnd(in, out, err), 0);
  EXPECT_NE(err.str().find("坐标超出棋盘"), std::string::npos);
  EXPECT_NE(err.str().find("棋盘格子已被占用"), std::string::npos);
  EXPECT_NE(out.str().find("对局结果：X 获胜"), std::string::npos);
}

}  // namespace
