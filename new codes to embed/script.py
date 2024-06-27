import pickle
import numpy as np
import cv2
import face_recognition
import serial

# Initialize serial port for Bluetooth communication
bluetooth_port = 'COM8'  # Change 'COM8' to the correct port for your Bluetooth module
baud_rate = 9600  # Make sure it matches the baud rate of your Bluetooth module

try:
    bluetooth_serial = serial.Serial(bluetooth_port, baud_rate, timeout=1)
    print("Bluetooth connected")
except serial.SerialException as e:
    print(f"Failed to connect to Bluetooth: {e}")
    exit()

# Function to send data over Bluetooth
def send_data_over_bluetooth(name, designation, year):
    try:
        # Send all data together separated by commas
        bluetooth_serial.write(f"{name},{designation},{year+' year exp '}\n".encode())
        print(f"Data sent: {name}, {designation}, {year}")
    except serial.SerialException as e:
        print(f"Failed to send data: {e}")

# Function to draw multiline text on an image
def draw_text(img, text, position, font_scale=0.5, font_thickness=1, spacing=2, color=(0, 255, 0)):
    x, y = position
    for line in text.split('\n'):
        cv2.putText(img, line, (x, y), cv2.FONT_HERSHEY_SIMPLEX,
                    font_scale, color, font_thickness, lineType=cv2.LINE_AA)
        y += int(font_scale * 40)  # Move to next line based on font scale

# Find external camera
def find_external_camera():
    for i in range(10):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            print(f"External camera found at index {i}")
            return cap
    print("No external camera found")
    return None

cap = find_external_camera()
if not cap:
    exit()

# Load the encoding file
print("Loading Encode File ...")
with open('EncodeFile.p', 'rb') as file:
    encoded_data = pickle.load(file)
print("Encode File Loaded")

while True:
    success, img = cap.read()

    if not success:
        print("Failed to read a frame from the webcam.")
        break

    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

    if faceCurFrame:
        for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
            matches = face_recognition.compare_faces(
                [data['encoding'] for data in encoded_data], encodeFace)
            faceDis = face_recognition.face_distance(
                [data['encoding'] for data in encoded_data], encodeFace)

            if matches and faceDis.size > 0:
                matchIndex = np.argmin(faceDis)
                if matches[matchIndex]:
                    matched_data = encoded_data[matchIndex]
                    name = matched_data['name']
                    designation = matched_data['designation']
                    years_experience = matched_data['years_experience']
                    info_text = f"{name}\n{designation}\n{years_experience} years"
                    send_data_over_bluetooth(
                        name, designation, years_experience)
                else:
                    info_text = "Outsider"
                    send_data_over_bluetooth("Outsider", "", "")
            else:
                info_text = "Outsider"
                send_data_over_bluetooth("Outsider", "", "")

            # Draw the text information without the rectangle
            top, right, bottom, left = faceLoc
            y = top * 4 - 20
            draw_text(img, info_text, (left * 4, y),
                      font_scale=0.6, font_thickness=1, spacing=3)
    else:
        print("Please show me your face")

    cv2.imshow("Webcam", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
bluetooth_serial.close()  # Close the serial connection when done
