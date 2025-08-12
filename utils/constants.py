"""
常量定义
"""

# 窗口设置
WINDOW_TITLE = "图像隐写解密程序 v3.0 - 完整支持自适应模式"
WINDOW_SIZE = "1200x700"

# 颜色主题
BG_COLOR = '#2b2b2b'
BG_DARK = '#1e1e1e'
FG_COLOR = 'white'
WARNING_COLOR = '#ffaa00'

# 按钮颜色
BTN_PRIMARY = '#4a9eff'
BTN_SUCCESS = '#4CAF50'
BTN_DANGER = '#FF6B6B'

# 字体设置
FONT_NORMAL = ('Arial', 10)
FONT_BOLD = ('Arial', 10, 'bold')
FONT_LARGE_BOLD = ('Arial', 12, 'bold')
FONT_MONO = ('Consolas', 9)

# 加密类型
ENCRYPT_TYPES = ['默认模式', '简单LSB', '通道LSB', '智能LSB', '自适应']

# 默认参数
DEFAULT_BOUNDARY = 128
DEFAULT_BRIGHTNESS = 55
DEFAULT_RESOLUTION = 0.5
DEFAULT_LSB_BITS = 2
DEFAULT_CHANNEL_BITS = [3, 4, 5]  # R, G, B