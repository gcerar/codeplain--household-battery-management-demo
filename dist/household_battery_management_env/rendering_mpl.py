import numpy as np
from typing import Optional

class LiveRenderWindow:
    """Basic Matplotlib-based live visualization."""
    def __init__(self):
        import matplotlib.pyplot as plt
        plt.ion()
        self.fig, self.axs = plt.subplots(2, 1, figsize=(8, 6))
        self.charge_history = []
        self.reward_history = []
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def update(self, charge: float, reward: float, step: int):
        import matplotlib.pyplot as plt
        self.charge_history.append(charge)
        self.reward_history.append(reward)
        
        # Keep window of last 100 steps
        window = 100
        data_c = self.charge_history[-window:]
        data_r = self.reward_history[-window:]
        
        self.axs[0].clear()
        self.axs[0].plot(data_c, color='blue')
        self.axs[0].set_title("Battery Charge (kWh)")
        
        self.axs[1].clear()
        self.axs[1].plot(data_r, color='green')
        self.axs[1].set_title("Reward")
        
        plt.pause(0.001)