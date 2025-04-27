# AirHockey with Hands!

Have you ever wondered if you could play Air Hockey virtually with your hands?  
### Well, now you can!
This project uses OpenCV and MediaPipe to track your hands and simulate an Air Hockey game.

The game is played on a virtual table, and you can control the puck with your hands.

## Technologies Used
- Python
- OpenCV  -- to capture camera feed and process images
- MediaPipe -- to detect and track hands
- PyGame -- to create the game window and draw the game elements
- NumPy -- for numerical operations because I really suck at math

## How to Run the Project
I suggest installing conda and creating a virtual environment.
```bash
conda create -n airhockey python=3.12
conda activate airhockey
```
Then install the required packages:
```bash
pip install opencv-python mediapipe pygame numpy
```
Then run the main script:
```bash
python main.py
```
