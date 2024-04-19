import io
#from torchvision import models
#import torchvision.transforms as transforms
#from PIL import Image
import fastapi
from fastapi import File, UploadFile, Request
import uvicorn
#import torch
from fastapi.responses import RedirectResponse, HTMLResponse
#import base64
import cv2
import numpy as np

# instantiate FastAPI object
app = fastapi.FastAPI()

# invoke AWS Sagemaker
import boto3
import json

client = boto3.client('sagemaker-runtime')
print(client)

def class_to_label(class_val):
    """return the class label as a string"""
    r = ''
    
    if class_val == 0.0:
        r = 'blue tape'
    if class_val == 1.0:
        r = 'black tape'
    if class_val == 2.0:
        r = 'gum'
    if class_val == 3.0:
        r = 'leaf'
        
    return r

def class_to_color(class_val):
    """return the class label as a color for the bounding box"""
    r = ''
    
    if class_val == 0.0:
        r = (0,0,255)
    if class_val == 1.0:
        r = (0,255,0)
    if class_val == 2.0:
        r = (255,0,0)
    if class_val == 3.0:
        r = (255,255,0)
        
    return r

def one_hot_label(label):
    """
    one hot encode label from string to int
    unknown class is 0 for now..
    @TODO = csv file?
    """
    r = 4
    if label == 'blue tape':
        r = 0
    if label == 'black tape':
        r = 1
    if label == 'gum':
        r = 2
    if label == 'leaf':
        r = 3
        
    return r


def make_inference(im):
  """invoke sagemaker model for inferencing"""
  
  f = open(im, 'rb')
  data = f.read()
  #print(data)
  
  response = client.invoke_endpoint(
  EndpointName='tape-test-endpoint',
  Body=data)

  results = json.loads(response['Body'].read().decode())

  img_r = cv2.imread(im)
  img = cv2.cvtColor(img_r, cv2.COLOR_BGR2RGB) # convert to correct color sequence    
  img = np.asarray(img)
          
  h, w, c = img.shape
      
  for r in results['prediction']:
      
      class_val = r[0]
      label = class_to_label(class_val)
      confidence = r[1]
      x = r[2] * w
      y = r[3] * h
      width = (r[4]) * w
      height = (r[5]) * h
      
      xmin = r[2] * w
      xmax = r[4] * w
      ymin = r[3] * h
      ymax = r[5] * h
      
      print('class:' + label)
      print('confidence: ' + str(confidence))
      
      if confidence > 0.05:
          
          start_point = (int(x),int(y+height)) # top left
          end_point = (int(x+width),int(y)) # bottom right
              # add rect
          color = class_to_color(class_val)
          thickness = 10 # Line thickness of 2 px 
          
          s_i = (int(xmin), int(ymax))
          s_f = (int(xmax), int(ymin))
          #img = cv2.rectangle(img, s_i, s_f, color, thickness) # show inference on img

## endpoints

@app.get("/")
def index():
    return {"message": "Hello Tape-Leaf-Exp April 19 2024"}

@app.post("/files/")
async def create_file(file: bytes = File()):
    return {"file_size": len(file)}

@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile):
    return {"filename": file.filename}






# @app.post("/predictOLD")
# async def predictFIle(file: UploadFile = File(...)):
#     image_bytes = await file.read()
#     print('length of inc image', len(image_bytes))
#     model_3_pred_idx, label_pred_3, model_10_pred_idx, label_pred_10 = get_prediction(image_bytes=image_bytes)
#     return {"earlyorlateID": model_3_pred_idx, "class_name_3": label_pred_3, "diseaseID": model_10_pred_idx, "class_name_10":label_pred_10}

# # adding Matthias's route, using requests
# # https://fastapi.tiangolo.com/advanced/using-request-directly/
# @app.post("/predict")
# async def predictRequest(request: Request):
    
#   if request.method == 'POST':
#     content_type = request.headers.get('Content-type')
        
#     if (content_type == 'application/json'):
      
#       data = await request.json()
#       if not data:
#         return
      
#       img_string = data.get('file')
#       #Clean string
#       img_string = img_string[img_string.find(",")+1:]
#       img_bytes = base64.b64decode(img_string)      
#     elif (content_type == 'multipart/form-data'):
#       print('you have multiformish dater!')
#       if 'file' not in request.files:
#         return {"oops":"no data in form"}
#       file = request.files.get('file')
#       if not file:
#         return
#       img_bytes = file.read()
#     else: 
#       return "Content type is not supported."
  
#     if len(img_bytes) > 0:   # not sure if that works like that in Python...
#       model_3_pred_idx, label_pred_3, model_10_pred_idx, label_pred_10 = get_prediction(image_bytes=img_bytes)        
#       return {"earlyorlateID": model_3_pred_idx, "class_name_3": label_pred_3, "diseaseID": model_10_pred_idx, "class_name_10":label_pred_10}
#     else: 
#       return "Cannot extract image data from request"