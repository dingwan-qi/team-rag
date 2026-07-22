# 文档处理和向量知识库说明

## 支持格式

- PDF：通过 PyMuPDF 解析。
- DOCX：通过 python-docx 解析。
- TXT：UTF-8 文本解析。
- Markdown：按文本解析，并识别标题作为章节元数据。

## 流程

```text
上传文件 -> 重复检测 -> 保存文件 -> 解析文本 -> 清洗 -> 分块 -> 元数据 -> Embedding -> 向量库
```

## 向量库

优先使用 ChromaDB。当前环境未安装 ChromaDB 时，`VectorRetriever` 自动降级到 JSON 哈希向量库，索引文件位于 `data/chroma/index.json`。

## 异常处理

- 空文件：返回明确错误。
- 不支持类型：返回明确错误。
- 重复文件：复用已有索引，不重复写入。
- PDF/DOCX 缺少依赖：返回解析失败提示。

