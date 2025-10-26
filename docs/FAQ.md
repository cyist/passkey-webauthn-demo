# 常见问题 FAQ

## 📋 目录

- [安装和配置](#安装和配置)
- [网络连接](#网络连接)
- [证书问题](#证书问题)
- [WebAuthn 错误](#webauthn-错误)
- [其他问题](#其他问题)

---

## 安装和配置

### Q: setup.py 报错找不到模块？

**A:** 需要先安装依赖:

```powershell
pip install -r requirements.txt
```

如果还是报错，尝试升级 pip:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Q: 防火墙配置失败？

**A:** 配置防火墙需要管理员权限。以管理员身份打开 PowerShell:

```powershell
# 右键开始菜单 → Windows PowerShell (管理员)
New-NetFirewallRule -DisplayName "Passkey Test Server" -Direction Inbound -Protocol TCP -LocalPort 5000 -Action Allow
```

### Q: Python 版本太低？

**A:** 本项目需要 Python 3.7+。检查版本:

```powershell
python --version
```

如果版本过低，请从 [python.org](https://www.python.org/downloads/) 下载最新版本。

---

## 网络连接

### Q: 手机无法访问服务器？

**检查清单:**

1. **确认手机和电脑在同一 WiFi**
   ```powershell
   # 查看电脑 IP
   ipconfig | findstr IPv4
   ```

2. **确认防火墙已配置**
   ```powershell
   Get-NetFirewallRule -DisplayName "Passkey Test Server"
   ```

3. **尝试使用 IP 地址**
   - 如果 `hostname.local` 不工作，使用 `https://IP地址:5000`

4. **检查服务器是否运行**
   ```powershell
   Get-Process python*
   ```

### Q: .local 域名无法解析？

**A:** mDNS 支持因平台而异:

| 平台 | 支持情况 | 解决方案 |
|------|---------|---------|
| iOS/macOS | ✅ 原生支持 | 直接使用 |
| Windows | ⚠️ 部分支持 | 使用 IP 地址 |
| Android | ⚠️ 不稳定 | 使用 IP 地址 |

**备用方案:**

1. 查看电脑 IP: `ipconfig`
2. 使用 IP 访问: `https://192.168.1.xxx:5000`

### Q: 连接被重置/超时？

**A:** 可能原因:

1. **路由器隔离模式**
   - 有些路由器启用了 AP 隔离，禁止设备间通信
   - 解决: 在路由器设置中关闭 AP 隔离

2. **电脑防火墙/安全软件**
   - 360、火绒等安全软件可能阻止连接
   - 解决: 临时关闭或添加例外

3. **VPN/代理**
   - 如果开启了 VPN，可能影响局域网访问
   - 解决: 临时关闭 VPN

---

## 证书问题

### Q: 浏览器显示证书无效？

**A:** 这是正常的！项目使用自签名证书。

**iOS Safari:**
1. 点击"显示详细信息"
2. 点击"访问此网站"
3. 确认

**Android Chrome:**
1. 点击"高级"
2. 点击"继续前往 xxx.local(不安全)"

**桌面浏览器:**
- 点击"高级" → "继续访问"

### Q: 证书过期或无效？

**A:** 重新生成证书:

```powershell
# 删除旧证书
Remove-Item cert.pem, key.pem

# 重新运行配置
python setup.py
```

---

## WebAuthn 错误

### Q: SecurityError: The relying party ID is not a registrable domain

**A:** RP ID 必须与访问的域名完全匹配（包括大小写）。

**检查:**

```powershell
# 查看配置
Get-Content config.py
```

确保:
- 使用小写域名: `wuchengyu.local` ✅
- 不要用大写: `WuChengyu.local` ❌
- 访问 URL 要匹配配置的 RP ID

**解决:**

```powershell
# 重新运行 setup.py 会自动使用小写
python setup.py
```

### Q: NotAllowedError: The operation either timed out or was not allowed

**A:** 可能原因:

1. **用户取消操作** - 正常情况
2. **不是 HTTPS** - WebAuthn 要求 HTTPS（localhost 除外）
3. **浏览器不支持** - 使用较新版本的浏览器

### Q: NotSupportedError: The security origin could not be verified

**A:** 确保:
- 使用 HTTPS 协议
- 域名格式正确
- 不是 IP 地址作为 RP ID（使用 `.local` 域名）

### Q: 注册/登录无响应？

**A:** 打开浏览器开发者工具 (F12):

1. **查看 Console 错误**
   - 是否有 JavaScript 错误？
   - 是否有网络请求失败？

2. **查看 Network 标签**
   - `/register/begin` 请求是否成功？
   - 返回的数据是否正常？

3. **清除缓存**
   - 强制刷新: `Ctrl+Shift+R`
   - 或清除浏览器缓存

---

## 其他问题

### Q: 重启后数据丢失？

**A:** 这是设计如此。本项目将数据存储在内存中，用于测试目的。

如需持久化:
- 使用数据库（SQLite、PostgreSQL 等）
- 修改 `server_dynamic.py` 中的存储逻辑

### Q: 可以用于生产环境吗？

**A:** ❌ **不建议！** 这是测试项目。

生产环境需要:
- ✅ 有效的 SSL 证书（非自签名）
- ✅ 数据库存储
- ✅ 用户会话管理
- ✅ 安全防护（CSRF、XSS 等）
- ✅ 速率限制
- ✅ 日志和监控
- ✅ 备份和恢复

### Q: 如何支持多个用户？

**A:** 当前版本已支持多用户:
- 每个用户名独立
- 一个用户可以注册多个 Passkey
- 数据存储在 `users_db` 字典中

### Q: 可以在 macOS/Linux 上运行吗？

**A:** 理论上可以，但需要修改:

1. **防火墙配置** - 使用 `iptables` 或 `ufw`
2. **启动脚本** - 使用 bash 而不是 PowerShell
3. **路径处理** - 确保路径兼容

目前项目主要针对 Windows 优化。

### Q: 如何修改端口？

**A:** 编辑 `config.py`:

```python
PORT = 8080  # 改为你想要的端口
```

**记得:**
- 更新防火墙规则
- 访问时使用新端口
- 重启服务器

### Q: 支持哪些认证器？

**A:** 支持所有 FIDO2 认证器:

- ✅ **平台认证器**
  - iOS: Face ID, Touch ID
  - Android: 指纹, 面部识别
  - Windows: Windows Hello
  - macOS: Touch ID

- ✅ **安全密钥**
  - YubiKey
  - Google Titan Key
  - Feitian Key
  - 任何 FIDO2 兼容密钥

- ✅ **混合认证**
  - 跨设备 Passkey (iOS 16+, Android 9+)

---

## 🆘 还是无法解决？

1. **查看日志**
   - 服务器控制台的错误信息
   - 浏览器 Console 的错误

2. **搜索 Issues**
   - GitHub Issues 中可能有类似问题

3. **创建 Issue**
   - 提供详细信息:
     - 操作系统版本
     - Python 版本
     - 错误信息
     - 复现步骤

4. **联系社区**
   - GitHub Discussions
   - 提交 Pull Request

---

**💡 提示:** 大多数问题都是网络配置或证书相关，请先检查这两项！
