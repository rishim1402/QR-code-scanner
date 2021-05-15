from Scanner.forms import ImageForm
from Scanner.models import Image
from django.http.response import HttpResponseRedirect
from django.shortcuts import render,redirect
from django.http import HttpResponse,StreamingHttpResponse
import cv2
from pyzbar import pyzbar
from pyzbar.pyzbar import decode
from django.views.decorators import gzip
import threading
import validators

def redirect_view(request):
    print("hellos")
    return HttpResponseRedirect('https://simpleblog.com/posts/archive/')
    response = redirect('/test/')

    return redirect('http://google.com')



barcode = ""
isURL = True
class VideoCamera(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)
        (self.grabbed, self.frame) = self.video.read()
        threading.Thread(target=self.update, args=()).start()

    def __del__(self):
        self.video.release()

    def get_frame(self):
        image = self.frame
        image = read_barcodes(image)
        _, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tobytes()

    def update(self):
        while True:
            (self.grabbed, self.frame) = self.video.read()
    def stop(self):
        self.video.release()

    def __del__(self):
        self.video.release()

def read_barcodes(frame):
    global barcode,isURL
    barcodes = pyzbar.decode(frame)
    for barcode in barcodes:
        x, y , w, h = barcode.rect        #1
        barcode_info = barcode.data.decode('utf-8')
        barcode = barcode_info
        isURL = validators.url(barcode)
        #print(barcode)
        camOn = False
        cv2.rectangle(frame, (x, y),(x+w, y+h), (0, 255, 0), 2)
        
        #2
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, barcode_info, (x + 6, y - 6), font, 2.0, (255, 255, 255), 1)        #3
        with open("barcode_result.txt", mode ='w') as file:
            file.write("Recognized Barcode:" + barcode_info)    
            #print(barcode_info)
    return frame

def gen(camera,request):
    global barcode,isURL
    while True:
        frame = camera.get_frame()
        if len(barcode)>0:
            camera.stop()
            break
        yield(b'--frame\r\n'
              b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
    redirect_view(request)


@gzip.gzip_page
def livefe(request):
    global barcode,isURL
    if len(barcode)>0:
        barcode = ""
        print("in live fun if")
    try:
        cam = VideoCamera()
        print("test")
        print(barcode)
        return StreamingHttpResponse(gen(cam,request), content_type="multipart/x-mixed-replace;boundary=frame")
    except: 
        print("test") # This is bad! replace it with proper handling
        pass

def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")
# Create your views here.

def ScannerView(request):
    global barcode,isURL
    return render(request, 'sc.html' , {"barcode" :  barcode, "isUrl" : isURL})

def getBarcode(request):
    global barcode,isURL
    print("in fun")
    print(barcode)
    return render(request, 'barcode.html' , {"barcode" :  barcode, "isUrl" : isURL})

def Get_image_view(request):
  
    if request.method == 'POST':
        form = ImageForm(request.POST, request.FILES)
  
        if form.is_valid():
            form.save()
            q2 = Image.objects.latest('id')
            print(type(q2))
            img = cv2.imread('q2.Main_Img.url')
            print(type(img))
            print(decode(img))
            return redirect('success')
    else:
        form = ImageForm()
    return render(request, 'barcode.html', {'form' : form})
  
  
def success(request):
    return HttpResponse('successfully uploaded')