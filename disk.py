import numpy as np
import pygame


class Disk:
    def __init__(self, color, radius, initial_position):
        self.color = color
        self.radius = radius
        self.position = np.array(initial_position, dtype=float)
        self.speed = np.array([0.0, 0.0], dtype=float)

    def reset(self, initial_position):
        self.position = np.array(initial_position, dtype=float)
        self.speed = np.array([0.0, 0.0], dtype=float)

    def update(self, delta_time):
        self.position += self.speed * delta_time

    def check_collision_with_wall(self, table_rect):
        left = table_rect.left
        right = table_rect.right
        top = table_rect.top
        bottom = table_rect.bottom

        if self.position[0] - self.radius < left:
            self.position[0] = left + self.radius
            self.speed[0] *= -1
        elif self.position[0] + self.radius > right:
            self.position[0] = right - self.radius
            self.speed[0] *= -1

        if self.position[1] - self.radius < top:
            self.position[1] = top + self.radius
            self.speed[1] *= -1
        elif self.position[1] + self.radius > bottom:
            self.position[1] = bottom - self.radius
            self.speed[1] *= -1

    def check_collision_with_player(self, player):
        distance_squared = np.sum((self.position - player.position)**2)
        radii_sum_squared = (self.radius + player.radius)**2

        if distance_squared <= radii_sum_squared:
            collision_normal = (self.position - player.position) / np.sqrt(distance_squared)
            relative_speed = self.speed - player.speed
            impulse_scalar = (-(1 + 0.95) * np.dot(relative_speed, collision_normal)) / \
                             (np.dot(collision_normal, collision_normal) * 2)

            impulse = impulse_scalar * collision_normal
            self.speed += impulse

            overlap = 0.5 * (np.sqrt(radii_sum_squared) - np.sqrt(distance_squared)) * collision_normal
            self.position += overlap
            player.position -= overlap
            return True
        return False

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.position[0]), int(self.position[1])), self.radius)
