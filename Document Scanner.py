import cv2
import numpy as np
from tkinter import Tk, Label, Button, Entry, Image, StringVar, filedialog, messagebox, Frame, ttk
from PIL import Image, ImageTk

# ===================
width, height = 800, 500
img_no = 0
with open("resources/dimension.txt") as d:
    dimen = d.read()
    d.close()


# ===================
class DocumentScanner:
    def __init__(self, window):
        self.root = window
        self.root.title("Document Scanner")
        self.root.geometry(
            f"{width}x{height}+{int((self.root.winfo_screenwidth() - width) / 2)}+{int((self.root.winfo_screenheight() - height) / 2)}")

        self.root.iconbitmap(r"resources/icon.ico")
        self.root.resizable(False, False)
        self.root.config(background="white")
        self.cam_ind = StringVar()
        self.img_no = StringVar()
        self.paper = StringVar()
        self.dimen = StringVar()

        self.paper.set(dimen)
        self.img_no.set("0")
        backgrimg = Image.open("resources/background.jpg")
        self.background = ImageTk.PhotoImage(backgrimg)
        self.background_lbl = Label(self.root, image=self.background)
        self.background_lbl.place(x=-1, y=-1)
        self.scan_btn = Button(self.root, text="Scan", font=("courier new", 25), bg="#1B346D", fg="white", activeforeground="#1B346D",
               activebackground="white", cursor="hand2",
               relief="solid", bd=0, command=self.start_cam)
        self.scan_btn.place(x=int((width - 250) / 2), y=430, width=250, height=50)
        setimg = Image.open("resources/setting.jpg")
        setimg = setimg.resize((30, 30))
        self.setting_img = ImageTk.PhotoImage(setimg)
        self.sett_but = Button(self.root, image=self.setting_img, relief="flat", bd=0, cursor="hand2", command=self.setting)
        self.sett_but.place(x=(width - 40), y=10, width=30, height=30)
        self.root.mainloop()

    def start_cam(self):
        self.scan_btn.config(text="Scanning...", fg="#1B346D", bg="white")
        self.sett_but.update()
        self.root.iconify()
        self.camera()

    def drawRec(self, biggestNew, mainFrame):
        cv2.line(mainFrame, (biggestNew[0][0][0], biggestNew[0][0][1]), (biggestNew[1][0][0], biggestNew[1][0][1]),
                 (0, 255, 0), 20)
        cv2.line(mainFrame, (biggestNew[0][0][0], biggestNew[0][0][1]), (biggestNew[2][0][0], biggestNew[2][0][1]),
                 (0, 255, 0), 20)
        cv2.line(mainFrame, (biggestNew[3][0][0], biggestNew[3][0][1]), (biggestNew[2][0][0], biggestNew[2][0][1]),
                 (0, 255, 0), 20)
        cv2.line(mainFrame, (biggestNew[3][0][0], biggestNew[3][0][1]), (biggestNew[1][0][0], biggestNew[1][0][1]),
                 (0, 255, 0), 20)

    def scan(self, image):
        print(self.paper.get())
        if self.paper.get() == "ISO A3":
            w, h = 480, 640
        elif self.paper.get() == "ISO A4":
            w, h = 480, 640
        elif self.paper.get() == "ISO A6":
            w, h = 480, 800

        # image = cv2.imread("img3.jpg")

        imgWarp = image.copy()
        # write code here
        GrayImg = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        BlurredFrame = cv2.GaussianBlur(GrayImg, (5, 5), 1)
        CannyFrame = cv2.Canny(BlurredFrame, 190, 190)
        contours, _ = cv2.findContours(CannyFrame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        ContourFrame = image.copy()
        ContourFrame = cv2.drawContours(ContourFrame, contours, -1, (255, 0, 255), 4)
        CornerFrame = image.copy()
        maxArea = 0
        biggest = []
        for i in contours:
            area = cv2.contourArea(i)
            if area > 500:
                peri = cv2.arcLength(i, True)
                edges = cv2.approxPolyDP(i, 0.02 * peri, True)
                if area > maxArea and len(edges) == 4:
                    biggest = edges
                    maxArea = area
        if len(biggest) != 0:
            biggest = biggest.reshape((4, 2))
            biggestNew = np.zeros((4, 1, 2), dtype=np.int32)
            add = biggest.sum(1)
            biggestNew[0] = biggest[np.argmin(add)]
            biggestNew[3] = biggest[np.argmax(add)]
            dif = np.diff(biggest, axis=1)
            biggestNew[1] = biggest[np.argmin(dif)]
            biggestNew[2] = biggest[np.argmax(dif)]
            self.drawRec(biggestNew, CornerFrame)
            CornerFrame = cv2.drawContours(CornerFrame, biggestNew, -1, (255, 0, 255), 25)
            pts1 = np.float32(biggestNew)
            pts2 = np.float32([[0, 0], [w, 0], [0, h], [w, h]])
            matrix = cv2.getPerspectiveTransform(pts1, pts2)
            imgWarp = cv2.warpPerspective(image, matrix, (w, h))
            cv2.putText(imgWarp, "Enter to Save", (15, 23), cv2.FONT_ITALIC, 0.9, (250, 250, 250), 1)
            cv2.putText(imgWarp, "Escape to Re-Take", (15, 53), cv2.FONT_ITALIC, 0.9, (250, 250, 250), 1)
            cv2.imshow("Scanned Image", imgWarp)
        else:
            cv2.destroyAllWindows()
            messagebox.showerror("Document Scanner", "No document found.", parent=self.root)
            self.camera()
        key = cv2.waitKey(1)
        if key == 13:
            cv2.destroyAllWindows()
            path = filedialog.asksaveasfilename(title="Select Folder to save Image",
                                                initialfile="Scanned Doc " + str(self.img_no.get()),
                                                filetypes=[("Image", "*.jpg")], defaultextension=".jpg")
            if path:
                cv2.imwrite(path, imgWarp)
                messagebox.showinfo("Document Scanner", "Successfully saved image...!", parent=self.root)
                self.img_no.set(str(int(self.img_no.get()) + 1))

            else:
                print("User refused to save")
        elif key == 27:
            cv2.destroyAllWindows()
            self.camera()

    def camera(self):
        with open("resources/cam.txt") as cam:
            cam_index = cam.read()
            try:
                cam_index = int(cam_index)
            except:
                cam_index = str(cam_index)
            cam.close()
        camera = cv2.VideoCapture(cam_index)
        if camera:
            while True:
                _, image = camera.read()
                cv2.putText(image, "Enter to Scan | Esc to Exit", (15, 33), cv2.FONT_ITALIC, 1.2, (250, 250, 250), 1)
                cv2.imshow("Camera", image)
                key = cv2.waitKey(1)
                if key == 13:
                    _, scan_img = camera.read()
                    cv2.destroyAllWindows()
                    camera.release()
                    self.scan(scan_img)
                    cv2.destroyAllWindows()
                    self.root.deiconify()
                    self.scan_btn.config(text="Scan", bg="#1B346D", fg="white")
                    break
                elif key == 27:
                    cv2.destroyAllWindows()
                    camera.release()
                    self.root.deiconify()
                    self.scan_btn.config(text="Scan", bg="#1B346D", fg="white")
                    break

    def setting(self):
        self.sett_but.destroy()
        self.set = Frame(self.root, bg="white", bd=2, relief="solid")
        self.set.place(x=int((width - 400) / 2), y=int((height - 200) / 2), width=400, height=200)
        Button(self.set, text="X", font=("segoe new", 12), bg="white", fg="black", activebackground="red",
               activeforeground="white",
               relief="solid", bd=0, command=self.close).place(x=400 - 54, y=0, width=50, height=30)
        with open("resources/cam.txt", "r") as cam:
            a = cam.read()
            cam.close()

        self.cam_ind.set(a)

        lbl = Label(self.set, text="Camera Index :", font=("courier new", "15"), bg="white", fg="black")
        lbl.place(x=10, y=60)
        self.cam_entry = Entry(self.set, textvariable=self.cam_ind, font=("segoe ui", "12"), bg="white", fg="black",
                               width=15)
        self.cam_entry.place(x=200, y=60)

        lbl = Label(self.set, text="Paper Size :", font=("courier new", "15"), bg="white", fg="black")
        lbl.place(x=10, y=120)
        self.type = ttk.Combobox(self.set, font=("segoe ui", "12"),
                                 textvariable=self.paper, state="readonly", width=15)
        self.type.place(x=200, y=120)
        self.type['values'] = ("ISO A3", "ISO A4", "ISO A6")
        # self.type.current(1)

        self.set.mainloop()

    def close(self):

        with open("resources/cam.txt", "w") as cam:
            cam.write(self.cam_ind.get())
            cam.close()
        with open("resources/dimension.txt", "w") as d:
            d.write(self.paper.get())
            d.close()
        self.set.destroy()
        self.sett_but = Button(self.root, image=self.setting_img, relief="flat", bd=0, command=self.setting)
        self.sett_but.place(x=(width - 40), y=10, width=30, height=30)


if __name__ == "__main__":
    main = Tk()
    obj = DocumentScanner(main)
    main.mainloop()
