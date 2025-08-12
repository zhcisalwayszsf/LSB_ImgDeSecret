"""
图像解密核心类
"""

from PIL import Image, PngImagePlugin
import numpy as np
import json
from typing import Optional, Dict
from .params import DecryptionParams

class ImageDecoder:
    """图像解密核心类 - 优化版 v3.0"""
    
    def __init__(self):
        self.encrypted_image = None
        self.decrypted_image = None
        self.metadata = {}
        
    def load_image(self, filepath: str) -> bool:
        """加载加密图像 - 优化元数据读取"""
        try:
            self.encrypted_image = Image.open(filepath)
            
            # 尝试读取PNG元数据
            if isinstance(self.encrypted_image, PngImagePlugin.PngImageFile):
                self.metadata = {}
                
                # 读取模式
                if 'Steganography_mode' in self.encrypted_image.info:
                    self.metadata['mode'] = self.encrypted_image.info['Steganography_mode']
                
                # 读取参数（JSON格式）
                if 'Steganography_parameters' in self.encrypted_image.info:
                    try:
                        params_json = self.encrypted_image.info['Steganography_parameters']
                        self.metadata['parameters'] = json.loads(params_json)
                    except json.JSONDecodeError as e:
                        print(f"JSON解析错误: {e}")
                        self.metadata['parameters'] = {}
                
                # 读取其他信息
                if 'Software' in self.encrypted_image.info:
                    self.metadata['software'] = self.encrypted_image.info['Software']
                    
                # 调试输出
                print(f"加载的元数据: {self.metadata}")
            
            return True
        except Exception as e:
            print(f"加载图像失败: {e}")
            return False
    
    def auto_detect_params(self) -> Optional[DecryptionParams]:
        """从元数据自动检测解密参数 - 完整支持自适应模式 v3.0"""
        if not self.metadata:
            return None
            
        params = DecryptionParams(mode='unknown')
        
        # 解析模式
        if 'mode' in self.metadata:
            params.mode = self.metadata['mode']
            
        # 解析参数
        if 'parameters' in self.metadata:
            meta_params = self.metadata['parameters']
            
            if params.mode == 'default':
                # 默认模式完整参数
                params.mode_type = meta_params.get('mode_type', 'light')
                params.boundary = meta_params.get('boundary', 128)
                params.resolution = meta_params.get('resolution', 0.5)
                params.direction = meta_params.get('direction', False)
                params.brightness = meta_params.get('brightness', 55)
                
            elif params.mode == 'simple_lsb':
                params.bits = meta_params.get('bits', 2)
                params.strength = meta_params.get('strength', 1.0)
                
            elif params.mode == 'channel_lsb':
                # 处理通道位数（支持新旧格式）
                if 'channel_bits' in meta_params and isinstance(meta_params['channel_bits'], dict):
                    params.channel_bits = meta_params['channel_bits']
                else:
                    # 兼容旧格式
                    params.channel_bits = {
                        'R': meta_params.get('r_bits', meta_params.get('R', 2)),
                        'G': meta_params.get('g_bits', meta_params.get('G', 3)),
                        'B': meta_params.get('b_bits', meta_params.get('B', 4))
                    }
                params.quality = meta_params.get('quality', 0.8)
                
            elif params.mode == 'smart_lsb':
                # 处理位数范围（支持新旧格式）
                if 'bit_range' in meta_params and isinstance(meta_params['bit_range'], dict):
                    params.bit_range = meta_params['bit_range']
                else:
                    # 兼容旧格式
                    params.bit_range = {
                        'min': meta_params.get('min_bits', 1),
                        'max': meta_params.get('max_bits', 5)
                    }
                params.threshold = meta_params.get('threshold', 0.5)
                params.edge_protect = meta_params.get('edge_protect', True)
                
            elif params.mode == 'adaptive':
                # 自适应模式 - 完整支持 v3.0
                params.threshold = meta_params.get('threshold', 0.5)
                params.precision = meta_params.get('precision', '中等')
                params.priority = meta_params.get('priority', '平衡')
                params.version = meta_params.get('version', '1.0')
                
                # 关键信息：具体策略和参数
                params.selected_strategy = meta_params.get('selected_strategy')
                params.strategy_params = meta_params.get('strategy_params', {})
                params.decryption_guide = meta_params.get('decryption_guide', {})
                
                # 调试输出
                print(f"[自适应模式解密] 检测到的参数:")
                print(f"  版本: {params.version}")
                print(f"  选择策略: {params.selected_strategy}")
                print(f"  策略参数: {params.strategy_params}")
                
                # 验证策略信息完整性
                if not params.selected_strategy:
                    print("[警告] 未找到策略信息，尝试从解密指导中获取")
                    # 尝试从解密指导信息中获取
                    if params.decryption_guide and 'strategy' in params.decryption_guide:
                        params.selected_strategy = params.decryption_guide['strategy']
                        print(f"  从解密指导获取策略: {params.selected_strategy}")
                    else:
                        # 使用默认策略
                        print("[警告] 使用默认策略: simple_lsb")
                        params.selected_strategy = 'simple_lsb'
                        params.strategy_params = {'bits': 2, 'strength': 1.0}
                
                # 验证策略参数完整性
                if params.selected_strategy and not params.strategy_params:
                    print("[警告] 策略参数缺失，使用默认参数")
                    params.strategy_params = self._get_default_strategy_params(params.selected_strategy)
                
        return params
    
    def _get_default_strategy_params(self, strategy: str) -> Dict:
        """获取策略的默认参数"""
        if strategy == 'simple_lsb':
            return {'bits': 2, 'strength': 1.0}
        elif strategy == 'channel_lsb':
            return {
                'channel_bits': {'R': 2, 'G': 3, 'B': 4},
                'quality': 0.8
            }
        elif strategy == 'smart_lsb':
            return {
                'bit_range': {'min': 1, 'max': 5},
                'threshold': 0.5,
                'edge_protect': True
            }
        else:
            return {'bits': 2, 'strength': 1.0}
    
    def decrypt_default_mode(self, mode_type: str = 'light', boundary: int = 128, 
                          resolution: float = 0.5, direction: bool = False,
                          brightness: int = 55) -> Optional[Image.Image]:
        """解密默认模式（色阶映射）"""
        if self.encrypted_image is None:
            return None

        img_array = np.array(self.encrypted_image).astype(np.float32)

        # k 参数对应 boundary，l 参数对应 brightness
        k = boundary
        l = brightness

        if mode_type == 'dark':
            # 暗色模式：
            # [0, k] 范围按比例映射到 [0, 255]
            # (k, 255] 范围设为 k
            
            # 创建查找表
            lut = np.zeros(256, dtype=np.float32)
            for x in range(256):
                if x <= k:
                    # [0, k] -> [0, 255] 的映射
                    if k > 0:
                        lut[x] = (x * 255.0 / k)
                    else:
                        lut[x] = 0
                else:
                    # (k, 255] -> k
                    lut[x] = k

        else:  # light mode
            # 亮色模式：
            # [0, k] 范围设为 l
            # [k, 255] 范围按比例映射到 [0, 255]
            
            # 创建查找表
            lut = np.zeros(256, dtype=np.float32)
            for x in range(256):
                if x < k:
                    # [0, k) -> l
                    lut[x] = l
                else:
                    # [k, 255] -> [0, 255] 的映射
                    if k < 255:
                        lut[x] = ((x - k) * 255.0 / (255 - k))
                    else:
                        lut[x] = 255

        # 应用查找表到图像
        if len(img_array.shape) == 3:
            # RGB图像
            result = np.zeros_like(img_array)
            for c in range(3):
                channel = img_array[:, :, c].astype(np.int32)
                channel = np.clip(channel, 0, 255)
                result[:, :, c] = lut[channel]
        else:
            # 灰度图像
            img_clipped = np.clip(img_array.astype(np.int32), 0, 255)
            result = lut[img_clipped]

        return Image.fromarray(result.astype(np.uint8))
    
    def decrypt_simple_lsb(self, bits: int = 2, strength: float = 1.0) -> Optional[Image.Image]:
        """解密简单LSB模式 - 支持1-8位"""
        if self.encrypted_image is None:
            return None
            
        img_array = np.array(self.encrypted_image)
        
        # 限制位数范围（1-8）
        bits = max(1, min(8, bits))
        
        # 提取最低有效位
        mask = (1 << bits) - 1
        extracted = img_array & mask
        
        # 扩展到完整范围
        shift = 8 - bits
        result = extracted << shift
        
        # 填充剩余位（改进的填充算法）
        remaining_bits = shift
        while remaining_bits > 0:
            bits_to_copy = min(bits, remaining_bits)
            result |= (extracted >> (bits - bits_to_copy)) << (remaining_bits - bits_to_copy)
            remaining_bits -= bits_to_copy
                
        return Image.fromarray(result.astype(np.uint8))
    
    def decrypt_channel_lsb(self, channel_bits: Dict[str, int], quality: float = 1) -> Optional[Image.Image]:
        """解密通道自适应LSB模式 - 支持1-8位"""
        if self.encrypted_image is None:
            return None
            
        if self.encrypted_image.mode != 'RGB':
            self.encrypted_image = self.encrypted_image.convert('RGB')
            
        img_array = np.array(self.encrypted_image)
        result = np.zeros_like(img_array)
        
        # 获取每个通道的位数
        r_bits = min(8, max(1, channel_bits.get('R', 2)))
        g_bits = min(8, max(1, channel_bits.get('G', 3)))
        b_bits = min(8, max(1, channel_bits.get('B', 4)))
        channel_bits_list = [r_bits, g_bits, b_bits]
        
        for c in range(3):
            bits = channel_bits_list[c]
            
            if bits == 8:
                # 如果使用全部8位，通道完全是底图数据
                result[:, :, c] = img_array[:, :, c]
            else:
                mask = (1 << bits) - 1
                extracted = img_array[:, :, c] & mask
                
                shift = 8 - bits
                result[:, :, c] = extracted << shift
                
                # 填充剩余位
                remaining_bits = shift
                while remaining_bits > 0:
                    bits_to_copy = min(bits, remaining_bits)
                    result[:, :, c] |= (extracted >> (bits - bits_to_copy)) << (remaining_bits - bits_to_copy)
                    remaining_bits -= bits_to_copy
                    
        return Image.fromarray(result.astype(np.uint8))
    
    def decrypt_smart_lsb(self, bit_range: Dict[str, int], threshold: float = 0.5, 
                        edge_protect: bool = False) -> Optional[Image.Image]:
        """
        解密智能分布LSB模式 - 简化统一版 v2.0
        使用与加密完全一致的逻辑
        """
        if self.encrypted_image is None:
            return None
        
        img_array = np.array(self.encrypted_image)
        
        # 获取位数范围
        min_bits = max(1, min(3, bit_range.get('min', 1)))
        max_bits = max(3, min(8, bit_range.get('max', 5)))
        
        # 使用与加密完全一致的位数计算
        # 线性插值计算位数
        avg_bits = min_bits + (max_bits - min_bits) * threshold
        # 四舍五入并限制范围
        avg_bits = int(round(avg_bits))
        avg_bits = max(min_bits, min(max_bits, avg_bits))
        
        # 提取最低有效位
        mask = (1 << avg_bits) - 1
        extracted = img_array & mask
        
        # 扩展到完整范围
        shift = 8 - avg_bits
        result = extracted << shift
        
        # 填充剩余位以改善视觉效果
        remaining_bits = shift
        temp_extracted = extracted
        while remaining_bits > 0:
            bits_to_copy = min(avg_bits, remaining_bits)
            if avg_bits > 0:
                result |= (temp_extracted >> max(0, avg_bits - bits_to_copy)) << max(0, remaining_bits - bits_to_copy)
            remaining_bits -= bits_to_copy
        
        return Image.fromarray(result.astype(np.uint8))
    
    def decrypt_adaptive(self, threshold: float = 0.5, strategy: str = None, 
                        strategy_params: Dict = None, **kwargs) -> Optional[Image.Image]:
        """
        解密多策略自适应模式 - 完整版 v3.0
        基于元数据中的具体策略信息进行精确解密
        """
        if self.encrypted_image is None:
            return None
        
        print(f"[自适应解密] 开始解密:")
        print(f"  策略: {strategy}")
        print(f"  参数: {strategy_params}")
        
        # 如果没有提供策略，尝试使用阈值推断（向后兼容）
        if not strategy or not strategy_params:
            print("[自适应解密] 策略信息不完整，尝试推断...")
            
            # 检查是否有解密指导信息
            if kwargs.get('decryption_guide'):
                guide = kwargs['decryption_guide']
                strategy = guide.get('strategy', 'simple_lsb')
                print(f"  从解密指导获取策略: {strategy}")
            else:
                # 使用阈值推断策略（向后兼容旧版本）
                if threshold < 0.3:
                    strategy = 'simple_lsb'
                    strategy_params = {'bits': 2, 'strength': 1.0}
                elif threshold < 0.7:
                    strategy = 'channel_lsb'
                    strategy_params = {
                        'channel_bits': {'R': 2, 'G': 3, 'B': 4},
                        'quality': 0.8
                    }
                else:
                    strategy = 'smart_lsb'
                    strategy_params = {
                        'bit_range': {'min': 1, 'max': 5},
                        'threshold': threshold,
                        'edge_protect': True
                    }
                print(f"  推断策略: {strategy}")
        
        # 根据具体策略进行解密
        try:
            if strategy == 'simple_lsb':
                print("[自适应解密] 使用简单LSB策略")
                bits = strategy_params.get('bits', 2)
                strength = strategy_params.get('strength', 1.0)
                return self.decrypt_simple_lsb(bits=bits, strength=strength)
                
            elif strategy == 'channel_lsb':
                print("[自适应解密] 使用通道LSB策略")
                # 处理通道位数参数的不同格式
                if 'channel_bits' in strategy_params and isinstance(strategy_params['channel_bits'], dict):
                    channel_bits = strategy_params['channel_bits']
                elif 'r_bits' in strategy_params:
                    # 兼容旧格式
                    channel_bits = {
                        'R': strategy_params.get('r_bits', 2),
                        'G': strategy_params.get('g_bits', 3),
                        'B': strategy_params.get('b_bits', 4)
                    }
                else:
                    # 直接从参数中获取
                    channel_bits = {
                        'R': strategy_params.get('R', 2),
                        'G': strategy_params.get('G', 3),
                        'B': strategy_params.get('B', 4)
                    }
                
                quality = strategy_params.get('quality', 0.8)
                print(f"  通道位数: R={channel_bits['R']}, G={channel_bits['G']}, B={channel_bits['B']}")
                return self.decrypt_channel_lsb(channel_bits=channel_bits, quality=quality)
                
            elif strategy == 'smart_lsb':
                print("[自适应解密] 使用智能LSB策略")
                # 处理位数范围参数的不同格式
                if 'bit_range' in strategy_params and isinstance(strategy_params['bit_range'], dict):
                    bit_range = strategy_params['bit_range']
                elif 'min_bits' in strategy_params:
                    # 兼容旧格式
                    bit_range = {
                        'min': strategy_params.get('min_bits', 1),
                        'max': strategy_params.get('max_bits', 5)
                    }
                else:
                    # 默认值
                    bit_range = {'min': 1, 'max': 5}
                
                threshold = strategy_params.get('threshold', 0.5)
                edge_protect = strategy_params.get('edge_protect', True)
                print(f"  位数范围: {bit_range['min']}-{bit_range['max']}, 阈值: {threshold}")
                return self.decrypt_smart_lsb(
                    bit_range=bit_range,
                    threshold=threshold,
                    edge_protect=edge_protect
                )
            else:
                print(f"[自适应解密] 未知策略 '{strategy}'，使用默认简单LSB")
                return self.decrypt_simple_lsb(2, 1.0)
                
        except Exception as e:
            print(f"[自适应解密] 策略解密失败: {e}")
            import traceback
            traceback.print_exc()
            # 尝试使用默认策略
            print("[自适应解密] 尝试使用默认策略...")
            return self.decrypt_simple_lsb(2, 1.0)
    
    def decrypt(self, params: DecryptionParams) -> Optional[Image.Image]:
        """根据参数解密图像 - 增强版"""
        if params.mode == 'default':
            self.decrypted_image = self.decrypt_default_mode(
                params.mode_type or 'light',
                params.boundary or 128,
                params.resolution or 0.5,
                params.direction or False,
                params.brightness or 55
            )
        elif params.mode == 'simple_lsb':
            self.decrypted_image = self.decrypt_simple_lsb(
                params.bits or 2,
                params.strength or 1.0
            )
        elif params.mode == 'channel_lsb':
            bits = params.channel_bits or {'R': 2, 'G': 3, 'B': 4}
            self.decrypted_image = self.decrypt_channel_lsb(
                bits,
                params.quality or 0.8
            )
        elif params.mode == 'smart_lsb':
            bit_range = params.bit_range or {'min': 1, 'max': 5}
            self.decrypted_image = self.decrypt_smart_lsb(
                bit_range,
                params.threshold or 0.5,
                params.edge_protect if params.edge_protect is not None else True
            )
        elif params.mode == 'adaptive':
            # 自适应模式 - 使用完整的策略信息
            self.decrypted_image = self.decrypt_adaptive(
                threshold=params.threshold or 0.5,
                strategy=params.selected_strategy,
                strategy_params=params.strategy_params,
                decryption_guide=params.decryption_guide,
                precision=params.precision,
                priority=params.priority,
                version=params.version
            )
        else:
            print(f"未知模式: {params.mode}")
            return None
            
        return self.decrypted_image