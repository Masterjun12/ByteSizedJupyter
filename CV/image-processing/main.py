import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
import cv2
import image_filters

im1 = None
im2 = None

def load_img():
    global im1, im2
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp")])
    if not file_path:
        return
    im1_temp = cv2.imread(file_path)
    if im1_temp is None:
        messagebox.showerror("오류", "이미지를 불러올 수 없습니다.")
        return
    im1 = im1_temp
    im2 = None

    im_tk = ImageTk.PhotoImage(Image.fromarray(im1[:, :, ::-1]))
    label1.config(image=im_tk)
    label1.image = im_tk
    label2.config(image="")
    label3.config(image="")

def apply_filter(filter_name):
    global im1, im2
    if im1 is None:
        messagebox.showwarning("경고", "이미지를 먼저 불러오세요.")
        return

    if filter_name == "머지":

        file_path = filedialog.askopenfilename(title="두 번째 이미지 선택", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp")])
        if not file_path:
            return
        im2_temp = cv2.imread(file_path)
        if im2_temp is None:
            messagebox.showerror("오류", "두 번째 이미지를 불러올 수 없습니다.")
            return
        im2 = im2_temp

        im2_tk = ImageTk.PhotoImage(Image.fromarray(im2[:, :, ::-1]))
        label2.config(image=im2_tk)
        label2.image = im2_tk

        try:
            func = getattr(image_filters, filter_name)
            result = func(im1, im2)
        except Exception as e:
            messagebox.showerror("오류", f"{filter_name} 처리 중 오류 발생: {e}")
            return

        # 결과 이미지 출력
        result_tk = ImageTk.PhotoImage(Image.fromarray(result[:, :, ::-1]))
        label3.config(image=result_tk)
        label3.image = result_tk

    else:
        try:
            func = getattr(image_filters, filter_name)
            result = func(im1)
        except Exception as e:
            messagebox.showerror("오류", f"{filter_name} 처리 중 오류 발생: {e}")
            return

        result_tk = ImageTk.PhotoImage(Image.fromarray(result[:, :, ::-1]))
        label2.config(image=result_tk)
        label2.image = result_tk

        label3.config(image="")

def exit_app():
    win.quit()

def say_hello():
    messagebox.showinfo("인사", "안녕하세요!")

win = tk.Tk()
win.title("영상처리 알고리즘")
win.geometry("1200x450")  

menubar = tk.Menu(win)
win.config(menu=menubar)

file_menu = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label="파일", menu=file_menu)
file_menu.add_command(label='열기', command=load_img)
file_menu.add_separator()
file_menu.add_command(label='종료', command=exit_app)

region_menu = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label='영역처리', menu=region_menu)

for name in image_filters.filter_list:
    region_menu.add_command(label=name, command=lambda n=name: apply_filter(n))

etc_menu = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label="기타", menu=etc_menu)
etc_menu.add_command(label="인사하기", command=say_hello)

frame = tk.Frame(win)
frame.pack()

label1 = tk.Label(frame)
label1.pack(side="left", padx=10, pady=10)

label2 = tk.Label(frame)
label2.pack(side="left", padx=10, pady=10)

label3 = tk.Label(frame)
label3.pack(side="left", padx=10, pady=10)

win.mainloop()
