import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageFilter, ImageEnhance
import os

class ImageProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Processing Tool")
        self.root.geometry("800x600")
        
        # Initialize variables
        self.image = None
        self.original_image = None
        self.image_path = ""
        
        # Create GUI elements
        self.create_widgets()
        
    def create_widgets(self):
        # Image display
        self.canvas = tk.Canvas(self.root, width=600, height=400, bg="gray")
        self.canvas.pack(pady=10)
        
        # Button frame
        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(pady=10)
        
        # Buttons
        tk.Button(self.button_frame, text="Load Image", command=self.load_image).pack(side=tk.LEFT, padx=5)
        tk.Button(self.button_frame, text="Grayscale", command=self.apply_grayscale).pack(side=tk.LEFT, padx=5)
        tk.Button(self.button_frame, text="Blur", command=self.apply_blur).pack(side=tk.LEFT, padx=5)
        tk.Button(self.button_frame, text="Increase Contrast", command=self.apply_contrast).pack(side=tk.LEFT, padx=5)
        tk.Button(self.button_frame, text="Resize (50%)", command=self.resize_image).pack(side=tk.LEFT, padx=5)
        tk.Button(self.button_frame, text="Crop Center", command=self.crop_image).pack(side=tk.LEFT, padx=5)
        tk.Button(self.button_frame, text="Save Image", command=self.save_image).pack(side=tk.LEFT, padx=5)
        
        # Status label
        self.status_label = tk.Label(self.root, text="No image loaded", font=("Arial", 12))
        self.status_label.pack(pady=10)
        
    def load_image(self):
        self.image_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp")]
        )
        if self.image_path:
            try:
                self.original_image = Image.open(self.image_path)
                self.image = self.original_image.copy()
                self.display_image(self.image)
                self.status_label.config(text=f"Loaded: {os.path.basename(self.image_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load image: {e}")
                
    def display_image(self, image):
        # Resize image for display (maintain aspect ratio)
        max_size = (600, 400)
        image.thumbnail(max_size, Image.Resampling.LANCZOS)
        self.photo = ImageTk.PhotoImage(image)
        self.canvas.create_image(300, 200, image=self.photo, anchor="center")
        
    def apply_grayscale(self):
        if self.image:
            try:
                self.image = self.original_image.convert("L").convert("RGB")
                self.display_image(self.image)
                self.status_label.config(text="Applied grayscale filter")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to apply grayscale: {e}")
                
    def apply_blur(self):
        if self.image:
            try:
                self.image = self.original_image.filter(ImageFilter.GaussianBlur(radius=2))
                self.display_image(self.image)
                self.status_label.config(text="Applied blur filter")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to apply blur: {e}")
                
    def apply_contrast(self):
        if self.image:
            try:
                enhancer = ImageEnhance.Contrast(self.original_image)
                self.image = enhancer.enhance(1.5)  # Increase contrast by 50%
                self.display_image(self.image)
                self.status_label.config(text="Applied contrast enhancement")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to apply contrast: {e}")
                
    def resize_image(self):
        if self.image:
            try:
                width, height = self.original_image.size
                self.image = self.original_image.resize((width//2, height//2), Image.Resampling.LANCZOS)
                self.display_image(self.image)
                self.status_label.config(text="Resized image to 50%")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to resize image: {e}")
                
    def crop_image(self):
        if self.image:
            try:
                width, height = self.original_image.size
                left = width * 0.25
                top = height * 0.25
                right = width * 0.75
                bottom = height * 0.75
                self.image = self.original_image.crop((left, top, right, bottom))
                self.display_image(self.image)
                self.status_label.config(text="Cropped image to center")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to crop image: {e}")
                
    def save_image(self):
        if self.image:
            save_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg")]
            )
            if save_path:
                try:
                    self.image.save(save_path)
                    self.status_label.config(text=f"Saved image to {os.path.basename(save_path)}")
                    messagebox.showinfo("Success", "Image saved successfully!")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to save image: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageProcessorApp(root)
    root.mainloop()