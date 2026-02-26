#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
BPM分析核心模块
功能：全局BPM检测 + 多段滑动窗口BPM分析 + 节拍格式化
"""

import os
import sys
import librosa
import numpy as np

class BPMAnalyzer:
    """BPM分析器 - 同时计算全局和局部BPM"""
    
    def __init__(self, window_sec=10.0, hop_sec=5.0):
        """
        初始化分析器
        
        参数:
            window_sec: 滑动窗口长度（秒）
            hop_sec: 窗口移动步长（秒）
        """
        self.window_sec = window_sec
        self.hop_sec = hop_sec
    
    def find_ffmpeg(self):
        """
        自动查找FFmpeg可执行文件
        支持：开发环境、打包后的onedir模式
        """
        # 获取基础路径
        if getattr(sys, 'frozen', False):
            # 打包后的程序 - exe所在目录
            base_path = os.path.dirname(sys.executable)
        else:
            # 开发环境 - 当前文件所在目录
            base_path = os.path.dirname(os.path.abspath(__file__))
        
        # 候选路径列表
        candidates = [
            os.path.join(base_path, 'ffmpeg.exe'),           # exe同目录
            os.path.join(base_path, 'ffmpeg', 'ffmpeg.exe'), # ffmpeg子文件夹
        ]
        
        # 查找存在的ffmpeg
        for path in candidates:
            if os.path.exists(path) and os.access(path, os.X_OK):
                return path
        
        # 都没找到，返回默认（使用系统PATH）
        return 'ffmpeg'
    
    def analyze(self, audio_path):
        """
        分析音频文件，返回所有结果
        
        参数:
            audio_path: 音频文件路径
            
        返回:
            dict: 包含所有分析结果的字典
        """
        # 设置FFmpeg环境变量
        ffmpeg_path = self.find_ffmpeg()
        if ffmpeg_path != 'ffmpeg':
            ffmpeg_dir = os.path.dirname(ffmpeg_path)
            os.environ['PATH'] = ffmpeg_dir + os.pathsep + os.environ.get('PATH', '')
            print(f"使用FFmpeg: {ffmpeg_path}")
        
        # 1. 加载音频
        print(f"正在加载音频: {audio_path}")
        audio, sr = librosa.load(audio_path, sr=22050, mono=True)
        duration = len(audio) / sr
        print(f"加载成功 - 采样率: {sr}Hz, 时长: {duration:.1f}秒")
        
        # 2. 计算全局BPM和所有节拍
        print("正在计算全局BPM...")
        global_tempo, global_beats = librosa.beat.beat_track(
            y=audio, 
            sr=sr, 
            units='time'
        )
        print(f"全局BPM: {global_tempo:.1f}")
        
        # 3. 滑动窗口分析
        print("正在进行多段分析...")
        window_samples = int(self.window_sec * sr)
        hop_samples = int(self.hop_sec * sr)
        
        times = []      # 窗口中心时间
        bpms = []       # 窗口BPM
        beats_list = [] # 窗口内的节拍
        
        window_count = 0
        for start in range(0, len(audio) - window_samples + 1, hop_samples):
            end = start + window_samples
            window = audio[start:end]
            
            # 计算窗口BPM
            tempo, beats = librosa.beat.beat_track(
                y=window, 
                sr=sr, 
                units='time'
            )
            
            # 转换为全局时间
            global_beats_window = [t + start/sr for t in beats]
            
            times.append((start + window_samples//2) / sr)
            bpms.append(float(tempo))
            beats_list.append(global_beats_window)
            
            window_count += 1
            if window_count % 5 == 0:
                print(f"已分析 {window_count} 个窗口...")
        
        print(f"分析完成，共 {window_count} 个窗口")
        
        # 返回所有结果
        return {
            'global_tempo': float(global_tempo),
            'global_beats': global_beats.tolist(),
            'window_times': times,
            'window_bpms': bpms,
            'window_beats': beats_list,
            'audio': audio,
            'sr': sr,
            'duration': duration
        }
    
    def format_beat_info(self, beats, time_signature=(4,4), max_count=4):
        """
        格式化节拍信息为 [小节,分子,分母]
        
        参数:
            beats: 节拍时间列表
            time_signature: 拍号，默认(4,4)表示4/4拍
            max_count: 最多返回多少个节拍信息
            
        返回:
            list: 格式化后的节拍信息列表
        """
        if not beats:
            return ["无节拍"]
        
        beats_per_bar = time_signature[0]  # 每小节拍数
        result = []
        
        for i, beat_time in enumerate(beats[:max_count]):
            bar = i // beats_per_bar + 1           # 第几小节
            beat_in_bar = i % beats_per_bar + 1    # 小节内的第几拍
            result.append(f"[{bar},{beat_in_bar},{time_signature[1]}]")
        
        if len(beats) > max_count:
            result.append("...")
        
        return result
    
    def get_beat_summary(self, result):
        """
        生成节拍摘要文本
        
        参数:
            result: analyze()返回的结果字典
            
        返回:
            str: 格式化的摘要文本
        """
        lines = []
        lines.append("=" * 60)
        lines.append("BPM分析结果")
        lines.append("=" * 60)
        lines.append(f"全局BPM: {result['global_tempo']:.1f}")
        lines.append(f"总节拍数: {len(result['global_beats'])}")
        lines.append(f"音频时长: {result['duration']:.1f}秒")
        lines.append("=" * 60)
        lines.append("多段BPM分析:")
        lines.append(f"{'窗口时间':<12}{'BPM':<8}节拍信息")
        lines.append("-" * 60)
        
        for t, bpm, beats in zip(
            result['window_times'], 
            result['window_bpms'],
            result['window_beats']
        ):
            beat_info = self.format_beat_info(beats, (4,4), 4)
            lines.append(f"{t:6.1f}秒    {bpm:5.1f}    {', '.join(beat_info)}")
        
        lines.append("=" * 60)
        lines.append("分析完成！")
        
        return "\n".join(lines)