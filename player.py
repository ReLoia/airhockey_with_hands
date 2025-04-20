import numpy as np
import pygame


class Player:
    def __init__(self, color, radius):
        self.color = color
        self.radius = radius
        self.position = np.array([0.0, 0.0])
        self.previous_position = np.array([0.0, 0.0])
        self.speed = np.array([0.0, 0.0])
        self.score = 0

    def update_position(self, new_position):
        self.previous_position = self.position.copy()
        self.position = np.array(new_position, dtype=float)
        self.calculate_speed()

    def calculate_speed(self):
        delta_time = 1 / 30.0
        self.speed = (self.position - self.previous_position) / delta_time

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.position[0]), int(self.position[1])), self.radius)
