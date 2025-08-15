#include <gtest/gtest.h>

#include <state_machine/Factory.hpp>

#include "state_machine_example/CalculateFibonacciSeries.hpp"
#include "state_machine_example/CalculateTwoFibonacciSeriesSequentially.hpp"

class TestPlugins : public ::testing::Test {
 protected:
  void SetUp() override {
    context_ = std::make_shared<state_machine::Context>();
    factory_ = std::make_shared<state_machine::Factory>(context_);
  }

  template <typename Type>
  void expectStatePluginExists(const state_machine::StateType& type) {
    const state_machine::StateName name("MyState");
    auto stateBase = factory_->createState(type, name);
    ASSERT_NE(nullptr, stateBase);
    EXPECT_EQ(type, stateBase->getType());
    EXPECT_EQ(name, stateBase->getName());
    auto* state = dynamic_cast<Type*>(stateBase.get());
    EXPECT_NE(nullptr, state);
  }

 protected:
  state_machine::ContextPtr context_;  // NOLINT
  state_machine::FactoryPtr factory_;  // NOLINT
};

#define EXPECT_STATE_PLUGIN_EXISTS(Type) expectStatePluginExists<Type>(state_machine::StateType(#Type));

TEST_F(TestPlugins, checkAllStatePluginsExist) {  // NOLINT
  EXPECT_STATE_PLUGIN_EXISTS(state_machine_example::CalculateFibonacciSeries)
  EXPECT_STATE_PLUGIN_EXISTS(state_machine_example::CalculateTwoFibonacciSeriesSequentially)
}
