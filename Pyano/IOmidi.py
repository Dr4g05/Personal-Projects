import mido
import os
import sys

def midiInputSetup():
    inports = mido.get_input_names()
    for name in inports:
        if 'Yamaha' in name or 'YDP' in name or 'ARIUS' in name:
            inport = name
            print(f"Connected for input to: {inport}")
            return mido.open_input(inport)
    print("Piano not found for input.")
    sys.exit()
    return 


def midiOutputSetup():
    outports = mido.get_output_names()
    for name in outports:
        if 'Yamaha' in name or 'YDP' in name or 'ARIUS' in name:
            outport = name
            print(f"Connected for output to: {outport}")
            return mido.open_output(outport)
    print("Piano not found for output.")
    sys.exit()
    return 


def playMidiFile(filename):
    filepath = os.path.join("saved", filename)
    try:
        song = mido.MidiFile(filepath)
    except Exception as e:
        print(f"File {filename} not found. {e}")
        return
    with midiOutputSetup() as outport:
        for sound in song.play():
            outport.send(sound)







"""
def playChord(chord):
    with midiInputSetup() as inport, midiOutputSetup() as outport:
        for msg in inport: 
            if msg.type in ['note_on', 'note_off']:
                if chord == "major":
                    msg1 = msg.copy(note=msg.note + 4)
                    msg2 = msg.copy(note=msg.note + 7)
                elif chord == "minor":
                    msg1 = msg.copy(note=msg.note + 3)
                    msg2 = msg.copy(note=msg.note + 7)
                outport.send(msg1)
                outport.send(msg2)
"""