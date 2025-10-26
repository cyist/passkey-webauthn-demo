#!/usr/bin/env python3
"""
Passkey 服务器 - 动态配置版本
自动读取 config.py 中的配置
"""

from flask import Flask, request, jsonify, send_from_directory
from webauthn import (
    generate_registration_options,
    verify_registration_response,
    generate_authentication_options,
    verify_authentication_response,
    options_to_json
)
from webauthn.helpers.structs import (
    PublicKeyCredentialDescriptor,
    UserVerificationRequirement,
    AuthenticatorSelectionCriteria,
    ResidentKeyRequirement,
    PublicKeyCredentialType
)
from webauthn.helpers.cose import COSEAlgorithmIdentifier
import secrets
import traceback
import base64
import os
import socket

# 尝试导入配置文件,如果不存在则使用默认值
try:
    from config import HOSTNAME, RP_ID, RP_NAME, PORT
    print(f"✅ 已加载配置文件")
except ImportError:
    # 默认配置
    HOSTNAME = socket.gethostname().lower()  # 转换为小写
    RP_ID = f"{HOSTNAME}.local"
    RP_NAME = "Passkey 测试"
    PORT = 5000
    print(f"⚠️  未找到 config.py,使用默认配置")

print(f"📋 服务器配置:")
print(f"   主机名: {HOSTNAME}")
print(f"   RP ID: {RP_ID}")
print(f"   RP Name: {RP_NAME}")
print(f"   端口: {PORT}")

app = Flask(__name__)

# 配置
RP_ORIGIN = f"https://{RP_ID}:{PORT}"

# 存储(实际应用中应使用数据库)
users_db = {}
challenges_db = {}

def base64url_to_bytes(data: str) -> bytes:
    """将 base64url 编码的字符串转换为 bytes"""
    # 添加填充
    padding = 4 - (len(data) % 4)
    if padding != 4:
        data += '=' * padding
    # 替换字符
    data = data.replace('-', '+').replace('_', '/')
    # 解码
    return base64.b64decode(data)

@app.route('/')
def index():
    """返回主页"""
    return send_from_directory('.', 'index_dynamic.html')

@app.route('/<path:path>')
def static_files(path):
    """返回静态文件"""
    return send_from_directory('.', path)

@app.route('/api')
def api_info():
    """API信息"""
    return jsonify({
        'name': RP_NAME,
        'rp_id': RP_ID,
        'rp_origin': RP_ORIGIN,
        'hostname': HOSTNAME,
        'endpoints': {
            'register_begin': '/register/begin',
            'register_complete': '/register/complete',
            'login_begin': '/login/begin',
            'login_complete': '/login/complete'
        }
    })

@app.route('/config.js')
def config_js():
    """动态生成前端配置文件"""
    js_config = f"""// 动态生成的配置文件
const config = {{
    apiUrl: 'https://{RP_ID}:{PORT}',
    rpId: '{RP_ID}',
    rpName: '{RP_NAME}'
}};
"""
    return js_config, 200, {'Content-Type': 'application/javascript'}

