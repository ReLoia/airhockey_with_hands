import sys

import cv2
import pygame
import mediapipe as mp
import numpy as np

from player import Player
from disk import Disk

DEBUG = False

class AirHockey:
    def __init__(self):
        pygame.init()

        # Camera
        self.cam = cv2.VideoCapture(0)
        if not self.cam.isOpened():
            print("Error: Could not open video.")
            return

        # Tracciamento mani
        mp_hands = mp.solutions.hands
        self.hands = mp_hands.Hands(static_image_mode=False,
                                    max_num_hands=2,
                                    min_detection_confidence=0.5,
                                    min_tracking_confidence=0.5)
        self.mp_drawing = mp.solutions.drawing_utils

        self.camera_bg = None
        self.mp_hand_landmarks = None

        self.cam_w = int(self.cam.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.cam_h = int(self.cam.get(cv2.CAP_PROP_FRAME_HEIGHT))

        display_ratio = self.cam_w / self.cam_h

        self.dis_w = 1000
        self.dis_h = int(self.dis_w / display_ratio)
        self.screen = pygame.display.set_mode((self.dis_w, self.dis_h))

        self.camera_surface = pygame.Surface((self.dis_w, self.dis_h), pygame.SRCALPHA)

        pygame.display.set_caption("Hand Air Hockey")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 86)

        # Tavolo
        padding = 20
        self.tab_w = self.dis_w - padding * 2
        self.tab_h = self.dis_h - padding * 2
        self.tab_x = padding 
        self.tab_y = padding
        self.table = pygame.Rect(self.tab_x, self.tab_y, self.tab_w, self.tab_h)
        self.table_surface = pygame.Surface((self.tab_w, self.tab_h), pygame.SRCALPHA)
        self.table_surface.fill((255, 255, 255, 100))

        # Porte
        self.doo_w = 10
        self.doo_h = self.tab_h // 3
        self.doo_y = self.tab_y + self.tab_h // 2 - self.doo_h // 2

        self.left_door = pygame.Rect(
            self.tab_x,                 # left
            self.doo_y,                 # top
            self.doo_w,                 # w
            self.doo_h                  # h
        )

        self.right_door = pygame.Rect(
            self.tab_x + self.tab_w - self.doo_w,
            self.doo_y,
            self.doo_w,
            self.doo_h
        )

        # Giocatori
        self.plr_r = 40 # Raggio del disco
        self.plr1 = Player((255, 0, 0), self.plr_r)
        self.plr1.position = np.array([self.tab_x + self.tab_w // 4, self.tab_y + self.tab_h // 2], dtype=float)
        self.plr2 = Player((0, 0, 255), self.plr_r)
        self.plr2.position = np.array([self.tab_x + self.tab_w * 3 // 4, self.tab_y + self.tab_h // 2], dtype=float)

        # Disco
        self.disk_r = 25
        initial_disk_position = [self.tab_x + self.tab_w // 2, self.tab_y + self.tab_h // 2]
        self.disk = Disk((0, 0, 0), self.disk_r, initial_disk_position)
        
        initial_angle = np.random.uniform(0, 2 * np.pi)
        self.disk.speed = np.array([np.cos(initial_angle), np.sin(initial_angle)]) * self.disk.speed

    def check_goal(self):
        disk_center_x = self.disk.position[0]
        disk_center_y = self.disk.position[1]

        if self.left_door.right > disk_center_x - self.disk.radius and self.left_door.top < disk_center_y < self.left_door.bottom:
            self.plr2.score += 1
            self.disk.reset([self.tab_x + self.tab_w // 2, self.tab_y + self.tab_h // 2])
            return True
        elif self.right_door.left < disk_center_x + self.disk.radius and \
                self.right_door.top < disk_center_y < self.right_door.bottom:
            self.plr1.score += 1
            self.disk.reset([self.tab_x + self.tab_w // 2, self.tab_y + self.tab_h // 2])
            return True
        return False

    def draw_score(self):
        score_p1_text = self.font.render(str(self.plr1.score), True, self.plr1.color)
        score_p2_text = self.font.render(str(self.plr2.score), True, self.plr2.color)
        self.screen.blit(score_p1_text, (self.tab_x + self.tab_w // 4 - score_p1_text.get_width() // 2, 20))
        self.screen.blit(score_p2_text, (self.tab_x + self.tab_w * 3 // 4 - score_p2_text.get_width() // 2, 20))

    def draw(self):
        self.screen.blit(self.table_surface, (self.tab_x, self.tab_y))

        # Linea centrale
        pygame.draw.line(
            self.screen,
            (0, 0, 0, 150),
            (self.tab_x + self.tab_w // 2, self.tab_y),
            (self.tab_x + self.tab_w // 2, self.tab_y + self.tab_h),
            5
        )

        # Bordi
        pygame.draw.rect(
            self.screen,
            (0, 0, 0),
            self.table,
            5
        )

        # Porte
        pygame.draw.rect(self.screen, (0, 255, 0), self.left_door)
        pygame.draw.rect(self.screen, (0, 255, 0), self.right_door)

        # Giocatori
        self.plr1.draw(self.screen)
        self.plr2.draw(self.screen)

        # Disco
        self.disk.draw(self.screen)

        # Punteggi
        self.draw_score()

        # Camera
        if self.camera_bg is not None:
            self.screen.blit(self.camera_surface, (0, 0))

            if DEBUG:
                pygame.draw.line(
                    self.screen,
                    self.plr1.color,
                    self.plr1.position,
                    (
                        self.plr1.position[0] + self.plr1.speed[0] * 10,
                        self.plr1.position[1] + self.plr1.speed[1] * 10
                    ),
                    3
                )
                
                pygame.draw.line(
                    self.screen,
                    self.plr2.color,
                    self.plr2.position,
                    (
                        self.plr2.position[0] + self.plr2.speed[0] * 10,
                        self.plr2.position[1] + self.plr2.speed[1] * 10
                    ),
                    3
                )

                if self.mp_hand_landmarks: # Mostra i punti delle mani solo in DEBUG
                    for hand_landmarks in self.mp_hand_landmarks:
                        for landmark in hand_landmarks.landmark:
                            x = int(landmark.x * self.dis_w)
                            y = int(landmark.y * self.dis_h)
                            if x < self.dis_w // 2:
                                color = (255, 0, 0)
                            else:
                                color = (0, 0, 255)
                            pygame.draw.circle(self.screen, color, (x, y), 5)

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            delta_time = self.clock.tick(60) / 1000.0
            
            dis_w = self.dis_w
            dis_h = self.dis_h
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.cam.release()
                    pygame.quit()
                    sys.exit()

            ret, frame = self.cam.read()
            if not ret:
                print("Error: Could not read frame.")
                break

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.flip(frame, 1)
            frame = cv2.resize(frame, (dis_w, dis_h))
            self.camera_bg = pygame.surfarray.make_surface(frame.swapaxes(0, 1))

            self.camera_surface.blit(self.camera_bg, (0, 0))
            self.camera_surface.set_alpha(150)

            mp_result = self.hands.process(frame)
            self.mp_hand_landmarks = mp_result.multi_hand_landmarks

            found_player1 = False
            found_player2 = False

            if self.mp_hand_landmarks:
                for hand_landmarks in self.mp_hand_landmarks:
                    hand_x = int((hand_landmarks.landmark[0].x + hand_landmarks.landmark[9].x) * self.dis_w // 2)
                    hand_y = int((hand_landmarks.landmark[0].y + hand_landmarks.landmark[9].y) * self.dis_h // 2)
                    hand_pos = np.array([hand_x, hand_y], dtype=float)

                    if hand_x < self.dis_w // 2 and not found_player1:
                        self.plr1.update_position(hand_pos)
                        found_player1 = True
                    elif hand_x >= self.dis_w // 2 and not found_player2:
                        self.plr2.update_position(hand_pos)
                        found_player2 = True

                    if found_player1 and found_player2:
                        break

            self.disk.update(delta_time)

            self.disk.check_collision_with_wall(self.table)
            self.disk.check_collision_with_player(self.plr1)
            self.disk.check_collision_with_player(self.plr2)

            self.check_goal()

            self.draw()

if __name__ == "__main__":
    game = AirHockey()
    game.run()