import pandas as pd
import numpy as np
import jieba
import torch
import pandas as pd
from transformers import BertTokenizer, BertForSequenceClassification
from torch.utils.data import Dataset, DataLoader
from sklearn.model_selection import train_test_split
from torch.optim import AdamW
from tqdm import tqdm
import jieba
from collections import Counter
file1="ADHD_set01-ljn.xlsx"
file2="ADHD_set02-gsy.xlsx"
file3="ADHD_set03-wxr.xlsx"
df1=pd.read_excel(file1)
df2=pd.read_excel(file2)
df3=pd.read_excel(file3)
# 合并df1, df2, df3
combined_df = pd.concat([df1, df2, df3], ignore_index=True)
combined_df["tag"] = combined_df["tag"].fillna(0) 
combined_df["tag"] = combined_df["tag"].astype(int) 
# 筛选出tag为1的所有行
filtered_df = combined_df[combined_df['tag'] == 1]

# 输出结果
#print(filtered_df)


# 1. 数据预处理：使用 jieba 分词
def tokenize_text(text):
    return " ".join(jieba.cut(text))

# 假设 combined_df 是你的 DataFrame，包含 "weibo_content" 和 "tag" 列
# combined_df = pd.read_csv("your_data.csv")  # 如果是 CSV 文件
combined_df["tokenized_text"] = combined_df["weibo_content"].astype(str).apply(tokenize_text)

# 2. 加载 BERT 的 Tokenizer
tokenizer = BertTokenizer.from_pretrained("bert-base-chinese")

# 3. 定义数据集类
class WeiboDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_length=128):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        text = self.texts[idx]
        label = self.labels[idx]
        encoding = self.tokenizer(
            text,
            truncation=True,
            padding="max_length",
            max_length=self.max_length,
            return_tensors="pt",
        )
        return {
            "input_ids": encoding["input_ids"].squeeze(0),  # 去掉 batch 维度
            "attention_mask": encoding["attention_mask"].squeeze(0),
            "label": torch.tensor(label, dtype=torch.long),
        }

# 4. 划分训练集和验证集
train_texts, val_texts, train_labels, val_labels = train_test_split(
    combined_df["tokenized_text"].tolist(),
    combined_df["tag"].tolist(),
    test_size=0.2,
    random_state=42,
)

# 创建 Dataset 和 DataLoader
train_dataset = WeiboDataset(train_texts, train_labels, tokenizer)
val_dataset = WeiboDataset(val_texts, val_labels, tokenizer)

train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=16, shuffle=False)

# 5. 加载 BERT 模型
device = torch.device("cpu")
model = BertForSequenceClassification.from_pretrained("bert-base-chinese", num_labels=2).to(device)

# 6. 定义优化器和损失函数
optimizer = AdamW(model.parameters(), lr=2e-5)
loss_fn = torch.nn.CrossEntropyLoss()


# 7. 训练函数
def train(model, train_loader, val_loader, optimizer, loss_fn, epochs=3):
    for epoch in range(epochs):
        model.train()
        total_loss = 0
        correct, total = 0, 0

        for batch in tqdm(train_loader, desc=f"Epoch {epoch + 1}/{epochs}"):
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["label"].to(device)

            optimizer.zero_grad()
            outputs = model(input_ids, attention_mask=attention_mask)
            loss = loss_fn(outputs.logits, labels)
            loss.backward()
            optimizer.step()

            total_loss += loss.item()
            preds = torch.argmax(outputs.logits, dim=1)
            correct += (preds == labels).sum().item()
            total += labels.size(0)

        train_accuracy = correct / total
        print(f"Epoch {epoch + 1}/{epochs}, Loss: {total_loss:.4f}, Train Accuracy: {train_accuracy:.4f}")

        # 验证集评估
        model.eval()
        correct, total = 0, 0
        with torch.no_grad():
            for batch in val_loader:
                input_ids = batch["input_ids"].to(device)
                attention_mask = batch["attention_mask"].to(device)
                labels = batch["label"].to(device)

                outputs = model(input_ids, attention_mask=attention_mask)
                preds = torch.argmax(outputs.logits, dim=1)
                correct += (preds == labels).sum().item()
                total += labels.size(0)

        val_accuracy = correct / total
        print(f"Validation Accuracy: {val_accuracy:.4f}")

# 8. 开始训练
train(model, train_loader, val_loader, optimizer, loss_fn, epochs=3)



