from collections import deque
import pygame
import Config
import os

class SongsMenu():
    def __init__(self, screen):
        self.sceneID = 2
        self.width = Config.SCREEN_WIDTH
        self.height = Config.SCREEN_HEIGHT
        self.screen = screen

        self.titleFont = Config.SONGS_TITLE_FONT
        self.titleText = self.titleFont.render("Select a recording", True, Config.TEXT_COLOR)
        self.listFont = Config.SONGS_LIST_FONT
        

        self.songs = []

        self.container = pygame.Rect(Config.SONGS_CONTAINER_RECT)
        self.backButton = pygame.Rect(Config.SONGS_BACK_BUTTON_RECT)

        self.selectedSong = None

        self.loadSongs()

        self.scrollY = 0
        self.minScroll = 0
        self.maxScroll = min(0, Config.SONGS_CONTAINER_HEIGHT - (len(self.songs) * Config.SONG_ITEM_TOTAL_HEIGHT))


    def loadSongs(self):
        if os.path.exists('saved'):
            for filename in os.listdir('saved'):
                if filename.endswith('.mid'):
                    self.songs.append(filename)
        else:
            os.makedirs('saved')
        self.songs.sort(key = lambda filename: os.path.getmtime(os.path.join('saved', filename)))
        
    def addSong(self, song):
        self.songs.append(song)
        self.maxScroll -= Config.SONG_ITEM_TOTAL_HEIGHT

    def removeSong(self, song):
        filePath = os.path.join('saved', song)
        if os.path.exists(filePath):
            os.remove(filePath)

        self.songs.remove(song)
        self.maxScroll += Config.SONG_ITEM_TOTAL_HEIGHT
        self.clampScroll()

        self.selectedSong = None

    def resetScroll(self):
        self.scrollY = 0
    
    def clampScroll(self):
        self.scrollY = min(self.minScroll, max(self.maxScroll, self.scrollY))

    def handleClick(self, pos):
        startIndex = int(abs(self.scrollY) // Config.SONG_ITEM_TOTAL_HEIGHT)
        visibleCount = abs(self.container.height // Config.SONG_ITEM_TOTAL_HEIGHT) + 2
        endIndex = min(len(self.songs), startIndex + visibleCount)

        for i in range(startIndex, endIndex):
            actualIndex = (len(self.songs) - 1) - i
            song = self.songs[actualIndex]

            targetY = self.container.y + Config.SONG_ITEM_SPACING + (i * Config.SONG_ITEM_TOTAL_HEIGHT) + self.scrollY

            itemRect = pygame.Rect(self.container.x + Config.SONG_ITEM_SPACING, targetY,
                        self.container.width - (2 * Config.SONG_ITEM_SPACING), Config.SONG_ITEM_HEIGHT)
                
            buttonY = itemRect.centery - (Config.SONG_BUTTON_SIZE // 2)
            playRect = pygame.Rect(Config.SONG_PLAY_X, buttonY,
                                   Config.SONG_BUTTON_SIZE, Config.SONG_BUTTON_SIZE)
            downloadRect = pygame.Rect(Config.SONG_DOWNLOAD_X, buttonY,
                                       Config.SONG_BUTTON_SIZE, Config.SONG_BUTTON_SIZE)
            deleteRect = pygame.Rect(Config.SONG_DELETE_X, buttonY,
                                         Config.SONG_BUTTON_SIZE, Config.SONG_BUTTON_SIZE)
                
                
            if (song == self.selectedSong):
                if (playRect.collidepoint(pos)):
                    return "PLAY", song
                elif (downloadRect.collidepoint(pos)):
                    return "DOWNLOAD", song
                elif (deleteRect.collidepoint(pos)):
                    return "DELETE", song
            if (itemRect.collidepoint(pos)):
                   return "SONG", song
        return "SONG", None
                
                    

            


    def draw(self):
        #BACKGROUND
        self.screen.fill(Config.BG_COLOR)

        #TOPBAR
        pygame.draw.rect(self.screen, Config.TOP_BAR_COLOR, Config.TOP_BAR_RECT)

        
        self.screen.blit(self.titleText, (self.width // 2 - self.titleText.get_width() // 2, 
                                Config.TOP_BAR_HEIGHT//2 - self.titleText.get_height() // 2))
        pygame.draw.line(self.screen, Config.TEXT_COLOR, 
                        (self.backButton.left + 10, self.backButton.centery) , (self.backButton.right - 10, self.backButton.centery), 5)
        pygame.draw.line(self.screen, Config.TEXT_COLOR, 
                        (self.backButton.left + 10, self.backButton.centery) , (self.backButton.centerx, self.backButton.top + 18), 5, )
        pygame.draw.line(self.screen, Config.TEXT_COLOR, 
                        (self.backButton.left + 10, self.backButton.centery) , (self.backButton.centerx, self.backButton.bottom - 18), 5, )

        #CONTAINER
        pygame.draw.rect(self.screen, Config.SONGS_CONTAINER_COLOR, Config.SONGS_CONTAINER_RECT)

        self.screen.set_clip(self.container)

        if len(self.songs) > 0:
            # Calculate Visible
            startIndex = int(abs(self.scrollY) // Config.SONG_ITEM_TOTAL_HEIGHT)
            visibleCount = int(self.container.height // Config.SONG_ITEM_TOTAL_HEIGHT) + 2
            endIndex = min(len(self.songs), startIndex + visibleCount)


            for virtualIndex in range(startIndex, endIndex):
                #Calculate index in reversed list
                actualIndex = (len(self.songs) - 1) - virtualIndex
                song = self.songs[actualIndex]
                
                # Calculate position
                targetY = self.container.y + Config.SONG_ITEM_SPACING + (virtualIndex * Config.SONG_ITEM_TOTAL_HEIGHT) + self.scrollY
                itemRect = pygame.Rect(self.container.x + Config.SONG_ITEM_SPACING, targetY, 
                                       self.container.width - (2 * Config.SONG_ITEM_SPACING), Config.SONG_ITEM_HEIGHT)

                isSelected = (song == self.selectedSong)
                color = Config.SONG_ITEM_SELECTED_COLOR if isSelected else Config.SONG_ITEM_COLOR

                pygame.draw.rect(self.screen, color, itemRect, border_radius=6)

                songText = self.listFont.render(song, True, Config.TEXT_COLOR)
                self.screen.blit(songText, (itemRect.x + Config.SONG_ITEM_SPACING, itemRect.centery - songText.get_height() // 2))


                if isSelected:
                    
                    buttonY = itemRect.centery - (Config.SONG_BUTTON_SIZE // 2)
                    playRect = pygame.Rect(Config.SONG_PLAY_X, buttonY, 
                                            Config.SONG_BUTTON_SIZE, Config.SONG_BUTTON_SIZE)
                    downloadRect = pygame.Rect(Config.SONG_DOWNLOAD_X, buttonY, 
                                          Config.SONG_BUTTON_SIZE, Config.SONG_BUTTON_SIZE)
                    deleteRect = pygame.Rect(Config.SONG_DELETE_X, buttonY,
                                             Config.SONG_BUTTON_SIZE, Config.SONG_BUTTON_SIZE)


                    #PLAY
                    pygame.draw.rect(self.screen, Config.SONG_PLAY_COLOR,playRect, border_radius=4)
                    trianglePoints = [(playRect.left + 10, playRect.top + 5), 
                                       (playRect.left + 10, playRect.bottom - 5), 
                                       (playRect.right - 5, playRect.centery)]
                    pygame.draw.polygon(self.screen, Config.TEXT_COLOR, trianglePoints)


                    #DOWNLOAD
                    pygame.draw.rect(self.screen, Config.SONG_DOWNLOAD_COLOR, downloadRect, border_radius=4)
                    pygame.draw.line(self.screen, Config.TEXT_COLOR, (downloadRect.centerx, downloadRect.top + 5), 
                                                                     (downloadRect.centerx, downloadRect.bottom - 6), 3) 
                    pygame.draw.line(self.screen, Config.TEXT_COLOR, (downloadRect.left + 10, downloadRect.centery + 5), 
                                                                     (downloadRect.centerx, downloadRect.bottom - 5), 3)
                    pygame.draw.line(self.screen, Config.TEXT_COLOR, (downloadRect.right - 10, downloadRect.centery +5), 
                                                                     (downloadRect.centerx, downloadRect.bottom - 5), 3)

                    self.screen.set_clip(None)
                    #DELETE
                    pygame.draw.rect(self.screen, Config.SONG_DELETE_COLOR, deleteRect, border_radius=4)
                    iconColor = Config.TEXT_COLOR
                    cx = deleteRect.centerx
                    cy = deleteRect.centery
                    
                    #The Lid
                    pygame.draw.line(self.screen, iconColor, (cx - 9, cy - 6), (cx + 9, cy - 7), 2)
                    #The Handle
                    pygame.draw.rect(self.screen, iconColor, (cx - 5, cy - 10, 10, 5), 2, border_radius=2)
                    #The Bin
                    pygame.draw.rect(self.screen, iconColor, (cx - 7, cy - 5, 14, 15), 3, border_radius=2)

                    self.screen.set_clip(self.container)

        self.screen.set_clip(None)

        pygame.display.flip()