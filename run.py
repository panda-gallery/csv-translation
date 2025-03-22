import pandas as pd
from zhipuai import ZhipuAI
import concurrent.futures
import logging
from tqdm import tqdm
import os
import re

# 配置信息
CONFIG = {
    "api_key": "",  # 替换为你的API Key
    "input_folder": "input",  # 输入文件夹
    "output_folder": "output",  # 输出文件夹
    "max_workers": 8,  # 最大线程数
    "batch_size": 100  # 每个线程处理的行数
}

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CSVTranslator:
    def __init__(self, config, input_file, output_file):
        self.config = config
        self.client = ZhipuAI(api_key=config["api_key"])
        self.df = pd.read_csv(input_file)
        self.total_rows = len(self.df)
        self.progress_bar = tqdm(total=self.total_rows, desc="翻译进度")
        self.input_file = input_file
        self.output_file = output_file

    def translate_text(self, text):
        """调用智谱AI进行翻译"""
        context = f'请将以下内容准确翻译为中文，保持格式不变：\n{text}'
        try:
            response = self.client.chat.completions.create(
                # 免费模型有：glm-4-flash, glm-4v-flash (截止至 2025/3/22
                model="glm-4v-flash",
                messages=[
                    {"role": "user", "content": context},
                ],
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"API调用失败：{str(e)}")
            return text  # 如果翻译失败，返回原文

    def process_batch(self, batch):
        """处理一批数据"""
        for index, row in batch.iterrows():
            # 翻译title
            if pd.notna(row["title"]):
                translated_title = self.translate_text(row["title"])
                self.df.at[index, "title"] = translated_title
            # 翻译text
            if pd.notna(row["text"]):
                translated_text = self.translate_text(row["text"])
                self.df.at[index, "text"] = translated_text
            self.progress_bar.update(1)

    def translate_csv(self):
        """翻译CSV文件中的text和title列"""
        batches = [self.df[i:i + self.config["batch_size"]] for i in
                   range(0, self.total_rows, self.config["batch_size"])]

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.config["max_workers"]) as executor:
            futures = [executor.submit(self.process_batch, batch) for batch in batches]
            concurrent.futures.wait(futures)

        self.progress_bar.close()

        # 保存到新的CSV文件
        self.df.to_csv(self.output_file, index=False, encoding='utf-8-sig')
        print(f"翻译完成，已保存到新的文件：{self.output_file}")


def main():
    # 创建输出文件夹（如果不存在）
    os.makedirs(CONFIG["output_folder"], exist_ok=True)

    # 获取输入文件夹中的所有CSV文件
    files = [f for f in os.listdir(CONFIG["input_folder"]) if f.endswith(".csv")]

    # 按文件名排序
    files.sort(key=lambda x: int(re.search(r'\d+', x).group()))

    # 遍历排序后的文件
    for filename in files:
        input_file = os.path.join(CONFIG["input_folder"], filename)
        output_file = os.path.join(CONFIG["output_folder"], filename)
        print(f"正在处理文件：{filename}")
        translator = CSVTranslator(CONFIG, input_file, output_file)
        translator.translate_csv()


if __name__ == "__main__":
    main()