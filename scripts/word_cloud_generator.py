import os
import jieba
import numpy as np
from collections import defaultdict
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from PIL import Image
import matplotlib.font_manager as fm

class WordCloudGenerator:
    def __init__(self):
        # 设置停用词
        self.stop_words = set([
            '的', '了', '和', '是', '就', '都', '而', '及', '与', '着',
            '或', '一个', '没有', '我们', '你们', '他们', '它们', '这个',
            '那个', '这些', '那些', '一些', '有些', '什么', '这样', '那样',
            '如此', '只是', '但是', '不过', '然后', '可以', '这', '那',
            '也', '在', '中', '为', '以', '及', '等', '能', '要', '会'
        ])
        
        # 设置中文字体
        # 尝试多个可能的字体路径
        possible_fonts = [
            '/System/Library/Fonts/PingFang.ttc',
            '/System/Library/Fonts/STHeiti Light.ttc',
            '/System/Library/Fonts/STHeiti Medium.ttc',
            '/Library/Fonts/Arial Unicode.ttf',
            '/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf',  # Linux
            'C:/Windows/Fonts/simhei.ttf',  # Windows
            'C:/Windows/Fonts/msyh.ttf'     # Windows
        ]
        
        # 查找可用的字体
        self.font_path = None
        for font in possible_fonts:
            if os.path.exists(font):
                self.font_path = font
                break
        
        if self.font_path is None:
            # 如果没有找到预定义的字体，尝试使用matplotlib的字体
            try:
                font_paths = fm.findSystemFonts()
                for font in font_paths:
                    try:
                        if any(name in font.lower() for name in ['ping', 'hei', 'micro', 'yuan', 'gothic']):
                            self.font_path = font
                            break
                    except:
                        continue
            except:
                pass
        
        if self.font_path is None:
            raise ValueError("未找到可用的中文字体，请手动指定字体路径")

        self.all_wordclouds = {}

    def read_files(self, base_path, year):
        """读取指定年份的所有文章"""
        texts = []
        year_path = os.path.join(base_path, str(year))
        
        if not os.path.exists(year_path):
            return texts
            
        for file in os.listdir(year_path):
            if file.endswith('.md'):
                with open(os.path.join(year_path, file), 'r', encoding='utf-8') as f:
                    texts.append(f.read())
        
        return texts
        
    def process_texts(self, texts):
        """处理文本并统计词频"""
        word_freq = defaultdict(int)
        
        for text in texts:
            words = jieba.lcut(text)
            for word in words:
                if len(word) > 1 and word not in self.stop_words:
                    word_freq[word] += 1
        
        return word_freq
        
    def generate_wordcloud(self, word_freq, year):
        """生成词云图并保存对象"""
        wc = WordCloud(
            font_path=self.font_path,
            width=800,  # 调整单个词云的大小
            height=500,
            background_color='white',
            max_words=100,
            max_font_size=100,
            min_font_size=10,
            random_state=42
        )
        
        # 生成词云并保存
        wc.generate_from_frequencies(word_freq)
        self.all_wordclouds[year] = wc
        
    def create_combined_visualization(self):
        """创建组合可视化"""
        if not self.all_wordclouds:
            print("没有可用的词云数据！")
            return
            
        # 计算网格布局
        years = sorted(self.all_wordclouds.keys())
        n_years = len(years)
        n_cols = 5  # 每行显示5个
        n_rows = (n_years + n_cols - 1) // n_cols
        
        # 创建大图
        fig, axes = plt.subplots(n_rows, n_cols, 
                                figsize=(20, 4*n_rows),
                                constrained_layout=True)
        fig.suptitle('历年关键词云图 (2000-2025)', fontsize=24, y=1.02)
        
        # 将axes转换为一维数组以便操作
        axes = axes.flatten() if n_rows > 1 else [axes]
        
        # 绘制每年的词云
        for idx, year in enumerate(years):
            if idx < len(axes):
                wc = self.all_wordclouds[year]
                axes[idx].imshow(wc, interpolation='bilinear')
                axes[idx].axis('off')
                axes[idx].set_title(f'{year}年', fontsize=16, pad=10)
        
        # 隐藏空白子图
        for idx in range(len(years), len(axes)):
            axes[idx].axis('off')
        
        # 保存组合图
        output_dir = '/Users/charlie_cao/Github/charlie-fox/sino-cybertrail/word_clouds'
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        plt.savefig(os.path.join(output_dir, 'combined_wordclouds.png'),
                    dpi=300, bbox_inches='tight')
        plt.close()

def main():
    base_path = '/Users/charlie_cao/Github/charlie-fox/sino-cybertrail'
    generator = WordCloudGenerator()
    
    # 生成所有年份的词云
    for year in range(2000, 2026):
        print(f"正在处理 {year} 年的数据...")
        texts = generator.read_files(base_path, year)
        
        if not texts:
            print(f"{year} 年没有找到文章，跳过...")
            continue
        
        word_freq = generator.process_texts(texts)
        generator.generate_wordcloud(word_freq, year)
        print(f"{year} 年的词云已生成！")
    
    # 创建组合可视化
    print("正在生成组合词云图...")
    generator.create_combined_visualization()
    print("组合词云图已生成！")

if __name__ == "__main__":
    main()