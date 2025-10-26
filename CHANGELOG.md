# 更新日志

本项目的所有重要更改都会记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [1.0.0] - 2025-10-27

### 新增
- ✨ 完整的 WebAuthn/Passkey 实现
- 🚀 自动配置脚本 (`setup.py`)
- 🌐 动态配置系统，无需手动修改代码
- 📱 支持 iOS Face ID/Touch ID
- 🔐 支持 Android 指纹识别
- 💻 支持 Windows Hello
- 🔑 支持硬件安全密钥
- 📖 完整的文档和 FAQ
- 🛠️ 一键启动脚本

### 功能
- 用户注册和登录
- 多凭证支持
- 自动 SSL 证书生成
- mDNS 域名支持
- 防火墙自动配置
- 实时错误处理和提示

### 技术栈
- Python 3.7+ + Flask
- py_webauthn 2.x
- 原生 JavaScript (无框架)
- HTML5 + CSS3

### 文档
- README.md - 项目概述
- docs/快速部署指南.md - 详细部署说明
- docs/FAQ.md - 常见问题
- docs/技术说明.md - 技术细节
- CONTRIBUTING.md - 贡献指南

---

## [未发布]

### 计划中
- [ ] 数据库持久化支持
- [ ] 用户管理界面
- [ ] Docker 支持
- [ ] Linux/macOS 支持
- [ ] 多语言支持
- [ ] 日志系统
- [ ] 单元测试

### 正在考虑
- [ ] QR 码登录
- [ ] 跨设备 Passkey 同步演示
- [ ] Resident Key 支持
- [ ] Attestation 验证
- [ ] 会话管理

---

## 版本说明

### 版本号格式: MAJOR.MINOR.PATCH

- **MAJOR**: 重大不兼容更改
- **MINOR**: 向后兼容的功能新增
- **PATCH**: 向后兼容的问题修正

### 标签说明

- `Added` - 新功能
- `Changed` - 现有功能的更改
- `Deprecated` - 即将废弃的功能
- `Removed` - 已移除的功能
- `Fixed` - Bug 修复
- `Security` - 安全相关更新
