"""
解密参数数据类定义
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class DecryptionParams:
    """解密参数数据类 - 优化版 v3.0"""
    mode: str
    # 默认模式参数
    mode_type: Optional[str] = None
    boundary: Optional[int] = None
    resolution: Optional[float] = None
    direction: Optional[bool] = None
    brightness: Optional[int] = None
    # 简单LSB参数
    bits: Optional[int] = None
    strength: Optional[float] = None
    # 通道LSB参数
    channel_bits: Optional[Dict[str, int]] = None
    quality: Optional[float] = None
    # 智能LSB参数
    bit_range: Optional[Dict[str, int]] = None
    threshold: Optional[float] = None
    edge_protect: Optional[bool] = None
    # 自适应模式参数 - 完整版 v3.0
    selected_strategy: Optional[str] = None      # 选择的具体策略
    strategy_params: Optional[Dict] = None       # 策略的完整参数
    precision: Optional[str] = None              # 分析精度
    priority: Optional[str] = None               # 优先级
    version: Optional[str] = None                # 版本信息
    decryption_guide: Optional[Dict] = None      # 解密指导