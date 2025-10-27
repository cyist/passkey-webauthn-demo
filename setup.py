#!/usr/bin/env python3
"""
Passkey 项目自动配置脚本
适用于任何 Windows 电脑的一键部署
"""

import socket
import subprocess
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
from cryptography import x509
from cryptography.x509.oid import NameOID, ExtensionOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
import ipaddress

def get_hostname():
    """获取本机hostname"""
    hostname = socket.gethostname().lower()  # 转换为小写,因为mDNS域名不区分大小写但WebAuthn区分
    print(f"✅ 检测到主机名: {hostname}")
    return hostname

def get_local_ip():
    """获取本机局域网IP"""
    try:
        # 创建一个UDP socket连接到外部地址(不会实际发送数据)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        print(f"✅ 检测到本机IP: {local_ip}")
        return local_ip
    except Exception as e:
        print(f"⚠️  无法获取本机IP: {e}")
        return "127.0.0.1"

def generate_certificate(hostname, local_ip):
    """生成SSL自签名证书"""
    print(f"\n📜 正在生成SSL证书...")
    
    # 生成私钥
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    
    # 证书主题信息
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "CN"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Beijing"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "Beijing"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Passkey Test"),
        x509.NameAttribute(NameOID.COMMON_NAME, f"{hostname}.local"),
    ])
    
    # 创建证书
    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        private_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.utcnow()
    ).not_valid_after(
        datetime.utcnow() + timedelta(days=365)
    ).add_extension(
        x509.SubjectAlternativeName([
            x509.DNSName(f"{hostname}.local"),
            x509.DNSName(hostname),
            x509.DNSName("localhost"),
            x509.IPAddress(ipaddress.IPv4Address(local_ip)),
            x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
        ]),
        critical=False,
    ).sign(private_key, hashes.SHA256(), default_backend())
    
    # 保存证书
    with open("cert.pem", "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))
    
    # 保存私钥
    with open("key.pem", "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))
    
    print(f"✅ SSL证书已生成: cert.pem, key.pem")
    print(f"   - 主机名: {hostname}.local")
    print(f"   - IP地址: {local_ip}")

def setup_firewall():
    """配置Windows防火墙"""
    print(f"\n🔥 正在配置防火墙...")
    
    # 检查是否有管理员权限
    try:
        # 先尝试删除旧规则(如果存在)
        subprocess.run([
            "powershell", "-Command",
            "Remove-NetFirewallRule -DisplayName 'Passkey Test Server' -ErrorAction SilentlyContinue"
        ], check=False, capture_output=True)
        
        # 添加新规则
        result = subprocess.run([
            "powershell", "-Command",
            "New-NetFirewallRule -DisplayName 'Passkey Test Server' -Direction Inbound -Protocol TCP -LocalPort 5000 -Action Allow -Profile Private,Domain"
        ], check=True, capture_output=True, text=True)
        
        print(f"✅ 防火墙规则已配置 (端口 5000)")
        return True
    except subprocess.CalledProcessError as e:
        print(f"⚠️  无法配置防火墙,可能需要管理员权限")
        print(f"   请手动运行以下命令(以管理员身份):")
        print(f"   New-NetFirewallRule -DisplayName 'Passkey Test Server' -Direction Inbound -Protocol TCP -LocalPort 5000 -Action Allow")
        return False

def update_config_file(hostname):
    """更新配置文件"""
    print(f"\n⚙️  正在更新配置文件...")
    
    # 创建配置文件
    config_content = f"""# Passkey 项目配置
# 自动生成于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

HOSTNAME = "{hostname}"
RP_ID = "{hostname}.local"
RP_NAME = "Passkey 测试"
PORT = 5000
"""
    
    with open("config.py", "w", encoding="utf-8") as f:
        f.write(config_content)
    
    print(f"✅ 配置文件已创建: config.py")
    print(f"   - RP ID: {hostname}.local")

def check_dependencies():
    """检查Python依赖"""
    print(f"\n📦 正在检查依赖...")
    
    required_packages = {
        'flask': 'Flask',
        'webauthn': 'webauthn',
        'cryptography': 'cryptography'
    }
    
    missing = []
    for module, package in required_packages.items():
        try:
            __import__(module)
            print(f"✅ {package} 已安装")
        except ImportError:
            print(f"❌ {package} 未安装")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  缺少以下依赖包: {', '.join(missing)}")
        print(f"   正在安装...")
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
            ], check=True)
            print(f"✅ 依赖安装完成")
        except subprocess.CalledProcessError:
            print(f"❌ 依赖安装失败,请手动运行: pip install -r requirements.txt")
            return False
    
    return True

def create_startup_script(hostname):
    """创建启动脚本"""
    print(f"\n📝 正在创建启动脚本...")
    
    # PowerShell启动脚本
    ps_script = f"""# Passkey 项目启动脚本
# 主机名: {hostname}

Write-Host "🚀 正在启动 Passkey 服务器..." -ForegroundColor Green
Write-Host "   主机名: {hostname}.local" -ForegroundColor Cyan
Write-Host "   端口: 5000" -ForegroundColor Cyan
Write-Host ""

# 停止旧的Python进程
Get-Process python* -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue

# 启动服务器
python run_server_threaded.py

Write-Host ""
Write-Host "按任意键退出..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
"""
    
    with open("start.ps1", "w", encoding="utf-8") as f:
        f.write(ps_script)
    
    print(f"✅ 启动脚本已创建: start.ps1")

def print_instructions(hostname, local_ip):
    """打印使用说明"""
    print(f"\n" + "="*60)
    print(f"🎉 配置完成!")
    print(f"="*60)
    print(f"\n📱 在手机上访问:")
    print(f"   https://{hostname}.local:5000")
    print(f"   或")
    print(f"   https://{local_ip}:5000")
    print(f"\n⚠️  首次访问需要:")
    print(f"   1. 确保手机和电脑在同一局域网")
    print(f"   2. 在浏览器中接受自签名证书")
    print(f"\n🚀 启动服务器:")
    print(f"   方法1: 双击 start.ps1")
    print(f"   方法2: 运行 python run_server_threaded.py")
    print(f"\n💡 提示:")
    print(f"   - 如果手机无法访问 {hostname}.local,请使用IP地址 {local_ip}")
    print(f"   - 防火墙已配置,如果仍无法访问请检查网络设置")
    print(f"="*60)

def main():
    """主函数"""
    print("="*60)
    print("🔧 Passkey 项目自动配置工具")
    print("="*60)
    
    # 切换到脚本所在目录
    script_dir = Path(__file__).parent.resolve()
    os.chdir(script_dir)
    print(f"📁 工作目录: {script_dir}\n")
    
    # 检查依赖
    if not check_dependencies():
        print("\n❌ 配置失败: 依赖检查未通过")
        return 1
    
    # 获取主机信息
    hostname = get_hostname()
    local_ip = get_local_ip()
    
    # 生成证书
    generate_certificate(hostname, local_ip)
    
    # 配置防火墙
    setup_firewall()
    
    # 更新配置
    update_config_file(hostname)
    
    # 创建启动脚本
    create_startup_script(hostname)
    
    # 打印说明
    print_instructions(hostname, local_ip)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
