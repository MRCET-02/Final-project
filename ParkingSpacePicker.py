import cv2
import pickle

# Define parking space dimensions
width, height = 107, 48

# Try to load existing parking positions, or create an empty list if not available
try:
    with open('CarParkPos', 'rb') as f:
        posList = pickle.load(f)
except:
    posList = []

# Function to handle mouse events for adding/removing parking spots
def mouseClick(events, x, y, flags, params):
    if events == cv2.EVENT_LBUTTONDOWN:  # Add a new parking spot
        posList.append((x, y))
        print(f"Added position: ({x}, {y})")
    if events == cv2.EVENT_RBUTTONDOWN:  # Remove a parking spot
        for i, pos in enumerate(posList):
            x1, y1 = pos
            if x1 < x < x1 + width and y1 < y < y1 + height:
                posList.pop(i)
                print(f"Removed position: ({x1}, {y1})")

    # Auto-save the position list after every click event
    savePositions()

# Function to save parking positions to a file
def savePositions():
    with open('CarParkPos', 'wb') as f:
        pickle.dump(posList, f)

# Function to draw parking spots and labels
def drawParkingSpots(img):
    for i, pos in enumerate(posList):
        cv2.rectangle(img, pos, (pos[0] + width, pos[1] + height), (255, 0, 255), 2)
        cv2.putText(img, f"Spot {i+1}", (pos[0], pos[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

while True:
    # Load parking lot image
    img = cv2.imread('carParkImg.png')
    
    # Draw parking spots and their labels
    drawParkingSpots(img)

    # Display the image
    cv2.imshow("Parking Lot", img)

    # Set the mouse callback to handle clicks
    cv2.setMouseCallback("Parking Lot", mouseClick)

    # Wait for the 's' key to be pressed for manual save or exit with 'q'
    key = cv2.waitKey(1)
    if key == ord('s'):
        print("Manually saving positions.")
        savePositions()
    elif key == ord('q'):
        print("Exiting program.")
        break

cv2.destroyAllWindows()
