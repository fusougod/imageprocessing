import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk, ImageFilter, ImageEnhance, ImageOps
import os
import numpy as np

class ImageProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Image Processing Tool")
        self.root.geometry("1368x768")
        self.root.minsize(800, 600)
        # Setup theme
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("TFrame", background="#F5F5F5")
        self.style.configure("TLabel", background="#F5F5F5", font=("Arial", 10))
        self.style.configure("TButton", background="#4285F4", foreground="white", font=("Arial", 10, "bold"))
        self.style.map("TButton", background=[("active", "#2A60B8")])
        self.style.configure("TScale", background="#F5F5F5", troughcolor="#E0E0E0")
        self.style.configure("TCombobox", fieldbackground="#FFFFFF", background="#4285F4", foreground="black", font=("Arial", 10))

        # Variables
        self.image = None
        self.original_image = None
        self.image_path = ""
        self.undo_stack = []
        self.redo_stack = []
        # Filter variables (examples)
        self.grayscale_var = tk.DoubleVar(value=0)
        self.blur_var = tk.DoubleVar(value=0)
        self.contrast_var = tk.DoubleVar(value=1)
        self.brightness_var = tk.DoubleVar(value=1)
        self.sharpen_var = tk.DoubleVar(value=0)
        self.saturation_var = tk.DoubleVar(value=1)
        self.edge_enhance_var = tk.DoubleVar(value=0)
        self.rotation_var = tk.DoubleVar(value=0)
        self.resolution_var = tk.StringVar(value="1920x1080 (16:9)")
        self.posterize_var = tk.IntVar(value=8)
        self.emboss_intensity_var = tk.IntVar(value=0)
        self.hue_shift_var = tk.IntVar(value=0)
        self.noise_reduction_size_var = tk.IntVar(value=1)
        self.invert_active = False
        self.flip_horizontal_active = False
        self.flip_vertical_active = False
        self.auto_contrast_active = False
        self.sepia_var = tk.DoubleVar(value=0)
        self.preview_enabled = tk.BooleanVar(value=True)  # Preview checkbox
        self.fast_preview = tk.BooleanVar(value=True)  # Toggle for optimized (fast) preview

        # Debounce
        self._after_id = None

        # Canvas image item
        self.canvas_image = None

        # Build UI
        self.create_widgets()
        self.setup_grid_weights()

    def create_widgets(self):
        self.main_frame = tk.Frame(self.root, bg="#F5F5F5")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.main_frame.columnconfigure(0, weight=3, uniform="group1")
        self.main_frame.columnconfigure(1, weight=1, uniform="group1")
        self.main_frame.rowconfigure(0, weight=1)

        # Left - canvas for image
        self.left_frame = tk.Frame(self.main_frame, bg="#F5F5F5")
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        title_label = ttk.Label(self.left_frame, text="Image Processing Tool",
                                font=("Arial", 14, "bold"), background="#F5F5F5", foreground="#202124")
        title_label.pack(pady=(0,10))

        self.canvas_frame = tk.Frame(self.left_frame, bg="#E0E0E0", bd=2, relief="sunken")
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.canvas_frame, bg="#E0E0E0", highlightthickness=2, highlightbackground="#4285F4")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Configure>", self.on_canvas_resize)
        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)  # Zoom support Windows
        self.canvas.bind("<Button-4>", self.on_mouse_wheel)  # Linux scroll up
        self.canvas.bind("<Button-5>", self.on_mouse_wheel)  # Linux scroll down

        # Right - controls
        self.right_frame = tk.Frame(self.main_frame, bg="#F5F5F5")
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.right_frame.columnconfigure(0, weight=1)

        self.controls_frame = tk.Frame(self.right_frame, bg="#F5F5F5", bd=2, relief="groove")
        self.controls_frame.grid(row=0, column=0, sticky="nsew", pady=5)
        self.controls_frame.columnconfigure(0, weight=1)

        # Buttons
        self.button_frame = tk.Frame(self.controls_frame, bg="#F5F5F5")
        self.button_frame.grid(row=0, column=0, pady=5, sticky="ew")

        ttk.Button(self.button_frame, text="Load Image", command=self.load_image).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.button_frame, text="Reset", command=self.reset_image).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.button_frame, text="Save Image", command=self.save_image).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.button_frame, text="Undo", command=self.undo).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.button_frame, text="Redo", command=self.redo).pack(side=tk.LEFT, padx=5)

        # Preview options
        preview_frame = tk.Frame(self.controls_frame, bg="#F5F5F5")
        preview_frame.grid(row=1, column=0, sticky="w", padx=5, pady=(0,10))

        preview_check = ttk.Checkbutton(preview_frame, text="Live Preview",
                                        variable=self.preview_enabled, command=self.on_preview_toggle)
        preview_check.pack(side=tk.LEFT, padx=5)

        fast_check = ttk.Checkbutton(preview_frame, text="Fast Preview",
                                     variable=self.fast_preview, command=self.on_fast_toggle)
        fast_check.pack(side=tk.LEFT, padx=5)

        # Sliders frame with scrollable canvas if too long
        self.sliders_canvas = tk.Canvas(self.controls_frame, bg="#F5F5F5", borderwidth=0, highlightthickness=0)
        self.sliders_scrollbar = ttk.Scrollbar(self.controls_frame, orient="vertical", command=self.sliders_canvas.yview)
        self.sliders_inner_frame = tk.Frame(self.sliders_canvas, bg="#F5F5F5")

        self.sliders_inner_frame.bind(
            "<Configure>",
            lambda e: self.sliders_canvas.configure(
                scrollregion=self.sliders_canvas.bbox("all")
            )
        )

        self.sliders_canvas.create_window((0,0), window=self.sliders_inner_frame, anchor="nw")
        self.sliders_canvas.configure(yscrollcommand=self.sliders_scrollbar.set)

        self.sliders_canvas.grid(row=2, column=0, sticky="nsew")
        self.sliders_scrollbar.grid(row=2, column=1, sticky="ns", padx=(0,5))
        self.controls_frame.rowconfigure(2, weight=1)
        self.controls_frame.columnconfigure(0, weight=1)

        # Add all sliders and controls inside sliders_inner_frame
        self.add_sliders(self.sliders_inner_frame)

        # Crop and resize controls
        self.crop_frame = tk.Frame(self.right_frame, bg="#F5F5F5", bd=1, relief="ridge")
        self.crop_frame.grid(row=1, column=0, sticky="ew", pady=10)

        ttk.Button(self.crop_frame, text="Crop Center (50%)", command=self.crop_image).pack(side=tk.LEFT, padx=5, pady=2)

        ttk.Label(self.crop_frame, text="Resolution:").pack(side=tk.LEFT, padx=5)

        resolutions = ["1920x1080 (16:9)", "1280x720 (16:9)", "854x480 (16:9)",
                        "1600x1200 (4:3)", "1024x768 (4:3)", "800x600 (4:3)"]
        self.resolution_menu = ttk.Combobox(self.crop_frame, textvariable=self.resolution_var, values=resolutions,
                                            state="readonly", width=15, style="TCombobox")
        self.resolution_menu.pack(side=tk.LEFT, padx=5)

        ttk.Button(self.crop_frame, text="Apply Resize", command=self.resize_image).pack(side=tk.LEFT, padx=5, pady=2)

        # Status bar
        self.status_label = ttk.Label(self.right_frame, text="No image loaded", font=("Arial", 12, "bold"),
                                     background="#F5F5F5", foreground="#202124")
        self.status_label.grid(row=2, column=0, sticky="ew", pady=10)

        # Zoom scale
        self.zoom_level = 1.0

    def setup_grid_weights(self):
        # Configure main frame to be responsive
        for i in range(2):
            self.main_frame.columnconfigure(i, weight=1)
        self.main_frame.rowconfigure(0, weight=1)

        # Left frame
        self.left_frame.pack_propagate(False)

        # Right frame
        self.right_frame.grid_rowconfigure(0, weight=1)
        self.right_frame.grid_columnconfigure(0, weight=1)

    def add_sliders(self, parent):
        # Helper to create sliders with label, slider, value label and entry box bound.

        def add_slider_row(row, text, var, frm, min_, max_, resolution=0.01, allow_int=False, command=None):
            ttk.Label(frm, text=text).grid(row=row, column=0, sticky="w", padx=5, pady=1)

            scale = ttk.Scale(frm, from_=min_, to=max_, variable=var, orient=tk.HORIZONTAL, length=200)
            scale.grid(row=row, column=1, padx=5, pady=1, sticky="ew")
            # No direct command on scale; handled via trace

            lbl = ttk.Label(frm, text=f"{var.get():.2f}" if not allow_int else f"{int(var.get())}")
            lbl.grid(row=row, column=2, padx=5, pady=1)

            entry = tk.Entry(frm, width=6, bg="#FFFFFF")
            entry.grid(row=row, column=3, padx=5, pady=1)
            # Set initial entry text
            entry.insert(0, f"{var.get():.2f}" if not allow_int else f"{int(var.get())}")

            # Trace update var to update label and entry
            def var_changed(*args):
                val = var.get()
                lbl.config(text=f"{val:.2f}" if not allow_int else f"{int(val)}")
                # update entry without triggering callback again
                if allow_int:
                    entry_value = f"{int(val)}"
                else:
                    entry_value = f"{val:.2f}"
                if entry.get() != entry_value:
                    entry.delete(0, tk.END)
                    entry.insert(0, entry_value)
                self.schedule_apply()

            var.trace_add("write", var_changed)

            # Sync entry -> var on Enter
            def entry_validate(event):
                try:
                    v = float(entry.get())
                    if min_ <= v <= max_:
                        var.set(v)
                    else:
                        messagebox.showwarning("Invalid Input", f"Enter value between {min_} and {max_}")
                        entry.delete(0, tk.END)
                        entry.insert(0, str(var.get()))
                except Exception:
                    messagebox.showwarning("Invalid Input", "Please enter a valid number")
                    entry.delete(0, tk.END)
                    entry.insert(0, str(var.get()))
                return "break"

            entry.bind("<Return>", entry_validate)
            entry.bind("<FocusOut>", entry_validate)

            return scale, lbl, entry

        # Layout sliders - example with main ones from your original
        # Use grid column weight for slider to fill space
        parent.columnconfigure(1, weight=1)

        add_slider_row(0, "Grayscale (0-1)", self.grayscale_var, parent, 0, 1)
        add_slider_row(1, "Blur (0-10)", self.blur_var, parent, 0, 10)
        add_slider_row(2, "Contrast (0.1-3)", self.contrast_var, parent, 0.1, 3)
        add_slider_row(3, "Brightness (0.1-3)", self.brightness_var, parent, 0.1, 3)
        add_slider_row(4, "Sharpen (0-5)", self.sharpen_var, parent, 0, 5)
        add_slider_row(5, "Saturation (0-2)", self.saturation_var, parent, 0, 2)
        add_slider_row(6, "Edge Enhance (0-5)", self.edge_enhance_var, parent, 0, 5)
        add_slider_row(7, "Rotation (0-360°)", self.rotation_var, parent, 0, 360, allow_int=True)
        add_slider_row(8, "Sepia Tone", self.sepia_var, parent, 0, 1)
        add_slider_row(9, "Posterize Bits (1-8)", self.posterize_var, parent, 1, 8, allow_int=True)
        add_slider_row(10, "Emboss Intensity (0-5)", self.emboss_intensity_var, parent, 0, 5, allow_int=True)
        add_slider_row(11, "Hue Shift (-180 to 180)", self.hue_shift_var, parent, -180, 180, allow_int=True)
        add_slider_row(12, "Noise Reduction Size (1-5)", self.noise_reduction_size_var, parent, 1, 5, allow_int=True)

        # Toggle buttons
        btn_frame = tk.Frame(parent, bg="#F5F5F5")
        btn_frame.grid(row=13, column=0, columnspan=4, sticky="ew", pady=10)
        for i in range(4):
            btn_frame.columnconfigure(i, weight=1)

        ttk.Button(btn_frame, text="Invert Colors", command=self.toggle_invert).grid(row=0, column=0, sticky="ew", padx=2)
        ttk.Button(btn_frame, text="Flip Horizontal", command=self.toggle_flip_horizontal).grid(row=0, column=1, sticky="ew", padx=2)
        ttk.Button(btn_frame, text="Flip Vertical", command=self.toggle_flip_vertical).grid(row=0, column=2, sticky="ew", padx=2)
        ttk.Button(btn_frame, text="Auto Contrast", command=self.toggle_auto_contrast).grid(row=0, column=3, sticky="ew", padx=2)

    def load_image(self):
        filetypes = [("Image files", "*.png *.jpg *.jpeg *.bmp *.gif"), ("All files", "*.*")]
        path = filedialog.askopenfilename(filetypes=filetypes)
        if path:
            try:
                img = Image.open(path).convert("RGB")
                self.image_path = path
                self.original_image = img.copy()
                self.image = img
                self.undo_stack.clear()
                self.redo_stack.clear()
                self.push_undo()
                self.zoom_level = 1.0
                self.display_image(self.image)
                self.status_label.config(text=f"Loaded: {os.path.basename(self.image_path)}")
                self.reset_filter_vars()
                self.initial_image = img.copy()  # Keep immutable original
            except Exception as e:
                messagebox.showerror("Error", f"Error loading image: {e}")

    def reset_filter_vars(self):
        self.grayscale_var.set(0)
        self.blur_var.set(0)
        self.contrast_var.set(1)
        self.brightness_var.set(1)
        self.sharpen_var.set(0)
        self.saturation_var.set(1)
        self.edge_enhance_var.set(0)
        self.rotation_var.set(0)
        self.sepia_var.set(0)
        self.posterize_var.set(8)
        self.emboss_intensity_var.set(0)
        self.hue_shift_var.set(0)
        self.noise_reduction_size_var.set(1)
        self.invert_active = False
        self.flip_horizontal_active = False
        self.flip_vertical_active = False
        self.auto_contrast_active = False
        self.resolution_var.set("1920x1080 (16:9)")

    def reset_image(self):
        if self.initial_image:
            self.original_image = self.initial_image.copy()
            self.undo_stack.clear()
            self.redo_stack.clear()
            self.push_undo()
            self.display_image(self.original_image)
            self.status_label.config(text="Image reset to original")
            self.reset_filter_vars()

    def schedule_apply(self):
        if not self.preview_enabled.get():
            return
        if self.fast_preview.get():
            if self._after_id is not None:
                self.root.after_cancel(self._after_id)
            self._after_id = self.root.after(200, self.apply_filters)
        else:
            self.apply_filters()

    def apply_filters(self):
        self._after_id = None
        if not self.original_image:
            return

        if self.fast_preview.get():
            max_preview = 800
            w, h = self.original_image.size
            scale = min(1.0, max_preview / max(w, h))
            if scale < 1.0:
                base = self.original_image.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)
            else:
                base = self.original_image.copy()
            status_text = "Applied filters (fast preview)"
        else:
            base = self.original_image.copy()
            status_text = "Applied filters"

        im = self.apply_filters_to(base)
        self.image = im
        self.display_image(self.image)
        self.status_label.config(text=status_text)

    def apply_filters_to(self, im):
        # Rotation
        if self.rotation_var.get() != 0:
            im = im.rotate(-self.rotation_var.get(), expand=True, resample=Image.Resampling.BICUBIC)

        # Grayscale blending
        if self.grayscale_var.get() > 0:
            gs = im.convert("L").convert("RGB")
            im = Image.blend(im, gs, self.grayscale_var.get())

        # Blur
        if self.blur_var.get() > 0:
            im = im.filter(ImageFilter.GaussianBlur(radius=self.blur_var.get()))

        # Contrast
        if self.contrast_var.get() != 1:
            im = ImageEnhance.Contrast(im).enhance(self.contrast_var.get())

        # Brightness
        if self.brightness_var.get() != 1:
            im = ImageEnhance.Brightness(im).enhance(self.brightness_var.get())

        # Sharpen
        if self.sharpen_var.get() > 0:
            im = ImageEnhance.Sharpness(im).enhance(self.sharpen_var.get())

        # Saturation
        if self.saturation_var.get() != 1:
            im = ImageEnhance.Color(im).enhance(self.saturation_var.get())

        # Edge Enhance
        if self.edge_enhance_var.get() > 0:
            im = im.filter(ImageFilter.EDGE_ENHANCE)
            if self.edge_enhance_var.get() > 1:
                im = ImageEnhance.Sharpness(im).enhance(self.edge_enhance_var.get() / 2)

        # Sepia Tone
        if self.sepia_var.get() > 0:
            sepia = self.apply_sepia(im)
            im = Image.blend(im, sepia, self.sepia_var.get())

        # Posterize
        if self.posterize_var.get() < 8:
            im = ImageOps.posterize(im, self.posterize_var.get())

        # Emboss
        if self.emboss_intensity_var.get() > 0:
            im = im.filter(ImageFilter.EMBOSS)
            if self.emboss_intensity_var.get() > 1:
                im = ImageEnhance.Sharpness(im).enhance(self.emboss_intensity_var.get() / 2)

        # Hue shift
        if self.hue_shift_var.get() != 0:
            im = self.shift_hue(im, self.hue_shift_var.get())

        # Noise reduction (Median filter)
        size = self.noise_reduction_size_var.get()
        if size > 1:
            if size % 2 == 0:
                size += 1  # Make it odd
            size = max(size, 3)  # Ensure at least 3
            im = im.filter(ImageFilter.MedianFilter(size=size))

        # Toggles
        if self.invert_active:
            im = ImageOps.invert(im)

        if self.flip_horizontal_active:
            im = im.transpose(Image.FLIP_LEFT_RIGHT)

        if self.flip_vertical_active:
            im = im.transpose(Image.FLIP_TOP_BOTTOM)

        if self.auto_contrast_active:
            im = ImageOps.autocontrast(im)

        return im

    def display_image(self, image):
        if image:
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()

            img_width, img_height = image.size
            # Apply zoom
            display_width = int(img_width * self.zoom_level)
            display_height = int(img_height * self.zoom_level)

            # Fit inside canvas keeping aspect ratio with zoom
            if display_width > canvas_width or display_height > canvas_height:
                scale = min(canvas_width / display_width, canvas_height / display_height)
                display_width = int(display_width * scale)
                display_height = int(display_height * scale)
                self.zoom_level *= scale

            resized_image = image.resize((display_width, display_height), Image.Resampling.LANCZOS)

            self.photo = ImageTk.PhotoImage(resized_image)
            if self.canvas_image is None:
                self.canvas_image = self.canvas.create_image(canvas_width//2, canvas_height//2, image=self.photo, anchor="center")
            else:
                self.canvas.itemconfig(self.canvas_image, image=self.photo)

    def on_canvas_resize(self, event):
        if self.image:
            self.display_image(self.image)

    def on_mouse_wheel(self, event):
        if not self.image:
            return
        if event.num == 5 or event.delta < 0:  # scroll down = zoom out
            self.zoom_level = max(0.1, self.zoom_level - 0.1)
        elif event.num == 4 or event.delta > 0:  # scroll up = zoom in
            self.zoom_level = min(5.0, self.zoom_level + 0.1)
        self.display_image(self.image)

    def toggle_invert(self):
        self.invert_active = not self.invert_active
        self.schedule_apply()

    def toggle_flip_horizontal(self):
        self.flip_horizontal_active = not self.flip_horizontal_active
        self.schedule_apply()

    def toggle_flip_vertical(self):
        self.flip_vertical_active = not self.flip_vertical_active
        self.schedule_apply()

    def toggle_auto_contrast(self):
        self.auto_contrast_active = not self.auto_contrast_active
        self.schedule_apply()

    def resize_image(self):
        """Resize the original image to the selected resolution"""
        if not self.original_image:
            return
        try:
            res_str = self.resolution_var.get()
            width, height = map(int, res_str.split()[0].split('x'))
            self.push_undo()
            self.original_image = self.original_image.resize((width, height), Image.Resampling.LANCZOS)
            self.schedule_apply()
            self.status_label.config(text=f"Resized image to {res_str}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to resize image: {e}")

    def crop_image(self):
        """Crop center 50%"""
        if not self.original_image:
            return
        try:
            width, height = self.original_image.size
            left = int(width * 0.25)
            top = int(height * 0.25)
            right = int(width * 0.75)
            bottom = int(height * 0.75)
            self.push_undo()
            self.original_image = self.original_image.crop((left, top, right, bottom))
            self.schedule_apply()
            self.status_label.config(text="Cropped image to center")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to crop image: {e}")

    def save_image(self):
        if not self.original_image:
            return
        save_path = filedialog.asksaveasfilename(defaultextension=".png",
                                filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg")])
        if save_path:
            try:
                im = self.apply_filters_to(self.original_image.copy())
                im.save(save_path)
                self.status_label.config(text=f"Saved image to {os.path.basename(save_path)}")
                messagebox.showinfo("Success", "Image saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save image: {e}")

    def push_undo(self):
        if self.original_image:
            self.undo_stack.append(self.original_image.copy())
            if len(self.undo_stack) > 20:  # Limit undo history
                self.undo_stack.pop(0)

    def undo(self):
        if self.undo_stack:
            self.redo_stack.append(self.original_image.copy())
            self.original_image = self.undo_stack.pop()
            self.schedule_apply()
            self.status_label.config(text="Undo applied")

    def redo(self):
        if self.redo_stack:
            self.undo_stack.append(self.original_image.copy())
            self.original_image = self.redo_stack.pop()
            self.schedule_apply()
            self.status_label.config(text="Redo applied")

    def on_preview_toggle(self):
        if self.preview_enabled.get():
            self.schedule_apply()
        else:
            if self.original_image:
                self.display_image(self.original_image)
                self.status_label.config(text="Preview disabled")

    def on_fast_toggle(self):
        if self.preview_enabled.get():
            self.schedule_apply()

    def apply_sepia(self, img):
        arr = np.array(img).astype(np.float32)
        r, g, b = arr[:,:,0], arr[:,:,1], arr[:,:,2]
        tr = 0.393 * r + 0.769 * g + 0.189 * b
        tg = 0.349 * r + 0.686 * g + 0.168 * b
        tb = 0.272 * r + 0.534 * g + 0.131 * b
        sepia_arr = np.stack([tr, tg, tb], axis=2)
        sepia_arr = np.clip(sepia_arr, 0, 255).astype(np.uint8)
        return Image.fromarray(sepia_arr)

    def shift_hue(self, img, hue_shift):
        """Shift hue by given degrees"""
        hsv = img.convert('HSV')
        np_hsv = np.array(hsv)
        # hue_shift expected in degrees, convert to 0-255 range
        shift = int((hue_shift / 360.0) * 255)
        np_hsv[...,0] = ((np_hsv[...,0].astype(np.int16) + shift) % 256).astype(np.uint8)
        shifted = Image.fromarray(np_hsv, 'HSV').convert('RGB')
        return shifted

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageProcessorApp(root)
    root.mainloop()