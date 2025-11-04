import tkinter as tk
from tkinter import ttk, colorchooser, messagebox
import math


class ColorConverter:
    """Класс для конвертации цветов между различными цветовыми моделями"""
    
    @staticmethod
    def rgb_to_hsv(r, g, b):
        """Конвертация RGB в HSV"""
        r, g, b = r/255.0, g/255.0, b/255.0
        
        max_val = max(r, g, b)
        min_val = min(r, g, b)
        diff = max_val - min_val
        
        # Value
        v = max_val
        
        # Saturation
        s = 0 if max_val == 0 else diff / max_val
        
        # Hue
        if diff == 0:
            h = 0
        elif max_val == r:
            h = (60 * ((g - b) / diff) + 360) % 360
        elif max_val == g:
            h = (60 * ((b - r) / diff) + 120) % 360
        else:  # max_val == b
            h = (60 * ((r - g) / diff) + 240) % 360
        
        return round(h, 2), round(s * 100, 2), round(v * 100, 2)
    
    @staticmethod
    def hsv_to_rgb(h, s, v):
        """Конвертация HSV в RGB"""
        h = h % 360
        s = max(0, min(100, s)) / 100.0
        v = max(0, min(100, v)) / 100.0
        
        c = v * s
        x = c * (1 - abs((h / 60) % 2 - 1))
        m = v - c
        
        if 0 <= h < 60:
            r, g, b = c, x, 0
        elif 60 <= h < 120:
            r, g, b = x, c, 0
        elif 120 <= h < 180:
            r, g, b = 0, c, x
        elif 180 <= h < 240:
            r, g, b = 0, x, c
        elif 240 <= h < 300:
            r, g, b = x, 0, c
        else:
            r, g, b = c, 0, x
        
        r = int(round((r + m) * 255))
        g = int(round((g + m) * 255))
        b = int(round((b + m) * 255))
        
        # Ограничиваем значения в пределах 0-255
        r = max(0, min(255, r))
        g = max(0, min(255, g))
        b = max(0, min(255, b))
        
        return r, g, b
    
    @staticmethod
    def rgb_to_cmyk(r, g, b):
        """Конвертация RGB в CMYK"""
        if r == 0 and g == 0 and b == 0:
            return 0, 0, 0, 100
        
        r, g, b = r/255.0, g/255.0, b/255.0
        
        k = 1 - max(r, g, b)
        c = (1 - r - k) / (1 - k) if k != 1 else 0
        m = (1 - g - k) / (1 - k) if k != 1 else 0
        y = (1 - b - k) / (1 - k) if k != 1 else 0
        
        return round(c * 100, 2), round(m * 100, 2), round(y * 100, 2), round(k * 100, 2)
    
    @staticmethod
    def cmyk_to_rgb(c, m, y, k):
        """Конвертация CMYK в RGB"""
        c = max(0, min(100, c)) / 100.0
        m = max(0, min(100, m)) / 100.0
        y = max(0, min(100, y)) / 100.0
        k = max(0, min(100, k)) / 100.0
        
        r = 255 * (1 - c) * (1 - k)
        g = 255 * (1 - m) * (1 - k)
        b = 255 * (1 - y) * (1 - k)
        
        r = int(round(max(0, min(255, r))))
        g = int(round(max(0, min(255, g))))
        b = int(round(max(0, min(255, b))))
        
        return r, g, b


