from flask import Flask, render_template, request
import os
import cv2
import numpy as np

app = Flask(__name__)

def center_crop(img, frac=0.6):
    """
    Crops the image so that it is only the center (assuming that is where the matcha is).
    Args:
        img (numpy.ndarray): Input image array
        frac (float): Fraction of image to keep (we have 0.6)

    Returns:
        numpy.ndarray: Center of cropped image
    """

    h, w = img.shape[:2]
    cropped_h = int(h * frac)
    cropped_w = int(w * frac)
    top = (h - cropped_h) // 2
    left = (w - cropped_w) // 2
    return img[top:top+cropped_h, left:left+cropped_w]



def grade_matcha(image_path):
    """
    Reads an image of matcha drink/owder, analyzes its color, 
    assigns a grade based on HSV color thresholds.

    Args:
        image_path (str): Path to input image file

    Returns: 
        tuple: (grade (str), tip (str)) describing matcha quality
    """

    img = cv2.imread(image_path)
    if img is None:
        return None, "Could not read image"
    
    max_dim = 1000 # Resizing larger images for faster processing 
    h, w = img.shape[:2] 

    if max(h, w) > max_dim:
        scale = max_dim / max(h, w)
        img = cv2.resize(img, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
    
    crop = center_crop(img, frac=0.6)
    hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV) # Convert cropped image from BGR to HSV
    
    avg_hue = float(np.mean(hsv[:, :, 0]))  
    avg_sat = float(np.mean(hsv[:, :, 1]))   
    avg_val = float(np.mean(hsv[:, :, 2]))   
    avg_hue_deg = avg_hue * 2.0        # Convert hue to degrees (0-360)

    # Grade based on heuristics of hue, saturation, and brightness
    if 90 <= avg_hue_deg <= 140 and avg_sat >= 100 and avg_val >= 60:
        grade = "Ceremonial"
        tip = "Bright, vibrant green. Likely fresh, high-quality matcha."
    elif (70 <= avg_hue_deg < 90 or 140 < avg_hue_deg <= 160) and avg_sat >= 70:
        grade = "Culinary / Medium"
        tip = "Green but less vibrant. Could be culinary grade or slightly older."
    else:
        grade = "Low Grade / Old"
        tip = "Yellow/brown tones or low saturation. Could be oxidized or low-grade matcha."

    return grade, tip

@app.route('/', methods=['GET', 'POST'])
def index():
    error = None
    grade = None
    tip = None
    if request.method == 'POST':
        if 'file' not in request.files:
            error = "No file part"
        else:
            file = request.files['file']
            if file.filename == '':
                error = "No selected file"
            else:
                filename = os.path.join('uploads', file.filename)
                os.makedirs('uploads', exist_ok=True)
                file.save(filename)
                grade, tip = grade_matcha(filename)

    return render_template('index.html', error=error, grade=grade, tip=tip)

if __name__ == '__main__':
    app.run(debug=True)
