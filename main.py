import tkinter as tk
from tkinter import ttk
import time
from PIL import ImageGrab
import os
import aip
import random
import hashlib
import urllib
import requests
import http.client
import json

class GUI:
    def __init__(self) -> None:
        self.X = tk.IntVar(value=0)
        self.Y = tk.IntVar(value=0)
        self.flag = False
        self.capture_img = 'cap.png'
        self.ocr_text = ''
        self.translate_text = ''

        self.text_box = tk.Text(window)
        self.text_box.place(x=20, y=70, anchor='nw', width=170, height=330)

        self.tran_text_box = tk.Text(window)
        self.tran_text_box.place(x=210, y=70, anchor='nw', width=170, height=330)

        self.capture_btn = tk.Button(text='ScreenShot', command=self.capture_cmd)
        self.capture_btn.place(x=70, y=10, anchor='nw', width=80, height=30)

        self.trans_btn = tk.Button(text='Translate', command=self.translate_cmd)
        self.trans_btn.place(x=260, y=10, anchor='nw', width=80, height=30)

        self.from_lang = 'en'
        self.to_lang = 'zh'
        self.lang_dic = {'Chinese':'zh', 'English':'en', 'Japanese':'jp'}
        self.from_lang_label = tk.Label(window, text='from: ')
        self.from_lang_box = ttk.Combobox(window, state='readonly')
        self.from_lang_box['value'] = ('Chinese', 'English', 'Japanese')
        self.from_lang_box.current(1)
        self.from_lang_label.place(x=30, y=45, anchor='nw')
        self.from_lang_box.place(x=80, y=45, anchor='nw', width=80, height=20)

        self.to_lang_label = tk.Label(window, text='to: ')
        self.to_lang_box = ttk.Combobox(window, state='readonly')
        self.to_lang_box['value'] = ('Chinese', 'English', 'Japanese')
        self.to_lang_box.current(0)
        self.to_lang_label.place(x=240, y=45, anchor='nw')
        self.to_lang_box.place(x=270, y=45, anchor='nw', width=80, height=20)

        self.screenWidth = window.winfo_screenwidth()
        self.screenHeight = window.winfo_screenheight()
        self.tmp_img = 'tmp.png'

    def create_canvas(self):
        im = ImageGrab.grab()
        im.save(self.tmp_img)
        self.top = tk.Toplevel(window, width=self.screenWidth, height=self.screenHeight)
        self.top.overrideredirect(True) # 隐藏掉边框
        self.canvas = tk.Canvas(self.top, bg='white', width=self.screenWidth, height=self.screenHeight)
        self.image = tk.PhotoImage(file=self.tmp_img)
        self.canvas.create_image(0, 0, anchor='nw', image=self.image)
        
        self.canvas.bind('<Button-1>', self.mouse_left_down)
        self.canvas.bind('<B1-Motion>', self.mouse_move)
        self.canvas.bind('<ButtonRelease-1>', self.mouse_left_up)

        self.canvas.pack(fill=tk.BOTH, expand=tk.YES)

    def mouse_left_down(self, event):
        self.X.set(event.x)
        self.Y.set(event.y)
        self.flag = True
    
    def mouse_move(self, event):
        if not self.flag:
            return
        try:
            self.canvas.delete(self.lastDraw)
        except Exception as e:
            pass
        self.lastDraw = self.canvas.create_rectangle(self.X.get(), self.Y.get(), event.x, event.y, outline='red')
    
    def mouse_left_up(self, event):
        self.flag = False
        try:
            self.canvas.delete(self.lastDraw)
        except Exception as e:
            pass
        x1, x2 = sorted([self.X.get(), event.x])
        y1, y2 = sorted([self.Y.get(), event.y])
        pic = ImageGrab.grab((x1 + 1, y1 + 1, x2, y2))
        pic.save(self.capture_img)
        self.top.destroy()

    def capture_cmd(self):
        window.iconify()
        window.withdraw()
        self.create_canvas()
        self.capture_btn.wait_window(self.top)
        os.remove(self.tmp_img)
        self.ocr_text = self.baidu_ocr(self.capture_img)
        if (self.ocr_text):
            self.text_box.delete(1.0, tk.END)
            self.tran_text_box.delete(1.0, tk.END)
            self.text_box.insert(1.0, self.ocr_text)
            window.deiconify()
            os.remove(self.capture_img)
    
    def baidu_ocr(self, file):
        app_id = '19890128'
        api_key = 'BqvwEKnyBhHX6QAj0Ezc2KH7'
        secret_key = '2wQh1smTldG9qvKdUKvZe5uXhb6L1o59'
        ocr_text = ''
        if os.path.isfile(file):
            with open(file, 'rb') as f:
                image = f.read()
            ocr_ret = aip.AipOcr(app_id, api_key, secret_key).basicGeneral(image)
            words = ocr_ret.get('words_result')
            print(words)
            if words is not None and len(words):
                for word in words:
                    ocr_text += word['words'] + '\n'
                return ocr_text
        return None

    def translate_cmd(self):
        if self.ocr_text:
            self.translate_text = self.baidu_translate(self.ocr_text)
            self.tran_text_box.delete(1.0, tk.END)
            if self.translate_text:
                self.tran_text_box.insert('end', self.translate_text)

    def baidu_translate(self, content):
        app_id = '20200515000455294'
        secret_key = 'TH9UQhQX1yMCQzbVsPaa'
        http_client = None
        myurl = '/api/trans/vip/translate'
        q = content
        from_lang = self.from_lang
        to_lang = self.to_lang
        salt = random.randint(32768, 65536)
        sign = app_id + q + str(salt) + secret_key
        sign = hashlib.md5(sign.encode()).hexdigest()
        myurl = myurl + '?appid=' + app_id + '&q=' + urllib.parse.quote(q) + \
                '&from=' + from_lang + '&to=' + to_lang + '&salt=' + str(salt) + '&sign=' + sign
        
        try:
            http_client = http.client.HTTPConnection('api.fanyi.baidu.com')
            http_client.request('GET', myurl)
            response = http_client.getresponse()
            json_response = response.read().decode('utf-8')
            js = json.loads(json_response)
            dst = str(js["trans_result"][0]["dst"])
            return dst
        except Exception as e:
            print(e)
            return None
        finally:
            if http_client:
                http_client.close()
    
    def get_from_lang(self, event):
        self.from_lang = self.lang_dic[self.from_lang_box.get()]
    
    def get_to_lang(self, event):
        self.to_lang = self.lang_dic[self.to_lang_box.get()]

window = tk.Tk()
window.title('GUI')
window.geometry('400x420')
gui = GUI()
window.mainloop()
