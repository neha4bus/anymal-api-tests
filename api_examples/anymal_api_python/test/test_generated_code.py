#!/usr/bin/env python3

from anymal_api_proto import NavigationGoal, ServiceCallStatus


def test_use_generated_message():
    goal = NavigationGoal()
    assert goal.label == ""
    goal.label = "label"
    assert goal.label == "label"


def test_use_generated_enum():
    # Just test that enums can be imported and used.
    assert ServiceCallStatus.SCS_OK is not None
