# 贡献指南

感谢你对本项目的关注！我们欢迎各种形式的贡献。

## 🤝 如何贡献

### 报告 Bug

如果你发现了 Bug，请：

1. 检查 [Issues](https://github.com/你的用户名/passkey-webauthn-demo/issues) 是否已有相关报告
2. 如果没有，创建新 Issue，包含：
   - 清晰的标题
   - 详细的描述
   - 复现步骤
   - 期望行为 vs 实际行为
   - 环境信息（OS、Python 版本、浏览器等）
   - 截图或日志（如果有）

### 提出新功能

1. 先在 Issues 中讨论你的想法
2. 说明功能的用途和价值
3. 等待维护者反馈

### 提交代码

1. **Fork 本仓库**

2. **创建特性分支**
   ```bash
   git checkout -b feature/AmazingFeature
   ```

3. **进行修改**
   - 遵循代码风格
   - 添加必要的注释
   - 更新文档（如果需要）

4. **测试你的修改**
   - 确保现有功能正常
   - 测试新功能

5. **提交更改**
   ```bash
   git commit -m 'Add some AmazingFeature'
   ```

6. **推送到你的 Fork**
   ```bash
   git push origin feature/AmazingFeature
   ```

7. **创建 Pull Request**
   - 清晰描述你的更改
   - 引用相关 Issue
   - 等待审核

## 📝 代码规范

### Python

- 遵循 [PEP 8](https://pep8.org/)
- 使用有意义的变量名
- 添加类型提示（Python 3.7+）
- 添加文档字符串

```python
def example_function(param: str) -> bool:
    """
    函数功能描述
    
    Args:
        param: 参数描述
        
    Returns:
        返回值描述
    """
    return True
```

### JavaScript

- 使用 ES6+ 语法
- 使用 `const` 和 `let`，避免 `var`
- 添加注释说明复杂逻辑

```javascript
/**
 * 函数功能描述
 * @param {string} param - 参数描述
 * @returns {boolean} 返回值描述
 */
function exampleFunction(param) {
    return true;
}
```

### 提交信息

使用清晰的提交信息：

```
feat: 添加新功能
fix: 修复 bug
docs: 更新文档
style: 代码格式调整
refactor: 重构代码
test: 添加测试
chore: 构建/工具链更新
```

## 🧪 测试

- 在提交前测试你的代码
- 测试不同的浏览器和设备
- 确保向后兼容

## 📚 文档

如果你的更改影响用户使用：

- 更新 README.md
- 更新相关文档
- 添加示例（如果需要）

## ⚖️ 许可证

提交代码即表示你同意将代码以 MIT 许可证发布。

## 💬 社区

- 保持友好和尊重
- 乐于帮助他人
- 接受建设性反馈

感谢你的贡献！🎉
