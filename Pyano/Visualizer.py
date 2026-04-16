import pygame
import Config
from Note import Note


class Visualizer():
    def __init__(self, screen):
        self.sceneID = 1
        self.width = Config.SCREEN_WIDTH
        self.height = Config.SCREEN_HEIGHT
        self.screen = screen
        self.popUpFont = Config.SAVE_POPUP_FONT
        self.titleFont = Config.VIS_TITLE_FONT

        self.song = None
        self.speedMultiplier = 0

        self.keyboardTopY = self.height - Config.KEYBOARD_HEIGHT

        self.keys = self.buildKeyboard()

        self.activeNotes = {}
        self.floatingNotes = []
        self.whiteNotes = []
        self.blackNotes = []

        #TOPBAR BUTTONS
        self.recordButton = pygame.Rect(Config.RECORD_BUTTON_RECT)
        self.toSongsButton = pygame.Rect(Config.TO_SONGS_BUTTON_RECT)
        
        size = Config.PLAYBACK_BUTTONS_SIZE
        buttony = Config.PLAYBACK_BUTTONS_Y
        spacing = Config.PLAYBACK_BUTTONS_SPACING

        self.playButton = pygame.Rect((self.width//2) - (size//2), buttony, size , size)
        self.rewindButton = pygame.Rect(self.playButton.left - size - spacing, buttony, size , size)
        self.speedButton = pygame.Rect(self.rewindButton.left - size - spacing, buttony, size, size)
        self.forwardButton = pygame.Rect(self.playButton.right + spacing, buttony, size , size)
        self.cancelButton = pygame.Rect(self.forwardButton.right + spacing, buttony, size , size)
        self.muteButton = pygame.Rect(self.cancelButton.right + spacing, buttony, size , size)
        self.timeBar = pygame.Rect(self.speedButton.left - spacing, 55, 6*(size + spacing) + spacing, 3)

        self.popUpSave = pygame.Rect((self.width/2) - Config.SAVE_POPUP_WIDTH/2, (self.height/2)-Config.SAVE_POPUP_HEIGHT/2, 
                                    Config.SAVE_POPUP_WIDTH, Config.SAVE_POPUP_HEIGHT)
        self.yesButton = pygame.Rect(self.popUpSave.x + 30 , self.popUpSave.y + 90 , 
                                    Config.SAVE_BUTTON_WIDTH, Config.SAVE_BUTTON_HEIGHT)
        self.noButton = pygame.Rect(self.popUpSave.x + 170, self.popUpSave.y + 90, 
                                    Config.SAVE_BUTTON_WIDTH, Config.SAVE_BUTTON_HEIGHT)
        
        self.playAreaRect = pygame.Rect(0, Config.TOP_BAR_HEIGHT-5, self.width, self.keyboardTopY - Config.TOP_BAR_HEIGHT + 10)
        
        self.saveText = self.popUpFont.render("Save this recording?", True, Config.TEXT_COLOR)
        self.yesText = self.popUpFont.render("Yes", True, Config.TEXT_COLOR)
        self.noText = self.popUpFont.render("No", True, Config.TEXT_COLOR)
        
        self.showPopUp = False
        self.isRecording = False
        self.isLoaded = False
        self.isPlaying = False
        self.isMuted = False

    def isPopUp(self):
        return self.showPopUp
    
    def loadSong(self, song):
        self.isLoaded = True
        self.song = song
        self.titleText = self.titleFont.render(f"{self.song}", True, Config.TEXT_COLOR)

    def clearNotes(self):
        self.activeNotes.clear()
        self.floatingNotes.clear()
        self.whiteNotes.clear()
        self.blackNotes.clear()


    
    def buildKeyboard(self):
        keys = {}

        wKeyWidth = self.width / 52
        bKeyWidth = wKeyWidth * 0.65
        bKeyHeight = Config.KEYBOARD_HEIGHT * 0.7

        wId = 0
        for m in range(21,109):
            if (m%12) not in (1, 3, 6, 8, 10):
                xPos = wId * wKeyWidth
                keys[m] =  {
                          'type' : 'white',
                          'x' : xPos,
                          'y' : self.keyboardTopY,
                          'w' : wKeyWidth,          
                          'h' :  Config.KEYBOARD_HEIGHT,
                          'isPressed' : False,
                          'isCorrect' : False,               
                          'cx' : xPos + (wKeyWidth / 2)
                          }
                wId += 1
            
        wId = 0 
        for m in range(21, 109):
            if(m%12) not in (1,3,6,8,10):
                wId +=1
            else:
                cxPos = wId  * wKeyWidth
                keys[m] =  {
                          'type' : 'black',
                          'x' : cxPos - (bKeyWidth / 2),
                          'y' : self.keyboardTopY,
                          'w' : bKeyWidth,          
                          'h' : bKeyHeight,
                          'isPressed' : False,
                          'isCorrect' : False,               
                          'cx' : cxPos
                          }
        return keys


    ##invata asta----------------------
    def processMidi(self, msg):
        mn = msg.note
        if mn not in self.keys: return
        key_data = self.keys[mn]
        
        if msg.type == 'note_on' and msg.velocity > 0:
            key_data['isPressed'] = True
            if not self.isLoaded:
                isWhite = (key_data['type'] == 'white')
                newNote = Note(mn, key_data['cx'], key_data['w'], key_data['y'], isWhite)
                self.whiteNotes.append(newNote) if isWhite else self.blackNotes.append(newNote)
                self.activeNotes[mn] = newNote

        elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
            key_data['isPressed'] = False
            if not self.isLoaded and mn in self.activeNotes:
                note = self.activeNotes.pop(mn)
                note.release()
                self.floatingNotes.append(note)

    def updateNotes(self, distance):
        toDeleteNotes = []
        
        if not self.isLoaded:
            for note in self.activeNotes.values():
                note.updateRecording(distance)
            for note in self.floatingNotes:
                note.updateRecording(distance)
                if (note.y + note.height) < Config.TOP_BAR_HEIGHT:
                    toDeleteNotes.append(note)
        else:
            if self.isPlaying:

                for k in self.keys.values():
                    k['isCorrect'] = False

                for note in self.floatingNotes:
                    note.updatePlayBacking(distance)
                    if (note.y + note.height >= self.keyboardTopY and note.y < self.keyboardTopY):
                        self.keys[note.midi]['isCorrect'] = True

                    if (note.y > self.keyboardTopY):
                        toDeleteNotes.append(note)

        if toDeleteNotes:
            deleteSet = set(toDeleteNotes)
            self.floatingNotes = [n for n in self.floatingNotes if n not in deleteSet]
            self.whiteNotes = [n for n in self.whiteNotes if n not in deleteSet]
            self.blackNotes = [n for n in self.blackNotes if n not in deleteSet]


    
    def draw(self):
        # BACKGROUND
        self.screen.fill(Config.BG_COLOR)

        
        self.screen.set_clip(self.playAreaRect)
        # NOTES
        allNotes = self.whiteNotes + self.blackNotes
        for note in allNotes:
            note.draw(self.screen)

        self.screen.set_clip(None)

        # TOPBAR 
        pygame.draw.rect(self.screen, Config.TOP_BAR_COLOR, Config.TOP_BAR_RECT)

        recCX = self.recordButton.centerx
        recCY = self.recordButton.centery
        pygame.draw.circle(self.screen, Config.VERY_INTENSE_PURPLE if self.isRecording else Config.LIGHT_PURPLE, 
                          (recCX,recCY), 15)
        pygame.draw.circle(self.screen, Config.VERY_INTENSE_PURPLE if self.isRecording else Config.LIGHT_PURPLE, 
                          (recCX,recCY), 20, 3)
        

        pygame.draw.rect(self.screen, Config.LIGHT_PURPLE, 
                        (self.toSongsButton.left + 15, self.toSongsButton.centery - 10, self.toSongsButton.width - 25, 5),
                        border_radius=4)
        pygame.draw.rect(self.screen, Config.LIGHT_PURPLE, 
                        (self.toSongsButton.left + 15, self.toSongsButton.centery, self.toSongsButton.width - 25, 5),
                        border_radius=4)
        pygame.draw.rect(self.screen, Config.LIGHT_PURPLE, 
                        (self.toSongsButton.left + 15, self.toSongsButton.centery + 10, self.toSongsButton.width - 25, 5),
                        border_radius=4)
        
        if self.isLoaded:

            self.screen.blit(self.titleText, (self.playButton.centerx - (self.titleText.get_width()//2), self.playButton.top // 4))
            #BUTTONS 
            pygame.draw.rect(self.screen, Config.LIGHT_PURPLE, self.playButton, border_radius=4)
            pygame.draw.rect(self.screen, Config.LIGHT_PURPLE, self.rewindButton, border_radius=4)
            pygame.draw.rect(self.screen, Config.LIGHT_PURPLE, self.speedButton, border_radius=4)
            pygame.draw.rect(self.screen, Config.LIGHT_PURPLE, self.forwardButton, border_radius=4)
            pygame.draw.rect(self.screen, Config.LIGHT_PURPLE, self.cancelButton, border_radius=4)

            #PLAY
            trianglePoints = [(self.playButton.left + 10, self.playButton.top + 5), 
                              (self.playButton.left + 10, self.playButton.bottom - 5), 
                              (self.playButton.right - 5, self.playButton.centery)]
            if self.isPlaying:
                pygame.draw.line(self.screen, Config.WHITE, (self.playButton.left + 10, self.playButton.top + 5), (self.playButton.left + 10, self.playButton.bottom - 5), 4)
                pygame.draw.line(self.screen, Config.WHITE, (self.playButton.right - 10, self.playButton.top + 5), (self.playButton.right - 10, self.playButton.bottom - 5), 4)
            else:
                pygame.draw.polygon(self.screen, Config.WHITE, trianglePoints)
                
            
            
            #FORWARD
            f1Points = [(self.forwardButton.centerx, self.forwardButton.top + 5), 
                              (self.forwardButton.centerx, self.forwardButton.bottom - 5), 
                              (self.forwardButton.right - 5, self.forwardButton.centery)]
            f2Points = [(self.forwardButton.left + 5, self.forwardButton.top + 5), 
                              (self.forwardButton.left + 5, self.forwardButton.bottom - 5), 
                              (self.forwardButton.centerx, self.forwardButton.centery)]
            pygame.draw.polygon(self.screen, Config.WHITE, f1Points)
            pygame.draw.polygon(self.screen, Config.WHITE, f2Points)
            
            #REWIND
            r1Points = [(self.rewindButton.centerx, self.rewindButton.top + 5), 
                              (self.rewindButton.centerx, self.rewindButton.bottom - 5), 
                              (self.rewindButton.left + 5, self.rewindButton.centery)]
            r2Points = [(self.rewindButton.right - 5, self.rewindButton.top + 5), 
                              (self.rewindButton.right - 5, self.rewindButton.bottom - 5), 
                              (self.rewindButton.centerx, self.rewindButton.centery)]
            pygame.draw.polygon(self.screen, Config.WHITE, r1Points)
            pygame.draw.polygon(self.screen, Config.WHITE, r2Points)
            
            #CANCEL
            pygame.draw.line(self.screen, Config.WHITE, 
                             (self.cancelButton.left + 7, self.cancelButton.top + 5) , (self.cancelButton.right - 7, self.cancelButton.bottom - 5), 5)
            pygame.draw.line(self.screen, Config.WHITE, 
                             (self.cancelButton.left + 7, self.cancelButton.bottom - 5) , (self.cancelButton.right - 7, self.cancelButton.top + 5), 5)
            
            #SPEEDMULTIPLIER
            if self.speedMultiplier == 1.0:
                pygame.draw.circle(self.screen, Config.WHITE, (self.speedButton.centerx, self.speedButton.bottom - 7) , 3)
            elif self.speedMultiplier == 0.5:
                pygame.draw.circle(self.screen, Config.WHITE, (self.speedButton.centerx - 4, self.speedButton.bottom - 7) , 3)
                pygame.draw.circle(self.screen, Config.WHITE, (self.speedButton.centerx + 4, self.speedButton.bottom - 7) , 3)
            elif self.speedMultiplier == 0.25:
                pygame.draw.circle(self.screen, Config.WHITE, (self.speedButton.centerx - 8, self.speedButton.bottom - 7) , 3)
                pygame.draw.circle(self.screen, Config.WHITE, (self.speedButton.centerx + 8, self.speedButton.bottom - 7) , 3)
                pygame.draw.circle(self.screen, Config.WHITE, (self.speedButton.centerx, self.speedButton.bottom - 7) , 3)
            

            #MUTE
            pygame.draw.rect(self.screen, Config.WHITE, (self.muteButton.left, self.muteButton.centery - 5, 8, 10))
            pygame.draw.polygon(self.screen, Config.WHITE, [
                (self.muteButton.left + 8, self.muteButton.centery - 5),
                (self.muteButton.centerx, self.muteButton.top + 5),
                (self.muteButton.centerx, self.muteButton.bottom - 5),
                (self.muteButton.left + 8, self.muteButton.centery + 5)
            ])

            if self.isMuted:
                pygame.draw.line(self.screen, Config.WHITE, (self.muteButton.centerx + 5, self.muteButton.top + 8), (self.muteButton.right - 2, self.muteButton.bottom - 8), 3)
                pygame.draw.line(self.screen, Config.WHITE, (self.muteButton.right - 2, self.muteButton.top + 8), (self.muteButton.centerx + 5, self.muteButton.bottom - 8), 3)
            else:
                pygame.draw.arc(self.screen, Config.WHITE, (self.muteButton.centerx - 3, self.muteButton.top + 5, 12, 20), -1.0, 1.0, 2)
                pygame.draw.arc(self.screen, Config.WHITE, (self.muteButton.centerx - 4, self.muteButton.top, 18, 30), -1.0, 1.0, 2)

            #TIMEBAR
            pygame.draw.rect(self.screen, Config.WHITE, self.timeBar, border_radius = 7)
            


        # KEYBOARD
        for m, k in self.keys.items():
            
            if k['type'] == "white":
                if k['isPressed']:
                    if not self.isLoaded:
                        color = Config.KEY_WHITE_PRESSED
                    else:
                        color = Config.KEY_WHITE_CORRECT if k['isCorrect'] else Config.KEY_WHITE_WRONG
                else:
                    color = Config.KEY_WHITE_IDLE
                pygame.draw.rect(self.screen, color, (k['x'], k['y'], k['w'], k['h']))
                pygame.draw.rect(self.screen, Config.KEY_WHITE_OUTLINE, (k['x'], k['y'], k['w'], k['h']), 1)

            elif k['type'] == "black":
                if k['isPressed']:
                    if not self.isLoaded:
                        color = Config.KEY_BLACK_PRESSED
                    else:
                        color = Config.KEY_BLACK_CORRECT if k['isCorrect'] else Config.KEY_BLACK_WRONG
                else:
                    color = Config.KEY_BLACK_IDLE
                    
                pygame.draw.rect(self.screen, color, (k['x'], k['y'], k['w'], k['h']))
                

        # SAVE POPUP
        if self.showPopUp:

            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150)) # Black with 150/255 transparency
            self.screen.blit(overlay, (0, 0))

            pygame.draw.rect(self.screen, Config.SAVE_POPUP_COLOR, self.popUpSave, border_radius=12)
            pygame.draw.rect(self.screen, Config.WHITE, self.popUpSave, 1, border_radius=12)
            self.screen.blit(self.saveText, (self.popUpSave.centerx - self.saveText.get_width()//2, self.popUpSave.y + 25))

            pygame.draw.rect(self.screen, Config.PURPLE, self.yesButton, border_radius=6) 
            pygame.draw.rect(self.screen, Config.WHITE, self.yesButton, 1, border_radius=6) 
            pygame.draw.rect(self.screen, Config.DARK_PURPLE, self.noButton, border_radius=6)
            pygame.draw.rect(self.screen, Config.WHITE, self.noButton, 1, border_radius=6)
            self.screen.blit(self.yesText, (self.yesButton.centerx - self.yesText.get_width()//2, self.yesButton.centery - self.yesText.get_height()//2))
            self.screen.blit(self.noText, (self.noButton.centerx - self.noText.get_width()//2, self.noButton.centery - self.noText.get_height()//2))
        pygame.display.flip()

