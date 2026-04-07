---
description: 分析台股除權息後的回填狀況，生成完整報告。用法：/stock-dividend:analyze <股票代號> <年份>，例如 /stock-dividend:analyze 2330 2024
argument-hint: <股票代號> <年份>
---

請使用 @dividend-recovery-analyst 子代理人，分析以下台股的除權息回填狀況：

股票代號與參數：$ARGUMENTS

子代理人將自動：
1. 查詢指定年份的除權息紀錄
2. 判斷每次除息後是否在當天或一週內回填
3. 生成完整的 Markdown 分析報告
