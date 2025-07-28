import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk, ImageFilter, ImageEnhance, ImageOps
import os

class ImageProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Image Processing Tool")
        self.root.geometry("1368x768")  # Initial size, now resizable
        
        # Set custom style
        self.style = ttk.Style()
        self.style.theme_use('clam')  # Use a modern theme
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("TLabel", background="#f0f0f0", font=("Arial", 10))
        self.style.configure("TButton", background="#4a90e2", foreground="white", font=("Arial", 10, "bold"))
        self.style.map("TButton", background=[("active", "#357abd")])
        self.style.configure("TScale", background="#f0f0f0")
        self.style.configure("TCombobox", fieldbackground="#ffffff", background="#4a90e2", foreground="white")

        # Initialize variables
        self.image = None
        self.original_image = None
        self.image_path = ""
        self.grayscale_var = tk.DoubleVar(value=0)
        self.blur_var = tk.DoubleVar(value=0)
        self.contrast_var = tk.DoubleVar(value=1)
        self.brightness_var = tk.DoubleVar(value=1)
        self.sharpen_var = tk.DoubleVar(value=0)
        self.saturation_var = tk.DoubleVar(value=1)
        self.edge_enhance_var = tk.DoubleVar(value=0)
        self.rotation_var = tk.DoubleVar(value=0)
        self.resolution_var = tk.StringVar(value="1920x1080 (16:9)")
        
        # Create GUI elements
        self.create_widgets()
        
    def create_widgets(self):
        # Main frame with two columns
        self.main_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Left frame for image preview
        self.left_frame = tk.Frame(self.main_frame, bg="#f0f0f0")
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Title label
        title_label = ttk.Label(self.left_frame, text="Image Processing Tool", font=("Arial", 14, "bold"), background="#f0f0f0", foreground="#2e2e2e")
        title_label.pack(pady=(0, 10))

        # Image display
        self.canvas_frame = tk.Frame(self.left_frame, bg="#d3d3d3", bd=2, relief="sunken")
        self.canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.canvas = tk.Canvas(self.canvas_frame, bg="#d3d3d3", highlightthickness=2, highlightbackground="#4a90e2")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Configure>", self.on_canvas_resize)  # Bind resize event

        # Right frame for controls
        self.right_frame = tk.Frame(self.main_frame, bg="#f0f0f0")
        self.right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)

        # Controls frame with border
        self.controls_frame = tk.Frame(self.right_frame, bg="#f0f0f0", bd=2, relief="groove")
        self.controls_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # Button frame
        self.button_frame = tk.Frame(self.controls_frame, bg="#f0f0f0")
        self.button_frame.pack(pady=5)

        # Buttons
        ttk.Button(self.button_frame, text="Load Image", command=self.load_image, style="TButton").pack(side=tk.TOP, padx=5, pady=2)
        ttk.Button(self.button_frame, text="Reset", command=self.reset_image, style="TButton").pack(side=tk.TOP, padx=5, pady=2)
        ttk.Button(self.button_frame, text="Save Image", command=self.save_image, style="TButton").pack(side=tk.TOP, padx=5, pady=2)

        # Sliders frame with border
        self.sliders_frame = tk.Frame(self.controls_frame, bg="#f0f0f0", bd=1, relief="ridge")
        self.sliders_frame.pack(fill=tk.BOTH, expand=True, pady=2)

        # Sliders, value labels, and entry fields
        # Grayscale
        ttk.Label(self.sliders_frame, text="Grayscale", style="TLabel").grid(row=0, column=0, sticky=tk.W, padx=5, pady=1)
        ttk.Scale(self.sliders_frame, from_=0, to=1, orient=tk.HORIZONTAL, 
                 variable=self.grayscale_var, command=self.apply_filters, length=200).grid(row=0, column=1, padx=5, pady=1, sticky='ew')
        self.grayscale_value = ttk.Label(self.sliders_frame, text="0.00", style="TLabel")
        self.grayscale_value.grid(row=0, column=2, padx=5, pady=1)
        self.grayscale_entry = tk.Entry(self.sliders_frame, width=6, bg="#ffffff")
        self.grayscale_entry.grid(row=0, column=3, padx=5, pady=1)
        self.grayscale_entry.insert(0, "0.00")
        self.grayscale_var.trace("w", lambda *args: self.update_value_label(self.grayscale_var, self.grayscale_value, self.grayscale_entry, 0, 1))
        self.grayscale_entry.bind("<Return>", lambda event: self.update_from_entry(self.grayscale_var, self.grayscale_entry, 0, 1))

        # Blur
        ttk.Label(self.sliders_frame, text="Blur", style="TLabel").grid(row=1, column=0, sticky=tk.W, padx=5, pady=1)
        ttk.Scale(self.sliders_frame, from_=0, to=10, orient=tk.HORIZONTAL, 
                 variable=self.blur_var, command=self.apply_filters, length=200).grid(row=1, column=1, padx=5, pady=1, sticky='ew')
        self.blur_value = ttk.Label(self.sliders_frame, text="0.00", style="TLabel")
        self.blur_value.grid(row=1, column=2, padx=5, pady=1)
        self.blur_entry = tk.Entry(self.sliders_frame, width=6, bg="#ffffff")
        self.blur_entry.grid(row=1, column=3, padx=5, pady=1)
        self.blur_entry.insert(0, "0.00")
        self.blur_var.trace("w", lambda *args: self.update_value_label(self.blur_var, self.blur_value, self.blur_entry, 0, 10))
        self.blur_entry.bind("<Return>", lambda event: self.update_from_entry(self.blur_var, self.blur_entry, 0, 10))

        # Contrast
        ttk.Label(self.sliders_frame, text="Contrast", style="TLabel").grid(row=2, column=0, sticky=tk.W, padx=5, pady=1)
        ttk.Scale(self.sliders_frame, from_=0.1, to=3, orient=tk.HORIZONTAL, 
                 variable=self.contrast_var, command=self.apply_filters, length=200).grid(row=2, column=1, padx=5, pady=1, sticky='ew')
        self.contrast_value = ttk.Label(self.sliders_frame, text="0.33", style="TLabel")
        self.contrast_value.grid(row=2, column=2, padx=5, pady=1)
        self.contrast_entry = tk.Entry(self.sliders_frame, width=6, bg="#ffffff")
        self.contrast_entry.grid(row=2, column=3, padx=5, pady=1)
        self.contrast_entry.insert(0, "0.33")
        self.contrast_var.trace("w", lambda *args: self.update_value_label(self.contrast_var, self.contrast_value, self.contrast_entry, 0.1, 3))
        self.contrast_entry.bind("<Return>", lambda event: self.update_from_entry(self.contrast_var, self.contrast_entry, 0.1, 3))

        # Brightness
        ttk.Label(self.sliders_frame, text="Brightness", style="TLabel").grid(row=3, column=0, sticky=tk.W, padx=5, pady=1)
        ttk.Scale(self.sliders_frame, from_=0.1, to=3, orient=tk.HORIZONTAL, 
                 variable=self.brightness_var, command=self.apply_filters, length=200).grid(row=3, column=1, padx=5, pady=1, sticky='ew')
        self.brightness_value = ttk.Label(self.sliders_frame, text="0.33", style="TLabel")
        self.brightness_value.grid(row=3, column=2, padx=5, pady=1)
        self.brightness_entry = tk.Entry(self.sliders_frame, width=6, bg="#ffffff")
        self.brightness_entry.grid(row=3, column=3, padx=5, pady=1)
        self.brightness_entry.insert(0, "0.33")
        self.brightness_var.trace("w", lambda *args: self.update_value_label(self.brightness_var, self.brightness_value, self.brightness_entry, 0.1, 3))
        self.brightness_entry.bind("<Return>", lambda event: self.update_from_entry(self.brightness_var, self.brightness_entry, 0.1, 3))

        # Sharpen
        ttk.Label(self.sliders_frame, text="Sharpen", style="TLabel").grid(row=4, column=0, sticky=tk.W, padx=5, pady=1)
        ttk.Scale(self.sliders_frame, from_=0, to=5, orient=tk.HORIZONTAL, 
                 variable=self.sharpen_var, command=self.apply_filters, length=200).grid(row=4, column=1, padx=5, pady=1, sticky='ew')
        self.sharpen_value = ttk.Label(self.sliders_frame, text="0.00", style="TLabel")
        self.sharpen_value.grid(row=4, column=2, padx=5, pady=1)
        self.sharpen_entry = tk.Entry(self.sliders_frame, width=6, bg="#ffffff")
        self.sharpen_entry.grid(row=4, column=3, padx=5, pady=1)
        self.sharpen_entry.insert(0, "0.00")
        self.sharpen_var.trace("w", lambda *args: self.update_value_label(self.sharpen_var, self.sharpen_value, self.sharpen_entry, 0, 5))
        self.sharpen_entry.bind("<Return>", lambda event: self.update_from_entry(self.sharpen_var, self.sharpen_entry, 0, 5))

        # Saturation
        ttk.Label(self.sliders_frame, text="Saturation", style="TLabel").grid(row=5, column=0, sticky=tk.W, padx=5, pady=1)
        ttk.Scale(self.sliders_frame, from_=0, to=2, orient=tk.HORIZONTAL, 
                 variable=self.saturation_var, command=self.apply_filters, length=200).grid(row=5, column=1, padx=5, pady=1, sticky='ew')
        self.saturation_value = ttk.Label(self.sliders_frame, text="0.50", style="TLabel")
        self.saturation_value.grid(row=5, column=2, padx=5, pady=1)
        self.saturation_entry = tk.Entry(self.sliders_frame, width=6, bg="#ffffff")
        self.saturation_entry.grid(row=5, column=3, padx=5, pady=1)
        self.saturation_entry.insert(0, "0.50")
        self.saturation_var.trace("w", lambda *args: self.update_value_label(self.saturation_var, self.saturation_value, self.saturation_entry, 0, 2))
        self.saturation_entry.bind("<Return>", lambda event: self.update_from_entry(self.saturation_var, self.saturation_entry, 0, 2))

        # Edge Enhancement
        ttk.Label(self.sliders_frame, text="Edge Enhance", style="TLabel").grid(row=6, column=0, sticky=tk.W, padx=5, pady=1)
        ttk.Scale(self.sliders_frame, from_=0, to=5, orient=tk.HORIZONTAL, 
                 variable=self.edge_enhance_var, command=self.apply_filters, length=200).grid(row=6, column=1, padx=5, pady=1, sticky='ew')
        self.edge_enhance_value = ttk.Label(self.sliders_frame, text="0.00", style="TLabel")
        self.edge_enhance_value.grid(row=6, column=2, padx=5, pady=1)
        self.edge_enhance_entry = tk.Entry(self.sliders_frame, width=6, bg="#ffffff")
        self.edge_enhance_entry.grid(row=6, column=3, padx=5, pady=1)
        self.edge_enhance_entry.insert(0, "0.00")
        self.edge_enhance_var.trace("w", lambda *args: self.update_value_label(self.edge_enhance_var, self.edge_enhance_value, self.edge_enhance_entry, 0, 5))
        self.edge_enhance_entry.bind("<Return>", lambda event: self.update_from_entry(self.edge_enhance_var, self.edge_enhance_entry, 0, 5))

        # Rotation
        ttk.Label(self.sliders_frame, text="Rotation (degrees)", style="TLabel").grid(row=7, column=0, sticky=tk.W, padx=5, pady=1)
        ttk.Scale(self.sliders_frame, from_=0, to=360, orient=tk.HORIZONTAL, 
                 variable=self.rotation_var, command=self.apply_filters, length=200).grid(row=7, column=1, padx=5, pady=1, sticky='ew')
        self.rotation_value = ttk.Label(self.sliders_frame, text="0", style="TLabel")
        self.rotation_value.grid(row=7, column=2, padx=5, pady=1)
        self.rotation_entry = tk.Entry(self.sliders_frame, width=6, bg="#ffffff")
        self.rotation_entry.grid(row=7, column=3, padx=5, pady=1)
        self.rotation_entry.insert(0, "0")
        self.rotation_var.trace("w", lambda *args: self.update_rotation_label(self.rotation_var, self.rotation_value, self.rotation_entry))
        self.rotation_entry.bind("<Return>", lambda event: self.update_from_rotation_entry(self.rotation_var, self.rotation_entry))

        # Crop and resize frame with border
        self.crop_frame = tk.Frame(self.controls_frame, bg="#f0f0f0", bd=1, relief="ridge")
        self.crop_frame.pack(fill=tk.X, pady=5)
        ttk.Button(self.crop_frame, text="Crop Center (50%)", command=self.crop_image, style="TButton").pack(side=tk.LEFT, padx=5, pady=2)
        ttk.Label(self.crop_frame, text="Resolution:", style="TLabel").pack(side=tk.LEFT, padx=5)
        resolutions = [
            "1920x1080 (16:9)", "1280x720 (16:9)", "854x480 (16:9)",
            "1600x1200 (4:3)", "1024x768 (4:3)", "800x600 (4:3)"
        ]
        self.resolution_menu = ttk.Combobox(self.crop_frame, textvariable=self.resolution_var, values=resolutions, state="readonly", width=15, style="TCombobox")
        self.resolution_menu.pack(side=tk.LEFT, padx=5)
        ttk.Button(self.crop_frame, text="Apply Resize", command=self.resize_image, style="TButton").pack(side=tk.LEFT, padx=5, pady=2)

        # Status label
        self.status_label = ttk.Label(self.right_frame, text="No image loaded", font=("Arial", 12, "bold"), background="#f0f0f0", foreground="#2e2e2e")
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X, pady=10)

        # Configure grid columns for resizing
        for i in range(1, 4):
            self.sliders_frame.grid_columnconfigure(i, weight=1)

    def on_canvas_resize(self, event):
        # Redraw image when canvas resizes
        if self.image:
            self.display_image(self.image)

    def update_value_label(self, var, label, entry, min_val, max_val):
        # Normalize the slider value to 0-1 range and update label and entry
        value = var.get()
        normalized = (value - min_val) / (max_val - min_val) if max_val != min_val else 0
        label.config(text=f"{normalized:.2f}")
        entry.delete(0, tk.END)
        entry.insert(0, f"{normalized:.2f}")

    def update_rotation_label(self, var, label, entry):
        # Update rotation label and entry with degree value
        value = var.get()
        label.config(text=f"{int(value)}")
        entry.delete(0, tk.END)
        entry.insert(0, f"{int(value)}")

    def update_from_entry(self, var, entry, min_val, max_val):
        # Update slider from normalized entry value (0-1)
        try:
            normalized = float(entry.get())
            if 0 <= normalized <= 1:
                value = min_val + normalized * (max_val - min_val)
                var.set(value)
                self.apply_filters()
            else:
                messagebox.showwarning("Invalid Input", "Please enter a value between 0 and 1")
        except ValueError:
            messagebox.showwarning("Invalid Input", "Please enter a valid number")

    def update_from_rotation_entry(self, var, entry):
        # Update rotation slider from degree entry value (0-360)
        try:
            degrees = float(entry.get())
            if 0 <= degrees <= 360:
                var.set(degrees)
                self.apply_filters()
            else:
                messagebox.showwarning("Invalid Input", "Please enter a value between 0 and 360 degrees")
        except ValueError:
            messagebox.showwarning("Invalid Input", "Please enter a valid number")

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
                # Reset sliders and entries
                self.grayscale_var.set(0)
                self.blur_var.set(0)
                self.contrast_var.set(1)
                self.brightness_var.set(1)
                self.sharpen_var.set(0)
                self.saturation_var.set(1)
                self.edge_enhance_var.set(0)
                self.rotation_var.set(0)
                self.resolution_var.set("1920x1080 (16:9)")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load image: {e}")

    def display_image(self, image):
        if image:
            # Get current canvas size
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            # Calculate aspect ratio and scale image
            img_width, img_height = image.size
            aspect = img_width / img_height
            if canvas_width / canvas_height > aspect:
                new_height = canvas_height
                new_width = int(new_height * aspect)
            else:
                new_width = canvas_width
                new_height = int(new_width / aspect)
            
            # Resize image and display
            resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            self.photo = ImageTk.PhotoImage(resized_image)
            self.canvas.delete("all")
            self.canvas.create_image(canvas_width // 2, canvas_height // 2, image=self.photo, anchor="center")

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
                self.saturation_var.set(1)
                self.edge_enhance_var.set(0)
                self.rotation_var.set(0)
                self.resolution_var.set("1920x1080 (16:9)")
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

                # Apply saturation
                if self.saturation_var.get() != 1:
                    enhancer = ImageEnhance.Color(self.image)
                    self.image = enhancer.enhance(self.saturation_var.get())

                # Apply edge enhancement
                if self.edge_enhance_var.get() > 0:
                    self.image = self.image.filter(ImageFilter.EDGE_ENHANCE)
                    if self.edge_enhance_var.get() > 1:
                        enhancer = ImageEnhance.Sharpness(self.image)
                        self.image = enhancer.enhance(self.edge_enhance_var.get() / 2)  # Scale for smoother effect

                self.display_image(self.image)
                self.status_label.config(text="Applied filters")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to apply filters: {e}")

    def resize_image(self):
        if self.original_image:
            try:
                resolution = self.resolution_var.get()
                width, height = map(int, resolution.split(" ")[0].split("x"))
                self.original_image = self.original_image.resize((width, height), Image.Resampling.LANCZOS)
                self.apply_filters()
                self.status_label.config(text=f"Resized image to {resolution}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to resize image: {e}")

    def crop_image(self):
        if self.original_image:
            try:
                width, height = self.original_image.size
                left = int(width * 0.25)
                top = int(height * 0.25)
                right = int(width * 0.75)
                bottom = int(height * 0.75)
                self.original_image = self.original_image.crop((left, top, right, bottom))
                self.apply_filters()
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