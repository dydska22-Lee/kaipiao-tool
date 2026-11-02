# 开票导入模板小工具

给代账公司批量开票用的小工具：识别图片 / PDF / Excel 单据，提取品名、规格、单位、数量、单价、金额，
自动匹配商品税收分类编码，生成广东电子税务局「发票开具项目信息导入模板」。

- 形态：本地网页版。exe 双击启动后在本机浏览器里使用，识别全部在本地完成，发票数据不上传。
- OCR：RapidOCR（PaddleOCR 模型家族 onnxruntime 版）。
- 编码库：4205 条商品和服务税收分类编码内置；查不到的可一键跳转百望智能赋码。
- 打包：`pyinstaller kaipiao.spec`（在 Windows 上运行，见 `.github/workflows/build.yml`）。
