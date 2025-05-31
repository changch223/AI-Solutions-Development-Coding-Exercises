import gymnasium as gym
import numpy as np
import matplotlib.pyplot as plt

env = gym.make('FrozenLake-v1', render_mode='human', is_slippery=True)


def heuristic_agent(env, episodes=5):
    """An agent with a simple strategy: always try to move towards goal"""
    successes = 0

    # Simple heuristic: prefer right and down movements (goal is bottom-right)
    action_preferences = [1, 2]  # Down=1, Right=2 (Up=0, Left=3)

    for episode in range(episodes):
        state, _ = env.reset()
        total_reward = 0
        steps = 0

        print(f"\n--- Episode {episode + 1} ---")

        while True:
            # Choose action based on simple heuristic
            if np.random.random() < 0.8:  # 80% of time follow heuristic
                action = np.random.choice(action_preferences)
            else:  # 20% of time explore
                action = env.action_space.sample()

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

    print(f"\n📊 Heuristic Agent Results: {successes}/{episodes} successes ({successes/episodes*100:.1f}%)")
    return successes / episodes

# Test heuristic agent
heuristic_success_rate = heuristic_agent(env)
