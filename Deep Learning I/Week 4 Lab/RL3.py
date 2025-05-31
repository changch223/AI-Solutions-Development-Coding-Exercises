import gymnasium as gym
import numpy as np
import matplotlib.pyplot as plt

env = gym.make('FrozenLake-v1', render_mode='human', is_slippery=True)

def q_learning_with_tracking(env, episodes=5, alpha=0.1, gamma=0.99, epsilon=0.1):
    """Q-learning with detailed tracking for educational purposes"""

    # Initialize Q-table
    Q = np.zeros([env.observation_space.n, env.action_space.n])

    # Tracking variables
    episode_rewards = []
    episode_lengths = []
    success_rate_window = []

    print("🚀 Starting Q-Learning Training...")
    print(f"Parameters: α={alpha}, γ={gamma}, ε={epsilon}")

    for episode in range(episodes):
        state, _ = env.reset()
        total_reward = 0
        steps = 0
        done = False

        while not done:
            # ε-greedy action selection
            if np.random.uniform(0, 1) < epsilon:
                action = env.action_space.sample()  # Explore
                action_type = "explore"
            else:
                action = np.argmax(Q[state])  # Exploit
                action_type = "exploit"

            # Take action and observe result
            next_state, reward, done, _, _ = env.step(action)

            # Store old Q-value for comparison
            old_q_value = Q[state, action]

            # Q-learning update
            Q[state, action] = Q[state, action] + alpha * (
                reward + gamma * np.max(Q[next_state]) - Q[state, action]
            )

            # Track the update
            q_update = Q[state, action] - old_q_value

            # Detailed logging for first few episodes
            if episode < 3:
                print(f"Episode {episode+1}, Step {steps+1}:")
                print(f"  State: {state}, Action: {action} ({action_type})")
                print(f"  Reward: {reward}, Next State: {next_state}")
                print(f"  Q-update: {old_q_value:.3f} → {Q[state, action]:.3f} (Δ{q_update:+.3f})")

            total_reward += reward
            steps += 1
            state = next_state

        # Track episode statistics
        episode_rewards.append(total_reward)
        episode_lengths.append(steps)
        success_rate_window.append(1 if total_reward > 0 else 0)

        # Print progress every 100 episodes
        if (episode + 1) % 100 == 0:
            recent_success_rate = np.mean(success_rate_window[-100:]) * 100
            avg_reward = np.mean(episode_rewards[-100:])
            avg_length = np.mean(episode_lengths[-100:])

            print(f"Episode {episode+1}: Success Rate: {recent_success_rate:.1f}%, "
                  f"Avg Reward: {avg_reward:.2f}, Avg Length: {avg_length:.1f}")

    return Q, episode_rewards, episode_lengths

# Train the agent
print("=" * 50)
Q_learned, rewards, lengths = q_learning_with_tracking(env)
print("=" * 50)




def visualize_learning(rewards, lengths):
    """Create visualizations of the learning process"""

    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15, 5))

    # Success rate over time
    window_size = 100
    success_rates = []
    for i in range(len(rewards)):
        start_idx = max(0, i - window_size + 1)
        window_rewards = rewards[start_idx:i+1]
        success_rate = np.mean([1 if r > 0 else 0 for r in window_rewards]) * 100
        success_rates.append(success_rate)

    ax1.plot(success_rates)
    ax1.set_title('Success Rate Over Time')
    ax1.set_xlabel('Episode')
    ax1.set_ylabel('Success Rate (%)')
    ax1.grid(True)

    # Average reward over time
    avg_rewards = []
    for i in range(len(rewards)):
        start_idx = max(0, i - window_size + 1)
        avg_rewards.append(np.mean(rewards[start_idx:i+1]))

    ax2.plot(avg_rewards)
    ax2.set_title('Average Reward Over Time')
    ax2.set_xlabel('Episode')
    ax2.set_ylabel('Average Reward')
    ax2.grid(True)

    # Episode length distribution
    ax3.hist(lengths, bins=30, alpha=0.7, edgecolor='black')
    ax3.set_title('Distribution of Episode Lengths')
    ax3.set_xlabel('Steps to Complete')
    ax3.set_ylabel('Frequency')
    ax3.grid(True)

    plt.tight_layout()
    plt.show()

# Visualize the learning process
visualize_learning(rewards, lengths)


def analyze_learned_policy(Q, env):
    """Analyze what the agent learned"""

    print("🔍 Analyzing the Learned Policy...")
    print("\nQ-Table (rounded to 3 decimal places):")
    print("Actions: [Up, Down, Left, Right]")
    print("-" * 40)

    action_names = ['Up ↑', 'Down ↓', 'Left ←', 'Right →']

    for state in range(env.observation_space.n):
        print(f"State {state:2d}: {Q[state].round(3)} → Best: {action_names[np.argmax(Q[state])]}")

    # Test the learned policy
    print("\n🎮 Testing Learned Policy (5 episodes):")

    successes = 0
    for episode in range(5):
        state, _ = env.reset()
        total_reward = 0
        steps = 0
        path = [state]

        print(f"\nEpisode {episode + 1}:")

        while True:
            action = np.argmax(Q[state])
            next_state, reward, done, _, _ = env.step(action)
            path.append(next_state)
            total_reward += reward
            steps += 1

            print(f"  Step {steps}: {state} → {action_names[action]} → {next_state}")

            if done:
                if reward > 0:
                    print(f"  🎉 SUCCESS in {steps} steps!")
                    successes += 1
                else:
                    print(f"  💀 Failed after {steps} steps")
                print(f"  Path: {' → '.join(map(str, path))}")
                break

            state = next_state

    final_success_rate = successes / 5 * 100
    print(f"\n📊 Final Policy Success Rate: {final_success_rate}%")

    return final_success_rate

# Analyze the learned policy
final_success_rate = analyze_learned_policy(Q_learned, env)
