import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter import font as tkfont
from typing import Optional, Tuple

import cv2
import numpy as np
from PIL import Image, ImageTk


class ImageProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Обработка изображений - Lab 3")

        self.root.minsize(900, 550)

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        window_width = int(screen_width * 0.85)
        window_height = int(screen_height * 0.85)

        x_position = (screen_width - window_width) // 2
        y_position = (screen_height - window_height) // 2

        self.root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

        self.original_image: Optional[np.ndarray] = None
        self.processed_image: Optional[np.ndarray] = None

        self.display_size = (600, 400)

        self.resize_after_id = None

        self.setup_styles()

        self.setup_ui()

        self.root.bind("<Configure>", self.on_window_resize)

    def setup_styles(self):
        """Настройка стилей интерфейса"""
        style = ttk.Style()
        style.theme_use("clam")

        bg_color = "#f0f0f0"
        accent_color = "#4a90e2"
        button_color = "#5cb85c"

        style.configure("TFrame", background=bg_color)
        style.configure("TLabel", background=bg_color, padding=2)
        style.configure("TLabelframe", background=bg_color, padding=5)
        style.configure(
            "TLabelframe.Label", background=bg_color, font=("Arial", 10, "bold")
        )

        style.configure("TButton", padding=6, relief="flat", background=button_color)
        style.map("TButton", background=[("active", "#4cae4c")])

        style.configure(
            "Accent.TButton",
            padding=8,
            relief="flat",
            background=accent_color,
            foreground="white",
        )
        style.map("Accent.TButton", background=[("active", "#357abd")])

        style.configure("TSpinbox", padding=2)

    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        self.main_paned = tk.PanedWindow(
            self.root,
            orient=tk.VERTICAL,
            sashrelief=tk.RAISED,
            sashwidth=4,
            bg="#d0d0d0",
        )
        self.main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.top_frame = ttk.Frame(self.main_paned)
        self.main_paned.add(self.top_frame, minsize=300)

        self.load_button = ttk.Button(
            self.top_frame,
            text="📂 Загрузить изображение",
            command=self.load_image,
            style="Accent.TButton",
        )
        self.load_button.pack(pady=8, padx=10, fill=tk.X)

        self.images_frame = ttk.Frame(self.top_frame)
        self.images_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.original_frame = ttk.LabelFrame(
            self.images_frame, text="📷 Исходное изображение", padding="5"
        )
        self.original_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=3)

        self.original_canvas = tk.Canvas(
            self.original_frame, bg="#2c3e50", highlightthickness=0
        )
        self.original_canvas.pack(fill=tk.BOTH, expand=True)
        self.original_label = tk.Label(self.original_canvas, bg="#2c3e50")
        self.original_canvas_window = self.original_canvas.create_window(
            0, 0, window=self.original_label, anchor="nw"
        )

        self.processed_frame = ttk.LabelFrame(
            self.images_frame, text="✨ Обработанное изображение", padding="5"
        )
        self.processed_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=3)

        self.processed_canvas = tk.Canvas(
            self.processed_frame, bg="#2c3e50", highlightthickness=0
        )
        self.processed_canvas.pack(fill=tk.BOTH, expand=True)
        self.processed_label = tk.Label(self.processed_canvas, bg="#2c3e50")
        self.processed_canvas_window = self.processed_canvas.create_window(
            0, 0, window=self.processed_label, anchor="nw"
        )

        self.control_container = ttk.Frame(self.main_paned)
        self.main_paned.add(self.control_container, minsize=200)

        self.control_canvas = tk.Canvas(self.control_container, highlightthickness=0)
        self.control_scrollbar = ttk.Scrollbar(
            self.control_container, orient="vertical", command=self.control_canvas.yview
        )
        self.control_scrollable_frame = ttk.Frame(self.control_canvas)

        self.control_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.control_canvas.configure(
                scrollregion=self.control_canvas.bbox("all")
            ),
        )

        self.control_canvas_window = self.control_canvas.create_window(
            (0, 0), window=self.control_scrollable_frame, anchor="nw"
        )
        self.control_canvas.configure(yscrollcommand=self.control_scrollbar.set)

        self.control_canvas.bind("<Configure>", self._on_canvas_configure)

        self.control_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.control_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.control_canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        self.control_frame = ttk.LabelFrame(
            self.control_scrollable_frame, text="🛠 Методы обработки", padding="15"
        )
        self.control_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=10)

        row_counter = 0

        threshold_section = ttk.LabelFrame(
            self.control_frame, text="🔍 Локальная пороговая обработка", padding="10"
        )
        threshold_section.grid(
            row=row_counter, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5, padx=5
        )
        row_counter += 1

        # Метод Niblack
        niblack_frame = ttk.Frame(threshold_section)
        niblack_frame.pack(pady=3, anchor='center')

        ttk.Label(niblack_frame, text="Niblack:", font=("Arial", 9, "bold")).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Label(niblack_frame, text="Размер окна:").pack(side=tk.LEFT, padx=3)
        self.niblack_window = tk.IntVar(value=15)
        ttk.Spinbox(
            niblack_frame,
            from_=3,
            to=51,
            increment=2,
            textvariable=self.niblack_window,
            width=8,
        ).pack(side=tk.LEFT, padx=2)

        ttk.Label(niblack_frame, text="k:").pack(side=tk.LEFT, padx=3)
        self.niblack_k = tk.DoubleVar(value=-0.2)
        ttk.Spinbox(
            niblack_frame,
            from_=-1,
            to=1,
            increment=0.1,
            textvariable=self.niblack_k,
            width=8,
        ).pack(side=tk.LEFT, padx=2)

        ttk.Button(niblack_frame, text="Применить", command=self.apply_niblack).pack(
            side=tk.LEFT, padx=8
        )

        sauvola_frame = ttk.Frame(threshold_section)
        sauvola_frame.pack(pady=3, anchor='center')

        ttk.Label(sauvola_frame, text="Sauvola:", font=("Arial", 9, "bold")).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Label(sauvola_frame, text="Размер окна:").pack(side=tk.LEFT, padx=3)
        self.sauvola_window = tk.IntVar(value=15)
        ttk.Spinbox(
            sauvola_frame,
            from_=3,
            to=51,
            increment=2,
            textvariable=self.sauvola_window,
            width=8,
        ).pack(side=tk.LEFT, padx=2)

        ttk.Label(sauvola_frame, text="k:").pack(side=tk.LEFT, padx=3)
        self.sauvola_k = tk.DoubleVar(value=0.2)
        ttk.Spinbox(
            sauvola_frame,
            from_=0,
            to=1,
            increment=0.1,
            textvariable=self.sauvola_k,
            width=8,
        ).pack(side=tk.LEFT, padx=2)

        ttk.Button(sauvola_frame, text="Применить", command=self.apply_sauvola).pack(
            side=tk.LEFT, padx=8
        )

        adaptive_section = ttk.LabelFrame(
            self.control_frame, text="⚙️ Адаптивная пороговая обработка", padding="10"
        )
        adaptive_section.grid(
            row=row_counter, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5, padx=5
        )
        row_counter += 1

        adaptive_frame = ttk.Frame(adaptive_section)
        adaptive_frame.pack(pady=3, anchor='center')

        ttk.Label(adaptive_frame, text="Размер окна:").pack(side=tk.LEFT, padx=5)
        self.adaptive_window = tk.IntVar(value=11)
        ttk.Spinbox(
            adaptive_frame,
            from_=3,
            to=51,
            increment=2,
            textvariable=self.adaptive_window,
            width=8,
        ).pack(side=tk.LEFT, padx=2)

        ttk.Label(adaptive_frame, text="C:").pack(side=tk.LEFT, padx=5)
        self.adaptive_c = tk.IntVar(value=2)
        ttk.Spinbox(
            adaptive_frame,
            from_=-10,
            to=10,
            increment=1,
            textvariable=self.adaptive_c,
            width=8,
        ).pack(side=tk.LEFT, padx=2)

        ttk.Button(
            adaptive_frame,
            text="Mean",
            command=lambda: self.apply_adaptive_threshold("mean"),
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(
            adaptive_frame,
            text="Gaussian",
            command=lambda: self.apply_adaptive_threshold("gaussian"),
        ).pack(side=tk.LEFT, padx=5)

        element_section = ttk.LabelFrame(
            self.control_frame, text="➕ Поэлементные операции", padding="10"
        )
        element_section.grid(
            row=row_counter, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5, padx=5
        )
        row_counter += 1

        element_frame = ttk.Frame(element_section)
        element_frame.pack(pady=3, anchor='center')

        ttk.Label(element_frame, text="Значение:").pack(side=tk.LEFT, padx=5)
        self.element_value = tk.IntVar(value=50)
        ttk.Spinbox(
            element_frame,
            from_=-255,
            to=255,
            increment=10,
            textvariable=self.element_value,
            width=8,
        ).pack(side=tk.LEFT, padx=2)

        ttk.Button(
            element_frame,
            text="➕ Добавить",
            command=lambda: self.apply_element_operation("add"),
        ).pack(side=tk.LEFT, padx=3)
        ttk.Button(
            element_frame,
            text="➖ Вычесть",
            command=lambda: self.apply_element_operation("subtract"),
        ).pack(side=tk.LEFT, padx=3)
        ttk.Button(
            element_frame,
            text="✖️ Умножить",
            command=lambda: self.apply_element_operation("multiply"),
        ).pack(side=tk.LEFT, padx=3)
        ttk.Button(
            element_frame,
            text="➗ Разделить",
            command=lambda: self.apply_element_operation("divide"),
        ).pack(side=tk.LEFT, padx=3)

        contrast_section = ttk.LabelFrame(
            self.control_frame, text="📊 Линейное контрастирование", padding="10"
        )
        contrast_section.grid(
            row=row_counter, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5, padx=5
        )
        row_counter += 1

        contrast_frame = ttk.Frame(contrast_section)
        contrast_frame.pack(pady=3, anchor='center')

        ttk.Label(contrast_frame, text="Мин. выход:").pack(side=tk.LEFT, padx=5)
        self.contrast_min = tk.IntVar(value=0)
        ttk.Spinbox(
            contrast_frame,
            from_=0,
            to=255,
            increment=10,
            textvariable=self.contrast_min,
            width=8,
        ).pack(side=tk.LEFT, padx=2)

        ttk.Label(contrast_frame, text="Макс. выход:").pack(side=tk.LEFT, padx=5)
        self.contrast_max = tk.IntVar(value=255)
        ttk.Spinbox(
            contrast_frame,
            from_=0,
            to=255,
            increment=10,
            textvariable=self.contrast_max,
            width=8,
        ).pack(side=tk.LEFT, padx=2)

        ttk.Button(
            contrast_frame, text="Применить", command=self.apply_linear_contrast
        ).pack(side=tk.LEFT, padx=10)

        action_container = ttk.Frame(self.control_frame)
        action_container.grid(row=row_counter, column=0, columnspan=3, pady=15, sticky='')
        row_counter += 1
        
        action_section = ttk.Frame(action_container)
        action_section.pack()

        ttk.Button(
            action_section,
            text="🔄 Сбросить",
            command=self.reset_image,
            style="Accent.TButton",
        ).pack(side=tk.LEFT, padx=5, ipadx=20)
        ttk.Button(
            action_section,
            text="💾 Сохранить результат",
            command=self.save_image,
            style="Accent.TButton",
        ).pack(side=tk.LEFT, padx=5, ipadx=20)

        self.control_frame.columnconfigure(0, weight=1)
        self.control_frame.columnconfigure(1, weight=1)
        self.control_frame.columnconfigure(2, weight=1)

    def _on_mousewheel(self, event):
        """Обработка прокрутки колесом мыши"""
        self.control_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_canvas_configure(self, event):
        """Растягивание фрейма на всю ширину canvas"""
        canvas_width = event.width
        self.control_canvas.itemconfig(self.control_canvas_window, width=canvas_width)

    def on_window_resize(self, event):
        """Обработчик изменения размера окна с задержкой (debouncing)"""
        if event.widget == self.root:
            if self.resize_after_id is not None:
                self.root.after_cancel(self.resize_after_id)

            self.resize_after_id = self.root.after(100, self.delayed_resize)

    def delayed_resize(self):
        """Отложенное обновление размера изображений"""
        self.resize_after_id = None
        self.update_display_size()
        if self.original_image is not None:
            self.display_images()

    def update_display_size(self):
        """Обновление размера отображения изображений на основе текущего размера окна"""
        try:
            self.images_frame.update_idletasks()

            frame_width = self.original_frame.winfo_width()
            frame_height = self.original_frame.winfo_height()

            if frame_width <= 1 or frame_height <= 1:
                window_width = self.root.winfo_width()
                window_height = self.root.winfo_height()

                available_height = max(300, int(window_height * 0.55))
                available_width = max(300, (window_width - 60) // 2)
            else:
                available_width = max(200, frame_width - 30)
                available_height = max(200, frame_height - 60)

            self.display_size = (available_width, available_height)
        except:
            self.display_size = (600, 400)

    def load_image(self):
        """Загрузка изображения из файла"""
        file_path = filedialog.askopenfilename(
            title="Выберите изображение",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff"),
                ("All files", "*.*"),
            ],
        )

        if file_path:
            self.original_image = cv2.imread(file_path)
            if self.original_image is not None:
                self.processed_image = self.original_image.copy()
                self.update_display_size()
                self.display_images()
            else:
                messagebox.showerror("Ошибка", "Не удалось загрузить изображение")

    def display_images(self):
        """Отображение изображений в GUI"""
        if self.original_image is not None:
            original_rgb = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB)
            original_resized = self.resize_for_display(original_rgb)
            original_pil = Image.fromarray(original_resized)
            original_photo = ImageTk.PhotoImage(original_pil)
            self.original_label.configure(image=original_photo)
            self.original_label.image = original_photo

            self._center_image_on_canvas(
                self.original_canvas,
                self.original_canvas_window,
                original_resized.shape[1],
                original_resized.shape[0],
            )

        if self.processed_image is not None:
            if len(self.processed_image.shape) == 2:
                processed_resized = self.resize_for_display(self.processed_image)
                processed_pil = Image.fromarray(processed_resized)
            else:
                processed_rgb = cv2.cvtColor(self.processed_image, cv2.COLOR_BGR2RGB)
                processed_resized = self.resize_for_display(processed_rgb)
                processed_pil = Image.fromarray(processed_resized)

            processed_photo = ImageTk.PhotoImage(processed_pil)
            self.processed_label.configure(image=processed_photo)
            self.processed_label.image = processed_photo

            self._center_image_on_canvas(
                self.processed_canvas,
                self.processed_canvas_window,
                processed_resized.shape[1],
                processed_resized.shape[0],
            )

    def _center_image_on_canvas(self, canvas, canvas_window_id, img_width, img_height):
        """Центрирование изображения на canvas"""
        canvas.update_idletasks()
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()

        x = max(0, (canvas_width - img_width) // 2)
        y = max(0, (canvas_height - img_height) // 2)

        canvas.coords(canvas_window_id, x, y)

    def resize_for_display(self, image: np.ndarray) -> np.ndarray:
        """Изменение размера изображения для отображения"""
        h, w = image.shape[:2]
        max_w, max_h = self.display_size

        scale = min(max_w / w, max_h / h)

        if scale < 1:
            new_w = int(w * scale)
            new_h = int(h * scale)
            return cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)

        return image

    def get_grayscale(self) -> Optional[np.ndarray]:
        """Получение изображения в градациях серого"""
        if self.original_image is None:
            messagebox.showwarning("Предупреждение", "Сначала загрузите изображение")
            return None

        if len(self.original_image.shape) == 3:
            return cv2.cvtColor(self.original_image, cv2.COLOR_BGR2GRAY)
        return self.original_image


    def apply_niblack(self):
        """Применение метода Niblack для пороговой обработки"""
        gray = self.get_grayscale()
        if gray is None:
            return

        window_size = self.niblack_window.get()
        k = self.niblack_k.get()

        if window_size % 2 == 0:
            window_size += 1

        threshold = self.niblack_threshold(gray, window_size, k)
        self.processed_image = ((gray > threshold) * 255).astype(np.uint8)
        self.display_images()

    def niblack_threshold(
        self, image: np.ndarray, window_size: int, k: float
    ) -> np.ndarray:
        """
        Метод Niblack для локальной пороговой обработки
        T(x,y) = m(x,y) + k * s(x,y)
        где m - локальное среднее, s - локальное стандартное отклонение
        """
        mean = cv2.blur(image.astype(np.float32), (window_size, window_size))
        mean_sq = cv2.blur((image.astype(np.float32) ** 2), (window_size, window_size))
        std = np.sqrt(mean_sq - mean**2)

        threshold = mean + k * std
        return threshold

    def apply_sauvola(self):
        """Применение метода Sauvola для пороговой обработки"""
        gray = self.get_grayscale()
        if gray is None:
            return

        window_size = self.sauvola_window.get()
        k = self.sauvola_k.get()

        if window_size % 2 == 0:
            window_size += 1

        threshold = self.sauvola_threshold(gray, window_size, k)
        self.processed_image = ((gray > threshold) * 255).astype(np.uint8)
        self.display_images()

    def sauvola_threshold(
        self, image: np.ndarray, window_size: int, k: float, R: float = 128
    ) -> np.ndarray:
        """
        Метод Sauvola для локальной пороговой обработки
        T(x,y) = m(x,y) * (1 + k * (s(x,y)/R - 1))
        где m - локальное среднее, s - локальное стандартное отклонение, R - динамический диапазон
        """
        mean = cv2.blur(image.astype(np.float32), (window_size, window_size))
        mean_sq = cv2.blur((image.astype(np.float32) ** 2), (window_size, window_size))
        std = np.sqrt(mean_sq - mean**2)

        threshold = mean * (1 + k * (std / R - 1))
        return threshold


    def apply_adaptive_threshold(self, method: str):
        """Применение адаптивной пороговой обработки"""
        gray = self.get_grayscale()
        if gray is None:
            return

        window_size = self.adaptive_window.get()
        c = self.adaptive_c.get()

        if window_size % 2 == 0:
            window_size += 1

        adaptive_method = (
            cv2.ADAPTIVE_THRESH_MEAN_C
            if method == "mean"
            else cv2.ADAPTIVE_THRESH_GAUSSIAN_C
        )

        self.processed_image = cv2.adaptiveThreshold(
            gray, 255, adaptive_method, cv2.THRESH_BINARY, window_size, c
        )
        self.display_images()


    def apply_element_operation(self, operation: str):
        """Применение поэлементных операций"""
        if self.original_image is None:
            messagebox.showwarning("Предупреждение", "Сначала загрузите изображение")
            return

        value = self.element_value.get()
        image = self.original_image.astype(np.float32)

        if operation == "add":
            result = image + value
        elif operation == "subtract":
            result = image - value
        elif operation == "multiply":
            result = image * (
                value / 100.0
            ) 
        elif operation == "divide":
            if value == 0:
                messagebox.showerror("Ошибка", "Деление на ноль невозможно")
                return
            result = image / (value / 100.0)
        else:
            return

        result = np.clip(result, 0, 255).astype(np.uint8)
        self.processed_image = result
        self.display_images()

    def apply_linear_contrast(self):
        """Применение линейного контрастирования"""
        if self.original_image is None:
            messagebox.showwarning("Предупреждение", "Сначала загрузите изображение")
            return

        min_out = self.contrast_min.get()
        max_out = self.contrast_max.get()

        if min_out >= max_out:
            messagebox.showerror(
                "Ошибка", "Минимальное значение должно быть меньше максимального"
            )
            return

        image = self.original_image.astype(np.float32)

        min_in = image.min()
        max_in = image.max()

        # out = (in - min_in) * (max_out - min_out) / (max_in - min_in) + min_out
        if max_in - min_in > 0:
            result = (image - min_in) * (max_out - min_out) / (
                max_in - min_in
            ) + min_out
        else:
            result = image

        result = np.clip(result, 0, 255).astype(np.uint8)
        self.processed_image = result
        self.display_images()


    def reset_image(self):
        """Сброс обработанного изображения к оригиналу"""
        if self.original_image is not None:
            self.processed_image = self.original_image.copy()
            self.display_images()

    def save_image(self):
        """Сохранение обработанного изображения"""
        if self.processed_image is None:
            messagebox.showwarning("Предупреждение", "Нет изображения для сохранения")
            return

        file_path = filedialog.asksaveasfilename(
            title="Сохранить изображение",
            defaultextension=".png",
            filetypes=[
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg"),
                ("All files", "*.*"),
            ],
        )

        if file_path:
            cv2.imwrite(file_path, self.processed_image)
            messagebox.showinfo("Успех", "Изображение успешно сохранено")


def main():
    root = tk.Tk()
    app = ImageProcessorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
