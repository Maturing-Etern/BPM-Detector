import argparse
from analyzer import BPMAnalyzer
import json

def main():
    parser = argparse.ArgumentParser(description='BPM检测工具')
    parser.add_argument('file', help='音频文件路径')
    parser.add_argument('--window', type=float, default=10.0, help='窗口长度(秒)')
    parser.add_argument('--hop', type=float, default=5.0, help='步长(秒)')
    args = parser.parse_args()
    
    # 分析
    analyzer = BPMAnalyzer(window_sec=args.window, hop_sec=args.hop)
    result = analyzer.analyze(args.file)
    
    # 打印结果
    print(f"\n{'='*50}")
    print(f"文件: {args.file}")
    print(f"全局BPM: {result['global_tempo']:.1f}")
    print(f"总节拍数: {len(result['global_beats'])}")
    print(f"{'='*50}")
    
    print("\n多段BPM分析:")
    print("窗口时间\tBPM\t节拍信息")
    print("-" * 50)
    
    for i, (t, bpm, beats) in enumerate(zip(
        result['window_times'], 
        result['window_bpms'],
        result['window_beats']
    )):
        # 格式化前3个节拍作为示例
        beat_display = analyzer.format_beat_info(beats[:3], (4,4))
        print(f"{t:6.1f}秒\t{bpm:5.1f}\t{', '.join(beat_display)}...")

if __name__ == '__main__':
    main()