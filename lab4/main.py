import math
import time
import tkinter as tk
from tkinter import messagebox, ttk


class RasterizationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Алгоритмы растеризации")

        # Минимальный размер окна
        self.root.minsize(900, 600)

        # Таймер для отложенной перерисовки (убирает лаги при ресайзе)
        self.resize_timer = None

        # Параметры сетки
        self.grid_size = 20  # размер ячейки в пикселях
        self.canvas_width = 800  # начальный размер
        self.canvas_height = 600
        self.offset_x = self.canvas_width // 2
        self.offset_y = self.canvas_height // 2

        # Режимы рисования
        self.drawing_mode = None
        self.click_points = []

        # Хранилище для векторных (идеальных) фигур
        self.vector_shapes = []

        # Результаты измерений
        self.last_time = 0
        self.last_pixels_count = 0

        self.setup_ui()

        # Первичная отрисовка
        self.root.update_idletasks()  # Ждем обновления геометрии
        self.draw_grid()

    def setup_ui(self):
        """Создание пользовательского интерфейса"""
        # Основной контейнер
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # === Левая панель управления ===
        control_frame_outer = ttk.Frame(main_container, width=350)
        control_frame_outer.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        control_frame_outer.pack_propagate(False)  # Фиксируем ширину панели

        # Canvas для скроллинга
        self.control_canvas = tk.Canvas(control_frame_outer, highlightthickness=0)
        scrollbar = ttk.Scrollbar(
            control_frame_outer, orient="vertical", command=self.control_canvas.yview
        )

        # Внутренний фрейм с контролами
        self.control_panel = ttk.Frame(self.control_canvas)

        # Создаем окно внутри канваса
        self.canvas_window = self.control_canvas.create_window(
            (0, 0), window=self.control_panel, anchor="nw"
        )

        # Настройка скроллинга
        self.control_panel.bind("<Configure>", self.on_frame_configure)
        # Адаптация ширины внутреннего фрейма к ширине канваса
        self.control_canvas.bind("<Configure>", self.on_canvas_configure)

        self.control_canvas.configure(yscrollcommand=scrollbar.set)

        self.control_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Привязка прокрутки мышью
        self.bind_mouse_scroll(self.control_canvas)

        # === Наполнение панели управления ===
        self.create_control_widgets()

        # === Холст (Правая часть) ===
        canvas_frame = ttk.Frame(main_container)
        canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(
            canvas_frame,
            bg="white",
            highlightthickness=1,
            highlightbackground="#cccccc",
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Привязка событий мыши и ресайза К КАНВАСУ, а не к root
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<Motion>", self.on_mouse_move)
        self.canvas.bind("<Configure>", self.on_resize_event)

        # Статус бар
        self.status_label = ttk.Label(
            self.root, text="Готов к работе", relief=tk.SUNKEN, anchor=tk.W
        )
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

    def create_control_widgets(self):
        """Создание виджетов внутри панели управления"""
        # Заголовок
        title_label = ttk.Label(
            self.control_panel,
            text="Алгоритмы растеризации",
            font=("Arial", 16, "bold"),
        )
        title_label.pack(pady=10)

        # Выбор алгоритма для отрезков
        line_frame = ttk.LabelFrame(
            self.control_panel, text="Алгоритмы отрезков", padding=10
        )
        line_frame.pack(fill=tk.X, pady=5, padx=5)

        self.line_algorithm = tk.StringVar(value="bresenham_line")
        algorithms = [
            ("Пошаговый алгоритм", "step_by_step"),
            ("Алгоритм ЦДА", "dda"),
            ("Алгоритм Брезенхема", "bresenham_line"),
            ("Алгоритм Кастла-Питвея", "castle_piteway"),
            ("Алгоритм Ву (сглаживание)", "wu"),
        ]

        for text, value in algorithms:
            ttk.Radiobutton(
                line_frame, text=text, variable=self.line_algorithm, value=value
            ).pack(anchor=tk.W)

        # Ввод координат для отрезка
        coords_frame = ttk.LabelFrame(
            self.control_panel, text="Координаты отрезка", padding=10
        )
        coords_frame.pack(fill=tk.X, pady=5, padx=5)

        # Grid layout for coords
        coords_grid = ttk.Frame(coords_frame)
        coords_grid.pack(fill=tk.X)

        ttk.Label(coords_grid, text="Точка 1:").grid(row=0, column=0, sticky=tk.W)
        self.x1_var = tk.StringVar(value="0")
        self.y1_var = tk.StringVar(value="0")
        ttk.Entry(coords_grid, textvariable=self.x1_var, width=6).grid(
            row=0, column=1, padx=2
        )
        ttk.Label(coords_grid, text="X").grid(row=0, column=2)
        ttk.Entry(coords_grid, textvariable=self.y1_var, width=6).grid(
            row=0, column=3, padx=2
        )
        ttk.Label(coords_grid, text="Y").grid(row=0, column=4)

        ttk.Label(coords_grid, text="Точка 2:").grid(
            row=1, column=0, sticky=tk.W, pady=5
        )
        self.x2_var = tk.StringVar(value="15")
        self.y2_var = tk.StringVar(value="10")
        ttk.Entry(coords_grid, textvariable=self.x2_var, width=6).grid(
            row=1, column=1, padx=2
        )
        ttk.Label(coords_grid, text="X").grid(row=1, column=2)
        ttk.Entry(coords_grid, textvariable=self.y2_var, width=6).grid(
            row=1, column=3, padx=2
        )
        ttk.Label(coords_grid, text="Y").grid(row=1, column=4)

        ttk.Button(
            coords_frame, text="Нарисовать отрезок", command=self.draw_line
        ).pack(fill=tk.X, pady=(10, 0))

        # Рисование мышью
        mouse_frame = ttk.LabelFrame(
            self.control_panel, text="Рисование мышью", padding=10
        )
        mouse_frame.pack(fill=tk.X, pady=5, padx=5)
        ttk.Button(
            mouse_frame, text="Нарисовать отрезок мышью", command=self.start_mouse_line
        ).pack(fill=tk.X, pady=2)

        # Алгоритм окружности
        circle_frame = ttk.LabelFrame(
            self.control_panel, text="Алгоритм окружности", padding=10
        )
        circle_frame.pack(fill=tk.X, pady=5, padx=5)

        circle_grid = ttk.Frame(circle_frame)
        circle_grid.pack(fill=tk.X)

        ttk.Label(circle_grid, text="Центр:").grid(row=0, column=0, sticky=tk.W)
        self.cx_var = tk.StringVar(value="0")
        self.cy_var = tk.StringVar(value="0")
        ttk.Entry(circle_grid, textvariable=self.cx_var, width=6).grid(
            row=0, column=1, padx=2
        )
        ttk.Label(circle_grid, text="X").grid(row=0, column=2)
        ttk.Entry(circle_grid, textvariable=self.cy_var, width=6).grid(
            row=0, column=3, padx=2
        )
        ttk.Label(circle_grid, text="Y").grid(row=0, column=4)

        ttk.Label(circle_grid, text="Радиус:").grid(
            row=1, column=0, sticky=tk.W, pady=5
        )
        self.radius_var = tk.StringVar(value="10")
        ttk.Entry(circle_grid, textvariable=self.radius_var, width=6).grid(
            row=1, column=1, padx=2
        )

        ttk.Button(
            circle_frame, text="Нарисовать окружность", command=self.draw_circle
        ).pack(fill=tk.X, pady=(10, 0))

        ttk.Button(
            mouse_frame,
            text="Нарисовать окружность мышью",
            command=self.start_mouse_circle,
        ).pack(fill=tk.X, pady=2)

        # Информация о производительности
        perf_frame = ttk.LabelFrame(
            self.control_panel, text="Производительность", padding=10
        )
        perf_frame.pack(fill=tk.X, pady=5, padx=5)

        self.time_label = ttk.Label(perf_frame, text="Время выполнения: - мкс")
        self.time_label.pack(anchor=tk.W)

        self.pixels_label = ttk.Label(perf_frame, text="Количество пикселей: -")
        self.pixels_label.pack(anchor=tk.W)

        # Управление масштабом
        scale_frame = ttk.LabelFrame(
            self.control_panel, text="Масштаб сетки", padding=10
        )
        scale_frame.pack(fill=tk.X, pady=5, padx=5)

        ttk.Label(scale_frame, text="Размер ячейки:").pack(anchor=tk.W)
        self.scale_var = tk.IntVar(value=20)
        scale_slider = ttk.Scale(
            scale_frame,
            from_=10,
            to=40,
            variable=self.scale_var,
            orient=tk.HORIZONTAL,
            command=self.update_scale,
        )
        scale_slider.pack(fill=tk.X, pady=5)
        self.scale_label = ttk.Label(scale_frame, text="20 пикселей")
        self.scale_label.pack()

        # Кнопки управления
        btn_frame = ttk.Frame(self.control_panel)
        btn_frame.pack(fill=tk.X, pady=10, padx=5)

        ttk.Button(btn_frame, text="🗑️ Очистить холст", command=self.clear_canvas).pack(
            fill=tk.X, pady=2
        )

        ttk.Button(btn_frame, text="❓ Справка", command=self.show_help).pack(
            fill=tk.X, pady=2
        )

    # === Обработчики Scrollable Frame ===
    def on_frame_configure(self, event):
        """Обновление области прокрутки"""
        self.control_canvas.configure(scrollregion=self.control_canvas.bbox("all"))

    def on_canvas_configure(self, event):
        """Растягивание содержимого панели по ширине"""
        canvas_width = event.width
        self.control_canvas.itemconfig(self.canvas_window, width=canvas_width)

    def bind_mouse_scroll(self, widget):
        """Кросс-платформенный скроллинг"""

        def _on_mousewheel(event):
            self.control_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def _on_mousewheel_linux(event):
            if event.num == 4:
                self.control_canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                self.control_canvas.yview_scroll(1, "units")

        widget.bind_all("<MouseWheel>", _on_mousewheel)
        widget.bind_all("<Button-4>", _on_mousewheel_linux)
        widget.bind_all("<Button-5>", _on_mousewheel_linux)

    # === Логика отрисовки и событий ===

    def on_resize_event(self, event):
        """Обработчик изменения размера с задержкой (debounce)"""
        # Если таймер уже запущен, отменяем его
        if self.resize_timer is not None:
            self.root.after_cancel(self.resize_timer)

        # Запускаем новый таймер на 100мс
        self.resize_timer = self.root.after(100, lambda: self.perform_resize(event))

    def perform_resize(self, event):
        """Фактическая перерисовка при изменении размера"""
        new_width = event.width
        new_height = event.height

        if new_width < 10 or new_height < 10:
            return

        # Если размеры изменились
        if new_width != self.canvas_width or new_height != self.canvas_height:
            # Сохраняем нарисованные пиксели в мировых координатах
            pixels_backup = []
            for item in self.canvas.find_withtag("pixel"):
                coords = self.canvas.coords(item)
                color = self.canvas.itemcget(item, "fill")
                if len(coords) == 4:
                    center_x = (coords[0] + coords[2]) / 2
                    center_y = (coords[1] + coords[3]) / 2
                    # Используем старые параметры для восстановления world координат
                    old_world_x, old_world_y = self.screen_to_world(center_x, center_y)
                    pixels_backup.append((old_world_x, old_world_y, color))

            # Обновляем размеры
            self.canvas_width = new_width
            self.canvas_height = new_height
            self.offset_x = self.canvas_width // 2
            self.offset_y = self.canvas_height // 2

            # Перерисовываем
            self.draw_grid()
            self.canvas.delete("pixel")  # Удаляем старые пиксели
            self.canvas.delete("ideal_shape")  # Удаляем старые векторные формы

            # Восстанавливаем пиксели на новых позициях
            for x, y, color in pixels_backup:
                self.draw_pixel(x, y, color)

            # Восстанавливаем векторные формы
            for shape in self.vector_shapes:
                self.render_vector_shape(shape)

        self.resize_timer = None

    def draw_grid(self):
        """Рисование координатной сетки"""
        self.canvas.delete("grid")
        self.canvas.delete("axis")
        self.canvas.delete("labels")

        # Вычисляем смещение сетки, чтобы (0,0) был точно по центру
        start_x_idx = -self.offset_x // self.grid_size
        end_x_idx = (self.canvas_width - self.offset_x) // self.grid_size + 1

        start_y_idx = -self.offset_y // self.grid_size
        end_y_idx = (self.canvas_height - self.offset_y) // self.grid_size + 1

        # Вертикальные линии
        for i in range(start_x_idx, end_x_idx):
            x = self.offset_x + i * self.grid_size
            self.canvas.create_line(
                x, 0, x, self.canvas_height, fill="#e0e0e0", tags="grid"
            )
            # Подписи X
            if (
                i != 0 and i % 2 == 0
            ):  # Подписываем каждую вторую линию, чтобы не было кучи
                self.canvas.create_text(
                    x,
                    self.offset_y + 18,
                    text=str(i),
                    font=("Arial", 11, "bold"),
                    fill="#0066cc",
                    tags="labels",
                )

        # Горизонтальные линии
        for i in range(start_y_idx, end_y_idx):
            y = self.offset_y - i * self.grid_size
            self.canvas.create_line(
                0, y, self.canvas_width, y, fill="#e0e0e0", tags="grid"
            )
            # Подписи Y
            if i != 0 and i % 2 == 0:
                self.canvas.create_text(
                    self.offset_x - 20,
                    y,
                    text=str(i),
                    font=("Arial", 11, "bold"),
                    fill="#0066cc",
                    tags="labels",
                )

        # Оси координат
        self.canvas.create_line(
            self.offset_x,
            0,
            self.offset_x,
            self.canvas_height,
            fill="black",
            width=2,
            tags="axis",
            arrow=tk.LAST,
        )
        self.canvas.create_line(
            0,
            self.offset_y,
            self.canvas_width,
            self.offset_y,
            fill="black",
            width=2,
            tags="axis",
            arrow=tk.LAST,
        )

        # 0
        self.canvas.create_text(
            self.offset_x - 12,
            self.offset_y + 12,
            text="0",
            font=("Arial", 12, "bold"),
            fill="#cc0000",
            tags="labels",
        )

        # Буквы осей
        self.canvas.create_text(
            self.canvas_width - 20,
            self.offset_y - 20,
            text="X",
            font=("Arial", 16, "bold"),
            tags="labels",
        )
        self.canvas.create_text(
            self.offset_x + 20, 20, text="Y", font=("Arial", 16, "bold"), tags="labels"
        )

    def world_to_screen(self, x, y):
        screen_x = self.offset_x + x * self.grid_size
        screen_y = self.offset_y - y * self.grid_size
        return screen_x, screen_y

    def screen_to_world(self, screen_x, screen_y):
        x = round((screen_x - self.offset_x) / self.grid_size)
        y = round((self.offset_y - screen_y) / self.grid_size)
        return x, y

    def draw_pixel(self, x, y, color="blue", intensity=1.0):
        screen_x, screen_y = self.world_to_screen(x, y)
        x1 = screen_x - self.grid_size // 2 + 1
        y1 = screen_y - self.grid_size // 2 + 1
        x2 = screen_x + self.grid_size // 2 - 1
        y2 = screen_y + self.grid_size // 2 - 1
        
        final_color = color
        if intensity < 1.0:
            # Смешивание с белым (фоном)
            # Предполагаем, что color - это имя цвета tk или hex
            # Для упрощения работаем только с базовыми цветами или hex
            
            # Получаем RGB компоненты
            if color == "blue":
                r, g, b = 0, 0, 255
            elif color == "red":
                r, g, b = 255, 0, 0
            elif color == "green":
                r, g, b = 0, 128, 0
            elif color.startswith("#") and len(color) == 7:
                r = int(color[1:3], 16)
                g = int(color[3:5], 16)
                b = int(color[5:7], 16)
            else:
                r, g, b = 0, 0, 0 # Fallback
            
            # Смешиваем с белым (255, 255, 255)
            r = int(r * intensity + 255 * (1 - intensity))
            g = int(g * intensity + 255 * (1 - intensity))
            b = int(b * intensity + 255 * (1 - intensity))
            
            final_color = f"#{r:02x}{g:02x}{b:02x}"
            
        self.canvas.create_rectangle(
            x1, y1, x2, y2, fill=final_color, outline=final_color, tags="pixel"
        )

    def render_vector_shape(self, shape_data):
        """Отрисовка векторной формы на основе данных"""
        if shape_data["type"] == "line":
            x1, y1, x2, y2 = shape_data["coords"]
            sx1, sy1 = self.world_to_screen(x1, y1)
            sx2, sy2 = self.world_to_screen(x2, y2)
            self.canvas.create_line(
                sx1, sy1, sx2, sy2, fill="green", width=2, tags="ideal_shape"
            )
        elif shape_data["type"] == "circle":
            cx, cy, r = shape_data["coords"]
            sx, sy = self.world_to_screen(cx, cy)
            sr = r * self.grid_size
            self.canvas.create_oval(
                sx - sr,
                sy - sr,
                sx + sr,
                sy + sr,
                outline="green",
                width=2,
                tags="ideal_shape",
            )

    # ========== Алгоритмы растеризации ==========

    def step_by_step_algorithm(self, x1, y1, x2, y2):
        pixels = []
        dx = x2 - x1
        dy = y2 - y1
        steps = max(abs(dx), abs(dy))
        if steps == 0:
            pixels.append((x1, y1))
            return pixels
        x_inc = dx / steps
        y_inc = dy / steps
        x = x1
        y = y1
        for _ in range(steps + 1):
            pixels.append((round(x), round(y)))
            x += x_inc
            y += y_inc
        return pixels

    def dda_algorithm(self, x1, y1, x2, y2):
        pixels = []
        dx = x2 - x1
        dy = y2 - y1
        steps = max(abs(dx), abs(dy))
        if steps == 0:
            pixels.append((x1, y1))
            return pixels
        x_inc = dx / steps
        y_inc = dy / steps
        x = float(x1)
        y = float(y1)
        for _ in range(steps + 1):
            pixels.append((round(x), round(y)))
            x += x_inc
            y += y_inc
        return pixels

    def bresenham_line_algorithm(self, x1, y1, x2, y2):
        pixels = []
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        x = x1
        y = y1
        x_sign = 1 if x2 > x1 else -1
        y_sign = 1 if y2 > y1 else -1
        if dx > dy:
            error = dx / 2
            while x != x2:
                pixels.append((x, y))
                error -= dy
                if error < 0:
                    y += y_sign
                    error += dx
                x += x_sign
            pixels.append((x, y))
        else:
            error = dy / 2
            while y != y2:
                pixels.append((x, y))
                error -= dx
                if error < 0:
                    x += x_sign
                    error += dy
                y += y_sign
            pixels.append((x, y))
        return pixels

    def bresenham_circle_algorithm(self, cx, cy, radius):
        pixels = []
        x = 0
        y = radius
        d = 3 - 2 * radius

        def add_circle_points(cx, cy, x, y):
            return [
                (cx + x, cy + y),
                (cx - x, cy + y),
                (cx + x, cy - y),
                (cx - x, cy - y),
                (cx + y, cy + x),
                (cx - y, cy + x),
                (cx + y, cy - x),
                (cx - y, cy - x),
            ]

        while x <= y:
            pixels.extend(add_circle_points(cx, cy, x, y))
            if d < 0:
                d = d + 4 * x + 6
            else:
                d = d + 4 * (x - y) + 10
                y -= 1
            x += 1
        return pixels

    def castle_piteway_algorithm(self, x1, y1, x2, y2):
        """Алгоритм Кастла-Питвея (целочисленный Брезенхем)"""
        pixels = []
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        
        step_x = 1 if x2 >= x1 else -1
        step_y = 1 if y2 >= y1 else -1
        
        # Обмен ролями осей, если угол наклона > 45 градусов
        swapped = False
        if dy > dx:
            dx, dy = dy, dx
            swapped = True
            
        e = 2 * dy - dx
        x, y = x1, y1
        
        for _ in range(dx + 1):
            pixels.append((x, y))
            
            while e >= 0:
                if swapped:
                    x += step_x
                else:
                    y += step_y
                e = e - 2 * dx
            
            if swapped:
                y += step_y
            else:
                x += step_x
            e = e + 2 * dy
            
        return pixels

    def wu_algorithm(self, x1, y1, x2, y2):
        """Алгоритм Ву для сглаживания линий"""
        if abs(y2 - y1) > abs(x2 - x1):
            return self._wu_algorithm_impl(y1, x1, y2, x2, True)
        else:
            return self._wu_algorithm_impl(x1, y1, x2, y2, False)

    def _wu_algorithm_impl(self, x1, y1, x2, y2, swap_xy):
        pixels = []
        
        def plot(x, y, c):
            if swap_xy:
                pixels.append((y, x, c))
            else:
                pixels.append((x, y, c))
        
        def ipart(x): return int(x)
        def round_func(x): return ipart(x + 0.5)
        def fpart(x): return x - ipart(x)
        def rfpart(x): return 1 - fpart(x)

        dx = x2 - x1
        dy = y2 - y1
        
        if abs(dx) < abs(dy):
            # Should not happen if called correctly
            pass
            
        if x2 < x1:
            x1, x2 = x2, x1
            y1, y2 = y2, y1
            dx = x2 - x1
            dy = y2 - y1
            
        gradient = dy / dx if dx != 0 else 1.0
        
        # Первая точка
        xend = round_func(x1)
        yend = y1 + gradient * (xend - x1)
        xgap = rfpart(x1 + 0.5)
        xpxl1 = xend
        ypxl1 = ipart(yend)
        
        plot(xpxl1, ypxl1, rfpart(yend) * xgap)
        plot(xpxl1, ypxl1 + 1, fpart(yend) * xgap)
        
        intery = yend + gradient
        
        # Вторая точка
        xend = round_func(x2)
        yend = y2 + gradient * (xend - x2)
        xgap = fpart(x2 + 0.5)
        xpxl2 = xend
        ypxl2 = ipart(yend)
        
        plot(xpxl2, ypxl2, rfpart(yend) * xgap)
        plot(xpxl2, ypxl2 + 1, fpart(yend) * xgap)
        
        # Основной цикл
        for x in range(xpxl1 + 1, xpxl2):
            plot(x, ipart(intery), rfpart(intery))
            plot(x, ipart(intery) + 1, fpart(intery))
            intery = intery + gradient
            
        return pixels

    # ========== Функции рисования ==========

    def draw_line(self):
        try:
            x1 = int(self.x1_var.get())
            y1 = int(self.y1_var.get())
            x2 = int(self.x2_var.get())
            y2 = int(self.y2_var.get())

            algorithm = self.line_algorithm.get()
            start_time = time.perf_counter()

            if algorithm == "step_by_step":
                pixels = self.step_by_step_algorithm(x1, y1, x2, y2)
                algo_name = "Пошаговый алгоритм"
            elif algorithm == "dda":
                pixels = self.dda_algorithm(x1, y1, x2, y2)
                algo_name = "Алгоритм ЦДА"
            elif algorithm == "castle_piteway":
                pixels = self.castle_piteway_algorithm(x1, y1, x2, y2)
                algo_name = "Алгоритм Кастла-Питвея"
            elif algorithm == "wu":
                pixels = self.wu_algorithm(x1, y1, x2, y2)
                algo_name = "Алгоритм Ву (сглаживание)"
            else:
                pixels = self.bresenham_line_algorithm(x1, y1, x2, y2)
                algo_name = "Алгоритм Брезенхема"

            end_time = time.perf_counter()

            # Рисуем идеальную векторную линию
            shape_data = {"type": "line", "coords": (x1, y1, x2, y2)}
            self.vector_shapes.append(shape_data)
            self.render_vector_shape(shape_data)

            for point in pixels:
                if len(point) == 2:
                    self.draw_pixel(point[0], point[1])
                elif len(point) == 3:
                     self.draw_pixel(point[0], point[1], intensity=point[2])

            exec_time = (end_time - start_time) * 1_000_000
            self.last_time = exec_time
            self.last_pixels_count = len(pixels)

            self.time_label.config(text=f"Время выполнения: {exec_time:.2f} мкс")
            self.pixels_label.config(text=f"Количество пикселей: {len(pixels)}")
            self.status_label.config(
                text=f"{algo_name}: отрезок ({x1},{y1}) - ({x2},{y2})"
            )

        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректные целые числа")

    def draw_circle(self):
        try:
            cx = int(self.cx_var.get())
            cy = int(self.cy_var.get())
            radius = int(self.radius_var.get())

            if radius <= 0:
                messagebox.showerror("Ошибка", "Радиус должен быть положительным")
                return

            start_time = time.perf_counter()
            pixels = self.bresenham_circle_algorithm(cx, cy, radius)
            end_time = time.perf_counter()

            # Рисуем идеальную векторную окружность
            shape_data = {"type": "circle", "coords": (cx, cy, radius)}
            self.vector_shapes.append(shape_data)
            self.render_vector_shape(shape_data)

            for x, y in pixels:
                self.draw_pixel(x, y, color="red")

            exec_time = (end_time - start_time) * 1_000_000
            self.last_time = exec_time
            self.last_pixels_count = len(pixels)

            self.time_label.config(text=f"Время выполнения: {exec_time:.2f} мкс")
            self.pixels_label.config(text=f"Количество пикселей: {len(pixels)}")
            self.status_label.config(
                text=f"Алгоритм Брезенхема: окружность центр ({cx},{cy}), радиус {radius}"
            )

        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректные целые числа")

    # ========== Рисование мышью ==========

    def start_mouse_line(self):
        self.drawing_mode = "line"
        self.click_points = []
        self.status_label.config(text="Кликните на две точки для рисования отрезка")

    def start_mouse_circle(self):
        self.drawing_mode = "circle"
        self.click_points = []
        self.status_label.config(text="Кликните центр, затем точку на окружности")

    def on_canvas_click(self, event):
        if self.drawing_mode is None:
            return

        x, y = self.screen_to_world(event.x, event.y)
        self.click_points.append((x, y))

        screen_x, screen_y = self.world_to_screen(x, y)
        self.canvas.create_oval(
            screen_x - 5,
            screen_y - 5,
            screen_x + 5,
            screen_y + 5,
            fill="green",
            tags="marker",
        )

        if self.drawing_mode == "line" and len(self.click_points) == 2:
            x1, y1 = self.click_points[0]
            x2, y2 = self.click_points[1]

            self.x1_var.set(str(x1))
            self.y1_var.set(str(y1))
            self.x2_var.set(str(x2))
            self.y2_var.set(str(y2))

            self.draw_line()
            self.canvas.delete("marker")
            self.drawing_mode = None
            self.click_points = []

        elif self.drawing_mode == "circle" and len(self.click_points) == 2:
            cx, cy = self.click_points[0]
            px, py = self.click_points[1]
            radius = round(math.sqrt((px - cx) ** 2 + (py - cy) ** 2))

            self.cx_var.set(str(cx))
            self.cy_var.set(str(cy))
            self.radius_var.set(str(radius))

            self.draw_circle()
            self.canvas.delete("marker")
            self.drawing_mode = None
            self.click_points = []

    def on_mouse_move(self, event):
        x, y = self.screen_to_world(event.x, event.y)
        if self.drawing_mode:
            self.status_label.config(
                text=f"Текущая позиция: ({x}, {y}) | Выбрано точек: {len(self.click_points)}"
            )

    # ========== Управление ==========

    def update_scale(self, value):
        self.grid_size = int(float(value))
        self.scale_label.config(text=f"{self.grid_size} пикселей")
        self.clear_canvas()

    def clear_canvas(self):
        self.canvas.delete("pixel")
        self.canvas.delete("marker")
        self.canvas.delete("ideal_shape")
        self.vector_shapes = []  # Очищаем список векторных фигур
        self.draw_grid()
        self.drawing_mode = None
        self.click_points = []
        self.status_label.config(text="Холст очищен")

    def show_help(self):
        help_text = """
Справка по использованию программы:
1. РИСОВАНИЕ: Выберите алгоритм и введите координаты или используйте мышь.
2. МАСШТАБ: Используйте ползунок для изменения размера ячеек.
3. АДАПТИВНОСТЬ: Окно можно менять в размерах, сетка перестроится автоматически.

Описание алгоритмов:
- Кастла-Питвея: Целочисленная оптимизация Брезенхема (без деления).
- Ву (Wu): Алгоритм сглаживания (anti-aliasing). Интенсивность пикселя зависит от расстояния до идеальной линии.
        """
        messagebox.showinfo("Справка", help_text)


def main():
    root = tk.Tk()
    app = RasterizationApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
