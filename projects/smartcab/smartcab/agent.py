import random
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator

import random

class LearningAgent(Agent):
    """An agent that learns to drive in the smartcab world."""

    def __init__(self, env):
        super(LearningAgent, self).__init__(env)  # sets self.env = env, state = None, next_waypoint = None, and a default color
        self.color      = 'red'  # override color
        self.planner    = RoutePlanner(self.env, self)  # simple route planner to get next_waypoint
        self.q_values   = {}
        self.epsilon    = 0.5

    def reset(self, destination=None):
        self.planner.route_to(destination)
        # TODO: Prepare for a new trip; reset any variables here, if required

    def update(self, t):
        possible_actions = [None, "forward", "left", "right"]

        # Gather inputs
        self.next_waypoint  = self.planner.next_waypoint()  # from route planner, also displayed by simulator
        inputs              = self.env.sense(self)
        deadline            = self.env.get_deadline(self)

        self.state = (inputs["light"], inputs["oncoming"], deadline)

        # Select action according to your policy
        best_action  = None
        best_q_value = self.q_values.get((self.state, best_action), 0)

        for action in possible_actions:
            q_value = self.q_values.get((self.state, action), 0)
            if q_value > best_q_value:
                best_action  = action
                best_q_value = q_value

        if random.random() < self.epsilon:
            next_action = best_action
        else:
            print "random choice"
            other_actions = filter(lambda x: x != best_action, possible_actions)
            next_action = random.choice(other_actions)

        # Execute action and get reward
        reward = self.env.act(self, next_action)

        # TODO: Learn policy based on state, action, reward
        print "LearningAgent.update(): state = {}".format(self.state)
        print "LearningAgent.update(): deadline = {}, inputs = {}, action = {}, reward = {}".format(deadline, inputs, next_action, reward)  # [debug]
        import pdb; pdb.set_trace()

def run():
    """Run the agent for a finite number of trials."""

    # Set up environment and agent
    e = Environment()  # create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent)  # create agent
    e.set_primary_agent(a, enforce_deadline=True)  # specify agent to track
    # NOTE: You can set enforce_deadline=False while debugging to allow longer trials

    # Now simulate it
    sim = Simulator(e, update_delay=0.5, display=True)  # create simulator (uses pygame when display=True, if available)
    # NOTE: To speed up simulation, reduce update_delay and/or set display=False

    sim.run(n_trials=100)  # run for a specified number of trials
    # NOTE: To quit midway, press Esc or close pygame window, or hit Ctrl+C on the command-line


if __name__ == '__main__':
    run()
