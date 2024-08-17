from flask import Flask, render_template, request, jsonify
import os
import uuid
import cv2
from ultralytics import YOLO
import face_recognition

# Initialize the Flask application
app = Flask(__name__)

# Configure the upload folder
UPLOAD_FOLDER = 'static/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load the YOLO model
model = YOLO('best.pt')
# Perform a dummy inference
warm_up_image=r"C:\Users\aaii1\final2\static\assets\img\bagExample.jpg"
model.predict(warm_up_image)

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}

# Load known criminal faces
criminal_images_folder = 'static/criminals/'

def load_known_faces(known_faces_folder):
    known_face_encodings = []
    known_face_names = []
    known_face_ids = ["Y32510","Y32511","Y32512","Y32513","Y32514","Y32515","Y32516","Y32517","Y32518","Y32519","Y32520","Y32521","Y32522","Y32523","Y32524","Y32525","Y32526","Y32579","Y32580"]

    for filename in os.listdir(known_faces_folder):
        if filename.endswith(('.jpg', '.png')):
            img_path = os.path.join(known_faces_folder, filename)
            image = face_recognition.load_image_file(img_path)
            encoding = face_recognition.face_encodings(image)[0]
            known_face_encodings.append(encoding)
            known_face_names.append(os.path.splitext(filename)[0])  # Name or ID of the criminal
            
    return known_face_encodings, known_face_names, known_face_ids

criminal_encodings, criminal_names, criminal_ids = load_known_faces(criminal_images_folder)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/xray-detect', methods=['GET', 'POST'])
def xray_detect():
    result_img_path = None
    
    if request.method == 'POST':
        # Save the uploaded image
        file = request.files['file']
        
        # Debug: Check if the file is received correctly
        if file:
            print(f"Received file: {file.filename}")
        else:
            print("No file received")
        
        # Generate a unique filename to prevent overwriting
        original_filename = file.filename
        unique_filename = f"{uuid.uuid4().hex}_{original_filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        # Save the file to the upload directory
        file.save(file_path)
        
        # Debug: Check if the file is saved correctly
        if os.path.exists(file_path):
            print(f"File saved successfully at {file_path}")
        else:
            print(f"File not saved: {file_path}")
        
        # Predict the image using YOLO
        try:
            results = model.predict(file_path)
            
            # Debug: Check if YOLO returns results
            if results:
                print("YOLO prediction successful")
            else:
                print("YOLO returned no results")
            
            # Save the prediction results with the format "annotated_<original_filename>"
            for result in results:
                # Plot the results on the image
                plotted_img = result.plot()
                
                # Save the image with the "annotated_" prefix
                annotated_filename = f"annotated_{unique_filename}"
                result_img_path = os.path.join(app.config['UPLOAD_FOLDER'], annotated_filename)
                
                cv2.imwrite(result_img_path, plotted_img)
                
                # Debug: Check if the result image is saved
                if os.path.exists(result_img_path):
                    print(f"Annotated image saved at {result_img_path}")
                else:
                    print(f"Annotated image not saved at {result_img_path}")
        except Exception as e:
            print(f"Error during YOLO prediction: {e}")

    # If the method is POST, return JSON response with the result image path
    if request.method == 'POST':
        return jsonify({'result_img_path': result_img_path})
    
    # For GET requests, return the main page
    return render_template('xray-detect.html', result_img_path=result_img_path)



@app.route('/face-detect', methods=['GET', 'POST'])
def face_detect():

    result_img_path = None
    
    if request.method == 'POST':
        # Save the uploaded image
        file = request.files['file']
        
        # Debug: Check if the file is received correctly
        if file:
            print(f"Received file: {file.filename}")
        else:
            print("No file received")
        
        # Generate a unique filename to prevent overwriting
        original_filename = file.filename
        unique_filename = f"{uuid.uuid4().hex}_{original_filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        # Save the file to the upload directory
        file.save(file_path)

        # Debug: Check if the file is saved correctly
        if os.path.exists(file_path):
            print(f"File saved successfully at {file_path}")
        else:
            print(f"File not saved: {file_path}")
        
        '''oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo'''
        try:
            
                result_img_path = process_image(file_path)
                                
                # Debug: Check if the result image is saved
                if os.path.exists(result_img_path):
                    print(f"Annotated image saved at {result_img_path}")
                else:
                    print(f"Annotated image not saved at {result_img_path}")
        except Exception as e:
            print(f"Error during YOLO prediction: {e}")

    # If the method is POST, return JSON response with the result image path
    if request.method == 'POST':
        return jsonify({'result_img_path': result_img_path})
    
    # For GET requests, return the main page
    return render_template('face-detect.html', result_img_path=result_img_path)




    

@app.route('/')
def index():
    return render_template('index.html')

 

@app.route('/stats')
def stats():
    return render_template('stats.html')


def process_image(image_path):
    # Load the image
    image = cv2.imread(image_path)
    if image is None:
        print(f"Failed to load image: {image_path}")
        return
    
    # Detect faces and capture if a criminal is found
    annotated_image_path = detect_faces_and_capture(image, image_path)
    
    if annotated_image_path:
        print(f"Annotated image saved to: {annotated_image_path}")
        return annotated_image_path
    else:
        print("No faces detected or image not processed.")



def detect_faces_and_capture(frame, image_path):
    # Convert the frame to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Detect faces in the frame
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
    
    if len(face_locations) > 0:
        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            cv2.rectangle(frame, (left, top), (right, bottom), (255, 0, 0), 2)
            
            # Compare the detected face to known criminals
            matches = face_recognition.compare_faces(criminal_encodings, face_encoding)
            name = "No criminal match."
            
            if True in matches:
                match_index = matches.index(True)
                name = criminal_names[match_index]
                id = criminal_ids[match_index]
                print(f"Criminal detected: {name}, {id}!")
                
                # Display "Wanted Criminal" above the rectangle
                cv2.putText(frame, "Wanted Criminal", (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)
                
                # Display the name below the rectangle
                cv2.putText(frame, name, (left, bottom + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)
            else:
                print("No criminal match.")
                
                # Display "No criminal match" above the rectangle
                cv2.putText(frame, "No criminal match.", (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 0, 0), 2)

    # Save the image with annotations
    annotated_image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'annotated_' + os.path.basename(image_path))
    cv2.imwrite(annotated_image_path, frame)
    
    return annotated_image_path

if __name__ == '__main__':
    app.run(debug=True)
