from stable_baselines3 import PPO

def create_rl_agent(env):

    model = PPO(
        "MlpPolicy",
        env,
        verbose=1
    )

    return model