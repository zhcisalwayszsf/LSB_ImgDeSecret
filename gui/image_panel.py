"""
图像显示面板组件
"""

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

class ImageDisplayPanel(tk.Frame):
    """图像显示面板"""
    
    def __init__(self, parent, title="图像"):
        super().__init__(parent)
        
        self.title = title
        self.original_image = None
        self.display_image = None
        self.photo_image = None
        self.scale = 1.0
        self.canvas_width = 0
        self.canvas_height = 0
        
        self._setup_ui()
        
    def _setup_ui(self):
        """设置UI"""
        # 标题
        title_frame = tk.Frame(self, bg='#2b2b2b')
        title_frame.pack(fill=tk.X)
        
        tk.Label(title_frame, text=self.title, 
                fg='white', bg='#2b2b2b', 
                font=('Arial', 10, 'bold')).pack(pady=5)
        
        # 图像显示区域
        self.canvas_frame = tk.Frame(self, bg='#1e1e1e')
        self.canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.canvas = tk.Canvas(self.canvas_frame, bg='#1e1e1e', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # 滚动条
        v_scrollbar = ttk.Scrollbar(self.canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        h_scrollbar = ttk.Scrollbar(self.canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        
        self.canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # 缩放控制
        control_frame = tk.Frame(self, bg='#2b2b2b')
        control_frame.pack(fill=tk.X)
        
        tk.Label(control_frame, text="缩放:", fg='white', bg='#2b2b2b').pack(side=tk.LEFT, padx=5)
        
        self.scale_var = tk.DoubleVar(value=1.0)
        self.scale_slider = ttk.Scale(control_frame, from_=0.1, to=3.0, 
                                      variable=self.scale_var, orient=tk.HORIZONTAL,
                                      command=self._on_scale_change)
        self.scale_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        self.scale_label = tk.Label(control_frame, text="100%", fg='white', bg='#2b2b2b')
        self.scale_label.pack(side=tk.LEFT, padx=5)
        
        # 鼠标事件绑定
        self.canvas.bind("<ButtonPress-1>", self._on_mouse_press)
        self.canvas.bind("<B1-Motion>", self._on_mouse_drag)
        self.canvas.bind("<MouseWheel>", self._on_mouse_wheel)
        self.canvas.bind("<Configure>", self._on_canvas_resize)
        
    def _on_canvas_resize(self, event):
        """画布大小变化时的处理"""
        self.canvas_width = event.width
        self.canvas_height = event.height
        if self.original_image:
            self._fit_image_to_canvas()
    
    def _fit_image_to_canvas(self):
        """让图像按最长边适应画布并居中"""
        if not self.original_image or self.canvas_width == 0 or self.canvas_height == 0:
            return
        
        # 计算缩放比例，使最长边铺满画布
        img_width = self.original_image.width
        img_height = self.original_image.height
        
        scale_x = self.canvas_width / img_width
        scale_y = self.canvas_height / img_height
        
        # 选择能让最长边铺满的缩放比例
        self.scale = min(scale_x, scale_y)
        
        # 更新缩放滑块
        self.scale_var.set(self.scale)
        self._update_display(center=True)
        
    def _on_scale_change(self, event=None):
        """缩放变化处理"""
        self.scale = self.scale_var.get()
        self.scale_label.config(text=f"{int(self.scale * 100)}%")
        self._update_display()
        
    def _on_mouse_press(self, event):
        """鼠标按下"""
        self.canvas.scan_mark(event.x, event.y)
        
    def _on_mouse_drag(self, event):
        """鼠标拖动"""
        self.canvas.scan_dragto(event.x, event.y, gain=1)
        
    def _on_mouse_wheel(self, event):
        """鼠标滚轮缩放"""
        if event.delta > 0:
            self.scale *= 1.1
        else:
            self.scale /= 1.1
            
        self.scale = max(0.1, min(3.0, self.scale))
        self.scale_var.set(self.scale)
        self._update_display()
        
    def set_image(self, image: Image.Image):
        """设置显示图像"""
        self.original_image = image
        # 等待Canvas更新后再适应
        self.canvas.after(100, self._fit_image_to_canvas)
        
    def _update_display(self, center=False):
        """更新显示"""
        if self.original_image is None:
            return
            
        # 计算显示尺寸
        width = int(self.original_image.width * self.scale)
        height = int(self.original_image.height * self.scale)
        
        # 调整图像大小
        self.display_image = self.original_image.resize((width, height), Image.Resampling.LANCZOS)
        self.photo_image = ImageTk.PhotoImage(self.display_image)
        
        # 更新画布
        self.canvas.delete("all")
        
        if center and self.canvas_width > 0 and self.canvas_height > 0:
            # 居中显示
            x = max(0, (self.canvas_width - width) // 2)
            y = max(0, (self.canvas_height - height) // 2)
            self.canvas.create_image(x, y, anchor=tk.NW, image=self.photo_image)
        else:
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo_image)
            
        self.canvas.config(scrollregion=self.canvas.bbox("all"))
        
    def clear(self):
        """清空显示"""
        self.original_image = None
        self.display_image = None
        self.photo_image = None
        self.canvas.delete("all")