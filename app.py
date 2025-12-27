from flask import Flask, render_template, request, jsonify
from ultralytics import YOLO
import os
import time
import base64
import portalocker
import shutil  # Added for directory cleanup

app = Flask(__name__)
model = YOLO('best.pt')

def get_and_update_current_num():
    if not os.path.exists('filt.txt'):
        with open('filt.txt', 'w') as f:
            f.write('0')
    
    with open('filt.txt', 'r+') as file:
        portalocker.lock(file, portalocker.LOCK_EX)
        current_num = int(file.read().strip())
        updated_num = current_num + 1
        file.seek(0)
        file.write(str(updated_num))
        file.truncate()
        portalocker.unlock(file)
        return current_num

def clear_previous_predictions():
    """Clean up previous prediction directories"""
    predict_base = "C:\\Users\\Santhosh\\OneDrive\\Desktop\\final_final_proj\\runs\\detect"
    if os.path.exists(predict_base):
        # Remove all prediction directories except the most recent one
        pred_dirs = [d for d in os.listdir(predict_base) 
                    if os.path.isdir(os.path.join(predict_base, d))]
        if len(pred_dirs) > 1:
            for d in pred_dirs[:-1]:  # Keep only the most recent
                shutil.rmtree(os.path.join(predict_base, d))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    start_time = time.time()
    
    # Clear previous predictions before new detection
    clear_previous_predictions()
    
    if 'file' not in request.files:
        return "No file part", 400
    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400

    # Create upload directory if needed
    upload_dir = "C:\\Users\\Santhosh\\OneDrive\\Desktop\\final_final_proj\\uploaded images"
    os.makedirs(upload_dir, exist_ok=True)

    # Save with unique filename using timestamp
    timestamp = int(time.time())
    filename, ext = os.path.splitext(file.filename)
    unique_filename = f"{filename}_{timestamp}{ext}"
    img_path = os.path.join(upload_dir, unique_filename)
    file.save(img_path)

    # Perform detection with fresh settings
    results = model.predict(
        source=img_path,
        imgsz=640,
        conf=0.5,
        show=False,
        save=True,
        exist_ok=False,  # Don't allow existing directories
        name=f"predict_{timestamp}"  # Unique directory name
    )
    
    end_time = time.time()
    execution_time = end_time - start_time

    # Find the specific prediction directory we just created
    predict_base = "C:\\Users\\Santhosh\\OneDrive\\Desktop\\final_final_proj\\runs\\detect"
    pred_dir = os.path.join(predict_base, f"predict_{timestamp}")
    
    # Find the predicted image (YOLO might rename it)
    pred_files = [f for f in os.listdir(pred_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    if not pred_files:
        return "Predicted image not found", 500
        
    predicted_img_path = os.path.join(pred_dir, pred_files[0])

    # Encode image
    with open(predicted_img_path, "rb") as img_file:
        encoded_image = base64.b64encode(img_file.read()).decode('utf-8')

    return jsonify({
        'execution_time': execution_time,
        'image': encoded_image
    })

if __name__ == '__main__':
    # Ensure base directories exist
    os.makedirs("C:\\Users\\Santhosh\\OneDrive\\Desktop\\final_final_proj\\runs\\detect", exist_ok=True)
    os.makedirs("C:\\Users\\Santhosh\\OneDrive\\Desktop\\final_final_proj\\uploaded images", exist_ok=True)
    app.run(debug=True)