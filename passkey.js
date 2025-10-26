// Passkey 配置
// 注意: 使用动态配置时,config 对象会从 /config.js 加载
// 如果没有加载 /config.js (例如独立使用此文件),则使用以下默认配置
if (typeof config === 'undefined') {
    const config = {
        // 使用 mDNS 域名 - WebAuthn 需要有效域名
        apiUrl: 'https://localhost:5000',
        // RP ID 必须是域名，不能包含端口
        rpId: 'localhost',
        rpName: 'Passkey Test'
    };
}

// 显示状态消息
function showStatus(message, type = 'info') {
    const statusDiv = document.getElementById('message') || document.getElementById('status');
    if (!statusDiv) {
        console.error('找不到消息显示元素');
        return;
    }
    statusDiv.textContent = message;
    statusDiv.className = `message ${type}`;
    statusDiv.style.display = 'block';
    
    // 5秒后自动隐藏
    setTimeout(() => {
        statusDiv.style.display = 'none';
    }, 5000);
}

// Base64 URL 编码/解码工具
function bufferToBase64url(buffer) {
    const bytes = new Uint8Array(buffer);
    let binary = '';
    for (let i = 0; i < bytes.length; i++) {
        binary += String.fromCharCode(bytes[i]);
    }
    return btoa(binary)
        .replace(/\+/g, '-')
        .replace(/\//g, '_')
        .replace(/=/g, '');
}

function base64urlToBuffer(base64url) {
    const base64 = base64url
        .replace(/-/g, '+')
        .replace(/_/g, '/');
    const binary = atob(base64);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) {
        bytes[i] = binary.charCodeAt(i);
    }
    return bytes.buffer;
}

// 检查浏览器支持
function checkSupport() {
    if (!window.PublicKeyCredential) {
        showStatus('❌ 您的浏览器不支持 WebAuthn API', 'error');
        const registerBtn = document.getElementById('registerBtn');
        const loginBtn = document.getElementById('loginBtn');
        if (registerBtn) registerBtn.disabled = true;
        if (loginBtn) loginBtn.disabled = true;
        return false;
    }
    return true;
}

// 注册 Passkey
async function registerPasskey() {
    if (!checkSupport()) return;

    const username = document.getElementById('username').value;
    if (!username) {
        showStatus('请输入用户名', 'error');
        return;
    }

    try {
        showStatus('🔄 正在准备注册...', 'info');
        
        // 1. 从服务器获取注册选项
        const optionsResponse = await fetch(`${config.apiUrl}/register/begin`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username })
        });

        if (!optionsResponse.ok) {
            throw new Error('获取注册选项失败');
        }

        const options = await optionsResponse.json();
        
        // 2. 转换 Base64url 数据为 ArrayBuffer
        const publicKeyCredentialCreationOptions = {
            challenge: base64urlToBuffer(options.challenge),
            rp: {
                name: options.rp.name,
                id: options.rp.id
            },
            user: {
                id: base64urlToBuffer(options.user.id),
                name: options.user.name,
                displayName: options.user.displayName
            },
            pubKeyCredParams: options.pubKeyCredParams,
            authenticatorSelection: options.authenticatorSelection,
            timeout: options.timeout,
            attestation: options.attestation
        };

        showStatus('📱 请使用您的设备进行生物识别认证...', 'info');

        // 3. 调用 WebAuthn API 创建凭证
        const credential = await navigator.credentials.create({
            publicKey: publicKeyCredentialCreationOptions
        });

        showStatus('🔄 正在完成注册...', 'info');

        // 4. 将凭证发送到服务器
        const credentialResponse = {
            id: credential.id,
            rawId: bufferToBase64url(credential.rawId),
            type: credential.type,
            response: {
                clientDataJSON: bufferToBase64url(credential.response.clientDataJSON),
                attestationObject: bufferToBase64url(credential.response.attestationObject)
            }
        };

        const verifyResponse = await fetch(`${config.apiUrl}/register/complete`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                username,
                credential: credentialResponse
            })
        });

        if (!verifyResponse.ok) {
            throw new Error('注册验证失败');
        }

        const result = await verifyResponse.json();
        showStatus('✅ Passkey 注册成功！', 'success');
        
        // 保存用户名到本地
        localStorage.setItem('lastUsername', username);

    } catch (error) {
        console.error('注册错误:', error);
        showStatus(`❌ 注册失败: ${error.message}`, 'error');
    }
}

