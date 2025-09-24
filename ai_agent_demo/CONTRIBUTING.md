# 贡献指南

感谢您对Agent Demo项目的关注！我们欢迎并感谢所有形式的贡献，无论是代码提交、问题报告、文档改进还是功能建议。

## 行为准则

请尊重所有社区成员，保持友好和建设性的交流氛围。

## 开始贡献

### 报告问题

如果您发现了Bug或者有新功能的建议，请在GitHub上创建一个新的Issue。在创建Issue时，请提供尽可能详细的信息：

- 清晰描述问题或建议
- 如果是Bug，请提供复现步骤、预期行为和实际行为
- 如有可能，附上截图或错误日志
- 说明您的环境信息（操作系统、Python版本等）

### 提交代码

1. **Fork项目仓库**
   在GitHub上点击"Fork"按钮创建您自己的项目副本。

2. **克隆仓库**
   ```bash
   git clone https://github.com/YOUR-USERNAME/agent-demo.git
   cd agent-demo
   ```

3. **创建分支**
   为您的修改创建一个新的分支：
   ```bash
   git checkout -b feature/your-feature-name
   # 或者
   git checkout -b fix/your-bugfix-name
   ```

4. **安装开发依赖**
   ```bash
   pip install -r requirements.txt
   ```

5. **进行修改**
   - 遵循项目的代码风格和命名规范
   - 为新功能添加适当的测试
   - 更新相关文档

6. **提交更改**
   ```bash
   git add .
   git commit -m "简明扼要的提交信息"
   ```
   提交信息应清晰描述您的更改内容和目的。

7. **推送到远程分支**
   ```bash
   git push origin feature/your-feature-name
   ```

8. **创建Pull Request**
   在GitHub上导航到您的Fork，点击"Pull request"按钮，填写详细的描述信息，说明您的更改内容和目的。

## 代码规范

- 遵循PEP 8代码规范
- 使用4个空格进行缩进（不使用Tab）
- 每行不超过100个字符
- 为类和函数添加文档字符串
- 关键逻辑添加注释说明

## 测试

在提交代码前，请确保您的修改通过了现有测试，并为新功能添加适当的测试。

## 文档

- 对于新功能，请更新相关文档以反映这些变化
- 确保文档语言清晰、准确，避免使用模糊或歧义的表述

## 版本控制

- 主分支（main）用于稳定版本
- 开发分支（develop）用于新功能开发
- 功能分支（feature/*）用于具体功能的开发
- 修复分支（fix/*）用于Bug修复

## 联系方式

如有任何问题或需要帮助，请联系项目维护者。

再次感谢您的贡献！