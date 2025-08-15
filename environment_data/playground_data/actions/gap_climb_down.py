#! /usr/bin/env python

class Action(SimpleAction):

    def __init__(self, receiver):

        placeholders = {'<source_frame>': 'map',
                        '<target_frame>': 'odom',
                        '<position_x>': -7.0,
                        '<position_y>': -13.0,
                        '<position_z>': 2.1,
                        '<orientation_yaw>': 1.5078,
                        '<step_height>': -0.1}

        goal = load_action_from_file(get_package_path('anymal_basic_actions') \
                                     + '/actions/step_climb_down.yaml', placeholders)

        SimpleAction.__init__(self, receiver, goal)


action = Action(action_loader.execute_steps_relay)
