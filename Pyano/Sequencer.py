import mido
import time
import datetime
import os
import Config
from Note import Note


class Recorder():
    def __init__(self, vis):
        self.isRecording = False

        self.vis = vis

        self.midiFile = mido.MidiFile()
        self.track = mido.MidiTrack()
        self.midiFile.tracks.append(self.track)
        
        self.lastTime = 0
        
    def start(self):
        self.isRecording = True
        self.vis.isRecording = self.isRecording
        self.track.clear()
        self.lastTime = time.time()

    def stop(self):
        self.isRecording = False
        self.vis.isRecording = self.isRecording

    def discard(self):
        self.track.clear()
        self.vis.showPopUp = False
        print("Recording discarded.")

        
    def addMessage(self, msg):
        if not self.isRecording:
            return
        
        currentTime = time.time()
        passedTime = currentTime - self.lastTime
        self.lastTime = currentTime
        tickTime = int(passedTime * 1000)
        
        newMsg = msg.copy(time=tickTime)
        self.track.append(newMsg)

    def save(self):

        if not os.path.exists('saved'):
            os.makedirs('saved')

        timestamp  = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        filename = f"{timestamp}.mid"
        filepath = os.path.join('saved', filename)

        self.midiFile.save(filepath)
        print(f"Saved {filename}")

        self.vis.showPopUp = False

        return filename

        


