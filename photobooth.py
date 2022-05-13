import tkinter as tk
import cv2 as cv
import threading
import os
import sys
import datetime as dt
from PIL import Image
from PIL import ImageTk

def get_path(filename):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, filename)
    return filename

filter = 0

def changeFilter(num):
    global filter
    filter = num

def gray(frame):
    return cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

def xyz(frame):
    return cv.cvtColor(frame, cv.COLOR_BGR2XYZ)

def lab(frame):
    return cv.cvtColor(frame, cv.COLOR_BGR2LAB)

def blur(frame):
    return cv.GaussianBlur(frame, (7, 7), 0)

def gauss_th(frame):
    return cv.adaptiveThreshold(gray(frame), 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 7, 2)

def gauss_th_inv(frame):
    return cv.adaptiveThreshold(gray(frame), 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY_INV, 7, 2)

def otsu_th(frame):
    _, th = cv.threshold(blur(gray(frame)), 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)
    return th

def otsu_th_inv(frame):
    _, th = cv.threshold(blur(gray(frame)), 0, 255, cv.THRESH_BINARY_INV + cv.THRESH_OTSU)
    return th

def canny(frame):
    return cv.Canny(frame, 100, 200)

class PhotoBooth:
    def __init__(self, cam):
        self.cam = cam

        self.root = tk.Tk()
        self.root.title('PhotoBooth')
        self.root.config(background='#e0e0e0')
        self.root.iconphoto(True, tk.PhotoImage(file=get_path('icon.png')))

        self.panel = None

        frm = tk.Frame()
        frm.pack(side='left')
        frm.config(background='#e0e0e0')

        self.btn_images = []        
        for i in range(10):
            self.btn_images.append(tk.PhotoImage(file=get_path('btn_image{}.png').format(i)))
            b = tk.Button(frm, image=self.btn_images[i], command=lambda i = i: changeFilter(i))
            b.pack(side='top', fill='both', expand='yes', padx=3, pady=3)

        btn_snapshot = tk.Button(self.root, text='Snapshot!',command=self.takeSnapshot)
        btn_snapshot.pack(side='bottom', fill='both', expand='yes', padx=10, pady=10)

        self.thread = threading.Thread(target=self.videoLoop)
        self.thread.start()

    def videoLoop(self):
        while True:
            try:
                _, self.frame = self.cam.read()

                match filter:
                    case 1:
                        self.frame = gray(self.frame)
                    case 2:
                        self.frame = xyz(self.frame) 
                    case 3:
                        self.frame = lab(self.frame)
                    case 4:
                        self.frame = blur(self.frame)
                    case 5:
                        self.frame = gauss_th(self.frame)
                    case 6:
                        self.frame = gauss_th_inv(self.frame)
                    case 7:
                        self.frame = otsu_th(self.frame)
                    case 8:
                        self.frame = otsu_th_inv(self.frame)
                    case 9:
                        self.frame = canny(self.frame)

                image = cv.cvtColor(self.frame, cv.COLOR_BGR2RGB)
                image = Image.fromarray(image)
                image = ImageTk.PhotoImage(image)

                if self.panel is None:
                    self.panel = tk.Label(image=image)
                    self.panel.image = image
                    self.panel.pack(side="left", padx=10, pady=10)
                else:
                    self.panel.configure(image=image)
                    self.panel.image = image
            except Exception as ignored:
                pass

    def takeSnapshot(self):
        if not os.path.isdir('images'):
            os.makedirs('images')

        path = 'images\PB_{}.png'.format(dt.datetime.now().strftime('%d-%m-%y_%H.%M.%S.%f'))
        cv.imwrite(path, self.frame)

width, height = 1280, 720
cam = cv.VideoCapture(0)
cam.set(cv.CAP_PROP_FRAME_WIDTH, width)
cam.set(cv.CAP_PROP_FRAME_HEIGHT, height)

pba = PhotoBooth(cam)
pba.root.mainloop()
cam.release()