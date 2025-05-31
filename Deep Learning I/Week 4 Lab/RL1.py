import gymnasium as gym
import numpy as np
import matplotlib.pyplot as plt

# Create the environment
env = gym.make('FrozenLake-v1', render_mode='human', is_slippery=True)

def random_agent(env, episodes=5):
    """An agent that chooses actions randomly"""
    successes = 0

    for episode in range(episodes):
        state, _ = env.reset()
        total_reward = 0
        steps = 0

        print(f"\n--- Episode {episode + 1} ---")

        while True:
            # Choose random action
            action = env.action_space.sample()

            # Take action
            next_state, reward, done, _, _ = env.step(action)
            total_reward += reward
            steps += 1

            print(f"Step {steps}: State {state} → Action {action} → State {next_state}, Reward: {reward}")

            if done:
                if reward > 0:
                    print(f"🎉 SUCCESS! Reached goal in {steps} steps!")
                    successes += 1
                else:
                    print(f"💀 Failed after {steps} steps")
                break

            state = next_state

    print(f"\n📊 Random Agent Results: {successes}/{episodes} successes ({successes/episodes*100:.1f}%)")
    return successes / episodes

# Test random agent
random_success_rate = random_agent(env)
