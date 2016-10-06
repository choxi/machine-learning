import random
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator

import random

class LearningAgent(Agent):
    """An agent that learns to drive in the smartcab world."""

    def __init__(self, env):
        super(LearningAgent, self).__init__(env)  # sets self.env = env, state = None, next_waypoint = None, and a default color
        self.color          = 'red'  # override color
        self.planner        = RoutePlanner(self.env, self)  # simple route planner to get next_waypoint
        self.q_values       = {}
        self.epsilon        = 0.2
        self.alpha          = 0.1
        self.gamma          = 0.1
        self.rewards        = []
        self.current_iteration = 0
        self.successes      = 0

    def reset(self, destination=None):
        self.planner.route_to(destination)
        self.current_iteration += 1
        # TODO: Prepare for a new trip; reset any variables here, if required

    def best_action_from_state(self, state, epsilon=1.0):
        possible_actions    = [ None, "forward", "left", "right" ]
        best_action         = None
        best_q_value        = self.q_values.get((state, best_action), 0)

        for action in possible_actions:
            q_value = self.q_values.get((state, action), 0)
            if q_value > best_q_value:
                best_action  = action
                best_q_value = q_value

        if random.random() < (1 - self.epsilon):
            next_action = best_action
        else:
            other_actions = filter(lambda x: x != best_action, possible_actions)
            next_action = random.choice(other_actions)

        return next_action

    def current_state(self):
        inputs              = self.env.sense(self)
        next_waypoint       = self.planner.next_waypoint()
        deadline            = self.env.get_deadline(self)

        return ( inputs["light"], inputs["oncoming"], next_waypoint )

    def update(self, t):
        # Gather inputs and set state
        self.next_waypoint  = self.planner.next_waypoint()
        self.state          = self.current_state()

        #######################################################################
        # Select action according to your policy
        action = self.best_action_from_state(self.state, epsilon=(self.epsilon ** t))

        #######################################################################
        # Execute action and get reward
        reward = self.env.act(self, action)
        self.rewards.append(reward)

        #######################################################################
        # Learn policy based on state, action, reward
        new_state = self.current_state()

        # The updated q value for our current state equals
        #       the reward we just saw
        #     + the q value of the best action to take from this state
        #     * the learning rate
        # Q(s) = r(s) + gamma * sigma(Q(s', a'))
        new_action = self.best_action_from_state(new_state)
        self.q_values[(self.state, action)] = \
            self.q_values.get((self.state, action), 0) + \
            (self.alpha ** t) * (reward + (self.gamma ** t) * self.q_values.get((new_state, new_action), 0))

        # Check to see if successful
        location    = self.env.agent_states[self]["location"]
        destination = self.env.agent_states[self]["destination"]

        if location == destination:
            self.successes += 1

        print "="*80
        print "Current Iteration: {}".format(self.current_iteration)
        print "     state                    = {}".format(self.state)
        print "     total reward             = {}".format(sum(self.rewards))
        print "     avg points per iteration = {}".format(sum(self.rewards) / float(self.current_iteration))
        print "     successes                = {}".format(self.successes)

def run():
    """Run the agent for a finite number of trials."""

    # Set up environment and agent
    e = Environment()  # create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent)  # create agent
    e.set_primary_agent(a, enforce_deadline=True)  # specify agent to track
    # NOTE: You can set enforce_deadline=False while debugging to allow longer trials

    # Now simulate it
    sim = Simulator(e, update_delay=0, display=False)  # create simulator (uses pygame when display=True, if available)
    # NOTE: To speed up simulation, reduce update_delay and/or set display=False

    sim.run(n_trials=100)  # run for a specified number of trials
    # NOTE: To quit midway, press Esc or close pygame window, or hit Ctrl+C on the command-line

if __name__ == '__main__':
    run()
