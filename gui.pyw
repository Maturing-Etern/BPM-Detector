#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
BPM检测工具 - 图形界面版
运行时不显示控制台窗口 (.pyw后缀)
"""

import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import threading
import os
import sys
from analyzer import BPMAnalyzer

class BPMApp:
    def __init__(self, root):
        self.root = root
        self.root.title("BPM检测器 v2.0")
        self.root.geometry("900x700")
        
        # 设置窗口图标
        self.set_icon()
        
        # 设置窗口最小尺寸
        self.root.minsize(700, 500)
        
        # 变量
        self.file_path = tk.StringVar()
        self.analyzer = BPMAnalyzer(window_sec=10.0, hop_sec=5.0)
        
        # 创建界面
        self.create_widgets()
        
        # 居中显示
        self.center_window()
        
        # 绑定关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def set_icon(self):
        """设置窗口图标"""
        try:
            # 获取图标路径
            if getattr(sys, 'frozen', False):
                base_path = os.path.dirname(sys.executable)
            else:
                base_path = os.path.dirname(os.path.abspath(__file__))
            
            icon_path = os.path.join(base_path, 'icon.ico')
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except Exception:
            pass  # 图标不是必须的
    
    def center_window(self):
        """使窗口居中"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        """创建界面组件"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill='both', expand=True)
        
        # ===== 顶部：文件选择 =====
        file_frame = ttk.LabelFrame(main_frame, text="音频文件", padding="10")
        file_frame.pack(fill='x', pady=(0, 15))
        
        # 文件路径显示
        ttk.Entry(file_frame, textvariable=self.file_path, width=60).pack(side='left', padx=(0, 5))
        
        # 按钮框架
        btn_frame = ttk.Frame(file_frame)
        btn_frame.pack(side='left')
        
        self.btn_browse = ttk.Button(btn_frame, text="浏览...", command=self.select_file, width=10)
        self.btn_browse.pack(side='left', padx=2)
        
        self.btn_analyze = ttk.Button(btn_frame, text="开始分析", command=self.start_analysis, width=10)
        self.btn_analyze.pack(side='left', padx=2)
        
        # ===== 中间：结果显示 =====
        result_frame = ttk.LabelFrame(main_frame, text="分析结果", padding="10")
        result_frame.pack(fill='both', expand=True)
        
        # 创建文本框和滚动条
        text_frame = ttk.Frame(result_frame)
        text_frame.pack(fill='both', expand=True)
        
        # 文本框
        self.result_text = tk.Text(
            text_frame, 
            height=20, 
            font=('Consolas', 10),
            wrap='word',
            relief='sunken',
            borderwidth=1,
            bg='#ffffff',
            fg='#333333'
        )
        self.result_text.pack(side='left', fill='both', expand=True)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(text_frame, orient='vertical', command=self.result_text.yview)
        scrollbar.pack(side='right', fill='y')
        self.result_text.config(yscrollcommand=scrollbar.set)
        
        # ===== 底部：状态栏 =====
        self.status_var = tk.StringVar()
        self.status_var.set("就绪")
        status_bar = ttk.Label(
            main_frame, 
            textvariable=self.status_var,
            relief='sunken',
            anchor='w',
            padding=(5, 2)
        )
        status_bar.pack(fill='x', pady=(10, 0))
        
        # 配置文本样式
        self.result_text.tag_config('title', font=('Consolas', 12, 'bold'), foreground='#2c3e50')
        self.result_text.tag_config('highlight', foreground='#27ae60', font=('Consolas', 10, 'bold'))
        self.result_text.tag_config('normal', font=('Consolas', 10))
        self.result_text.tag_config('error', foreground='#e74c3c', font=('Consolas', 10, 'bold'))
        
        # 显示欢迎信息
        self.show_welcome()
    
    def show_welcome(self):
        """显示欢迎信息"""
        welcome = [
            "=" * 60,
            "欢迎使用 BPM检测器 v2.0",
            "=" * 60,
            "",
            "使用说明：",
            "1. 点击【浏览】选择音频文件",
            "2. 点击【开始分析】等待结果",
            "3. 分析结果将显示在下方",
            "",
            "支持格式：MP3、WAV、FLAC、M4A、OGG等",
            "分析参数：窗口10秒，步长5秒",
            "",
            "=" * 60
        ]
        for line in welcome:
            self.result_text.insert(tk.END, line + "\n", 'normal')
    
    def select_file(self):
        """选择音频文件"""
        filename = filedialog.askopenfilename(
            title="选择音频文件",
            filetypes=[
                ("音频文件", "*.mp3 *.wav *.flac *.m4a *.ogg *.aac"),
                ("MP3文件", "*.mp3"),
                ("WAV文件", "*.wav"),
                ("FLAC文件", "*.flac"),
                ("所有文件", "*.*")
            ]
        )
        if filename:
            self.file_path.set(filename)
            self.status_var.set(f"已选择: {os.path.basename(filename)}")
    
    def start_analysis(self):
        """开始分析"""
        if not self.file_path.get():
            messagebox.showwarning("提示", "请先选择一个音频文件")
            return
        
        # 检查文件是否存在
        if not os.path.exists(self.file_path.get()):
            messagebox.showerror("错误", "文件不存在")
            return
        
        # 清空之前的结果
        self.result_text.delete(1.0, tk.END)
        
        # 禁用按钮，避免重复点击
        self.btn_browse.config(state='disabled')
        self.btn_analyze.config(state='disabled')
        self.status_var.set("正在分析中，请稍候...")
        
        # 在新线程中执行分析
        threading.Thread(target=self.analyze, daemon=True).start()
    
    def analyze(self):
        """执行分析（后台线程）"""
        try:
            file_path = self.file_path.get()
            file_name = os.path.basename(file_path)
            
            # 显示开始信息
            self.update_text("=" * 60 + "\n", 'title')
            self.update_text(f"开始分析: {file_name}\n", 'title')
            self.update_text("=" * 60 + "\n\n", 'title')
            
            # 执行分析
            result = self.analyzer.analyze(file_path)
            
            # 显示结果
            self.update_text(f"📁 文件: {file_name}\n", 'normal')
            self.update_text(f"⏱️  时长: {result['duration']:.1f}秒\n", 'normal')
            self.update_text(f"🎵 全局BPM: ", 'normal')
            self.update_text(f"{result['global_tempo']:.1f}\n", 'highlight')
            self.update_text(f"🎯 总节拍数: ", 'normal')
            self.update_text(f"{len(result['global_beats'])}\n\n", 'highlight')
            
            self.update_text("=" * 60 + "\n", 'title')
            self.update_text("多段BPM分析\n", 'title')
            self.update_text("=" * 60 + "\n", 'title')
            self.update_text(f"{'窗口时间':<12}{'BPM':<8}节拍信息\n", 'normal')
            self.update_text("-" * 60 + "\n", 'normal')
            
            # 显示每个窗口的结果
            for t, bpm, beats in zip(
                result['window_times'], 
                result['window_bpms'],
                result['window_beats']
            ):
                beat_info = self.analyzer.format_beat_info(beats, (4,4), 4)
                line = f"{t:6.1f}秒    {bpm:5.1f}    {', '.join(beat_info)}\n"
                self.update_text(line, 'normal')
            
            self.update_text("\n" + "=" * 60 + "\n", 'title')
            self.update_text("✅ 分析完成！\n", 'highlight')
            self.update_text("=" * 60 + "\n", 'title')
            
            self.status_var.set("分析完成")
            
        except Exception as e:
            error_msg = f"❌ 分析失败: {str(e)}"
            self.update_text("\n" + error_msg + "\n", 'error')
            self.status_var.set("分析失败")
            print(f"错误详情: {e}")  # 打印到控制台便于调试
        
        finally:
            # 重新启用按钮
            self.root.after(0, lambda: self.btn_browse.config(state='normal'))
            self.root.after(0, lambda: self.btn_analyze.config(state='normal'))
    
    def update_text(self, content, tag=None):
        """在主线程中更新文本框"""
        self.root.after(0, lambda: self._do_update_text(content, tag))
    
    def _do_update_text(self, content, tag):
        """实际更新文本框"""
        if tag:
            self.result_text.insert(tk.END, content, tag)
        else:
            self.result_text.insert(tk.END, content)
        self.result_text.see(tk.END)  # 自动滚动到底部
    
    def on_closing(self):
        """关闭窗口时的处理"""
        if messagebox.askokcancel("退出", "确定要退出吗？"):
            self.root.destroy()

def main():
    """主函数"""
    root = tk.Tk()
    app = BPMApp(root)
    root.mainloop()

if __name__ == '__main__':
    main()