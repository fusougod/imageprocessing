import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk, ImageFilter, ImageEnhance, ImageOps
import os

class ImageProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Image Processing Tool")
        self.root.geometry("900x700")
        
        # Initialize variables
        self.image = None
        self.original_image = None
        self.image_path = ""
        
        # Create GUI elements
        self.create_widgets()
        
    def create_widgets(self):
        # Create main frame
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Image display
        self.canvas = tk.Canvas(self.main_frame, width=600, height=400, bg="gray")
        self.canvas.pack(pady=10)
        
        # Controls frame
        self.controls_frame = tk.Frame(self.main_frame)
        self.controls_frame.pack(fill=tk.X, pady=5)
        
        # Button frame
        self.button_frame = tk.Frame(self.controls_frame)
        self.button_frame.pack(pady=5)
        
        # Buttons
        tk.Button(self.button_frame, text="Load Image", command=self.load_image).pack(side=tk.LEFT, padx=5)
        tk.Button(self.button_frame, text="Reset", command=self.reset_image).pack(side=tk.LEFT, padx=5)
        tk.Button(self.button_frame, text="Save Image", command=self.save_image).pack(side=tk.LEFT, padx=5)
        
        # Sliders frame
        self.sliders_frame = tk.Frame(self.controls_frame)
        self.sliders_frame.pack(fill=tk.X, pady=2)
        
        # Sliders and value labels
        # Grayscale
        self.grayscale_var = tk.DoubleVar(value=0)
        tk.Label(self.sliders_frame, text="Grayscale").grid(row=0, column=0, sticky=tk.W, padx=5, pady=1)
        ttk.Scale(self.sliders_frame, from_=0, to=1, orient=tk.HORIZONTAL, 
                 variable=self.grayscale_var, command=self.apply_filters, length=200).grid(row=0, column=1, padx=5, pady=1)
        self.grayscale_value = tk.Label(self.sliders_frame, text="0.00")
        self.grayscale_value.grid(row=0, column=2, padx=5, pady=1)
        self.grayscale_var.trace("w", lambda *args: self.update_value_label(self.grayscale_var, self.grayscale_value, 0, 1))
        
        # Blur
        self.blur_var = tk.DoubleVar(value=0)
        tk.Label(self.sliders_frame, text="Blur").grid(row=1, column=0, sticky=tk.W, padx=5, pady=1)
        ttk.Scale(self.sliders_frame, from_=0, to=10, orient=tk.HORIZONTAL, 
                 variable=self.blur_var, command=self.apply_filters, length=200).grid(row=1, column=1, padx=5, pady=1)
        self.blur_value = tk.Label(self.sliders_frame, text="0.00")
        self.blur_value.grid(row=1, column=2, padx=5, pady=1)
        self.blur_var.trace("w", lambda *args: self.update_value_label(self.blur_var, self.blur_value, 0, 10))
        
        # Contrast
        self.contrast_var = tk.DoubleVar(value=1)
        tk.Label(self.sliders_frame, text="Contrast").grid(row=2, column=0, sticky=tk.W, padx=5, pady=1)
        ttk.Scale(self.sliders_frame, from_=0.1, to=3, orient=tk.HORIZONTAL, 
                 variable=self.contrast_var, command=self.apply_filters, length=200).grid(row=2, column=1, padx=5, pady=1)
        self.contrast_value = tk.Label(self.sliders_frame, text="0.33")
        self.contrast_value.grid(row=2, column=2, padx=5, pady=1)
        self.contrast_var.trace("w", lambda *args: self.update_value_label(self.contrast_var, self.contrast_value, 0.1, 3))
        
        # Brightness
        self.brightness_var = tk.DoubleVar(value=1)
        tk.Label(self.sliders_frame, text="Brightness").grid(row=3, column=0, sticky=tk.W, padx=5, pady=1)
        ttk.Scale(self.sliders_frame, from_=0.1, to=3, orient=tk.HORIZONTAL, 
                 variable=self.brightness_var, command=self.apply_filters, length=200).grid(row=3, column=1, padx=5, pady=1)
        self.brightness_value = tk.Label(self.sliders_frame, text="0.33")
        self.brightness_value.grid(row=3, column=2, padx=5, pady=1)
        self.brightness_var.trace("w", lambda *args: self.update_value_label(self.brightness_var, self.brightness_value, 0.1, 3))
        
        # Sharpen
        self.sharpen_var = tk.DoubleVar(value=0)
        tk.Label(self.sliders_frame, text="Sharpen").grid(row=4, column=0, sticky=tk.W, padx=5, pady=1)
        ttk.Scale(self.sliders_frame, from_=0, to=5, orient=tk.HORIZONTAL, 
                 variable=self.sharpen_var, command=self.apply_filters, length=200).grid(row=4, column=1, padx=5, pady=1)
        self.sharpen_value = tk.Label(self.sliders_frame, text="0.00")
        self.sharpen_value.grid(row=4, column=2, padx=5, pady=1)
        self.sharpen_var.trace("w", lambda *args: self.update_value_label(self.sharpen_var, self.sharpen_value, 0, 5))
        
        # Rotation
        self.rotation_var = tk.DoubleVar(value=0)
        tk.Label(self.sliders_frame, text="Rotation").grid(row=5, column=0, sticky=tk.W, padx=5, pady=1)
        ttk.Scale(self.sliders_frame, from_=0, to=360, orient=tk.HORIZONTAL, 
                 variable=self.rotation_var, command=self.apply_filters, length=200).grid(row=5, column=1, padx=5, pady=1)
        self.rotation_value = tk.Label(self.sliders_frame, text="0.00")
        self.rotation_value.grid(row=5, column=2, padx=5, pady=1)
        self.rotation_var.trace("w", lambda *args: self.update_value_label(self.rotation_var, self.rotation_value, 0, 360))
        
        # Crop frame
        self.crop_frame = tk.Frame(self.controls_frame)
        self.crop_frame.pack(fill=tk.X, pady=5)
        tk.Button(self.crop_frame, text="Crop Center (50%)", command=self.crop_image).pack(side=tk.LEFT, padx=5)
        tk.Button(self.crop_frame, text="Resize (50%)", command=self.resize_image).pack(side=tk.LEFT, padx=5)
        
        # Status label
        self.status_label = tk.Label(self.main_frame, text="No image loaded", font=("Arial", 12))
        self.status_label.pack(pady=10)
        
    def update_value_label(self, var, label, min_val, max_val):
        # Normalize the slider value to 0-1 range
        value = var.get()
        normalized = (value - min_val) / (max_val - min_val) if max_val != min_val else 0
        label.config(text=f"{normalized:.2f}")
        
    def load_image(self):
        self.image_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp")]
        )
        if self.image_path:
            try:
                self.original_image = Image.open(self.image_path).convert("RGB")
                self.image = self.original_image.copy()
                self.display_image(self.image)
                self.status_label.config(text=f"Loaded: {os.path.basename(self.image_path)}")
                # Reset sliders
                self.grayscale_var.set(0)
                self.blur_var.set(0)
                self.contrast_var.set(1)
                self.brightness_var.set(1)
                self.sharpen_var.set(0)
                self.rotation_var.set(0)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load image: {e}")
                
    def display_image(self, image):
        max_size = (600, 400)
        image.thumbnail(max_size, Image.Resampling.LANCZOS)
        self.photo = ImageTk.PhotoImage(image)
        self.canvas.delete("all")
        self.canvas.create_image(300, 200, image=self.photo, anchor="center")
        
    def reset_image(self):
        if self.original_image:
            try:
                self.image = self.original_image.copy()
                self.display_image(self.image)
                self.status_label.config(text="Image reset to original")
                self.grayscale_var.set(0)
                self.blur_var.set(0)
                self.contrast_var.set(1)
                self.brightness_var.set(1)
                self.sharpen_var.set(0)
                self.rotation_var.set(0)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to reset image: {e}")
                
    def apply_filters(self, *args):
        if self.original_image:
            try:
                self.image = self.original_image.copy()
                
                # Apply rotation
                if self.rotation_var.get() > 0:
                    self.image = self.image.rotate(self.rotation_var.get(), expand=True, resample=Image.Resampling.BICUBIC)
                
                # Apply grayscale
                if self.grayscale_var.get() > 0:
                    grayscale_image = self.image.convert("L").convert("RGB")
                    if self.image.size != grayscale_image.size:
                        grayscale_image = grayscale_image.resize(self.image.size, Image.Resampling.LANCZOS)
                    self.image = Image.blend(self.image, grayscale_image, self.grayscale_var.get())
                
                # Apply blur
                if self.blur_var.get() > 0:
                    self.image = self.image.filter(
                        ImageFilter.GaussianBlur(radius=self.blur_var.get())
                    )
                
                # Apply contrast
                if self.contrast_var.get() != 1:
                    enhancer = ImageEnhance.Contrast(self.image)
                    self.image = enhancer.enhance(self.contrast_var.get())
                
                # Apply brightness
                if self.brightness_var.get() != 1:
                    enhancer = ImageEnhance.Brightness(self.image)
                    self.image = enhancer.enhance(self.brightness_var.get())
                
                # Apply sharpen
                if self.sharpen_var.get() > 0:
                    enhancer = ImageEnhance.Sharpness(self.image)
                    self.image = enhancer.enhance(self.sharpen_var.get())
                
                self.display_image(self.image)
                self.status_label.config(text="Applied filters")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to apply filters: {e}")
                
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