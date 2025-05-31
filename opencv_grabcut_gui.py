import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import numpy as np
import logging
import os
from datetime import datetime

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('background_removal.log'),
        logging.StreamHandler()
    ]
)

class GrabCutGUI:
    def __init__(self, root):
        self.root = root
        self.root.title('OpenCV GrabCut 배경 제거')
        self.root.geometry('900x600')
        self.logger = logging.getLogger(__name__)
        self.logger.info('GrabCut GUI initialized')

        self.image_path = None
        self.original_image = None
        self.display_image = None
        self.rect = None
        self.rect_id = None
        self.start_x = None
        self.start_y = None
        self.end_x = None
        self.end_y = None
        self.result_image = None

        self.create_widgets()

    def create_widgets(self):
        # 파일 선택 버튼
        btn_select = tk.Button(self.root, text='이미지 선택', command=self.select_image)
        btn_select.pack(pady=10)

        # 캔버스 (이미지 표시 및 박스 그리기)
        self.canvas = tk.Canvas(self.root, width=600, height=400, cursor='cross')
        self.canvas.pack()
        self.canvas.bind('<ButtonPress-1>', self.on_mouse_down)
        self.canvas.bind('<B1-Motion>', self.on_mouse_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_mouse_up)

        # 배경 제거 버튼
        btn_cut = tk.Button(self.root, text='배경 제거', command=self.run_grabcut)
        btn_cut.pack(pady=10)

        # 저장 버튼
        btn_save = tk.Button(self.root, text='결과 저장', command=self.save_result)
        btn_save.pack(pady=10)

        # 상태 표시
        self.status_var = tk.StringVar()
        self.status_var.set('이미지를 선택하세요.')
        lbl_status = tk.Label(self.root, textvariable=self.status_var)
        lbl_status.pack(pady=5)

    def select_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[('Image files', '*.jpg *.jpeg *.png *.bmp *.gif')]
        )
        if file_path:
            self.image_path = file_path
            self.logger.info(f'Selected image: {file_path}')
            self.status_var.set(f'이미지 선택됨: {os.path.basename(file_path)}')
            self.load_image()

    def load_image(self):
        img = cv2.imread(self.image_path)
        if img is None:
            messagebox.showerror('오류', '이미지를 불러올 수 없습니다.')
            return
        self.original_image = img
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)
        img_pil.thumbnail((600, 400))
        self.display_image = img_pil
        self.tk_image = ImageTk.PhotoImage(img_pil)
        self.canvas.delete('all')
        self.canvas.create_image(0, 0, anchor='nw', image=self.tk_image)
        self.rect = None
        self.rect_id = None
        self.result_image = None

    def on_mouse_down(self, event):
        if self.display_image is None:
            return
        self.start_x = event.x
        self.start_y = event.y
        if self.rect_id:
            self.canvas.delete(self.rect_id)
        self.rect_id = None

    def on_mouse_drag(self, event):
        if self.display_image is None or self.start_x is None or self.start_y is None:
            return
        if self.rect_id:
            self.canvas.delete(self.rect_id)
        self.rect_id = self.canvas.create_rectangle(
            self.start_x, self.start_y, event.x, event.y, outline='red', width=2
        )

    def on_mouse_up(self, event):
        if self.display_image is None or self.start_x is None or self.start_y is None:
            return
        self.end_x = event.x
        self.end_y = event.y
        self.rect = (self.start_x, self.start_y, self.end_x, self.end_y)
        self.logger.info(f'Rectangle selected: {self.rect}')
        self.status_var.set('박스를 그렸습니다. 배경 제거 버튼을 누르세요.')

    def run_grabcut(self):
        if self.rect is None or self.original_image is None:
            messagebox.showwarning('경고', '이미지와 박스를 모두 지정하세요.')
            return
        self.status_var.set('배경 제거 중...')
        self.logger.info('Running GrabCut...')
        # 원본 이미지와 썸네일 비율 계산
        img_h, img_w = self.original_image.shape[:2]
        disp_w, disp_h = self.display_image.size
        scale_x = img_w / disp_w
        scale_y = img_h / disp_h
        x1 = int(min(self.rect[0], self.rect[2]) * scale_x)
        y1 = int(min(self.rect[1], self.rect[3]) * scale_y)
        x2 = int(max(self.rect[0], self.rect[2]) * scale_x)
        y2 = int(max(self.rect[1], self.rect[3]) * scale_y)
        rect = (x1, y1, x2 - x1, y2 - y1)
        mask = np.zeros(self.original_image.shape[:2], np.uint8)
        bgdModel = np.zeros((1, 65), np.float64)
        fgdModel = np.zeros((1, 65), np.float64)
        cv2.grabCut(self.original_image, mask, rect, bgdModel, fgdModel, 5, cv2.GC_INIT_WITH_RECT)
        mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')
        img_cut = self.original_image * mask2[:, :, np.newaxis]
        # 투명 배경 PNG로 만들기
        b, g, r = cv2.split(img_cut)
        alpha = mask2 * 255
        result = cv2.merge((b, g, r, alpha))
        self.result_image = result
        # 미리보기
        preview = cv2.cvtColor(result, cv2.COLOR_BGRA2RGBA)
        preview_pil = Image.fromarray(preview)
        preview_pil.thumbnail((600, 400))
        self.tk_result = ImageTk.PhotoImage(preview_pil)
        self.canvas.create_image(0, 0, anchor='nw', image=self.tk_result)
        self.status_var.set('배경 제거 완료! 저장 버튼을 누르세요.')
        self.logger.info('GrabCut completed.')

    def save_result(self):
        if self.result_image is None:
            messagebox.showwarning('경고', '저장할 결과가 없습니다.')
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension='.png',
            filetypes=[('PNG files', '*.png')],
            initialfile=f'grabcut_result_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
        )
        if file_path:
            cv2.imwrite(file_path, self.result_image)
            self.logger.info(f'Result saved: {file_path}')
            self.status_var.set(f'저장 완료: {os.path.basename(file_path)}')
            messagebox.showinfo('완료', '이미지가 저장되었습니다.')


def main():
    root = tk.Tk()
    app = GrabCutGUI(root)
    root.mainloop()

if __name__ == '__main__':
    main() 