// 使用 Passkey 登录
async function authenticatePasskey() {
    console.log('🔵 authenticatePasskey 函数被调用');
    
    if (!checkSupport()) return;

    const username = document.getElementById('username').value;
    console.log('📝 用户名:', username);
    
    if (!username) {
        showStatus('请输入用户名', 'error');
        return;
    }

    try {
        showStatus('🔄 正在准备登录...', 'info');
        console.log('📡 发送请求到:', `${config.apiUrl}/login/begin`);

        // 1. 从服务器获取认证选项
        const optionsResponse = await fetch(`${config.apiUrl}/login/begin`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username })
        });

        console.log('📥 响应状态:', optionsResponse.status);
        
        if (!optionsResponse.ok) {
            const errorText = await optionsResponse.text();
            console.error('❌ 服务器错误:', errorText);
            throw new Error('获取登录选项失败');
        }

        const options = await optionsResponse.json();
        console.log('✅ 获取到登录选项:', options);

        // 2. 转换数据
        const publicKeyCredentialRequestOptions = {
            challenge: base64urlToBuffer(options.challenge),
            timeout: options.timeout,
            rpId: options.rpId,
            allowCredentials: options.allowCredentials.map(cred => ({
                type: cred.type,
                id: base64urlToBuffer(cred.id)
            })),
            userVerification: options.userVerification
        };

        showStatus('📱 请使用您的设备进行生物识别认证...', 'info');

        // 3. 调用 WebAuthn API 获取断言
        const assertion = await navigator.credentials.get({
            publicKey: publicKeyCredentialRequestOptions
        });

        showStatus('🔄 正在验证...', 'info');

        // 4. 将断言发送到服务器验证
        const assertionResponse = {
            id: assertion.id,
            rawId: bufferToBase64url(assertion.rawId),
            type: assertion.type,
            response: {
                clientDataJSON: bufferToBase64url(assertion.response.clientDataJSON),
                authenticatorData: bufferToBase64url(assertion.response.authenticatorData),
                signature: bufferToBase64url(assertion.response.signature),
                userHandle: assertion.response.userHandle ? bufferToBase64url(assertion.response.userHandle) : null
            }
        };

        const verifyResponse = await fetch(`${config.apiUrl}/login/complete`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                username,
                credential: assertionResponse
            })
        });

        if (!verifyResponse.ok) {
            throw new Error('登录验证失败');
        }

        const result = await verifyResponse.json();
        showStatus('✅ 登录成功！', 'success');
        
        // 显示用户信息
        showUserInfo(username);

    } catch (error) {
        console.error('登录错误:', error);
        showStatus(`❌ 登录失败: ${error.message}`, 'error');
    }
}

// 显示用户信息
function showUserInfo(username) {
    const userInfoDiv = document.getElementById('userInfo');
    if (userInfoDiv) {
        const loggedUsernameEl = document.getElementById('loggedUsername');
        const loginTimeEl = document.getElementById('loginTime');
        if (loggedUsernameEl) loggedUsernameEl.textContent = username;
        if (loginTimeEl) loginTimeEl.textContent = new Date().toLocaleString('zh-CN');
        userInfoDiv.classList.add('show');
    }
}

// 页面加载时检查支持情况
window.addEventListener('DOMContentLoaded', () => {
    checkSupport();
    
    // 恢复上次使用的用户名
    const lastUsername = localStorage.getItem('lastUsername');
    if (lastUsername) {
        document.getElementById('username').value = lastUsername;
    }
});
