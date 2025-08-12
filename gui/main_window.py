"""
主窗口类
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import traceback
from core import ImageDecoder, DecryptionParams
from .image_panel import ImageDisplayPanel
from utils.constants import *

class MainWindow:
    """主窗口类 - 优化自适应模式显示 v3.0"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(WINDOW_TITLE)
        self.root.geometry(WINDOW_SIZE)
        
        # 设置样式
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # 解密器
        self.decoder = ImageDecoder()
        
        # 当前模式
        self.current_mode = tk.StringVar(value="auto")
        
        # 参数变量
        self.params_vars = {}
        
        self._setup_ui()
        self._apply_dark_theme()
        
    def _setup_ui(self):
        """设置UI布局"""
        # 主容器
        main_container = tk.Frame(self.root, bg=BG_COLOR)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # 左侧控制面板
        left_panel = tk.Frame(main_container, bg=BG_COLOR, width=400)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        left_panel.pack_propagate(False)
        
        # 右侧显示区域
        right_panel = tk.Frame(main_container, bg=BG_COLOR)
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # === 左侧面板内容 ===
        
        # 文件操作区
        file_frame = tk.LabelFrame(left_panel, text="文件操作", 
                                  fg=FG_COLOR, bg=BG_COLOR, 
                                  font=FONT_BOLD)
        file_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Button(file_frame, text="导入加密图像", 
                 command=self._import_image,
                 bg=BTN_PRIMARY, fg=FG_COLOR, 
                 font=FONT_NORMAL, width=20).pack(pady=5)
        
        tk.Button(file_frame, text="保存解密结果", 
                 command=self._save_result,
                 bg=BTN_SUCCESS, fg=FG_COLOR,
                 font=FONT_NORMAL, width=20).pack(pady=5)
        
        # 模式选择区
        mode_frame = tk.LabelFrame(left_panel, text="解密模式", 
                                  fg=FG_COLOR, bg=BG_COLOR,
                                  font=FONT_BOLD)
        mode_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Radiobutton(mode_frame, text="自动模式（读取元数据）", 
                      variable=self.current_mode, value="auto",
                      fg=FG_COLOR, bg=BG_COLOR, selectcolor=BG_COLOR,
                      command=self._on_mode_change).pack(anchor=tk.W, padx=10, pady=5)
        
        tk.Radiobutton(mode_frame, text="手动模式（自定义参数）", 
                      variable=self.current_mode, value="manual",
                      fg=FG_COLOR, bg=BG_COLOR, selectcolor=BG_COLOR,
                      command=self._on_mode_change).pack(anchor=tk.W, padx=10, pady=5)
        
        # 参数设置区
        self.params_frame = tk.LabelFrame(left_panel, text="参数设置", 
                                         fg=FG_COLOR, bg=BG_COLOR,
                                         font=FONT_BOLD)
        self.params_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 自动模式信息
        self.auto_info_frame = tk.Frame(self.params_frame, bg=BG_COLOR)
        
        self.info_text = tk.Text(self.auto_info_frame, height=15, width=40,
                                 bg=BG_DARK, fg=FG_COLOR, 
                                 font=FONT_MONO)
        self.info_text.pack(padx=10, pady=10)
        
        # 手动模式参数
        self.manual_params_frame = tk.Frame(self.params_frame, bg=BG_COLOR)
        
        # 加密类型选择
        tk.Label(self.manual_params_frame, text="加密类型:", 
                fg=FG_COLOR, bg=BG_COLOR).grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        
        self.encrypt_type = ttk.Combobox(self.manual_params_frame, 
                                        values=ENCRYPT_TYPES,
                                        state='readonly', width=20)
        self.encrypt_type.grid(row=0, column=1, padx=10, pady=5)
        self.encrypt_type.current(0)
        self.encrypt_type.bind('<<ComboboxSelected>>', self._on_type_change)
        
        # 动态参数区
        self.dynamic_params_frame = tk.Frame(self.manual_params_frame, bg=BG_COLOR)
        self.dynamic_params_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10)
        
        # 解密按钮
        tk.Button(left_panel, text="开始解密", 
                 command=self._decrypt_image,
                 bg=BTN_DANGER, fg=FG_COLOR,
                 font=FONT_LARGE_BOLD, 
                 height=2).pack(fill=tk.X, padx=5, pady=10)
        
        # === 右侧显示区域 ===
        
        # 加密图像显示
        self.encrypted_display = ImageDisplayPanel(right_panel, "加密图像")
        self.encrypted_display.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # 解密图像显示
        self.decrypted_display = ImageDisplayPanel(right_panel, "解密结果")
        self.decrypted_display.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # 初始化显示
        self._on_mode_change()
        
    def _apply_dark_theme(self):
        """应用深色主题"""
        self.style.configure('TCombobox', fieldbackground='#3c3c3c', background='#3c3c3c')
        self.style.configure('TScale', background=BG_COLOR)
        
    def _on_mode_change(self):
        """模式切换处理"""
        if self.current_mode.get() == "auto":
            self.auto_info_frame.pack(fill=tk.BOTH, expand=True)
            self.manual_params_frame.pack_forget()
        else:
            self.auto_info_frame.pack_forget()
            self.manual_params_frame.pack(fill=tk.BOTH, expand=True)
            self._on_type_change()
            
    def _on_type_change(self, event=None):
        """加密类型变化处理"""
        # 清空动态参数区
        for widget in self.dynamic_params_frame.winfo_children():
            widget.destroy()
            
        encrypt_type = self.encrypt_type.get()
        
        if encrypt_type == '默认模式':
            self._create_default_params()
        elif encrypt_type == '简单LSB':
            self._create_simple_lsb_params()
        elif encrypt_type == '通道LSB':
            self._create_channel_lsb_params()
        elif encrypt_type == '智能LSB':
            self._create_smart_lsb_params()
        elif encrypt_type == '自适应':
            self._create_adaptive_params()
            
    def _create_default_params(self):
        """创建默认模式参数"""
        # 模式类型
        tk.Label(self.dynamic_params_frame, text="模式类型:", 
                fg=FG_COLOR, bg=BG_COLOR).grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.params_vars['mode_type'] = tk.StringVar(value='light')
        tk.Radiobutton(self.dynamic_params_frame, text="亮色", 
                      variable=self.params_vars['mode_type'], value='light',
                      fg=FG_COLOR, bg=BG_COLOR, selectcolor=BG_COLOR).grid(row=0, column=1, sticky=tk.W)
        tk.Radiobutton(self.dynamic_params_frame, text="暗色", 
                      variable=self.params_vars['mode_type'], value='dark',
                      fg=FG_COLOR, bg=BG_COLOR, selectcolor=BG_COLOR).grid(row=0, column=2, sticky=tk.W)
        
        # 分界点
        tk.Label(self.dynamic_params_frame, text="分界点(k):", 
                fg=FG_COLOR, bg=BG_COLOR).grid(row=1, column=0, sticky=tk.W, pady=5)
        
        self.params_vars['boundary'] = tk.IntVar(value=DEFAULT_BOUNDARY)
        boundary_scale = ttk.Scale(self.dynamic_params_frame, from_=0, to=255,
                                   variable=self.params_vars['boundary'],
                                   orient=tk.HORIZONTAL, length=150)
        boundary_scale.grid(row=1, column=1, columnspan=2, pady=5)
        
        boundary_label = tk.Label(self.dynamic_params_frame, text=str(DEFAULT_BOUNDARY), 
                                 fg=FG_COLOR, bg=BG_COLOR)
        boundary_label.grid(row=1, column=3, pady=5)
        
        boundary_scale.config(command=lambda v: boundary_label.config(text=str(int(float(v)))))
        
        # 亮度参数
        tk.Label(self.dynamic_params_frame, text="亮度(l):", 
                fg=FG_COLOR, bg=BG_COLOR).grid(row=2, column=0, sticky=tk.W, pady=5)
        
        self.params_vars['brightness'] = tk.IntVar(value=DEFAULT_BRIGHTNESS)
        brightness_scale = ttk.Scale(self.dynamic_params_frame, from_=0, to=255,
                                    variable=self.params_vars['brightness'],
                                    orient=tk.HORIZONTAL, length=150)
        brightness_scale.grid(row=2, column=1, columnspan=2, pady=5)
        
        brightness_label = tk.Label(self.dynamic_params_frame, text=str(DEFAULT_BRIGHTNESS), 
                                   fg=FG_COLOR, bg=BG_COLOR)
        brightness_label.grid(row=2, column=3, pady=5)
        
        brightness_scale.config(command=lambda v: brightness_label.config(text=str(int(float(v)))))
        
        # 分辨率
        tk.Label(self.dynamic_params_frame, text="分辨率:", 
                fg=FG_COLOR, bg=BG_COLOR).grid(row=3, column=0, sticky=tk.W, pady=5)
        
        self.params_vars['resolution'] = tk.DoubleVar(value=DEFAULT_RESOLUTION)
        tk.Radiobutton(self.dynamic_params_frame, text="0.5", 
                      variable=self.params_vars['resolution'], value=0.5,
                      fg=FG_COLOR, bg=BG_COLOR, selectcolor=BG_COLOR).grid(row=3, column=1, sticky=tk.W)
        tk.Radiobutton(self.dynamic_params_frame, text="0.75", 
                      variable=self.params_vars['resolution'], value=0.75,
                      fg=FG_COLOR, bg=BG_COLOR, selectcolor=BG_COLOR).grid(row=3, column=2, sticky=tk.W)
        
        # 方向
        tk.Label(self.dynamic_params_frame, text="方向:", 
                fg=FG_COLOR, bg=BG_COLOR).grid(row=4, column=0, sticky=tk.W, pady=5)
        
        self.params_vars['direction'] = tk.BooleanVar(value=False)
        tk.Checkbutton(self.dynamic_params_frame, text="反转", 
                      variable=self.params_vars['direction'],
                      fg=FG_COLOR, bg=BG_COLOR, selectcolor=BG_COLOR).grid(row=4, column=1, sticky=tk.W, pady=5)
        
    def _create_simple_lsb_params(self):
        """创建简单LSB参数"""
        tk.Label(self.dynamic_params_frame, text="编码位数:", 
                fg=FG_COLOR, bg=BG_COLOR).grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.params_vars['bits'] = tk.IntVar(value=DEFAULT_LSB_BITS)
        bits_scale = ttk.Scale(self.dynamic_params_frame, from_=1, to=8,
                              variable=self.params_vars['bits'],
                              orient=tk.HORIZONTAL, length=150)
        bits_scale.grid(row=0, column=1, pady=5)
        
        bits_label = tk.Label(self.dynamic_params_frame, text=f"{DEFAULT_LSB_BITS} bits", 
                             fg=FG_COLOR, bg=BG_COLOR)
        bits_label.grid(row=0, column=2, pady=5)
        
        bits_scale.config(command=lambda v: bits_label.config(text=f"{int(float(v))} bits"))
        
    def _create_channel_lsb_params(self):
        """创建通道LSB参数"""
        channels = ['R', 'G', 'B']
        default_bits = DEFAULT_CHANNEL_BITS
        max_bits = [8, 8, 8]  # 支持1-8位
        
        for i, (channel, default, max_bit) in enumerate(zip(channels, default_bits, max_bits)):
            tk.Label(self.dynamic_params_frame, text=f"{channel}通道:", 
                    fg=FG_COLOR, bg=BG_COLOR).grid(row=i, column=0, sticky=tk.W, pady=5)
            
            self.params_vars[f'{channel}_bits'] = tk.IntVar(value=default)
            scale = ttk.Scale(self.dynamic_params_frame, from_=1, to=max_bit,
                            variable=self.params_vars[f'{channel}_bits'],
                            orient=tk.HORIZONTAL, length=150)
            scale.grid(row=i, column=1, pady=5)
            
            label = tk.Label(self.dynamic_params_frame, text=f"{default} bits", 
                           fg=FG_COLOR, bg=BG_COLOR)
            label.grid(row=i, column=2, pady=5)
            
            scale.config(command=lambda v, l=label: l.config(text=f"{int(float(v))} bits"))
            
    def _create_smart_lsb_params(self):
        """创建智能LSB参数"""
        # 最小位数
        tk.Label(self.dynamic_params_frame, text="最小位数:", 
                fg=FG_COLOR, bg=BG_COLOR).grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.params_vars['min_bits'] = tk.IntVar(value=1)
        min_scale = ttk.Scale(self.dynamic_params_frame, from_=1, to=3,
                             variable=self.params_vars['min_bits'],
                             orient=tk.HORIZONTAL, length=150)
        min_scale.grid(row=0, column=1, pady=5)
        
        min_label = tk.Label(self.dynamic_params_frame, text="1 bit", 
                           fg=FG_COLOR, bg=BG_COLOR)
        min_label.grid(row=0, column=2, pady=5)
        
        min_scale.config(command=lambda v: min_label.config(text=f"{int(float(v))} bit{'s' if int(float(v))>1 else ''}"))
        
        # 最大位数
        tk.Label(self.dynamic_params_frame, text="最大位数:", 
                fg=FG_COLOR, bg=BG_COLOR).grid(row=1, column=0, sticky=tk.W, pady=5)
        
        self.params_vars['max_bits'] = tk.IntVar(value=5)
        max_scale = ttk.Scale(self.dynamic_params_frame, from_=3, to=8,
                             variable=self.params_vars['max_bits'],
                             orient=tk.HORIZONTAL, length=150)
        max_scale.grid(row=1, column=1, pady=5)
        
        max_label = tk.Label(self.dynamic_params_frame, text="5 bits", 
                           fg=FG_COLOR, bg=BG_COLOR)
        max_label.grid(row=1, column=2, pady=5)
        
        max_scale.config(command=lambda v: max_label.config(text=f"{int(float(v))} bits"))
        
        # 阈值
        tk.Label(self.dynamic_params_frame, text="阈值:", 
                fg=FG_COLOR, bg=BG_COLOR).grid(row=2, column=0, sticky=tk.W, pady=5)
        
        self.params_vars['threshold'] = tk.DoubleVar(value=0.5)
        threshold_scale = ttk.Scale(self.dynamic_params_frame, from_=0, to=1,
                                   variable=self.params_vars['threshold'],
                                   orient=tk.HORIZONTAL, length=150)
        threshold_scale.grid(row=2, column=1, pady=5)
        
        threshold_label = tk.Label(self.dynamic_params_frame, text="0.50", 
                                 fg=FG_COLOR, bg=BG_COLOR)
        threshold_label.grid(row=2, column=2, pady=5)
        
        threshold_scale.config(command=lambda v: threshold_label.config(text=f"{float(v):.2f}"))
        
    def _create_adaptive_params(self):
        """创建自适应参数"""
        # 说明信息
        info_label = tk.Label(self.dynamic_params_frame, 
                            text="自适应模式会自动选择策略\n手动模式仅供测试使用", 
                            fg=WARNING_COLOR, bg=BG_COLOR, justify=tk.LEFT)
        info_label.grid(row=0, column=0, columnspan=3, pady=10)
        
        # 策略阈值
        tk.Label(self.dynamic_params_frame, text="策略阈值:", 
                fg=FG_COLOR, bg=BG_COLOR).grid(row=1, column=0, sticky=tk.W, pady=5)
        
        self.params_vars['threshold'] = tk.DoubleVar(value=0.5)
        threshold_scale = ttk.Scale(self.dynamic_params_frame, from_=0, to=1,
                                   variable=self.params_vars['threshold'],
                                   orient=tk.HORIZONTAL, length=150)
        threshold_scale.grid(row=1, column=1, pady=5)
        
        threshold_label = tk.Label(self.dynamic_params_frame, text="0.5", 
                                 fg=FG_COLOR, bg=BG_COLOR)
        threshold_label.grid(row=1, column=2, pady=5)
        
        threshold_scale.config(command=lambda v: threshold_label.config(text=f"{float(v):.2f}"))
        
    def _import_image(self):
        """导入加密图像"""
        filepath = filedialog.askopenfilename(
            title="选择加密图像",
            filetypes=[("图像文件", "*.png *.jpg *.jpeg *.bmp"), ("所有文件", "*.*")]
        )
        
        if filepath:
            if self.decoder.load_image(filepath):
                self.encrypted_display.set_image(self.decoder.encrypted_image)
                
                # 自动模式下显示元数据
                if self.current_mode.get() == "auto":
                    self._display_metadata()
                    
                messagebox.showinfo("成功", "图像加载成功！")
            else:
                messagebox.showerror("错误", "无法加载图像！")
                
    def _display_metadata(self):
        """显示元数据信息 - 优化自适应模式显示 v3.0"""
        self.info_text.delete(1.0, tk.END)
        
        if not self.decoder.metadata:
            self.info_text.insert(tk.END, "未检测到元数据\n\n")
            self.info_text.insert(tk.END, "该图像可能：\n")
            self.info_text.insert(tk.END, "1. 不是PNG格式\n")
            self.info_text.insert(tk.END, "2. 未包含隐写元数据\n")
            self.info_text.insert(tk.END, "3. 使用了其他加密工具\n\n")
            self.info_text.insert(tk.END, "建议切换到手动模式")
        else:
            self.info_text.insert(tk.END, "检测到元数据：\n")
            self.info_text.insert(tk.END, "=" * 35 + "\n\n")
            
            # 显示模式
            if 'mode' in self.decoder.metadata:
                mode = self.decoder.metadata['mode']
                self.info_text.insert(tk.END, f"加密模式: {mode}\n")
                
                # 根据模式显示对应参数
                if 'parameters' in self.decoder.metadata:
                    params = self.decoder.metadata['parameters']
                    self.info_text.insert(tk.END, "\n参数详情:\n")
                    self.info_text.insert(tk.END, "-" * 30 + "\n")
                    
                    if mode == 'default':
                        self.info_text.insert(tk.END, f"模式类型: {params.get('mode_type', '-')}\n")
                        self.info_text.insert(tk.END, f"分界点: {params.get('boundary', '-')}\n")
                        self.info_text.insert(tk.END, f"分辨率: {params.get('resolution', '-')}\n")
                        self.info_text.insert(tk.END, f"方向: {'反转' if params.get('direction') else '正常'}\n")
                        self.info_text.insert(tk.END, f"亮度: {params.get('brightness', '-')}\n")
                        
                    elif mode == 'simple_lsb':
                        self.info_text.insert(tk.END, f"编码位数: {params.get('bits', '-')}\n")
                        self.info_text.insert(tk.END, f"编码强度: {params.get('strength', '-')}\n")
                        
                    elif mode == 'channel_lsb':
                        if isinstance(params.get('channel_bits'), dict):
                            bits = params['channel_bits']
                            self.info_text.insert(tk.END, f"R通道: {bits.get('R', '-')} bits\n")
                            self.info_text.insert(tk.END, f"G通道: {bits.get('G', '-')} bits\n")
                            self.info_text.insert(tk.END, f"B通道: {bits.get('B', '-')} bits\n")
                        self.info_text.insert(tk.END, f"质量: {params.get('quality', '-')}\n")
                        
                    elif mode == 'smart_lsb':
                        if 'bit_range' in params:
                            bit_range = params['bit_range']
                            self.info_text.insert(tk.END, f"最小位数: {bit_range.get('min', '-')}\n")
                            self.info_text.insert(tk.END, f"最大位数: {bit_range.get('max', '-')}\n")
                        self.info_text.insert(tk.END, f"阈值: {params.get('threshold', '-')}\n")
                        
                    elif mode == 'adaptive':
                        # 优化自适应模式显示 v3.0
                        self.info_text.insert(tk.END, f"精度: {params.get('precision', '-')}\n")
                        self.info_text.insert(tk.END, f"优先级: {params.get('priority', '-')}\n")
                        self.info_text.insert(tk.END, f"阈值: {params.get('threshold', '-')}\n")
                        
                        version = params.get('version', '1.0')
                        self.info_text.insert(tk.END, f"版本: {version}\n")
                        
                        # 显示选择的策略信息（关键信息）
                        strategy = params.get('selected_strategy')
                        if strategy:
                            self.info_text.insert(tk.END, f"\n【策略信息】\n")
                            self.info_text.insert(tk.END, f"选择策略: {strategy}\n")
                            
                            # 显示策略参数
                            strategy_params = params.get('strategy_params', {})
                            if strategy_params:
                                self.info_text.insert(tk.END, "策略参数:\n")
                                
                                if strategy == 'simple_lsb':
                                    self.info_text.insert(tk.END, f"  位数: {strategy_params.get('bits', '-')}\n")
                                    self.info_text.insert(tk.END, f"  强度: {strategy_params.get('strength', '-')}\n")
                                    
                                elif strategy == 'channel_lsb':
                                    if 'channel_bits' in strategy_params:
                                        cb = strategy_params['channel_bits']
                                        self.info_text.insert(tk.END, f"  R通道: {cb.get('R', '-')} bits\n")
                                        self.info_text.insert(tk.END, f"  G通道: {cb.get('G', '-')} bits\n")
                                        self.info_text.insert(tk.END, f"  B通道: {cb.get('B', '-')} bits\n")
                                    self.info_text.insert(tk.END, f"  质量: {strategy_params.get('quality', '-')}\n")
                                    
                                elif strategy == 'smart_lsb':
                                    if 'bit_range' in strategy_params:
                                        br = strategy_params['bit_range']
                                        self.info_text.insert(tk.END, f"  位数范围: {br.get('min', '-')}-{br.get('max', '-')}\n")
                                    self.info_text.insert(tk.END, f"  阈值: {strategy_params.get('threshold', '-')}\n")
                                    
                            # 显示解密状态
                            self.info_text.insert(tk.END, f"\n✅ 解密支持: 完整支持\n")
                            self.info_text.insert(tk.END, f"可以精确解密\n")
                        else:
                            self.info_text.insert(tk.END, f"\n⚠️ 警告: 策略信息缺失\n")
                            self.info_text.insert(tk.END, f"解密支持: 降级模式\n")
                            self.info_text.insert(tk.END, f"将使用阈值推断策略\n")
                        
                        # 显示解密指导信息（如果有）
                        if 'decryption_guide' in params:
                            guide = params['decryption_guide']
                            if guide:
                                self.info_text.insert(tk.END, f"\n【解密指导】\n")
                                self.info_text.insert(tk.END, f"策略: {guide.get('strategy', '-')}\n")
                                self.info_text.insert(tk.END, f"描述: {guide.get('description', '-')}\n")
                        
                        # 显示分析摘要（如果有）
                        if 'analysis_summary' in params:
                            summary = params['analysis_summary']
                            self.info_text.insert(tk.END, f"\n【分析摘要】\n")
                            self.info_text.insert(tk.END, f"相似度: {summary.get('similarity', '-'):.3f}\n")
                            self.info_text.insert(tk.END, f"复杂度: {summary.get('complexity', '-'):.3f}\n")
                            self.info_text.insert(tk.END, f"彩色图: {'是' if summary.get('is_color') else '否'}\n")
                            self.info_text.insert(tk.END, f"边缘密度: {summary.get('edge_density', '-'):.3f}\n")
            
            # 显示软件信息
            if 'software' in self.decoder.metadata:
                self.info_text.insert(tk.END, f"\n软件信息:\n")
                self.info_text.insert(tk.END, f"{self.decoder.metadata['software']}\n")
                
    def _decrypt_image(self):
        """执行解密 - 优化错误处理"""
        if self.decoder.encrypted_image is None:
            messagebox.showwarning("警告", "请先导入加密图像！")
            return
            
        try:
            if self.current_mode.get() == "auto":
                # 自动模式
                params = self.decoder.auto_detect_params()
                if params is None:
                    messagebox.showwarning("警告", "无法从元数据获取解密参数，请使用手动模式！")
                    return
                    
                print(f"使用自动检测参数: {params}")
            else:
                # 手动模式
                params = self._get_manual_params()
                print(f"使用手动参数: {params}")
                
            # 执行解密
            result = self.decoder.decrypt(params)
            
            if result:
                self.decrypted_display.set_image(result)
                messagebox.showinfo("成功", "解密完成！")
            else:
                messagebox.showerror("错误", "解密失败！请检查参数是否正确。")
                
        except Exception as e:
            print(f"解密异常: {e}")
            traceback.print_exc()
            messagebox.showerror("错误", f"解密过程出错：{str(e)}")
            
    def _get_manual_params(self) -> DecryptionParams:
        """获取手动模式参数"""
        encrypt_type = self.encrypt_type.get()
        
        if encrypt_type == '默认模式':
            return DecryptionParams(
                mode='default',
                mode_type=self.params_vars['mode_type'].get(),
                boundary=self.params_vars['boundary'].get(),
                resolution=self.params_vars['resolution'].get(),
                direction=self.params_vars['direction'].get(),
                brightness=self.params_vars.get('brightness', tk.IntVar(value=DEFAULT_BRIGHTNESS)).get()
            )
        elif encrypt_type == '简单LSB':
            return DecryptionParams(
                mode='simple_lsb',
                bits=self.params_vars['bits'].get()
            )
        elif encrypt_type == '通道LSB':
            return DecryptionParams(
                mode='channel_lsb',
                channel_bits={
                    'R': self.params_vars['R_bits'].get(),
                    'G': self.params_vars['G_bits'].get(),
                    'B': self.params_vars['B_bits'].get()
                }
            )
        elif encrypt_type == '智能LSB':
            return DecryptionParams(
                mode='smart_lsb',
                bit_range={
                    'min': self.params_vars['min_bits'].get(),
                    'max': self.params_vars['max_bits'].get()
                },
                threshold=self.params_vars['threshold'].get()
            )
        elif encrypt_type == '自适应':
            return DecryptionParams(
                mode='adaptive',
                threshold=self.params_vars['threshold'].get()
            )
            
    def _save_result(self):
        """保存解密结果"""
        if self.decoder.decrypted_image is None:
            messagebox.showwarning("警告", "没有可保存的解密结果！")
            return
            
        filepath = filedialog.asksaveasfilename(
            title="保存解密图像",
            defaultextension=".png",
            filetypes=[("PNG文件", "*.png"), ("JPEG文件", "*.jpg"), ("所有文件", "*.*")]
        )
        
        if filepath:
            self.decoder.decrypted_image.save(filepath)
            messagebox.showinfo("成功", f"图像已保存到：{filepath}")
            
    def run(self):
        """运行程序"""
        self.root.mainloop()