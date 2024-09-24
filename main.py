import cv2
import pickle
import cvzone
import numpy as np

# Video feed
cap = cv2.VideoCapture('carPark.mp4')

# Load parking positions from the pickle file
with open('CarParkPos', 'rb') as f:
    posList = pickle.load(f)

width, height = 107, 48

# List to store the current occupancy status (0 = free, 1 = occupied)
statusList = [0] * len(posList)

# Function to check the parking space status and detect if any car is leaving
def checkParkingSpace(imgPro):
    spaceCounter = 0
    global statusList
    newStatusList = []  # To track the new status in the current frame
    leavingCars = []  # List to track the cars that left

    for index, pos in enumerate(posList):
        x, y = pos
        # Crop the region of interest for the parking spot
        imgCrop = imgPro[y:y + height, x:x + width]
        count = cv2.countNonZero(imgCrop)

        # Determine if the spot is occupied or free based on pixel count
        if count < 900:
            color = (0, 255, 0)  # Green for free spots
            thickness = 5
            spaceCounter += 1
            newStatusList.append(0)  # Free
        else:
            color = (0, 0, 255)  # Red for occupied spots
            thickness = 2
            newStatusList.append(1)  # Occupied

        # Draw a rectangle around each parking spot
        cv2.rectangle(img, pos, (pos[0] + width, pos[1] + height), color, thickness)
        cvzone.putTextRect(img, str(count), (x, y + height - 3), scale=1,
                           thickness=2, offset=0, colorR=color)

        # Detect if the car has left the spot (previously occupied, now free)
        if statusList[index] == 1 and newStatusList[index] == 0:
            leavingCars.append(index)  # Add the index of the leaving car

    # Update the status list for the next frame
    statusList = newStatusList

    # Display the number of free spaces
    cvzone.putTextRect(img, f'Free: {spaceCounter}/{len(posList)}', (100, 50), scale=3,
                       thickness=5, offset=20, colorR=(0, 200, 0))

    # Display the index of the parking spots where cars have left
    for leaving in leavingCars:
        x, y = posList[leaving]
        cvzone.putTextRect(img, f"Car left spot {leaving + 1}", (x, y - 10), scale=1.5,
                           thickness=2, offset=10, colorR=(0, 0, 255))

# Main loop to process each video frame
while True:
    # Restart the video if it reaches the end
    if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    success, img = cap.read()
    if not success:
        break

    # Preprocess the image for parking spot detection
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    imgBlur = cv2.GaussianBlur(imgGray, (3, 3), 1)
    imgThreshold = cv2.adaptiveThreshold(imgBlur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                         cv2.THRESH_BINARY_INV, 25, 16)
    imgMedian = cv2.medianBlur(imgThreshold, 5)
    kernel = np.ones((3, 3), np.uint8)
    imgDilate = cv2.dilate(imgMedian, kernel, iterations=1)

    # Check parking space status and detect cars leaving
    checkParkingSpace(imgDilate)

    # Display the processed frame
    cv2.imshow("Parking Lot", img)

    # Exit if 'q' is pressed
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

# Release video capture object and close all windows
cap.release()
cv2.destroyAllWindows()
