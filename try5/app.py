from flask import Response, request, Flask, render_template, redirect, url_for
import cv2
import datetime, time
import os, sys
import numpy as np
from threading import Thread
import face_recognition
import json
import base64

def record(out):
    global rec_frame
    while(rec):
        time.sleep(0.05)
        out.write(rec_frame)


def gen_frames():  # generate frame by frame from camera
    global out, capture,rec_frame, username, code
    while True:
        success, frame = camera.read() 
        if success:
            #if(face):                
            #    frame= detect_face(frame)
            if(grey):
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            if(neg):
                frame=cv2.bitwise_not(frame)    
            if(capture):
                capture=0
                try :
                    now = datetime.datetime.now()
                    code = face_recognition.face_encodings(frame)[0]
                except :
                    pass
                if username != None :
                    #print(True)
                    f = open("/home/aaryen/Desktop/web-app-cgs402/try5/shots/" + username, 'w')
                    for s in code :
                        f.write(str(s) + '\n')
                    f.close()
                else :
                    #print(str(code))
                    pass
                        
            
            if(rec):
                rec_frame=frame
                frame= cv2.putText(cv2.flip(frame,1),"Recording...", (0,25), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255),4)
                frame=cv2.flip(frame,1)
            
                
            try:
                ret, buffer = cv2.imencode('.jpg', cv2.flip(frame,1))
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            except Exception as e:
                pass
                
        else:
            pass


#make shots directory to save pics
try:
    os.mkdir('./shots')
except OSError as error:
    pass



#Load pretrained face detection model    
#net = cv2.dnn.readNetFromCaffe('./saved_model/deploy.prototxt.txt', './saved_model/res10_300x300_ssd_iter_140000.caffemodel')

#instatiate flask app  
app = Flask(__name__, template_folder='./templates')
app.app_context().push

def recognize() :
    global login,code
    dir = "/home/aaryen/Desktop/web-app-cgs402/try5/shots"
    #print(str(code))
    for file in os.listdir(dir) :
        with open(dir + "/" + file) as f :
            data = [float(line.rstrip('\n')) for line in f]
        #print(str(code))
        #print(data)
        #face_recognition.compare_faces([my_face_encoding], unknown_face_encoding, tolerance=0.4)
        #print(data)
        #im = cv2.imread("/home/aaryen/Desktop/web-app-cgs402/image.jpeg")
        #code_ = face_recognition.face_encodings(im)[0]
        try :
            ret1 = face_recognition.compare_faces([data], code, tolerance=0.4)
        except :
            return 0
        #ret2 = face_recognition.compare_faces([data], code_, tolerance=0.4)
        if ret1[0] == True :
            return recognize2(data)
    return 0

def recognize2(data) :
    global login
    try :
        im = cv2.imread("/home/aaryen/Desktop/web-app-cgs402/try5/image.jpeg")
        code_ = face_recognition.face_encodings(im)[0]
        ret2 = face_recognition.compare_faces([data], code_, tolerance=0.4)
    except :
        return 2
    if ret2[0] == True :
        login = 1
        return 1
    return 0

@app.route('/upload-image', methods=['POST', 'GET'])
def upload_image():
    image_data = request.form['encoded']
    imgfile = base64.b64decode(image_data)
    with open("image.jpeg", "wb") as img:
        img.write(imgfile)
    x = recognize()
    if x == 1 :
        return success()
    elif x == 0 :
        return fail()
    elif x == 2 :
        return twofa()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/templates", methods=["GET"])
def loggedin() :
    return render_template("success.html")

@app.route("/templates", methods=["GET"])
def signup() :
    return render_template("signup.html")

@app.route("/", methods=["GET"])
def success():
    print("Success! You can Log In now!")
    return render_template('index.html', ip1="Success! You can Log In now!")

@app.route("/", methods=["POST"])
def fail() :
    print("Failed! Please try again or Sign Up!")
    return render_template('index.html', ip1="Failed! Please try again or Sign Up!")

@app.route("/", methods=["POST"])
def twofa() :
    print("Success! Try 2FA now!")
    return render_template('index.html', ip1="Success! Try 2FA now!")

@app.route("/", methods=["POST"])
def err() :
    print("Error! Try again.")
    return render_template('index.html', ip1="Error! Try again.")

@app.route("/", methods=["POST"])
def unclear() :
    print("Picture unclear. Try again.")
    return render_template('index.html', ip1="Picture unclear. Try again.")

@app.route('/requests',methods=['POST','GET'])
def tasks():
    global switch,camera,login,username, code
    #print(str(code))
    if request.method == 'POST':
        if  request.form.get('neg') == 'Negative':
            global neg
            neg=not neg
        elif request.form.get('click') == 'Capture':
            global capture
            capture=1
            if request.form.get('user') != None :
                username = request.form.get('user')
                #print(username)
            else :
                x = recognize()
                if x == 1 :
                    return success()
                elif x == 0 :
                    return fail()
                elif x == 2 :
                    return twofa()
        
        elif  request.form.get('face') == 'Face Only':
            global face
            face=not face 
            if(face):
                time.sleep(4)   
        elif  request.form.get('stop') == 'Stop/Start':
            
            if(switch==1):
                switch=0
                camera.release()
                cv2.destroyAllWindows()
                
            else:
                camera = cv2.VideoCapture(0)
                switch=1
        elif  request.form.get('rec') == 'Start/Stop Recording':
            global rec, out
            rec= not rec
            if(rec):
                now=datetime.datetime.now() 
                fourcc = cv2.VideoWriter_fourcc(*'XVID')
                out = cv2.VideoWriter('vid_{}.avi'.format(str(now).replace(":",'')), fourcc, 20.0, (640, 480))
                #Start new thread for recording the video
                thread = Thread(target = record, args=[out,])
                thread.start()
            elif(rec==False):
                out.release()
        elif request.form.get('log') == "signin" and login == 1 :
            return loggedin()
        elif request.form.get('sign') == "signup" :
            return signup()
        elif request.form['encoded'] :
            image_data = request.form['encoded']
            imgfile = base64.b64decode(image_data)
            with open("/home/aaryen/Desktop/web-app-cgs402/try5/image.jpeg", "wb") as img:
                img.write(imgfile)
            x = recognize()
            if x == 1 :
                return success()
            elif x == 0 :
                return fail()
            elif x == 2 :
                return twofa()
            #request.form.get('face')
        
    elif request.method=='GET' :
        return render_template('index.html')
    return render_template('index.html')


camera = cv2.VideoCapture(0)
global capture,rec_frame, grey, switch, neg, face, rec, out 
capture=0
grey=0
neg=0
face=0
switch=1
rec=0
login = 0
username = None
code = None

if __name__ == '__main__':
    app.run("0.0.0.0")