@app.route('/register/begin', methods=['POST'])
def register_begin():
    """开始注册流程"""
    try:
        data = request.json
        username = data.get('username')
        
        if not username:
            return jsonify({'error': '缺少用户名'}), 400
        
        print(f"\n🔵 开始注册流程: {username}")
        
        # 生成用户ID
        user_id = secrets.token_bytes(32)
        
        # 检查用户是否已存在
        if username in users_db:
            print(f"⚠️  用户已存在,将添加新凭证")
            user_id = users_db[username]['id']
            existing_credentials = [
                PublicKeyCredentialDescriptor(
                    id=cred['credential_id'],
                    type=PublicKeyCredentialType.PUBLIC_KEY
                )
                for cred in users_db[username]['credentials']
            ]
        else:
            existing_credentials = []
            users_db[username] = {
                'id': user_id,
                'credentials': []
            }
        
        # 生成注册选项
        options = generate_registration_options(
            rp_id=RP_ID,
            rp_name=RP_NAME,
            user_id=user_id,
            user_name=username,
            user_display_name=username,
            exclude_credentials=existing_credentials,
            authenticator_selection=AuthenticatorSelectionCriteria(
                resident_key=ResidentKeyRequirement.PREFERRED,
                user_verification=UserVerificationRequirement.PREFERRED
            ),
            supported_pub_key_algs=[
                COSEAlgorithmIdentifier.ECDSA_SHA_256,
                COSEAlgorithmIdentifier.RSASSA_PKCS1_v1_5_SHA_256,
            ]
        )
        
        # 保存challenge
        challenges_db[username] = options.challenge
        
        print(f"✅ 注册选项已生成")
        print(f"   Challenge: {options.challenge.hex()[:32]}...")
        
        # 返回选项
        return options_to_json(options)
        
    except Exception as e:
        print(f"❌ 注册开始失败: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/register/complete', methods=['POST'])
def register_complete():
    """完成注册流程"""
    try:
        data = request.json
        username = data.get('username')
        credential = data.get('credential')
        
        print(f"\n🔵 完成注册流程: {username}")
        
        if username not in challenges_db:
            return jsonify({'error': '未找到challenge'}), 400
        
        expected_challenge = challenges_db[username]
        
        # 验证注册响应
        verification = verify_registration_response(
            credential=credential,
            expected_challenge=expected_challenge,
            expected_origin=RP_ORIGIN,
            expected_rp_id=RP_ID
        )
        
        # 保存凭证
        users_db[username]['credentials'].append({
            'credential_id': verification.credential_id,
            'public_key': verification.credential_public_key,
            'sign_count': verification.sign_count,
            'credential_type': verification.credential_type,
            'credential_device_type': verification.credential_device_type,
            'credential_backed_up': verification.credential_backed_up
        })
        
        # 清除challenge
        del challenges_db[username]
        
        print(f"✅ 注册成功!")
        print(f"   用户: {username}")
        print(f"   凭证数量: {len(users_db[username]['credentials'])}")
        
        return jsonify({
            'verified': True,
            'credential_id': base64.b64encode(verification.credential_id).decode()
        })
        
    except Exception as e:
        print(f"❌ 注册完成失败: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/login/begin', methods=['POST'])
def login_begin():
    """开始登录流程"""
    try:
        data = request.json
        username = data.get('username')
        
        print(f"\n🔵 开始登录流程: {username}")
        
        if username not in users_db:
            return jsonify({'error': '用户不存在'}), 404
        
        # 获取用户的所有凭证
        credentials = users_db[username]['credentials']
        allow_credentials = [
            PublicKeyCredentialDescriptor(
                id=cred['credential_id'],
                type=PublicKeyCredentialType.PUBLIC_KEY
            )
            for cred in credentials
        ]
        
        print(f"   找到 {len(allow_credentials)} 个凭证")
        
        # 生成认证选项
        options = generate_authentication_options(
            rp_id=RP_ID,
            allow_credentials=allow_credentials,
            user_verification=UserVerificationRequirement.PREFERRED
        )
        
        # 保存challenge
        challenges_db[username] = options.challenge
        
        print(f"✅ 登录选项已生成")
        print(f"   Challenge: {options.challenge.hex()[:32]}...")
        
        return options_to_json(options)
        
    except Exception as e:
        print(f"❌ 登录开始失败: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/login/complete', methods=['POST'])
def login_complete():
    """完成登录流程"""
    try:
        data = request.json
        username = data.get('username')
        credential = data.get('credential')
        
        print(f"\n🔵 完成登录流程: {username}")
        
        if username not in challenges_db:
            return jsonify({'error': '未找到challenge'}), 400
        
        expected_challenge = challenges_db[username]
        
        # 获取credential ID并转换为bytes
        credential_id_str = credential.get('id') or credential.get('rawId')
        print(f"   收到的 credential ID (base64url): {credential_id_str[:32]}...")
        
        credential_id_bytes = base64url_to_bytes(credential_id_str)
        print(f"   转换后的 credential ID (bytes): {credential_id_bytes.hex()[:32]}...")
        
        # 查找匹配的凭证
        user_credential = None
        for i, cred in enumerate(users_db[username]['credentials']):
            stored_id = cred['credential_id']
            print(f"   比较凭证 {i}: {stored_id.hex()[:32]}...")
            if cred['credential_id'] == credential_id_bytes:
                user_credential = cred
                print(f"   ✅ 找到匹配的凭证 {i}")
                break
        
        if not user_credential:
            print(f"   ❌ 未找到匹配的凭证")
            return jsonify({'error': '未找到匹配的凭证'}), 404
        
        # 验证认证响应
        verification = verify_authentication_response(
            credential=credential,
            expected_challenge=expected_challenge,
            expected_origin=RP_ORIGIN,
            expected_rp_id=RP_ID,
            credential_public_key=user_credential['public_key'],
            credential_current_sign_count=user_credential['sign_count']
        )
        
        # 更新签名计数
        user_credential['sign_count'] = verification.new_sign_count
        
        # 清除challenge
        del challenges_db[username]
        
        print(f"✅ 登录验证成功!")
        print(f"   用户: {username}")
        print(f"   新签名计数: {verification.new_sign_count}")
        
        return jsonify({
            'verified': True,
            'user': username
        })
        
    except Exception as e:
        print(f"❌ 登录完成失败: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # 检查证书文件
    if not os.path.exists('cert.pem') or not os.path.exists('key.pem'):
        print("❌ 未找到SSL证书!")
        print("   请先运行: python setup.py")
        exit(1)
    
    print(f"\n🚀 服务器启动中...")
    print(f"   URL: {RP_ORIGIN}")
    print(f"   请在手机浏览器中访问上述地址")
    print(f"\n" + "="*60 + "\n")
    
    app.run(
        host='0.0.0.0',
        port=PORT,
        ssl_context=('cert.pem', 'key.pem'),
        threaded=True,
        debug=False
    )
