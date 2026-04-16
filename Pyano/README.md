# Pyano  

**Description:**
This is a custom desktop application built with Python that serves as a MIDI visualizer, recorder, and rhythm game engine.  
It reads standard MIDI files, maps them to a virtual 88-key piano, and allows users to visualize falling notes, play along, record their own tracks, and seamlessly manipulate the timeline and playback speed.

---

**Key Features:**  
- Custom UI & Scroll Physics: Engineered a completely custom graphical interface from scratch in Pygame, featuring mobile-style touch-and-drag virtual scrolling, mathematical rendering offsets, and algorithmic list clamping.  
- Audio-Visual Playback: Visualizes .mid files with falling blocks perfectly synced to real-time audio playback.  
- Recording Mode: Records real-time MIDI input and saves user performances as new .mid files.  
- Pure Song Time Engine: Features dynamic, live speed scaling (0.25x, 0.5x, 1.0x) and timeline scrubbing (Rewind/Fast-forward/Seek) with instant mathematical frame-redraws without dropping audio sync.  
- Stateless Rendering: Uses a custom stateless graphics loop to ensure overlapping notes and rapid-fire key presses illuminate the virtual keyboard flawlessly without visual glitches.  
- Smart Track Filtering: Automatically scans imported MIDI files to isolate piano channels while filtering out drums and background instruments.  
- Delta-Time Game Loop: Hardware-agnostic physics loop that ensures falling notes remain perfectly on beat regardless of monitor refresh rate or CPU lag.  

**Technologies Used:**  
- Python (Core application logic)  
- Pygame (UI, graphics rendering, delta-time clock management)  
- Mido (Parsing .mid files and queuing MIDI messages)  
- python-rtmidi (Real-time MIDI hardware input/output communication)  

**Setup Instructions:**  
1. Clone the repository to your local machine.  
2. Create and activate a Python virtual environment:  
3. python -m venv venv  
  
4. Windows: .\venv\Scripts\activate  
Mac/Linux: source venv/bin/activate  
  
6. Install the required dependencies: pip install pygame mido python-rtmidi  
7. Connect a physical MIDI keyboard to your computer  
8. Run the application via python main.py.  

**This project demonstrates:**  
- Engineering a custom, delta-time game loop for precise physics and audio synchronization.  
- Advanced state management using stateless graphic rendering to prevent UI bugs.  
- Implementing "Pure Song Time" architecture to seamlessly scale time and physics without needing to rebuild underlying data arrays.  
- Parsing, manipulating, and filtering complex data structures (MIDI signals).  
- Applying Object-Oriented Programming (OOP) to build scalable game architecture.  
