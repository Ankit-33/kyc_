import cv2
import sqlite3
from io import BytesIO
import numpy as np
from flask import Flask, render_template, request, jsonify

app = Flask(_name_)

# Connect to SQLite database
conn = sqlite3.connect('faces.db')
c = conn.cursor()
#c.execute("drop table faces")

# Create table to store face images
c.execute('''CREATE TABLE IF NOT EXISTS faces
             (id INTEGER PRIMARY KEY, name TEXT,dob date,address text ,pancardno varchar,adhaarno integer,incomerange varchar,typeofemploye text,sign blog,image BLOB)''')
@app.route('/')
def welcome():
    return render_template(r'index.html')

@app.route('/bmit',methods=['post','get'])
def bmit():
    id=1
    if request.method=='post':
        name = request.form['name']
        dob = request.form['dob']
        address = request.form['address']
        pan = request.form['pan']
        adhaar = request.form['adhaar']
        income = request.form['income']
        type= request.form['employeeType']
        sign1=request.files['signature']
        sign = sign1.read()
        c.execute("INSERT INTO faces (id,name,dob,address,pancardno,adhaarno,incomerange,typeofemploye,sign) VALUES (?,?,?,?,?,?,?,?,?)", (id,name,dob,address,pan,adhaar,income,type,sign))


def resize_image(img, height):
    """Resize image to specified height while preserving aspect ratio."""
    ratio = height / img.shape[0]
    return cv2.resize(img, (int(img.shape[1] * ratio), height))


# Initialize the face detector
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
@app.route('/capture_face',methods=['post','get'])
def capture_face():
    # Read image from webcam
    cap = cv2.VideoCapture(1)
    ret, frame = cap.read()
    
    # Convert frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces in the image
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    if len(faces) == 1:
        # Extract the face region
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 5)
            roi_gray = gray[y:y + w, x:x + w]
            roi_color = frame[y:y + h, x:x + w]
        
        # Convert image to bytes
        image_bytes = cv2.imencode('.jpg', roi_color)[1].tobytes()
        id=3
        # Save the face image to the database
        
        c.execute("INSERT INTO faces (image) VALUES (?)", ( image_bytes))
        conn.commit()
        print("Face captured and stored successfully!")
    else:
        print("No face detected or multiple faces detected.")
    
def show_all_faces():
    # Select all rows from the faces table
    c.execute("SELECT * FROM faces")
    rows = c.fetchall()
    images = []
    max_height = 0
    # Print the rows
    for row in rows:
        print("ID:", row[0])
        print("Name:", row[1])
        print("dob:", row[2])
        print("address:", row[3])
        print("pancardno:", row[4])
        print("adhaarno:", row[5])
        print("income range:", row[6])
        print("type of employe:", row[7])
        image_data = np.frombuffer(row[9], dtype=np.uint8)
        img = cv2.imdecode(image_data, cv2.IMREAD_COLOR)
        max_height = max(max_height, img.shape[0])
        images.append(img)
    resized_images = [resize_image(img, max_height) for img in images]
    combined_image = np.hstack(resized_images)
    cv2.imshow("All Faces", combined_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
if _name_ == "_main_":
    app.run()