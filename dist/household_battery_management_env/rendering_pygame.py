import pygame
import math
import random
from typing import Optional, Dict, Any
from .domain import BatteryAction, WeatherCondition, TariffBlock

class ShowcaseRenderWindow:
    """High-polish Pygame-based showcase visualization."""
    def __init__(self, width=1024, height=600):
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Household Battery Management Showcase")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 18, bold=True)
        self.large_font = pygame.font.SysFont("Arial", 24, bold=True)
        
        self.paused = False
        self.speed_factor = 1.0
        self.particles = []
        self.callouts = []
        
        # Node positions
        self.nodes = {
            "pv": (200, 150),
            "battery": (200, 450),
            "house": (512, 300),
            "grid": (824, 300)
        }

    def _draw_sky(self, hour: float, weather: WeatherCondition):
        # Determine sky color based on hour (0-24)
        if 6 <= hour < 18: # Day
            base_color = (135, 206, 235) if weather == WeatherCondition.CLEAR else (100, 100, 120)
        else: # Night
            base_color = (20, 24, 50)
            
        self.screen.fill(base_color)
        
        # Draw Sun/Moon
        angle = (hour - 6) * (math.pi / 12)
        center_x, center_y = 512, 600
        radius = 500
        x = center_x + radius * math.cos(angle + math.pi)
        y = center_y + radius * math.sin(angle + math.pi)
        
        if 6 <= hour < 18:
            pygame.draw.circle(self.screen, (255, 255, 0), (int(x), int(y)), 30)
        else:
            pygame.draw.circle(self.screen, (200, 200, 200), (int(x), int(y)), 20)

    def _spawn_particles(self, start_key, end_key, magnitude):
        if magnitude <= 0: return
        start = self.nodes[start_key]
        end = self.nodes[end_key]
        count = int(magnitude * 10)
        for _ in range(count):
            if random.random() < 0.1:
                self.particles.append({
                    "pos": list(start),
                    "target": end,
                    "speed": random.uniform(2, 5),
                    "color": (255, 255, 255)
                })

    def update(self, state: Dict[str, Any]):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE: self.paused = not self.paused
                if event.key == pygame.K_PLUS or event.key == pygame.K_KP_PLUS: self.speed_factor *= 1.2
                if event.key == pygame.K_MINUS or event.key == pygame.K_KP_MINUS: self.speed_factor /= 1.2

        if self.paused: return

        self._draw_sky(state['hour'], state['weather'])
        
        # Draw Nodes
        for name, pos in self.nodes.items():
            color = (80, 80, 80)
            if name == "battery":
                charge_pct = state['charge_pct']
                color = (int(255*(1-charge_pct)), int(255*charge_pct), 50)
            pygame.draw.rect(self.screen, color, (pos[0]-40, pos[1]-40, 80, 80), border_radius=10)
            lbl = self.font.render(name.upper(), True, (255, 255, 255))
            self.screen.blit(lbl, (pos[0]-30, pos[1]+45))

        # Handle flows
        if state['pv'] > 0: self._spawn_particles("pv", "house", state['pv'])
        if state['action'] == BatteryAction.CHARGE: self._spawn_particles("house", "battery", 0.5)
        if state['action'] == BatteryAction.DISCHARGE: self._spawn_particles("battery", "house", 0.5)
        if state['grid_kwh'] > 0: self._spawn_particles("grid", "house", state['grid_kwh'])
        elif state['grid_kwh'] < 0: self._spawn_particles("house", "grid", abs(state['grid_kwh']))

        # Update & Draw Particles
        for p in self.particles[:]:
            dx = p['target'][0] - p['pos'][0]
            dy = p['target'][1] - p['pos'][1]
            dist = math.sqrt(dx**2 + dy**2)
            if dist < 5:
                self.particles.remove(p)
            else:
                p['pos'][0] += (dx/dist) * p['speed']
                p['pos'][1] += (dy/dist) * p['speed']
                pygame.draw.circle(self.screen, p['color'], (int(p['pos'][0]), int(p['pos'][1])), 3)

        # Panel
        pygame.draw.rect(self.screen, (30, 30, 30), (750, 20, 250, 200), border_radius=15)
        texts = [
            f"Reward: {state['reward']:.4f}",
            f"Action: {state['action'].name}",
            f"Tariff Block: {state['block']}",
            f"Cost: {state['cost']:.4f} EUR"
        ]
        for i, t in enumerate(texts):
            img = self.font.render(t, True, (0, 255, 200))
            self.screen.blit(img, (770, 40 + i*30))

        pygame.display.flip()
        self.clock.tick(30)