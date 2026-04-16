import mido
import sys
import Config
import pygame
from Visualizer import Visualizer
from SongsMenu import SongsMenu
from Sequencer import Recorder, Player
from IOmidi import playMidiFile, midiInputSetup, midiOutputSetup

class App():
    def __init__(self, inport, outport):
        #PORTS
        self.inport = inport
        self.outport = outport

        #OBJECTS
        self.screen = pygame.display.set_mode((Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        

        #SCENES
        self.vis = Visualizer(self.screen)
        self.menu = SongsMenu(self.screen)
        self.currentScene = self.vis.sceneID

        #TOOLS
        self.recorder = Recorder(self.vis)
        self.player = Player(self.vis)

    def changeScene(self, scene):
        self.currentScene = scene.sceneID

        self.recorder.stop()
        self.player.pause()

        self.menu.resetScroll()
        self.menu.selectedSong = None

    def silenceMidi(self):
        for channel in range(16):
            
            # The elegant way: Send the official "All Sound Off" (120) and "All Notes Off" (123) commands
            self.outport.send(mido.Message('control_change', channel=channel, control=120, value=0))
            self.outport.send(mido.Message('control_change', channel=channel, control=123, value=0))
            
            '''   
            # The brute-force backup: For stubborn synths that ignore CC messages
            for note in range(128):
                self.outport.send(mido.Message('note_off', channel=channel, note=note, velocity=0))'''


        
    def run(self):
        # Initialize Touch Variables
        isDragging = False
        dragStartY = 0
        dragStartX = 0
        lastMouseY = 0

        while self.running:
            dt = self.clock.tick(Config.FPS) / 1000.0
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                #VISUALIZER
                if self.currentScene == self.vis.sceneID:
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        
                        #PopUp
                        if self.vis.isPopUp():
                            if self.vis.yesButton.collidepoint(event.pos):
                                self.menu.addSong(self.recorder.save())
                            elif self.vis.noButton.collidepoint(event.pos):
                                self.recorder.discard()

                        #Main Visualizer Buttons
                        else:
                            if self.vis.recordButton.collidepoint(event.pos):
                                if not self.recorder.isRecording:
                                    self.recorder.start()
                                else:
                                    self.recorder.stop()
                                    self.vis.showPopUp = True


                            if self.vis.isLoaded:
                                if self.vis.playButton.collidepoint(event.pos):
                                    if self.vis.isPlaying:
                                        self.player.pause()
                                        self.silenceMidi()
                                    else:
                                        self.player.play()
                                if self.vis.forwardButton.collidepoint(event.pos):
                                    self.player.moveTime(5.0)
                                    self.player.pause()
                                    self.silenceMidi()
                                if self.vis.rewindButton.collidepoint(event.pos):
                                    self.player.moveTime(-5.0)
                                    self.player.pause()
                                    self.silenceMidi()
                                if self.vis.cancelButton.collidepoint(event.pos):
                                    self.player.stop()
                                    self.player.reset()
                                    self.silenceMidi()
                                if self.vis.speedButton.collidepoint(event.pos):
                                    self.player.changeSpeed()
                                if self.vis.muteButton.collidepoint(event.pos):
                                    self.player.changeMute()
                                    self.silenceMidi()

                            if self.vis.toSongsButton.collidepoint(event.pos):
                                self.changeScene(self.menu)

                # ==========================================
                # SCENE 2: SONGS MENU
                # ==========================================
                elif self.currentScene == self.menu.sceneID:
                    
                    #TOUCH DOWN 
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        if self.menu.backButton.collidepoint(event.pos):
                            self.changeScene(self.vis)
                            continue
                        
                        isDragging = self.menu.container.collidepoint(event.pos)
                        lastMouseY = event.pos[1]
                        dragStartX = event.pos[0]
                        dragStartY = event.pos[1]

                    #TOUCH DRAGGING
                    elif event.type == pygame.MOUSEMOTION and isDragging:
                        dy = event.pos[1] - lastMouseY
                        self.menu.scrollY += dy
                        self.menu.clampScroll()
                        lastMouseY = event.pos[1]
                        self.menu.selectedSong = None

                    #TOUCH UP
                    elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                        isDragging = False
                        
                        if abs(event.pos[0] - dragStartX) + abs(event.pos[1] - dragStartY) < 10:
                            action, tappedSong = self.menu.handleClick(event.pos)
                            
                            if action == "PLAY":
                                print(f"▶️ Playing {tappedSong}")
                                self.player.load(tappedSong)
                                self.player.reset()
                                self.changeScene(self.vis)
                                self.vis.loadSong(tappedSong)
                            elif action == "DOWNLOAD":
                                print(f"⬇️ Downloading {tappedSong}")
                            elif action == "DELETE":
                                print(f" Deleting {tappedSong}")
                                self.menu.removeSong(tappedSong)
                            elif action == "SONG":
                                if self.menu.selectedSong == tappedSong:
                                    self.menu.selectedSong = None
                                else:
                                    self.menu.selectedSong = tappedSong

            # ==========================================
            # ALWAYS RUNNING: MIDI & RENDERING
            # ==========================================
            distance = (Config.NOTE_SPEED * self.player.speedMultiplier) * dt
            self.vis.updateNotes(distance)

            self.player.update(dt, self.outport)
            
            for msg in self.inport.iter_pending():
                self.vis.processMidi(msg)
                if self.vis.isRecording:
                    self.recorder.addMessage(msg)
                    
            if self.currentScene == self.vis.sceneID:
                self.vis.draw()
            elif self.currentScene == self.menu.sceneID:
                self.menu.draw()


if __name__ == "__main__":
    pygame.init()

    with midiInputSetup() as inport, midiOutputSetup() as outport:
        app = App(inport,outport)
        app.run()
        
    pygame.quit()
    sys.exit()