class Player():
    def __init__(self, vis):
        self.isLoaded = False
        self.isPlaying = False
        self.isMuted = False

        self.vis = vis

        # 0.25x , 0.5x , 1.0x
        self.speedMultiplier = 1.0
        currentScrollSpeed = Config.NOTE_SPEED * self.speedMultiplier
        self.fallTime = (self.vis.height - Config.KEYBOARD_HEIGHT - Config.TOP_BAR_HEIGHT) / currentScrollSpeed

        self.song = None
        self.masterNotes = []
        self.audioQueue = []
        self.noteIndex = 0
        self.audioIndex = 0

        self.pointerTime = 0.0
        
        
    def load(self, song):
        self.isLoaded = True
        self.isPlaying = False
        self.song = song

        filepath = os.path.join('saved', song)
        if not os.path.exists(filepath):
            print("File not found")
            return
        
        midiFile = mido.MidiFile(filepath)

        self.masterNotes = []
        self.audioQueue = []

        self.pianoChannels = {i for i in range(16) if i != 9}
        
        for msg in midiFile:
            if msg.type == 'program_change':
                if msg.program > 7:
                    self.pianoChannels.discard(msg.channel)
                else:
                    self.pianoChannels.add(msg.channel)

    
        self.__buildAudioQueue(midiFile)
        parsedData = self.__calculateDurations(midiFile)
        self.__buildMasterNotes(parsedData)
                
        self.masterNotes.sort(key = lambda x : x['spawnTime'])
        self.audioQueue.sort(key = lambda x : x['time'])

        #INTRO BUFFER
        #=================================================
        if len(self.masterNotes) > 0:

            firstSpawn = self.masterNotes[0]['spawnTime']
            targetSpawn = 1.0 / self.speedMultiplier
            offset = targetSpawn - firstSpawn

            for note in self.masterNotes:
                note['spawnTime'] += offset
                note['startTime'] += offset
            for note in self.audioQueue:
                note['time'] += offset + Config.AUDIO_LATENCY

        #===================================================

        self.vis.clearNotes()
        self.vis.isLoaded = self.isLoaded
        self.vis.isPlaying = self.isPlaying
        self.vis.song = self.song
        self.vis.speedMultiplier = self.speedMultiplier

    def changeSpeed(self):
        timeChange = 1
        if self.speedMultiplier == 1.0:
            self.speedMultiplier = 0.5
            self.pointerTime /= self.speedMultiplier
            timeChange = 2
        elif self.speedMultiplier == 0.5:
            self.pointerTime /= self.speedMultiplier
            self.speedMultiplier = 0.25
            timeChange = 2
        elif self.speedMultiplier == 0.25:
            self.pointerTime *= self.speedMultiplier
            self.speedMultiplier = 1.0
            timeChange = 0.25

        for data in self.masterNotes:
            data['spawnTime'] *= timeChange
            data['startTime'] *= timeChange
        for data in self.audioQueue:
            data['time'] *= timeChange

        currentScrollSpeed = Config.NOTE_SPEED * self.speedMultiplier
        self.fallTime = (self.vis.height - Config.KEYBOARD_HEIGHT - Config.TOP_BAR_HEIGHT) / currentScrollSpeed

        self.seek(self.pointerTime)

        self.vis.speedMultiplier = self.speedMultiplier

    def play(self):
        self.isPlaying = True
        self.vis.isPlaying = self.isPlaying

    def pause(self):
        self.isPlaying = False
        self.vis.isPlaying = self.isPlaying 

    def changeMute(self):
        self.isMuted = not self.isMuted
        self.vis.isMuted = self.isMuted

    def stop(self):
        self.isLoaded = False
        self.isPlaying = False
        self.song = None

        self.vis.floatingNotes.clear()
        self.vis.whiteNotes.clear()
        self.vis.blackNotes.clear()
        self.vis.isLoaded = self.isLoaded
        self.vis.isPlaying = self.isPlaying
        self.vis.song = self.song

    def reset(self):
        self.speedMultiplier = 1
        self.noteIndex = 0
        self.audioIndex = 0
        self.pointerTime = 0.0

        self.vis.speedMultiplier = self.speedMultiplier

    def moveTime(self, time):
        self.seek(self.pointerTime + time)

    def seek(self, targetTime):
        if not self.isLoaded:
            return
        
        maxTime = self.audioQueue[-1]['time'] if self.audioQueue else 0
        self.pointerTime = max(0.0, min(targetTime, maxTime))
        
        self.vis.floatingNotes.clear()
        self.vis.whiteNotes.clear()
        self.vis.blackNotes.clear()
        for k in self.vis.keys.values():
            k['isCorrect'] = False

        self.noteIndex = len(self.masterNotes)
        for i, data in enumerate(self.masterNotes):

            if data['spawnTime'] <= self.pointerTime:
                
                timeElapsed = self.pointerTime - data['spawnTime']
                distanceMoved =  timeElapsed * Config.NOTE_SPEED * self.speedMultiplier
                noteY = Config.TOP_BAR_HEIGHT - data['h'] + distanceMoved
                
                if noteY < self.vis.keyboardTopY:
                    newNote = Note(data['midi'], data['cx'], data['w'], noteY, data['isWhite'])
                    newNote.height = data['h']

                    self.vis.floatingNotes.append(newNote)
                    if data['isWhite'] == True:
                        self.vis.whiteNotes.append(newNote)
                    else:
                        self.vis.blackNotes.append(newNote)

            else:
                self.noteIndex = i
                break


        self.audioIndex = len(self.audioQueue)
        for i,data in enumerate(self.audioQueue):
            if data['time'] >= self.pointerTime:
                self.audioIndex = i
                break

        



    def update(self, dt, outport):
        if not self.isPlaying:
            return
        
        self.pointerTime += dt

        while self.noteIndex < len(self.masterNotes) and self.masterNotes[self.noteIndex]['spawnTime'] <= self.pointerTime:
            data = self.masterNotes[self.noteIndex]
            newNote = Note(data['midi'], data['cx'], data['w'], Config.TOP_BAR_HEIGHT, data['isWhite'])
            newNote.height = data['h']

            if data['spawnTime'] < 0:
                catchUpDist = abs(data['spawnTime']) * Config.NOTE_SPEED * self.speedMultiplier
                newNote.y = Config.TOP_BAR_HEIGHT - data['h'] + catchUpDist
            else:
                newNote.y = Config.TOP_BAR_HEIGHT - newNote.height

            self.vis.floatingNotes.append(newNote)
            if(data['isWhite']):
                self.vis.whiteNotes.append(newNote)
            else:
                self.vis.blackNotes.append(newNote)

            self.noteIndex +=1
        
        while self.audioIndex < len(self.audioQueue) and self.audioQueue[self.audioIndex]['time'] <= self.pointerTime:
            event = self.audioQueue[self.audioIndex]['msg']
            if not self.isMuted:
                outport.send(event)
            self.audioIndex += 1


    
    def __buildAudioQueue(self, mid):
        absoluteTime = 0.0
        for msg in mid:
            absoluteTime += msg.time
            if not msg.is_meta:
                self.audioQueue.append({
                        'time' : absoluteTime / self.speedMultiplier,
                        'msg' : msg
                    })
                
    def __calculateDurations(self, mid):
        parsedData = []
        activeNotes = {}
        absoluteTime = 0.0

        for msg in mid:
            absoluteTime += msg.time
            if msg.type == 'note_on' and msg.velocity > 0:
                activeNotes[msg.note] = absoluteTime
            elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                if msg.note in activeNotes:
                    startTime = activeNotes.pop(msg.note)
                    duration = absoluteTime - startTime
                    parsedData.append(
                        {
                            'midi' : msg.note,
                            'originalStart' : startTime,
                            'originalDuration' : duration
                        })
                    
        return parsedData
    
    def __buildMasterNotes(self, parsedData):
        for data in parsedData:
            if data['midi'] not in self.vis.keys:
                continue

            keyInfo = self.vis.keys[data['midi']]
            
            actualStart = data['originalStart'] / self.speedMultiplier
            spawnTime = actualStart - self.fallTime
            noteHeight = data['originalDuration'] * Config.NOTE_SPEED

            self.masterNotes.append({
                    'spawnTime' : spawnTime,
                    'startTime' : actualStart,
                    'duration' : data['originalDuration'] / self.speedMultiplier,
                    'midi' : data['midi'],
                    'h' : noteHeight, 
                    'cx' : keyInfo['cx'],
                    'w' : keyInfo['w'],
                    'isWhite' : (keyInfo['type'] == 'white')
                })

                    