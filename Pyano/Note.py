import pygame
import Config

class Note():
    def __init__(self , midiNum , centerX, width, startY, is_white):
        self.midi = midiNum

        self.width = width * 0.8 if is_white else width
        self.height = 0

        self.x = centerX - (self.width/2)
        self.y = startY

        self.color = Config.NOTE_WHITE_COLOR if is_white else Config.NOTE_BLACK_COLOR

        self.isHeld = True

    def release(self):
        self.isHeld = False

    def updateRecording(self, distance):
        if(self.isHeld == True):
            self.y -= distance
            self.height += distance
        else:
            self.y -= distance

    def updatePlayBacking(self, distance):
        self.y += distance


            
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))