class ColorConverterApp:
    """Основной класс приложения для конвертации цветов"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Конвертер цветов RGB ↔ CMYK ↔ HSV")
        self.root.geometry("900x800")
        self.root.resizable(True, True)
        self.root.configure(bg='#f0f0f0')
        
        # Флаг для предотвращения циклических обновлений
        self.updating = False
        
        # Текущий цвет (в RGB)
        self.current_color = [255, 0, 0]  # Красный по умолчанию
        
        # Размер круглого индикатора цвета
        self.circle_size = 150
        
        self.setup_ui()
        self.update_all_from_rgb()
    
    def setup_ui(self):
        """Создание пользовательского интерфейса"""
        
        # Главный контейнер
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Настройка сетки для растягивания
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)  # Верхняя половина
        main_frame.rowconfigure(2, weight=1)  # Нижняя половина
        
        # Верхний контейнер для заголовка и цветового индикатора
        top_frame = ttk.Frame(main_frame)
        top_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 20))
        top_frame.columnconfigure(0, weight=1)
        
        # Заголовок
        title_label = ttk.Label(top_frame, text="Конвертер цветов", font=("Arial", 18, "bold"))
        title_label.grid(row=0, column=0, pady=(0, 30))
        
        # Контейнер для круглого индикатора цвета
        color_frame = ttk.Frame(top_frame)
        color_frame.grid(row=1, column=0, pady=(0, 20))
        
        # Круглый индикатор цвета
        canvas_size = self.circle_size + 20  # Добавляем отступы
        self.color_canvas = tk.Canvas(color_frame, width=canvas_size, height=canvas_size, 
                                     bg='white', highlightthickness=0, relief='flat')
        self.color_canvas.grid(row=0, column=0)
        
        # Создаем круг
        margin = 10
        self.color_circle = self.color_canvas.create_oval(
            margin, margin, 
            self.circle_size + margin, self.circle_size + margin,
            fill='#FF0000', outline='#888888', width=3
        )
        
        # Кнопка выбора цвета из палитры
        color_button = ttk.Button(top_frame, text="🎨 Выбрать из палитры", command=self.choose_color)
        color_button.grid(row=2, column=0, pady=(10, 0))
        
        # Контейнер для трех колонок
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Настройка колонок с одинаковым весом
        for i in range(3):
            bottom_frame.columnconfigure(i, weight=1)
        
        # Создаем три колонки
        self.setup_rgb_column(bottom_frame, 0)
        self.setup_cmyk_column(bottom_frame, 1) 
        self.setup_hsv_column(bottom_frame, 2)
        
        # Статус бар для предупреждений
        self.status_var = tk.StringVar()
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, foreground="red", font=("Arial", 10))
        status_bar.grid(row=2, column=0, pady=(20, 0))
    
    def setup_rgb_column(self, parent, column):
        """Создание колонки RGB"""
        
        # Контейнер колонки
        rgb_frame = ttk.LabelFrame(parent, text="RGB (0-255)", padding="15")
        rgb_frame.grid(row=0, column=column, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10)
        rgb_frame.columnconfigure(1, weight=1)
        
        # Поля ввода RGB
        self.rgb_vars = [tk.StringVar(), tk.StringVar(), tk.StringVar()]
        self.rgb_entries = []
        rgb_labels = ["R:", "G:", "B:"]
        rgb_colors = ["#ffcccc", "#ccffcc", "#ccccff"]  # Цветовые подсказки
        
        for i, (label, color) in enumerate(zip(rgb_labels, rgb_colors)):
            # Метка
            label_widget = ttk.Label(rgb_frame, text=label, font=("Arial", 10, "bold"))
            label_widget.grid(row=i*3, column=0, sticky=tk.W, pady=(5, 0))
            
            # Поле ввода
            entry = ttk.Entry(rgb_frame, textvariable=self.rgb_vars[i], width=8, font=("Arial", 10))
            entry.grid(row=i*3, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=(5, 0))
            entry.bind('<KeyRelease>', lambda e, idx=i: self.on_rgb_change(idx))
            self.rgb_entries.append(entry)
            
            # Ползунок (одинаковая длина для всех)
            scale = ttk.Scale(rgb_frame, from_=0, to=255, orient=tk.HORIZONTAL, length=220,
                             command=lambda val, idx=i: self.on_rgb_scale_change(idx, val))
            scale.grid(row=i*3+1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 10))
            
            if not hasattr(self, 'rgb_scales'):
                self.rgb_scales = []
            self.rgb_scales.append(scale)
    
    def setup_cmyk_column(self, parent, column):
        """Создание колонки CMYK"""
        
        # Контейнер колонки
        cmyk_frame = ttk.LabelFrame(parent, text="CMYK (0-100%)", padding="15")
        cmyk_frame.grid(row=0, column=column, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10)
        cmyk_frame.columnconfigure(1, weight=1)
        
        # Поля ввода CMYK
        self.cmyk_vars = [tk.StringVar(), tk.StringVar(), tk.StringVar(), tk.StringVar()]
        self.cmyk_entries = []
        cmyk_labels = ["C:", "M:", "Y:", "K:"]
        cmyk_colors = ["#ccffff", "#ffccff", "#ffffcc", "#e0e0e0"]  # Цветовые подсказки
        
        for i, (label, color) in enumerate(zip(cmyk_labels, cmyk_colors)):
            # Метка
            label_widget = ttk.Label(cmyk_frame, text=label, font=("Arial", 10, "bold"))
            label_widget.grid(row=i*3, column=0, sticky=tk.W, pady=(5, 0))
            
            # Поле ввода
            entry = ttk.Entry(cmyk_frame, textvariable=self.cmyk_vars[i], width=8, font=("Arial", 10))
            entry.grid(row=i*3, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=(5, 0))
            entry.bind('<KeyRelease>', lambda e, idx=i: self.on_cmyk_change(idx))
            self.cmyk_entries.append(entry)
            
            # Ползунок (одинаковая длина, но другая чувствительность - разрешение 0.1)
            scale = ttk.Scale(cmyk_frame, from_=0, to=100, orient=tk.HORIZONTAL, length=220,
                             command=lambda val, idx=i: self.on_cmyk_scale_change(idx, val))
            scale.grid(row=i*3+1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 10))
            
            if not hasattr(self, 'cmyk_scales'):
                self.cmyk_scales = []
            self.cmyk_scales.append(scale)
    
    def setup_hsv_column(self, parent, column):
        """Создание колонки HSV"""
        
        # Контейнер колонки
        hsv_frame = ttk.LabelFrame(parent, text="HSV", padding="15")
        hsv_frame.grid(row=0, column=column, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10)
        hsv_frame.columnconfigure(1, weight=1)
        
        # Поля ввода HSV
        self.hsv_vars = [tk.StringVar(), tk.StringVar(), tk.StringVar()]
        self.hsv_entries = []
        hsv_labels = ["H (0-360°):", "S (0-100%):", "V (0-100%):"]
        hsv_colors = ["#ffe6e6", "#e6ffe6", "#e6e6ff"]  # Цветовые подсказки
        max_values = [360, 100, 100]
        
        for i, (label, color, max_val) in enumerate(zip(hsv_labels, hsv_colors, max_values)):
            # Метка
            label_widget = ttk.Label(hsv_frame, text=label, font=("Arial", 10, "bold"))
            label_widget.grid(row=i*3, column=0, sticky=tk.W, pady=(5, 0))
            
            # Поле ввода
            entry = ttk.Entry(hsv_frame, textvariable=self.hsv_vars[i], width=8, font=("Arial", 10))
            entry.grid(row=i*3, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=(5, 0))
            entry.bind('<KeyRelease>', lambda e, idx=i: self.on_hsv_change(idx))
            self.hsv_entries.append(entry)
            
            # Ползунок (одинаковая длина, но разная чувствительность)
            # H имеет большую чувствительность (0-360), S и V меньшую (0-100)
            scale = ttk.Scale(hsv_frame, from_=0, to=max_val, orient=tk.HORIZONTAL, length=220,
                             command=lambda val, idx=i: self.on_hsv_scale_change(idx, val))
            scale.grid(row=i*3+1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 10))
            
            if not hasattr(self, 'hsv_scales'):
                self.hsv_scales = []
            self.hsv_scales.append(scale)
    
    def clear_status(self):
        """Очистить статус бар"""
        self.status_var.set("")
    
    def set_status(self, message):
        """Установить сообщение в статус баре"""
        self.status_var.set(message)
        # Автоматически очистить через 3 секунды
        self.root.after(3000, self.clear_status)
    
    def validate_rgb_value(self, value, component):
        """Валидация значения RGB"""
        try:
            val = float(value)
            if val < 0:
                self.set_status(f"Предупреждение: {component} < 0, значение обрезано до 0")
                return 0
            elif val > 255:
                self.set_status(f"Предупреждение: {component} > 255, значение обрезано до 255")
                return 255
            return int(val)
        except ValueError:
            return None
    
    def validate_cmyk_value(self, value, component):
        """Валидация значения CMYK"""
        try:
            val = float(value)
            if val < 0:
                self.set_status(f"Предупреждение: {component} < 0%, значение обрезано до 0%")
                return 0
            elif val > 100:
                self.set_status(f"Предупреждение: {component} > 100%, значение обрезано до 100%")
                return 100
            return val
        except ValueError:
            return None
    
    def validate_hsv_value(self, value, component, max_val):
        """Валидация значения HSV"""
        try:
            val = float(value)
            if val < 0:
                self.set_status(f"Предупреждение: {component} < 0, значение обрезано до 0")
                return 0
            elif val > max_val:
                self.set_status(f"Предупреждение: {component} > {max_val}, значение обрезано до {max_val}")
                return max_val
            return val
        except ValueError:
            return None
    
    def choose_color(self):
        """Выбор цвета из палитры"""
        color = colorchooser.askcolor(title="Выберите цвет")
        if color[0]:  # Если пользователь выбрал цвет
            r, g, b = [int(c) for c in color[0]]
            self.current_color = [r, g, b]
            self.update_all_from_rgb()
    
    def update_color_preview(self):
        """Обновление круглого превью цвета"""
        r, g, b = self.current_color
        hex_color = f"#{r:02x}{g:02x}{b:02x}"
        
        # Обновляем цвет круга
        self.color_canvas.itemconfig(self.color_circle, fill=hex_color)
        
        # Добавляем градиент эффект для лучшего вида
        # Если цвет темный, делаем светлую границу, если светлый - темную
        brightness = (r * 0.299 + g * 0.587 + b * 0.114)
        outline_color = "#ffffff" if brightness < 128 else "#333333"
        self.color_canvas.itemconfig(self.color_circle, outline=outline_color)
    
    def on_rgb_change(self, index):
        """Обработчик изменения RGB через поля ввода"""
        if self.updating:
            return
        
        value = self.rgb_vars[index].get()
        if value == "":
            return
        
        components = ["R", "G", "B"]
        validated_value = self.validate_rgb_value(value, components[index])
        
        if validated_value is not None:
            self.current_color[index] = validated_value
            self.updating = True
            self.rgb_vars[index].set(str(validated_value))
            self.rgb_scales[index].set(validated_value)
            self.updating = False
            self.update_cmyk_hsv_from_rgb()
    
    def on_rgb_scale_change(self, index, value):
        """Обработчик изменения RGB через ползунки"""
        if self.updating:
            return
        
        val = int(float(value))
        self.current_color[index] = val
        self.updating = True
        self.rgb_vars[index].set(str(val))
        self.updating = False
        self.update_cmyk_hsv_from_rgb()
    
    def on_cmyk_change(self, index):
        """Обработчик изменения CMYK через поля ввода"""
        if self.updating:
            return
        
        value = self.cmyk_vars[index].get()
        if value == "":
            return
        
        components = ["C", "M", "Y", "K"]
        validated_value = self.validate_cmyk_value(value, components[index])
        
        if validated_value is not None:
            # Получаем все значения CMYK
            values = []
            for i in range(4):
                if i == index:
                    values.append(validated_value)
                else:
                    try:
                        val = float(self.cmyk_vars[i].get()) if self.cmyk_vars[i].get() else 0
                        values.append(max(0, min(100, val)))
                    except ValueError:
                        values.append(0)
            
            # Конвертируем в RGB
            r, g, b = ColorConverter.cmyk_to_rgb(*values)
            self.current_color = [r, g, b]
            
            self.updating = True
            self.cmyk_vars[index].set(f"{validated_value:.2f}")
            self.cmyk_scales[index].set(validated_value)
            self.updating = False
            
            self.update_rgb_hsv_from_current()
    
    def on_cmyk_scale_change(self, index, value):
        """Обработчик изменения CMYK через ползунки"""
        if self.updating:
            return
        
        values = []
        for i in range(4):
            if i == index:
                val = float(value)
            else:
                val = self.cmyk_scales[i].get()
            values.append(val)
        
        # Конвертируем в RGB
        r, g, b = ColorConverter.cmyk_to_rgb(*values)
        self.current_color = [r, g, b]
        
        self.updating = True
        for i, val in enumerate(values):
            self.cmyk_vars[i].set(f"{val:.2f}")
        self.updating = False
        
        self.update_rgb_hsv_from_current()
    
    def on_hsv_change(self, index):
        """Обработчик изменения HSV через поля ввода"""
        if self.updating:
            return
        
        value = self.hsv_vars[index].get()
        if value == "":
            return
        
        components = ["H", "S", "V"]
        max_vals = [360, 100, 100]
        validated_value = self.validate_hsv_value(value, components[index], max_vals[index])
        
        if validated_value is not None:
            # Получаем все значения HSV
            values = []
            for i in range(3):
                if i == index:
                    values.append(validated_value)
                else:
                    try:
                        val = float(self.hsv_vars[i].get()) if self.hsv_vars[i].get() else 0
                        values.append(max(0, min(max_vals[i], val)))
                    except ValueError:
                        values.append(0)
            
            # Конвертируем в RGB
            r, g, b = ColorConverter.hsv_to_rgb(*values)
            self.current_color = [r, g, b]
            
            self.updating = True
            self.hsv_vars[index].set(f"{validated_value:.2f}")
            self.hsv_scales[index].set(validated_value)
            self.updating = False
            
            self.update_rgb_cmyk_from_current()
    
    def on_hsv_scale_change(self, index, value):
        """Обработчик изменения HSV через ползунки"""
        if self.updating:
            return
        
        values = []
        for i in range(3):
            if i == index:
                val = float(value)
            else:
                val = self.hsv_scales[i].get()
            values.append(val)
        
        # Конвертируем в RGB
        r, g, b = ColorConverter.hsv_to_rgb(*values)
        self.current_color = [r, g, b]
        
        self.updating = True
        for i, val in enumerate(values):
            self.hsv_vars[i].set(f"{val:.2f}")
        self.updating = False
        
        self.update_rgb_cmyk_from_current()
    
    def update_all_from_rgb(self):
        """Обновить все модели из текущего RGB"""
        self.updating = True
        
        # Обновляем RGB
        for i, val in enumerate(self.current_color):
            self.rgb_vars[i].set(str(val))
            self.rgb_scales[i].set(val)
        
        # Обновляем CMYK
        c, m, y, k = ColorConverter.rgb_to_cmyk(*self.current_color)
        cmyk_values = [c, m, y, k]
        for i, val in enumerate(cmyk_values):
            self.cmyk_vars[i].set(f"{val:.2f}")
            self.cmyk_scales[i].set(val)
        
        # Обновляем HSV
        h, s, v = ColorConverter.rgb_to_hsv(*self.current_color)
        hsv_values = [h, s, v]
        for i, val in enumerate(hsv_values):
            self.hsv_vars[i].set(f"{val:.2f}")
            self.hsv_scales[i].set(val)
        
        self.update_color_preview()
        self.updating = False
    
    def update_cmyk_hsv_from_rgb(self):
        """Обновить CMYK и HSV из текущего RGB"""
        self.updating = True
        
        # Обновляем CMYK
        c, m, y, k = ColorConverter.rgb_to_cmyk(*self.current_color)
        cmyk_values = [c, m, y, k]
        for i, val in enumerate(cmyk_values):
            self.cmyk_vars[i].set(f"{val:.2f}")
            self.cmyk_scales[i].set(val)
        
        # Обновляем HSV
        h, s, v = ColorConverter.rgb_to_hsv(*self.current_color)
        hsv_values = [h, s, v]
        for i, val in enumerate(hsv_values):
            self.hsv_vars[i].set(f"{val:.2f}")
            self.hsv_scales[i].set(val)
        
        self.update_color_preview()
        self.updating = False
    
    def update_rgb_hsv_from_current(self):
        """Обновить RGB и HSV из текущего цвета"""
        self.updating = True
        
        # Обновляем RGB
        for i, val in enumerate(self.current_color):
            self.rgb_vars[i].set(str(val))
            self.rgb_scales[i].set(val)
        
        # Обновляем HSV
        h, s, v = ColorConverter.rgb_to_hsv(*self.current_color)
        hsv_values = [h, s, v]
        for i, val in enumerate(hsv_values):
            self.hsv_vars[i].set(f"{val:.2f}")
            self.hsv_scales[i].set(val)
        
        self.update_color_preview()
        self.updating = False
    
    def update_rgb_cmyk_from_current(self):
        """Обновить RGB и CMYK из текущего цвета"""
        self.updating = True
        
        # Обновляем RGB
        for i, val in enumerate(self.current_color):
            self.rgb_vars[i].set(str(val))
            self.rgb_scales[i].set(val)
        
        # Обновляем CMYK
        c, m, y, k = ColorConverter.rgb_to_cmyk(*self.current_color)
        cmyk_values = [c, m, y, k]
        for i, val in enumerate(cmyk_values):
            self.cmyk_vars[i].set(f"{val:.2f}")
            self.cmyk_scales[i].set(val)
        
        self.update_color_preview()
        self.updating = False


def main():
    """Главная функция приложения"""
    root = tk.Tk()
    app = ColorConverterApp(root)
    
    # Центрируем окно на экране
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()


if __name__ == "__main__":
    main()
