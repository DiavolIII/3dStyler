import tkinter as tk
from tkinter import ttk
import math
import numpy as np

class VRRayTracing3D:
    def __init__(self, root):
        self.root = root
        self.root.title("VR Трассировка лучей - 3D Отражения")
        self.root.geometry("1200x800")
        
        # Настройка стиля
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('VR.TNotebook', background='#1a1a2e', borderwidth=0)
        self.style.configure('VR.TFrame', background='#16213e')
        
        # Создание вкладок
        self.notebook = ttk.Notebook(root, style='VR.TNotebook')
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Вкладка 1: 3D VR сцена
        self.vr_frame = ttk.Frame(self.notebook, style='VR.TFrame')
        self.notebook.add(self.vr_frame, text="🌍 VR Сцена")
        
        # Вкладка 2: 2D схема
        self.schema_frame = ttk.Frame(self.notebook, style='VR.TFrame')
        self.notebook.add(self.schema_frame, text="📐 2D Схема")
        
        # Вкладка 3: Параметры
        self.params_frame = ttk.Frame(self.notebook, style='VR.TFrame')
        self.notebook.add(self.params_frame, text="⚙️ Параметры")
        
        # Инициализация сцен
        self.setup_vr_scene()
        self.setup_schema_scene()
        self.setup_params_scene()
        
        # Общие данные для сцен
        self.init_shared_data()
        
        # Привязка событий
        self.setup_bindings()

    def init_shared_data(self):
        """Общие данные для всех сцен"""
        # Параметры сцены
        self.width = 1000
        self.height = 700
        
        # 3D параметры камеры
        self.camera_pos = [5, 3, 10]  # x, y, z
        self.camera_target = [0, 0, 0]
        self.camera_angle = 0
        self.camera_elevation = 30
        
        # Объекты сцены (3D сферы)
        self.mirrors_3d = [
            {'pos': [-2, 0, 0], 'radius': 1.2, 'color': '#4169E1', 'reflectivity': 0.9},
            {'pos': [2, 1, -1], 'radius': 1.0, 'color': '#32CD32', 'reflectivity': 0.8},
            {'pos': [0, -1, 2], 'radius': 0.9, 'color': '#9370DB', 'reflectivity': 0.85},
            {'pos': [-1, 1.5, -2], 'radius': 0.8, 'color': '#FF6346', 'reflectivity': 0.7},
            {'pos': [1.5, -0.5, 1], 'radius': 0.7, 'color': '#FFD700', 'reflectivity': 0.95}
        ]
        
        # Источник и приемник в 3D
        self.source_3d = [-3, 1, 2]
        self.target_3d = [3, -1, -2]
        
        # 2D данные (для схемы)
        self.mirrors_2d = [
            {'center': (300, 300), 'radius': 80, 'color': 'blue'},
            {'center': (600, 400), 'radius': 60, 'color': 'green'},
            {'center': (450, 200), 'radius': 50, 'color': 'purple'},
            {'center': (750, 500), 'radius': 70, 'color': 'orange'}
        ]
        self.source_2d = (100, 600)
        self.target_2d = (900, 100)
        
        # Параметры лучей
        self.num_rays = 36
        self.show_normals = True
        self.show_grid = True
        self.ray_intensity = 0.8
        self.reflection_depth = 3
        
        # Анимация
        self.animation_running = False
        self.animation_angle = 0

    def setup_vr_scene(self):
        """Настройка 3D VR сцены"""
        # Основной холст для 3D
        self.vr_canvas = tk.Canvas(self.vr_frame, width=self.width, height=self.height, 
                                   bg='#0a0a1a', highlightthickness=0)
        self.vr_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Панель управления VR
        vr_control = tk.Frame(self.vr_frame, bg='#16213e', width=200)
        vr_control.pack(side=tk.RIGHT, fill=tk.Y)
        vr_control.pack_propagate(False)
        
        # Заголовок
        tk.Label(vr_control, text="🎮 VR УПРАВЛЕНИЕ", fg='white', bg='#16213e',
                font=('Arial', 12, 'bold')).pack(pady=10)
        
        # Кнопки управления камерой
        cam_frame = tk.LabelFrame(vr_control, text="Камера", fg='white', bg='#16213e',
                                 font=('Arial', 10, 'bold'))
        cam_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Button(cam_frame, text="⬆️ Вверх", command=lambda: self.move_camera(0, 0.5, 0),
                 bg='#0f3460', fg='white').pack(fill=tk.X, pady=2)
        tk.Button(cam_frame, text="⬇️ Вниз", command=lambda: self.move_camera(0, -0.5, 0),
                 bg='#0f3460', fg='white').pack(fill=tk.X, pady=2)
        tk.Button(cam_frame, text="⬅️ Влево", command=lambda: self.move_camera(-0.5, 0, 0),
                 bg='#0f3460', fg='white').pack(fill=tk.X, pady=2)
        tk.Button(cam_frame, text="➡️ Вправо", command=lambda: self.move_camera(0.5, 0, 0),
                 bg='#0f3460', fg='white').pack(fill=tk.X, pady=2)
        tk.Button(cam_frame, text="🔄 Приблизить", command=lambda: self.move_camera(0, 0, -0.5),
                 bg='#0f3460', fg='white').pack(fill=tk.X, pady=2)
        tk.Button(cam_frame, text="🔄 Отдалить", command=lambda: self.move_camera(0, 0, 0.5),
                 bg='#0f3460', fg='white').pack(fill=tk.X, pady=2)
        
        # Параметры лучей
        ray_frame = tk.LabelFrame(vr_control, text="Лучи", fg='white', bg='#16213e',
                                 font=('Arial', 10, 'bold'))
        ray_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Scale(ray_frame, from_=4, to=72, orient=tk.HORIZONTAL,
                label="Количество лучей", fg='white', bg='#16213e',
                command=self.update_ray_count).pack(fill=tk.X)
        
        # Кнопки анимации
        anim_frame = tk.LabelFrame(vr_control, text="Анимация", fg='white', bg='#16213e',
                                  font=('Arial', 10, 'bold'))
        anim_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Button(anim_frame, text="▶️ Старт", command=self.start_animation,
                 bg='#28a745', fg='white').pack(side=tk.LEFT, expand=True, padx=2)
        tk.Button(anim_frame, text="⏸️ Стоп", command=self.stop_animation,
                 bg='#dc3545', fg='white').pack(side=tk.LEFT, expand=True, padx=2)
        
        # Информация
        self.info_label = tk.Label(vr_control, text="", fg='#00ff00', bg='#16213e',
                                   font=('Courier', 8), justify=tk.LEFT)
        self.info_label.pack(pady=10)

    def setup_schema_scene(self):
        """Настройка 2D схемы"""
        # Холст для 2D
        self.schema_canvas = tk.Canvas(self.schema_frame, width=self.width, height=self.height,
                                       bg='black', highlightthickness=0)
        self.schema_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Панель управления 2D
        schema_control = tk.Frame(self.schema_frame, bg='#16213e', width=200)
        schema_control.pack(side=tk.RIGHT, fill=tk.Y)
        schema_control.pack_propagate(False)
        
        tk.Label(schema_control, text="📐 2D УПРАВЛЕНИЕ", fg='white', bg='#16213e',
                font=('Arial', 12, 'bold')).pack(pady=10)
        
        tk.Button(schema_control, text="Сбросить 2D", command=self.reset_2d_scene,
                 bg='#0f3460', fg='white').pack(fill=tk.X, padx=5, pady=5)
        
        # Переменные для перетаскивания в 2D
        self.drag_object_2d = None
        self.drag_offset_2d = (0, 0)

    def setup_params_scene(self):
        """Настройка вкладки параметров"""
        # Создаем прокручиваемую область
        canvas = tk.Canvas(self.params_frame, bg='#16213e', highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.params_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style='VR.TFrame')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Параметры сцены
        params = [
            ("🌍 ПАРАМЕТРЫ СЦЕНЫ", "title"),
            ("Интенсивность лучей", 0.1, 1.0, self.ray_intensity, "ray"),
            ("Глубина отражений", 1, 5, self.reflection_depth, "depth"),
            ("Показать нормали", None, None, self.show_normals, "normals"),
            ("Показать сетку", None, None, self.show_grid, "grid"),
            ("", None, None, None, "separator"),
            ("🎨 ЦВЕТА ОБЪЕКТОВ", "title"),
            ("Источник", "red"),
            ("Приемник", "yellow"),
            ("Зеркало 1", "#4169E1"),
            ("Зеркало 2", "#32CD32"),
            ("Зеркало 3", "#9370DB"),
            ("Зеркало 4", "#FF6346"),
            ("Зеркало 5", "#FFD700"),
        ]
        
        self.param_vars = {}
        
        for param in params:
            if param[1] == "title":
                tk.Label(scrollable_frame, text=param[0], fg='#00ff00', bg='#16213e',
                        font=('Arial', 12, 'bold')).pack(anchor=tk.W, padx=10, pady=(10,5))
            elif param[0] == "":
                tk.Frame(scrollable_frame, height=2, bg='#444').pack(fill=tk.X, padx=10, pady=10)
            elif len(param) == 4:  # Чекбокс
                var = tk.BooleanVar(value=param[3])
                self.param_vars[param[0]] = var
                cb = tk.Checkbutton(scrollable_frame, text=param[0], variable=var,
                                   fg='white', bg='#16213e', selectcolor='#16213e',
                                   command=lambda p=param[0]: self.update_param(p))
                cb.pack(anchor=tk.W, padx=20, pady=2)
            elif len(param) == 5:  # Слайдер
                frame = tk.Frame(scrollable_frame, bg='#16213e')
                frame.pack(fill=tk.X, padx=10, pady=5)
                tk.Label(frame, text=param[0], fg='white', bg='#16213e').pack(anchor=tk.W)
                var = tk.DoubleVar(value=param[3])
                self.param_vars[param[0]] = var
                scale = tk.Scale(frame, from_=param[1], to=param[2], orient=tk.HORIZONTAL,
                               variable=var, bg='#16213e', fg='white',
                               command=lambda v, p=param[0]: self.update_param(p))
                scale.pack(fill=tk.X)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def setup_bindings(self):
        """Привязка событий"""
        # 3D управление клавишами
        self.root.bind('<KeyPress-Left>', lambda e: self.move_camera(-0.5, 0, 0))
        self.root.bind('<KeyPress-Right>', lambda e: self.move_camera(0.5, 0, 0))
        self.root.bind('<KeyPress-Up>', lambda e: self.move_camera(0, 0.5, 0))
        self.root.bind('<KeyPress-Down>', lambda e: self.move_camera(0, -0.5, 0))
        self.root.bind('<KeyPress-plus>', lambda e: self.move_camera(0, 0, -0.5))
        self.root.bind('<KeyPress-minus>', lambda e: self.move_camera(0, 0, 0.5))
        
        # 2D события мыши
        self.schema_canvas.bind("<Button-1>", self.on_click_2d)
        self.schema_canvas.bind("<B1-Motion>", self.on_drag_2d)
        self.schema_canvas.bind("<ButtonRelease-1>", self.on_release_2d)

    def move_camera(self, dx, dy, dz):
        """Перемещение камеры в 3D"""
        self.camera_pos[0] += dx
        self.camera_pos[1] += dy
        self.camera_pos[2] += dz
        self.draw_vr_scene()

    def update_ray_count(self, value):
        """Обновление количества лучей"""
        self.num_rays = int(float(value))
        self.draw_vr_scene()

    def update_param(self, param):
        """Обновление параметра"""
        if param == "Интенсивность лучей":
            self.ray_intensity = self.param_vars[param].get()
        elif param == "Глубина отражений":
            self.reflection_depth = int(self.param_vars[param].get())
        elif param == "Показать нормали":
            self.show_normals = self.param_vars[param].get()
        elif param == "Показать сетку":
            self.show_grid = self.param_vars[param].get()
        
        self.draw_vr_scene()

    def start_animation(self):
        """Запуск анимации"""
        self.animation_running = True
        self.animate()

    def stop_animation(self):
        """Остановка анимации"""
        self.animation_running = False

    def animate(self):
        """Анимация вращения"""
        if self.animation_running:
            self.animation_angle += 2
            # Вращаем источник и приемник
            self.source_3d = [
                3 * math.cos(math.radians(self.animation_angle)),
                1,
                3 * math.sin(math.radians(self.animation_angle))
            ]
            self.target_3d = [
                3 * math.cos(math.radians(self.animation_angle + 180)),
                -1,
                3 * math.sin(math.radians(self.animation_angle + 180))
            ]
            self.draw_vr_scene()
            self.root.after(50, self.animate)

    def project_3d_to_2d(self, point):
        """
        Проекция 3D точки на 2D экран с эффектом VR
        """
        # Перенос точки в систему координат камеры
        dx = point[0] - self.camera_pos[0]
        dy = point[1] - self.camera_pos[1]
        dz = point[2] - self.camera_pos[2]
        
        # Вращение камеры
        angle_rad = math.radians(self.camera_angle)
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)
        
        x_rot = dx * cos_a - dz * sin_a
        z_rot = dx * sin_a + dz * cos_a
        y_rot = dy
        
        # Перспективная проекция
        if z_rot > 0.1:  # Избегаем деления на ноль
            fov = 500
            scale = fov / z_rot
            x_proj = self.width//2 + x_rot * scale
            y_proj = self.height//2 - y_rot * scale
            
            # Добавляем эффект VR искажения
            dist_factor = 1 + (z_rot / 10)
            return (x_proj, y_proj, dist_factor)
        
        return None

    def draw_vr_scene(self):
        """Отрисовка 3D VR сцены"""
        self.vr_canvas.delete("all")
        
        # Рисуем звездное небо (эффект VR)
        self.draw_starry_sky()
        
        # Рисуем сетку пола
        if self.show_grid:
            self.draw_vr_grid()
        
        # Рисуем зеркала (сферы)
        for mirror in self.mirrors_3d:
            self.draw_sphere(mirror['pos'], mirror['radius'], mirror['color'], 
                           mirror['reflectivity'])
        
        # Рисуем источник (светящаяся сфера)
        self.draw_sphere(self.source_3d, 0.3, '#ff4444', 1.0, emissive=True)
        
        # Рисуем приемник
        self.draw_sphere(self.target_3d, 0.3, '#ffff44', 1.0, emissive=True)
        
        # Рисуем лучи
        self.draw_3d_rays()
        
        # Обновляем информацию
        self.update_vr_info()

    def draw_starry_sky(self):
        """Рисуем звездное небо для VR эффекта"""
        import random
        random.seed(42)  # Для постоянства звезд
        
        for _ in range(100):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            brightness = random.randint(100, 255)
            size = random.randint(1, 2)
            color = f'#{brightness:02x}{brightness:02x}{brightness:02x}'
            self.vr_canvas.create_oval(x-size, y-size, x+size, y+size, fill=color, outline='')

    def draw_vr_grid(self):
        """Рисуем 3D сетку пола"""
        grid_size = 10
        grid_spacing = 1.0
        
        for i in range(-grid_size, grid_size + 1):
            for j in range(-grid_size, grid_size + 1):
                # Линии вдоль X
                p1 = self.project_3d_to_2d([i * grid_spacing, -1, j * grid_spacing])
                p2 = self.project_3d_to_2d([i * grid_spacing, -1, (j + 1) * grid_spacing])
                
                if p1 and p2:
                    alpha = max(0, min(255, int(100 * p1[2])))
                    color = f'#00{alpha:02x}00'
                    self.vr_canvas.create_line(p1[0], p1[1], p2[0], p2[1], 
                                              fill=color, width=1)
                
                # Линии вдоль Z
                p1 = self.project_3d_to_2d([i * grid_spacing, -1, j * grid_spacing])
                p2 = self.project_3d_to_2d([(i + 1) * grid_spacing, -1, j * grid_spacing])
                
                if p1 and p2:
                    alpha = max(0, min(255, int(100 * p1[2])))
                    color = f'#00{alpha:02x}00'
                    self.vr_canvas.create_line(p1[0], p1[1], p2[0], p2[1], 
                                              fill=color, width=1)

    def draw_sphere(self, pos, radius, color, reflectivity, emissive=False):
        """Рисуем 3D сферу с эффектом освещения"""
        proj = self.project_3d_to_2d(pos)
        if not proj:
            return
        
        x, y, dist = proj
        
        # Размер сферы зависит от расстояния
        screen_radius = radius * 200 / dist
        
        # Рисуем окружность
        if emissive:
            # Светящийся объект (источник/приемник)
            for i in range(3, 0, -1):
                alpha = int(100 / i)
                self.vr_canvas.create_oval(x - screen_radius*i, y - screen_radius*i,
                                         x + screen_radius*i, y + screen_radius*i,
                                         outline='', fill=color, width=0,
                                         stipple='gray50' if i > 1 else '')
        else:
            # Зеркало с градиентом
            self.vr_canvas.create_oval(x - screen_radius, y - screen_radius,
                                     x + screen_radius, y + screen_radius,
                                     outline='white', fill=color, width=2)
            
            # Блик
            highlight_x = x - screen_radius * 0.3
            highlight_y = y - screen_radius * 0.3
            highlight_r = screen_radius * 0.2
            self.vr_canvas.create_oval(highlight_x - highlight_r, highlight_y - highlight_r,
                                     highlight_x + highlight_r, highlight_y + highlight_r,
                                     fill='white', outline='', stipple='gray50')
            
            # Отражение (эффект зеркала)
            if reflectivity > 0.7:
                self.vr_canvas.create_oval(x - screen_radius*0.8, y - screen_radius*0.8,
                                         x + screen_radius*0.8, y + screen_radius*0.8,
                                         outline='cyan', width=1, dash=(2, 2))

    def draw_3d_rays(self):
        """Рисуем лучи в 3D пространстве"""
        # Используем метод Монте-Карло для распределения лучей
        for i in range(self.num_rays):
            # Случайное направление в конусе
            theta = random.uniform(0, 2 * math.pi)
            phi = random.uniform(-math.pi/4, math.pi/4)  # Конус 90 градусов
            
            dx = math.cos(phi) * math.cos(theta)
            dy = math.sin(phi)
            dz = math.cos(phi) * math.sin(theta)
            
            # Нормализуем
            length = math.sqrt(dx*dx + dy*dy + dz*dz)
            direction = (dx/length, dy/length, dz/length)
            
            # Трассируем луч
            self.trace_ray_3d(self.source_3d, direction, 0)

    def trace_ray_3d(self, start, direction, depth):
        """Рекурсивная трассировка луча в 3D"""
        if depth > self.reflection_depth:
            return
        
        # Поиск ближайшего пересечения
        closest_hit = None
        closest_dist = float('inf')
        hit_mirror = None
        
        for mirror in self.mirrors_3d:
            hit = self.ray_sphere_intersection(start, direction, 
                                               mirror['pos'], mirror['radius'])
            if hit and hit[0] > 0.01 and hit[0] < closest_dist:
                closest_dist = hit[0]
                closest_hit = hit[1]
                hit_mirror = mirror
        
        if closest_hit:
            # Рисуем луч до точки пересечения
            end_proj = self.project_3d_to_2d(closest_hit)
            start_proj = self.project_3d_to_2d(start)
            
            if start_proj and end_proj:
                # Цвет зависит от глубины
                intensity = self.ray_intensity * (1 - depth * 0.3)
                color_val = int(255 * intensity)
                colors = [(255, color_val, 0), (0, 255, color_val), 
                         (color_val, 0, 255), (255, 0, color_val)]
                color = f'#{colors[depth % 4][0]:02x}{colors[depth % 4][1]:02x}{colors[depth % 4][2]:02x}'
                
                self.vr_canvas.create_line(start_proj[0], start_proj[1],
                                         end_proj[0], end_proj[1],
                                         fill=color, width=3-depth, dash=(5, 3) if depth > 0 else ())
            
            # Нормаль в точке пересечения
            if self.show_normals:
                normal = (closest_hit[0] - hit_mirror['pos'][0],
                         closest_hit[1] - hit_mirror['pos'][1],
                         closest_hit[2] - hit_mirror['pos'][2])
                normal_len = math.sqrt(normal[0]**2 + normal[1]**2 + normal[2]**2)
                if normal_len > 0:
                    normal_end = (closest_hit[0] + normal[0]/normal_len,
                                 closest_hit[1] + normal[1]/normal_len,
                                 closest_hit[2] + normal[2]/normal_len)
                    
                    norm_proj1 = self.project_3d_to_2d(closest_hit)
                    norm_proj2 = self.project_3d_to_2d(normal_end)
                    
                    if norm_proj1 and norm_proj2:
                        self.vr_canvas.create_line(norm_proj1[0], norm_proj1[1],
                                                 norm_proj2[0], norm_proj2[1],
                                                 fill='white', width=1, dash=(2, 2))
            
            # Вычисляем отраженный луч
            normal = (closest_hit[0] - hit_mirror['pos'][0],
                     closest_hit[1] - hit_mirror['pos'][1],
                     closest_hit[2] - hit_mirror['pos'][2])
            normal_len = math.sqrt(normal[0]**2 + normal[1]**2 + normal[2]**2)
            if normal_len > 0:
                normal = (normal[0]/normal_len, normal[1]/normal_len, normal[2]/normal_len)
                
                # R = V - 2(V·N)N
                dot = direction[0]*normal[0] + direction[1]*normal[1] + direction[2]*normal[2]
                reflected = (direction[0] - 2*dot*normal[0],
                           direction[1] - 2*dot*normal[1],
                           direction[2] - 2*dot*normal[2])
                
                # Продолжаем трассировку
                self.trace_ray_3d(closest_hit, reflected, depth + 1)

    def ray_sphere_intersection(self, start, direction, sphere_pos, sphere_radius):
        """Проверка пересечения луча со сферой"""
        oc = (start[0] - sphere_pos[0], start[1] - sphere_pos[1], start[2] - sphere_pos[2])
        
        a = direction[0]**2 + direction[1]**2 + direction[2]**2
        b = 2*(oc[0]*direction[0] + oc[1]*direction[1] + oc[2]*direction[2])
        c = oc[0]**2 + oc[1]**2 + oc[2]**2 - sphere_radius**2
        
        discriminant = b*b - 4*a*c
        
        if discriminant < 0:
            return None
        
        t1 = (-b - math.sqrt(discriminant)) / (2*a)
        t2 = (-b + math.sqrt(discriminant)) / (2*a)
        
        if t1 > 0:
            return (t1, (start[0] + t1*direction[0],
                        start[1] + t1*direction[1],
                        start[2] + t1*direction[2]))
        elif t2 > 0:
            return (t2, (start[0] + t2*direction[0],
                        start[1] + t2*direction[1],
                        start[2] + t2*direction[2]))
        
        return None

    def update_vr_info(self):
        """Обновление информационной панели"""
        info = f"""
        Камера: ({self.camera_pos[0]:.1f}, {self.camera_pos[1]:.1f}, {self.camera_pos[2]:.1f})
        Источник: ({self.source_3d[0]:.1f}, {self.source_3d[1]:.1f}, {self.source_3d[2]:.1f})
        Приемник: ({self.target_3d[0]:.1f}, {self.target_3d[1]:.1f}, {self.target_3d[2]:.1f})
        Лучей: {self.num_rays}
        Отражений: {self.reflection_depth}
        """
        self.info_label.config(text=info)

    def draw_schema_scene(self):
        """Отрисовка 2D схемы"""
        self.schema_canvas.delete("all")
        
        # Рисуем сетку
        for i in range(0, self.width, 50):
            self.schema_canvas.create_line(i, 0, i, self.height, fill='#333')
        for i in range(0, self.height, 50):
            self.schema_canvas.create_line(0, i, self.width, i, fill='#333')
        
        # Рисуем зеркала
        for mirror in self.mirrors_2d:
            x, y = mirror['center']
            r = mirror['radius']
            color = mirror['color']
            self.schema_canvas.create_oval(x-r, y-r, x+r, y+r,
                                         outline=color, width=2, fill='')
            self.schema_canvas.create_oval(x-3, y-3, x+3, y+3, fill=color)
        
        # Рисуем источник и приемник
        self.schema_canvas.create_oval(self.source_2d[0]-8, self.source_2d[1]-8,
                                     self.source_2d[0]+8, self.source_2d[1]+8,
                                     fill='red', outline='white', width=2)
        self.schema_canvas.create_text(self.source_2d[0], self.source_2d[1]-15,
                                     text="ИСТОЧНИК", fill='white')
        
        self.schema_canvas.create_oval(self.target_2d[0]-8, self.target_2d[1]-8,
                                     self.target_2d[0]+8, self.target_2d[1]+8,
                                     fill='yellow', outline='white', width=2)
        self.schema_canvas.create_text(self.target_2d[0], self.target_2d[1]-15,
                                     text="ПРИЕМНИК", fill='white')
        
        # Рисуем лучи в 2D
        self.draw_2d_rays()

    def draw_2d_rays(self):
        """Отрисовка лучей в 2D"""
        # Прямой луч
        direct_blocked = False
        for mirror in self.mirrors_2d:
            if self.check_line_circle_intersection(
                self.source_2d, self.target_2d, mirror['center'], mirror['radius']):
                direct_blocked = True
                break
        
        if not direct_blocked:
            self.schema_canvas.create_line(self.source_2d[0], self.source_2d[1],
                                         self.target_2d[0], self.target_2d[1],
                                         fill='green', width=2, dash=(5, 3))
        
        # Отраженные лучи
        for mirror in self.mirrors_2d:
            self.find_reflection_path_2d(mirror)

    def check_line_circle_intersection(self, p1, p2, center, radius):
        """Проверка пересечения линии с кругом в 2D"""
        # Вектор направления
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        
        # Вектор от начальной точки до центра
        fx = p1[0] - center[0]
        fy = p1[1] - center[1]
        
        a = dx*dx + dy*dy
        b = 2*(fx*dx + fy*dy)
        c = fx*fx + fy*fy - radius*radius
        
        discriminant = b*b - 4*a*c
        
        if discriminant > 0:
            discriminant = math.sqrt(discriminant)
            t1 = (-b - discriminant) / (2*a)
            t2 = (-b + discriminant) / (2*a)
            
            if (0 <= t1 <= 1) or (0 <= t2 <= 1):
                return True
        
        return False

    def find_reflection_path_2d(self, mirror):
        """Поиск пути с отражением в 2D"""
        cx, cy = mirror['center']
        r = mirror['radius']
        
        # Перебор углов для поиска точки отражения
        for angle in range(0, 360, 10):
            rad = math.radians(angle)
            px = cx + r * math.cos(rad)
            py = cy + r * math.sin(rad)
            
            # Проверяем, видна ли точка из источника
            visible_from_source = True
            for other in self.mirrors_2d:
                if other != mirror and self.check_line_circle_intersection(
                    self.source_2d, (px, py), other['center'], other['radius']):
                    visible_from_source = False
                    break
            
            if not visible_from_source:
                continue
            
            # Проверяем, видна ли цель из точки
            visible_to_target = True
            for other in self.mirrors_2d:
                if other != mirror and self.check_line_circle_intersection(
                    (px, py), self.target_2d, other['center'], other['radius']):
                    visible_to_target = False
                    break
            
            if visible_to_target:
                # Рисуем путь
                self.schema_canvas.create_line(self.source_2d[0], self.source_2d[1],
                                             px, py, fill='cyan', width=2)
                self.schema_canvas.create_line(px, py, self.target_2d[0], self.target_2d[1],
                                             fill='cyan', width=2)
                self.schema_canvas.create_oval(px-4, py-4, px+4, py+4,
                                             fill='white', outline='cyan')
                break

    def on_click_2d(self, event):
        """Обработка нажатия в 2D"""
        x, y = event.x, event.y
        
        # Проверяем источник
        if self.distance_2d((x, y), self.source_2d) < 15:
            self.drag_object_2d = 'source'
            self.drag_offset_2d = (self.source_2d[0] - x, self.source_2d[1] - y)
            return
        
        # Проверяем приемник
        if self.distance_2d((x, y), self.target_2d) < 15:
            self.drag_object_2d = 'target'
            self.drag_offset_2d = (self.target_2d[0] - x, self.target_2d[1] - y)
            return
        
        # Проверяем зеркала
        for i, mirror in enumerate(self.mirrors_2d):
            if self.distance_2d((x, y), mirror['center']) < mirror['radius']:
                self.drag_object_2d = f'mirror_{i}'
                self.drag_offset_2d = (mirror['center'][0] - x, mirror['center'][1] - y)
                return

    def on_drag_2d(self, event):
        """Обработка перетаскивания в 2D"""
        if not self.drag_object_2d:
            return
        
        new_x = event.x + self.drag_offset_2d[0]
        new_y = event.y + self.drag_offset_2d[1]
        
        new_x = max(10, min(self.width-10, new_x))
        new_y = max(10, min(self.height-10, new_y))
        
        if self.drag_object_2d == 'source':
            self.source_2d = (new_x, new_y)
        elif self.drag_object_2d == 'target':
            self.target_2d = (new_x, new_y)
        elif self.drag_object_2d.startswith('mirror_'):
            idx = int(self.drag_object_2d.split('_')[1])
            self.mirrors_2d[idx]['center'] = (new_x, new_y)
        
        self.draw_schema_scene()

    def on_release_2d(self, event):
        """Отпускание мыши в 2D"""
        self.drag_object_2d = None

    def distance_2d(self, p1, p2):
        """Расстояние между 2D точками"""
        return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

    def reset_2d_scene(self):
        """Сброс 2D сцены"""
        self.mirrors_2d = [
            {'center': (300, 300), 'radius': 80, 'color': 'blue'},
            {'center': (600, 400), 'radius': 60, 'color': 'green'},
            {'center': (450, 200), 'radius': 50, 'color': 'purple'},
            {'center': (750, 500), 'radius': 70, 'color': 'orange'}
        ]
        self.source_2d = (100, 600)
        self.target_2d = (900, 100)
        self.draw_schema_scene()

def main():
    root = tk.Tk()
    app = VRRayTracing3D(root)
    
    # Начальная отрисовка
    app.draw_vr_scene()
    app.draw_schema_scene()
    
    root.mainloop()

if __name__ == "__main__":
    main()