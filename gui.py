import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
import io

class ImageViewerWithSelection:
    def __init__(self, root):
        self.root = root
        self.root.title("Загрузчик изображений с выделением области")
        self.root.geometry("900x700")
        
        # Переменные для изображения
        self.original_image = None  # Оригинальное изображение
        self.display_image = None    # Отображаемое изображение
        self.photo = None            # PhotoImage для отображения
        self.image_path = None       # Путь к файлу
        
        # Переменные для выделения области
        self.start_x = None
        self.start_y = None
        self.rect = None
        self.selection_rect = None   # Прямоугольник выделения
        self.selection_coords = None # Координаты выделения (x1,y1,x2,y2)
        
        # Коэффициенты масштабирования
        self.scale_x = 1.0
        self.scale_y = 1.0
        
        # Создаем интерфейс
        self.create_widgets()
        
    def create_widgets(self):
        # Верхняя панель с кнопками
        top_frame = tk.Frame(self.root)
        top_frame.pack(fill="x", padx=5, pady=5)
        
        # Кнопка загрузки
        self.btn_load = tk.Button(
            top_frame, 
            text="📁 Загрузить изображение", 
            command=self.load_image,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=10
        )
        self.btn_load.pack(side="left", padx=5)
        
        # Кнопка копирования выделенной области
        self.btn_copy = tk.Button(
            top_frame, 
            text="📋 Копировать выделенное", 
            command=self.copy_selection,
            state="disabled",
            bg="#2196F3",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=10
        )
        self.btn_copy.pack(side="left", padx=5)
        
        # Кнопка очистки выделения
        self.btn_clear = tk.Button(
            top_frame, 
            text="🗑 Очистить выделение", 
            command=self.clear_selection,
            state="disabled",
            bg="#FF9800",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=10
        )
        self.btn_clear.pack(side="left", padx=5)
        
        # Информационная метка
        self.info_label = tk.Label(
            top_frame,
            text="Нажмите на изображение и перетащите для выделения области",
            font=("Arial", 9)
        )
        self.info_label.pack(side="right", padx=5)
        
        # Canvas для отображения изображения
        self.canvas_frame = tk.Frame(self.root)
        self.canvas_frame.pack(expand=True, fill="both", padx=10, pady=5)
        
        self.canvas = tk.Canvas(
            self.canvas_frame, 
            bg="#f0f0f0",
            cursor="cross"  # Курсор в виде крестика для выделения
        )
        
        # Добавляем scrollbar
        self.v_scrollbar = tk.Scrollbar(self.canvas_frame, orient="vertical", command=self.canvas.yview)
        self.h_scrollbar = tk.Scrollbar(self.canvas_frame, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=self.v_scrollbar.set, xscrollcommand=self.h_scrollbar.set)
        
        # Размещаем элементы
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.v_scrollbar.grid(row=0, column=1, sticky="ns")
        self.h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        self.canvas_frame.grid_rowconfigure(0, weight=1)
        self.canvas_frame.grid_columnconfigure(0, weight=1)
        
        # Привязываем события мыши
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
        
        # Метка для изображения на canvas
        self.image_on_canvas = None
        
        # Нижняя панель статуса
        status_frame = tk.Frame(self.root)
        status_frame.pack(fill="x", padx=10, pady=5)
        
        self.status_label = tk.Label(
            status_frame, 
            text="Готов к работе",
            font=("Arial", 9),
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_label.pack(fill="x")
        
    def load_image(self):
        file_path = filedialog.askopenfilename(
            title="Выберите изображение",
            filetypes=[
                ("Изображения", "*.png *.jpg *.jpeg *.bmp *.gif *.tiff *.webp"),
                ("Все файлы", "*.*")
            ]
        )
        
        if file_path:
            try:
                # Загружаем оригинальное изображение
                self.original_image = Image.open(file_path)
                self.image_path = file_path
                
                # Очищаем выделение
                self.clear_selection()
                
                # Отображаем изображение
                self.display_image_on_canvas()
                
                # Активируем кнопки
                self.btn_copy.config(state="normal")
                self.btn_clear.config(state="normal")
                
                # Обновляем информацию
                file_name = os.path.basename(file_path)
                file_size = os.path.getsize(file_path) / 1024  # KB
                img_size = f"{self.original_image.size[0]}×{self.original_image.size[1]}"
                self.status_label.config(
                    text=f"✓ Загружен: {file_name} | Размер: {img_size} px | Объем: {file_size:.1f} KB",
                    fg="green"
                )
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить изображение:\n{str(e)}")
                self.status_label.config(text=f"✗ Ошибка загрузки: {str(e)}", fg="red")
                
    def display_image_on_canvas(self):
        """Отображает изображение на canvas с учетом размеров окна"""
        if self.original_image:
            # Получаем размеры canvas
            canvas_width = self.canvas.winfo_width() if self.canvas.winfo_width() > 1 else 800
            canvas_height = self.canvas.winfo_height() if self.canvas.winfo_height() > 1 else 600
            
            # Вычисляем масштаб для отображения
            img_width, img_height = self.original_image.size
            
            # Масштабируем изображение, чтобы оно помещалось в canvas
            scale_w = canvas_width / img_width
            scale_h = canvas_height / img_height
            self.scale = min(scale_w, scale_h, 1.0)  # Не увеличиваем изображение больше оригинала
            
            new_width = int(img_width * self.scale)
            new_height = int(img_height * self.scale)
            
            # Изменяем размер для отображения
            resized = self.original_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            self.display_image = resized
            
            # Конвертируем в PhotoImage
            self.photo = ImageTk.PhotoImage(resized)
            
            # Очищаем canvas
            self.canvas.delete("all")
            
            # Отображаем изображение
            self.image_on_canvas = self.canvas.create_image(0, 0, anchor="nw", image=self.photo)
            self.canvas.config(scrollregion=self.canvas.bbox("all"))
            
    def on_mouse_down(self, event):
        """Начало выделения области"""
        if self.original_image:
            # Удаляем предыдущее выделение
            if self.selection_rect:
                self.canvas.delete(self.selection_rect)
                self.selection_rect = None
            
            self.start_x = self.canvas.canvasx(event.x)
            self.start_y = self.canvas.canvasy(event.y)
            
            # Создаем временный прямоугольник
            self.rect = self.canvas.create_rectangle(
                self.start_x, self.start_y, self.start_x, self.start_y,
                outline="red", width=2, fill="blue", stipple="gray50"
            )
            
    def on_mouse_drag(self, event):
        """Перетаскивание для выделения области"""
        if self.rect:
            cur_x = self.canvas.canvasx(event.x)
            cur_y = self.canvas.canvasy(event.y)
            
            # Обновляем координаты прямоугольника
            self.canvas.coords(self.rect, self.start_x, self.start_y, cur_x, cur_y)
            
    def on_mouse_up(self, event):
        """Завершение выделения области"""
        if self.rect and self.original_image:
            end_x = self.canvas.canvasx(event.x)
            end_y = self.canvas.canvasy(event.y)
            
            # Получаем координаты выделения (нормализуем)
            x1, y1, x2, y2 = self.start_x, self.start_y, end_x, end_y
            
            # Приводим к правильному порядку (лево-право, верх-низ)
            x1, x2 = min(x1, x2), max(x1, x2)
            y1, y2 = min(y1, y2), max(y1, y2)
            
            # Сохраняем координаты выделения на canvas
            self.selection_coords = (x1, y1, x2, y2)
            
            # Преобразуем координаты canvas в координаты оригинального изображения
            orig_coords = self.canvas_to_image_coords(x1, y1, x2, y2)
            
            if orig_coords and orig_coords[2] > orig_coords[0] and orig_coords[3] > orig_coords[1]:
                # Сохраняем выделенную область
                self.selected_area = self.original_image.crop(orig_coords)
                
                # Делаем прямоугольник постоянным
                self.selection_rect = self.rect
                self.rect = None
                
                # Обновляем информацию
                width = orig_coords[2] - orig_coords[0]
                height = orig_coords[3] - orig_coords[1]
                self.status_label.config(
                    text=f"✓ Выделена область: {width}×{height} px",
                    fg="blue"
                )
                self.info_label.config(text="Область выделена! Нажмите 'Копировать выделенное'")
            else:
                # Слишком маленькая область
                self.canvas.delete(self.rect)
                self.rect = None
                self.status_label.config(text="✗ Область слишком маленькая", fg="red")
                
    def canvas_to_image_coords(self, x1, y1, x2, y2):
        """Преобразует координаты canvas в координаты оригинального изображения"""
        if self.original_image and self.display_image:
            # Получаем размеры отображаемого изображения
            display_width, display_height = self.display_image.size
            orig_width, orig_height = self.original_image.size
            
            # Вычисляем коэффициенты масштабирования
            scale_x = orig_width / display_width
            scale_y = orig_height / display_height
            
            # Преобразуем координаты
            orig_x1 = int(x1 * scale_x)
            orig_y1 = int(y1 * scale_y)
            orig_x2 = int(x2 * scale_x)
            orig_y2 = int(y2 * scale_y)
            
            # Ограничиваем границами изображения
            orig_x1 = max(0, min(orig_x1, orig_width))
            orig_y1 = max(0, min(orig_y1, orig_height))
            orig_x2 = max(0, min(orig_x2, orig_width))
            orig_y2 = max(0, min(orig_y2, orig_height))
            
            return (orig_x1, orig_y1, orig_x2, orig_y2)
        return None
        
    def copy_selection(self):
        """Копирует выделенную область в буфер обмена"""
        if hasattr(self, 'selected_area') and self.selected_area:
            try:

                import datetime
                import base64
                from core.parse_plan import parse_plan

                # распознать изображение
                start = datetime.datetime.now()
                print('Время старта: ' + str(start))
                 # Создаем временный буфер в памяти
                output = io.BytesIO()
                # Сохраняем выделенную область в PNG формате
                self.selected_area.save(output, format='jpeg')
                #self.selected_area.save("temp_selection.jpg", format='jpeg')
                output.seek(0)
                data = output.getvalue()  # Получаем байтовые данные
                base64_data = base64.b64encode(data).decode('utf-8')
                mime_type = 'image/jpeg'
                #base64_image = img64.image_to_base64(self.selected_area)
                f_base64_data = f"data:{mime_type};base64,{base64_data}"

                self.status_label.config(
                    text=f"✓ Выделенная область отправлена на распознование. Ожидание!",
                    fg="green"
                )

                result = parse_plan(f_base64_data)
        
                self.status_label.config(text=getattr(result, "content", None), fg="black")
                print(getattr(result, "content", None))

                finish = datetime.datetime.now()
                print('Время работы: ' + str(finish - start))

                
                #self.info_label.config(text="Область скопирована! Можно вставить в любой редактор")
            
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не в области распознования:\n{str(e)}")
                self.status_label.config(text=f"✗ Ошибка копирования: {str(e)}", fg="red")
        else:
            messagebox.showwarning("Нет выделения", "Сначала выделите область на изображении!")
            
    def clear_selection(self):
        """Очищает выделение"""
        if hasattr(self, 'selected_area'):
            del self.selected_area
            
        if self.selection_rect:
            self.canvas.delete(self.selection_rect)
            self.selection_rect = None
            
        if self.rect:
            self.canvas.delete(self.rect)
            self.rect = None
            
        self.selection_coords = None
        self.start_x = None
        self.start_y = None
        
        self.status_label.config(text="Выделение очищено", fg="black")
        self.info_label.config(text="Нажмите на изображение и перетащите для выделения области")
        
    def on_canvas_resize(self, event):
        """Обработка изменения размера canvas"""
        if self.original_image:
            self.display_image_on_canvas()
            if hasattr(self, 'selected_area'):
                self.clear_selection()

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageViewerWithSelection(root)
    
    # Привязываем событие изменения размера окна
    root.bind("<Configure>", lambda e: app.on_canvas_resize(e))
    
    root.mainloop()