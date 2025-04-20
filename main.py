import sys
from logging import DEBUG

import cv2
import pygame
import mediapipe as mp

DEBUG = True

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
        
        pygame.display.set_caption("Hand Air Hockey")
        
        # Tavolo
        padding = 20
        self.tab_w = self.dis_w - padding * 2
        self.tab_h = self.dis_h - padding * 2
        self.tab_x = padding
        self.tab_y = padding
        self.table = pygame.Rect(self.tab_x, self.tab_y, self.tab_w, self.tab_h)
        
        # Porte
        self.doo_w = 10
        self.doo_h = self.tab_h // 3
        self.doo_y = self.tab_y + self.tab_h // 2 - self.doo_h // 2
        
        self.left_door = pygame.Rect(
            self.tab_x - self.doo_w,
            self.doo_y,
            self.doo_w,
            self.doo_h
        )
        
        self.right_door = pygame.Rect(
            self.tab_x + self.tab_w,
            self.doo_y,
            self.doo_w,
            self.doo_h
        )
        
        # Giocatori
        self.plr_r = 40 # Raggio del disco
        self.plr1_pos = [
            self.tab_x + self.tab_w // 4,
            self.tab_y + self.tab_h // 2
        ]
        self.plr2_pos = [
            self.tab_x + self.tab_w * 3 // 4,
            self.tab_y + self.tab_h // 2
        ]
        
        
    def draw(self):
        s = pygame.Surface((self.tab_w, self.tab_h), pygame.SRCALPHA)
        s.fill((255, 255, 255, 100))  # White with alpha
        self.screen.blit(s, (self.tab_x, self.tab_y))

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
        
        # Camera
        if self.camera_bg is not None:
            cam_s = pygame.Surface((self.dis_w, self.dis_h), pygame.SRCALPHA)
            cam_s.blit(self.camera_bg, (0, 0))
            cam_s.set_alpha(150)
            self.screen.blit(cam_s, (0, 0))
            
            if self.mp_hand_landmarks:
                for hand_landmarks in self.mp_hand_landmarks:
                    # Disegna i dischi dei giocatori
                    # calculate the speed of the hand
                    plr_x = int((hand_landmarks.landmark[0].x + hand_landmarks.landmark[9].x) * self.dis_w // 2)
                    plr_y = int((hand_landmarks.landmark[0].y + hand_landmarks.landmark[9].y) * self.dis_h // 2)
                    
                    if plr_x < self.dis_w // 2:
                        color = (255, 0, 0)
                    else:
                        color = (0, 0, 255)
                        
                    pygame.draw.circle(
                        self.screen,
                        color,
                        (plr_x, plr_y),
                        self.plr_r
                    )
                    
                    if DEBUG: # Mostra i punti delle mani solo in DEBUG
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
            frame = cv2.resize(frame, (self.dis_w, self.dis_h))
            self.camera_bg = pygame.surfarray.make_surface(frame.swapaxes(0, 1))

            mp_result = self.hands.process(frame)

            if mp_result.multi_hand_landmarks:
                self.mp_hand_landmarks = mp_result.multi_hand_landmarks
            else: 
                self.mp_hand_landmarks = None
            
            self.draw()

        
        
if __name__ == "__main__":
    game = AirHockey()
    game.run()