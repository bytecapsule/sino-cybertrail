import os
import re
import jieba
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime
from collections import defaultdict

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']  # macOS 系统可用
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

class SentimentAnalyzer:
    def __init__(self):
        # 定义情绪词典
        self.sentiment_dict = {
            '乐观': [
                '乐观', '向好', '复苏', '增长', '提升', '发展',
                '机遇', '繁荣', '突破', '创新', '高涨', '信心',
                '憧憬', '希望', '上升', '成功', '胜利', '欢呼'
            ],
            '悲观': [
                '悲观', '下行', '衰退', '萧条', '危机', '风险',
                '崩溃', '暴跌', '亏损', '失败', '破产', '裁员',
                '倒闭', '亏空', '跌落', '低迷', '亏本', '困境'
            ],
            '焦虑': [
                '焦虑', '担忧', '压力', '困难', '问题', '挑战',
                '恐慌', '不安', '紧张', '惶恐', '忧心', '害怕',
                '慌乱', '恐惧', '烦躁', '痛苦', '煎熬', '失眠',
                '抑郁', '崩溃', '绝望', '无助'
            ],
            '愤怒': [
                '愤怒', '不满', '抗议', '愤懑', '怒火', '抱怨',
                '不公', '不平', '不忿', '不服', '反感', '憎恨',
                '怨恨', '仇视', '敌意', '对抗'
            ],
            '理性': [
                '理性', '客观', '分析', '思考', '研究', '规律',
                '冷静', '平和', '务实', '稳健', '审慎', '深入',
                '观察', '判断', '评估', '权衡', '思辨'
            ],
            '满意': [
                '满意', '欣慰', '称心', '舒心', '欢喜', '快乐',
                '幸福', '开心', '愉悦', '惬意', '欣喜', '感激',
                '感恩', '感动', '温暖'
            ]
        }
        
        # 定义情绪强度词权重
        self.intensity_weights = {
            '很': 1.5, '非常': 2.0, '极其': 2.5,
            '特别': 2.0, '十分': 2.0, '格外': 1.8,
            '超': 2.0, '太': 1.8, '真': 1.5
        }
        
        # 定义否定词
        self.negatives = {'不', '没', '无', '非', '莫', '勿', '未', '别', '甭', '休'}
        
        # 定义年份范围
        self.years = range(2000, 2026)
    
    def analyze_context(self, words, index, window=3):
        """分析词语上下文"""
        start = max(0, index - window)
        end = min(len(words), index + window + 1)
        context = words[start:end]
        
        # 检查否定词
        neg_count = sum(1 for w in context if w in self.negatives)
        return -1 if neg_count % 2 == 1 else 1
    
    def analyze_sentiment(self, content):
        """分析文本情绪"""
        words = jieba.lcut(content)
        sentiment_scores = defaultdict(float)
        
        for i, word in enumerate(words):
            for category, keywords in self.sentiment_dict.items():
                if word in keywords:
                    # 基础分数
                    score = 1.0
                    
                    # 检查情绪强度词
                    if i > 0 and words[i-1] in self.intensity_weights:
                        score *= self.intensity_weights[words[i-1]]
                    
                    # 检查上下文情绪反转
                    score *= self.analyze_context(words, i)
                    
                    sentiment_scores[category] += score
        
        return dict(sentiment_scores)
    
    def read_files(self, base_path):
        """读取所有年份的文章"""
        data = defaultdict(list)
        
        for year in self.years:
            year_path = os.path.join(base_path, str(year))
            if not os.path.exists(year_path):
                continue
                
            for file in os.listdir(year_path):
                if file.endswith('.md'):
                    with open(os.path.join(year_path, file), 'r', encoding='utf-8') as f:
                        content = f.read()
                        data[year].append(content)
        
        return data
    
    def generate_heatmap(self, data):
        """生成情绪热力图"""
        sentiment_matrix = []
        valid_years = []
        
        for year in self.years:
            if year not in data:
                continue
                
            valid_years.append(year)
            year_scores = defaultdict(float)
            total_articles = len(data[year])
            
            for content in data[year]:
                scores = self.analyze_sentiment(content)
                for category, score in scores.items():
                    year_scores[category] += score
            
            # 标准化得分
            normalized_scores = [year_scores[cat]/total_articles for cat in self.sentiment_dict.keys()]
            sentiment_matrix.append(normalized_scores)
        
        # 创建热力图
        plt.figure(figsize=(15, 10))
        sns.heatmap(
            sentiment_matrix,
            xticklabels=list(self.sentiment_dict.keys()),
            yticklabels=valid_years,
            cmap='RdYlBu_r',
            center=0,
            annot=True,
            fmt='.2f'
        )
        
        plt.title('社会情绪热力图 (2000-2025)', fontsize=14)
        plt.ylabel('年份', fontsize=12)
        plt.xlabel('情绪类别', fontsize=12)
        
        plt.xticks(fontsize=10, rotation=45)
        plt.yticks(fontsize=10)
        
        plt.tight_layout()
        plt.savefig('sentiment_heatmap.png', dpi=300, bbox_inches='tight')
        plt.close()

def main():
    base_path = '/Users/charlie_cao/Github/charlie-fox/sino-cybertrail'
    analyzer = SentimentAnalyzer()
    
    print("开始读取数据...")
    data = analyzer.read_files(base_path)
    
    print("开始生成热力图...")
    analyzer.generate_heatmap(data)
    
    print("热力图生成完成！")

if __name__ == "__main__":
    main()