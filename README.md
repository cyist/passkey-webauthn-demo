# Passkey WebAuthn 测试项目

一个**零配置**的 WebAuthn/Passkey 演示项目，支持在本地网络中快速部署和测试。

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)](https://www.microsoft.com/windows)

## ✨ 特性

- 🚀 **一键部署** - 运行一个命令即可完成所有配置
- 🔧 **自动配置** - 自动检测 hostname、生成证书、配置防火墙
- 📱 **跨平台测试** - 支持 iOS Face ID、Touch ID 和 Android 指纹识别
- 🌐 **局域网访问** - 使用 mDNS 域名，无需手动配置 IP
- 🔐 **标准实现** - 基于 W3C WebAuthn 标准和 FIDO2 协议
- 💼 **便携式** - 同一份代码可在任意 Windows 电脑上使用

## 📋 系统要求

- **操作系统**: Windows 10/11
- **Python**: 3.7 或更高版本
- **网络**: 测试设备需在同一局域网
- **权限**: 配置防火墙需要管理员权限（可选）

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/你的用户名/passkey-webauthn-demo.git
cd passkey-webauthn-demo
```

### 2. 自动配置

```powershell
python setup.py
```

**配置脚本会自动:**
- ✅ 检测本机 hostname
- ✅ 生成 SSL 自签名证书
- ✅ 配置 Windows 防火墙规则
- ✅ 安装 Python 依赖包
- ✅ 创建启动脚本

### 3. 启动服务器

**方法 1 (推荐):**
```powershell
# 双击生成的 start.ps1 文件
```

**方法 2:**
```powershell
python server_dynamic.py
```

### 4. 在手机上访问

1. 确保手机和电脑连接同一 WiFi
2. 在手机浏览器访问配置脚本输出的 URL
   - 例如: `https://你的电脑名.local:5000`
3. 接受自签名证书警告
4. 开始测试 Passkey！

## 📖 详细文档

- [快速部署指南](docs/快速部署指南.md) - 完整的部署和使用说明
- [常见问题](docs/FAQ.md) - 故障排查和解决方案
- [技术说明](docs/技术说明.md) - 架构和实现细节

## 🎯 使用示例

### 注册 Passkey

1. 在浏览器中打开项目 URL
2. 输入用户名（任意）
3. 点击"注册 Passkey"
4. 使用 Face ID / Touch ID / 指纹完成注册

### 登录

1. 输入之前注册的用户名
2. 点击"使用 Passkey 登录"
3. 使用生物识别认证
4. 登录成功！

## 📁 项目结构

```
passkey-webauthn-demo/
├── server_dynamic.py       # Flask 后端服务器
├── index_dynamic.html      # 前端界面
├── passkey.js             # WebAuthn 客户端逻辑
├── setup.py               # 自动配置脚本
├── requirements.txt       # Python 依赖
├── README.md             # 项目说明
├── LICENSE               # 开源许可证
├── .gitignore            # Git 忽略文件
└── docs/                 # 文档目录
    ├── 快速部署指南.md
    ├── FAQ.md
    └── 技术说明.md
```

## 🔧 配置说明

### 自动生成的文件

运行 `setup.py` 后会生成以下文件（已在 `.gitignore` 中）:

- `config.py` - 配置文件（包含 hostname、RP ID 等）
- `cert.pem` - SSL 证书
- `key.pem` - SSL 私钥
- `start.ps1` - 启动脚本

### 手动配置

如果自动配置失败，可以手动创建 `config.py`:

```python
HOSTNAME = "你的电脑名"
RP_ID = "你的电脑名.local"
RP_NAME = "Passkey 测试"
PORT = 5000
```

## 🌐 网络配置

### mDNS 域名

项目使用 mDNS (Multicast DNS) 实现局域网内的域名解析:
- **格式**: `hostname.local`
- **支持**: iOS、macOS 原生支持；Windows、Android 部分支持
- **备用**: 如果 `.local` 域名无法访问，使用 IP 地址

### 防火墙

Windows 防火墙规则会自动配置，如果失败请手动运行（需管理员权限）:

```powershell
New-NetFirewallRule -DisplayName "Passkey Test Server" -Direction Inbound -Protocol TCP -LocalPort 5000 -Action Allow
```

## 🔐 安全说明

⚠️ **这是测试项目，不要用于生产环境！**

存在的限制:
- 使用自签名 SSL 证书
- 数据存储在内存中（重启丢失）
- 没有用户会话管理
- 没有速率限制

如需生产部署，请:
1. 使用有效的 SSL 证书（Let's Encrypt 等）
2. 使用数据库存储凭证
3. 添加用户会话和权限管理
4. 实施安全防护措施

## 🛠️ 技术栈

- **后端**: Python 3 + Flask
- **WebAuthn 库**: py_webauthn
- **前端**: HTML5 + Vanilla JavaScript
- **认证**: WebAuthn / FIDO2
- **传输**: HTTPS (TLS)

## 📱 兼容性

### 浏览器

| 浏览器 | 平台 | 支持 |
|--------|------|------|
| Safari | iOS 14+ | ✅ Face ID, Touch ID |
| Safari | macOS | ✅ Touch ID |
| Chrome | Android 9+ | ✅ 指纹识别 |
| Edge | Windows 10+ | ✅ Windows Hello |

### 认证器

- ✅ 平台认证器（Face ID、Touch ID、指纹、Windows Hello）
- ✅ 安全密钥（YubiKey、Titan Key 等）
- ✅ 混合认证（跨设备 Passkey）

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- [W3C WebAuthn 规范](https://www.w3.org/TR/webauthn-2/)
- [FIDO Alliance](https://fidoalliance.org/)
- [py_webauthn](https://github.com/duo-labs/py_webauthn)

## 📞 支持

如果遇到问题:
1. 查看 [常见问题文档](docs/FAQ.md)
2. 搜索 [Issues](https://github.com/你的用户名/passkey-webauthn-demo/issues)
3. 创建新的 Issue

---

**⭐ 如果这个项目对你有帮助，请给个 Star！**
