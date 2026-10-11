//===------------------------------------------------------------------------------------------===//
// cli_test.cpp - 终端读入、提示与对局循环的测试。
//
// 用字符串流注入输入：越界行与非整数行都被丢弃，输入结束返回 1。
//===------------------------------------------------------------------------------------------===//

#include "cli.h"

#include <sstream>
#include <string>

#include <gtest/gtest.h>

namespace {

using tictactoe::PlayToEnd;
using tictactoe::ReadResult;
using tictactoe::ReadRowAndCol;

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

// 走完一整局返回 0，并打印完整结果行。
TEST(CliTest, PlayToEndFinishesScriptedMatch) {
  std::istringstream in("0 0\n1 0\n0 1\n1 1\n0 2\n");
  std::ostringstream out;
  std::ostringstream err;
  EXPECT_EQ(PlayToEnd(in, out, err), 0);
  EXPECT_NE(out.str().find("对局结果：X 获胜"), std::string::npos);
}

// 中途输入结束返回 1，并报告输入结束。
TEST(CliTest, PlayToEndReturnsOneOnInputEnd) {
  std::istringstream in("0 0\n");
  std::ostringstream out;
  std::ostringstream err;
  EXPECT_EQ(PlayToEnd(in, out, err), 1);
  EXPECT_NE(err.str().find("输入结束"), std::string::npos);
}

// 被拒绝的坐标按原因提示，随后照常继续读入。
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
