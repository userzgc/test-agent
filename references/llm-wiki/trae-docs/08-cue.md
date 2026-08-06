# CUE 智能编程助手

> 来源：https://docs.trae.cn/ide/cue

## 是什么
CUE（Context Understanding Engine）是 Trae 的智能编程工具，在编辑器内实时提供代码建议。

## 核心功能

### 1. 代码补全
基于上下文分析，实时预测和续写代码片段，支持多行修改。

### 2. 修改点预测
预测当前修改会影响的代码位置，支持修改点跳转。

### 3. 智能导入
在 Python、TypeScript、Golang 项目中智能识别并导入依赖模块。

### 4. 智能重命名
在 Python、TypeScript、Golang 项目中智能识别并提供变量和函数名称修改建议，支持跨文件级别。

## 使用
- 编辑代码时自动激活
- Tab 接受建议
- 连续 Tab 提升效率
- 快捷键可自定义（Cue 预览功能快捷键）

## 最佳实践
- 写出函数签名后让 CUE 补全实现
- 修改一个变量后用修改点预测查看影响范围
- 重命名时用智能重命名避免遗漏
- 智能导入减少手动 import

## 支持的语言
- Python
- TypeScript
- Golang
- JavaScript
- HTML/CSS
- Java
- Kotlin
- C
- Rust
- C++
- 等主流语言
