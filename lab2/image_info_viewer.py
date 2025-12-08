import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from PIL import Image
import threading
from pathlib import Path


class ImageInfoViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Просмотр информации об изображениях")
        self.root.geometry("1200x700")
        
        self.loading = False
        self.cancel_loading = False
        
        self.create_widgets()
        
    def create_widgets(self):
        top_frame = ttk.Frame(self.root, padding="10")
        top_frame.pack(fill=tk.X)
        
        ttk.Button(top_frame, text="Выбрать файлы", 
                  command=self.select_files).pack(side=tk.LEFT, padx=5)
        ttk.Button(top_frame, text="Выбрать папку", 
                  command=self.select_folder).pack(side=tk.LEFT, padx=5)
        ttk.Button(top_frame, text="Очистить", 
                  command=self.clear_table).pack(side=tk.LEFT, padx=5)
        
        self.cancel_button = ttk.Button(top_frame, text="Отменить загрузку", 
                                       command=self.cancel_load, state=tk.DISABLED)
        self.cancel_button.pack(side=tk.LEFT, padx=5)
        
        self.progress_frame = ttk.Frame(self.root, padding="10")
        self.progress_frame.pack(fill=tk.X)
        
        self.progress_label = ttk.Label(self.progress_frame, text="")
        self.progress_label.pack(side=tk.LEFT, padx=5)
        
        self.progress_bar = ttk.Progressbar(self.progress_frame, mode='determinate')
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        table_frame = ttk.Frame(self.root)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ("Имя файла", "Размер (пиксели)", "Разрешение (DPI)", 
                   "Глубина цвета", "Сжатие")
        
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=20)
        
        self.tree.heading("Имя файла", text="Имя файла")
        self.tree.heading("Размер (пиксели)", text="Размер (пиксели)")
        self.tree.heading("Разрешение (DPI)", text="Разрешение (DPI)")
        self.tree.heading("Глубина цвета", text="Глубина цвета")
        self.tree.heading("Сжатие", text="Сжатие")
        
        self.tree.column("Имя файла", width=300, anchor=tk.W)
        self.tree.column("Размер (пиксели)", width=150, anchor=tk.CENTER)
        self.tree.column("Разрешение (DPI)", width=150, anchor=tk.CENTER)
        self.tree.column("Глубина цвета", width=150, anchor=tk.CENTER)
        self.tree.column("Сжатие", width=200, anchor=tk.CENTER)
        
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(xscrollcommand=hsb.set)
        
        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        self.status_label = ttk.Label(self.root, text="Готов", relief=tk.SUNKEN)
        self.status_label.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=5)
    
    def select_files(self):
        """Выбор отдельных файлов"""
        filetypes = (
            ('Изображения', '*.bmp *.jpg *.jpeg *.png *.gif *.tiff *.tif'),
            ('BMP файлы', '*.bmp'),
            ('JPEG файлы', '*.jpg *.jpeg'),
            ('PNG файлы', '*.png'),
            ('Все файлы', '*.*')
        )
        
        filenames = filedialog.askopenfilenames(
            title='Выберите изображения',
            filetypes=filetypes
        )
        
        if filenames:
            self.process_files(list(filenames))
    
    def select_folder(self):
        """Выбор папки с изображениями"""
        folder = filedialog.askdirectory(title='Выберите папку с изображениями')
        
        if folder:
            image_extensions = ('.bmp', '.jpg', '.jpeg', '.png', '.gif', '.tiff', '.tif')
            files = []
            
            for file in Path(folder).rglob('*'):
                if file.is_file() and file.suffix.lower() in image_extensions:
                    files.append(str(file))
            
            if files:
                self.process_files(files)
            else:
                messagebox.showinfo("Информация", "В выбранной папке не найдено изображений")
    
    def clear_table(self):
        """Очистка таблицы"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.status_label.config(text="Готов")
        self.progress_label.config(text="")
        self.progress_bar['value'] = 0
    
    def cancel_load(self):
        """Отмена загрузки файлов"""
        self.cancel_loading = True
        self.cancel_button.config(state=tk.DISABLED)
    
    def process_files(self, files):
        """Обработка списка файлов в отдельном потоке"""
        if self.loading:
            messagebox.showwarning("Предупреждение", 
                                  "Дождитесь завершения текущей загрузки")
            return
        
        self.loading = True
        self.cancel_loading = False
        self.cancel_button.config(state=tk.NORMAL)
        
        thread = threading.Thread(target=self._process_files_thread, args=(files,))
        thread.daemon = True
        thread.start()
    
    def _process_files_thread(self, files):
        """Обработка файлов в отдельном потоке"""
        total = len(files)
        
        for idx, filepath in enumerate(files):
            if self.cancel_loading:
                self.root.after(0, lambda: self.status_label.config(
                    text=f"Загрузка отменена. Обработано {idx} из {total} файлов"))
                break
            
            progress = (idx / total) * 100
            self.root.after(0, lambda p=progress, i=idx, t=total: self._update_progress(p, i, t))
            
            info = self.get_image_info(filepath)
            
            if info:
                self.root.after(0, lambda i=info: self.tree.insert('', 'end', values=i))
        
        self.loading = False
        self.root.after(0, lambda: self.cancel_button.config(state=tk.DISABLED))
        self.root.after(0, lambda t=total: self.status_label.config(
            text=f"Загружено {t} файлов"))
        self.root.after(0, lambda: self.progress_bar.config(value=100))
    
    def _update_progress(self, progress, current, total):
        """Обновление прогресс-бара"""
        self.progress_bar['value'] = progress
        self.progress_label.config(text=f"Обработано {current} из {total}")
    
    def get_image_info(self, filepath):
        """Получение информации об изображении"""
        try:
            with Image.open(filepath) as img:
                filename = os.path.basename(filepath)
                
                size = f"{img.width} x {img.height}"
                
                dpi = img.info.get('dpi', None)
                if dpi:
                    if isinstance(dpi, tuple):
                        if dpi[0] > 0 and dpi[1] > 0:
                            dpi_str = f"{dpi[0]:.0f} x {dpi[1]:.0f}"
                        else:
                            dpi_str = "96 x 96 (по умолчанию)"
                    else:
                        if dpi > 0:
                            dpi_str = str(dpi)
                        else:
                            dpi_str = "96 x 96 (по умолчанию)"
                else:
                    dpi_str = "96 x 96 (по умолчанию)"
                
                mode = img.mode
                bit_depth = self._get_bit_depth(mode)
                
                file_size_kb = os.path.getsize(filepath) / 1024
                
                compression = img.info.get('compression', None)
                
                if compression is not None:
                    compression = self._get_bmp_compression(compression)
                elif hasattr(img, 'format'):
                    format_name = img.format
                    if format_name == 'JPEG':
                        compression = 'JPEG'
                    elif format_name == 'PNG':
                        compression = 'PNG (deflate)'
                    elif format_name == 'BMP':
                        compression = 'RGB (без сжатия)'
                    elif format_name == 'GIF':
                        compression = 'LZW'
                    elif format_name == 'TIFF':
                        compression = img.info.get('compression', 'Не указано')
                    else:
                        compression = 'Не указано'
                else:
                    compression = 'Не указано'
                
                compression_with_size = f"{compression}, {file_size_kb:.2f} КБ"
                
                return (filename, size, dpi_str, bit_depth, compression_with_size)
                
        except Exception as e:
            filename = os.path.basename(filepath)
            return (filename, "Ошибка", "Ошибка", "Ошибка", f"Ошибка: {str(e)}")
    
    def _get_bit_depth(self, mode):
        mode_bits = {
            '1': '1 бит (монохромное)',
            'L': '8 бит (градации серого)',
            'P': '8 бит (палитра)',
            'RGB': '24 бита (RGB)',
            'RGBA': '32 бита (RGBA)',
            'CMYK': '32 бита (CMYK)',
            'YCbCr': '24 бита (YCbCr)',
            'LAB': '24 бита (LAB)',
            'HSV': '24 бита (HSV)',
            'I': '32 бита (целые)',
            'F': '32 бита (float)',
            'LA': '16 бит (градации серого + альфа)',
            'PA': '16 бит (палитра + альфа)',
            'RGBX': '32 бита (RGB + padding)',
            'RGBa': '32 бита (RGB + альфа предварительно умноженная)',
            'La': '16 бит (градации серого + альфа предварительно умноженная)',
            'I;16': '16 бит (целые)',
            'I;16B': '16 бит (целые, big endian)',
            'I;16L': '16 бит (целые, little endian)',
            'I;16S': '16 бит (целые со знаком)',
            'I;16BS': '16 бит (целые со знаком, big endian)',
            'I;16LS': '16 бит (целые со знаком, little endian)',
        }
        return mode_bits.get(mode, f'{mode} (неизвестно)')
    
    def _get_bmp_compression(self, comp_code):
        """Определение типа сжатия BMP"""
        if isinstance(comp_code, int):
            compression_types = {
                0: 'RGB (без сжатия)',
                1: 'RLE 8-bit',
                2: 'RLE 4-bit',
                3: 'Bitfields',
                4: 'JPEG',
                5: 'PNG',
            }
            return compression_types.get(comp_code, f'Неизвестное ({comp_code})')
        return str(comp_code)


def main():
    root = tk.Tk()
    app = ImageInfoViewer(root)
    root.mainloop()


if __name__ == "__main__":
    main()

