#!/usr/bin/env python3
"""
Passkey 服务器启动脚本 - 多线程版本
使用 SSL 证书启动 HTTPS 服务器
"""

import os
import sys
from pathlib import Path

def main():
    """启动服务器"""
    # 检查证书文件
    cert_file = Path("cert.pem")
    key_file = Path("key.pem")
    
    if not cert_file.exists() or not key_file.exists():
        print("❌ 证书文件不存在!")
        print("   请先运行: python setup.py")
        return 1
    
    # 导入 Flask 应用
    try:
        from server_dynamic import app, PORT, RP_ID
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        print("   请确保已安装所有依赖: pip install -r requirements.txt")
        return 1
    
    print("\n" + "="*60)
    print("🚀 启动 Passkey 服务器")
    print("="*60)
    print(f"   访问地址: https://{RP_ID}:{PORT}")
    print(f"   证书文件: {cert_file.absolute()}")
    print(f"   私钥文件: {key_file.absolute()}")
    print("="*60)
    print("\n⚠️  首次访问请在浏览器中接受自签名证书")
    print("💡 按 Ctrl+C 停止服务器\n")
    
    # 启动服务器
    try:
        app.run(
            host='0.0.0.0',
            port=PORT,
            ssl_context=(str(cert_file), str(key_file)),
            threaded=True,
            debug=True
        )
    except KeyboardInterrupt:
        print("\n\n👋 服务器已停止")
        return 0
    except Exception as e:
        print(f"\n❌ 服务器错误: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
