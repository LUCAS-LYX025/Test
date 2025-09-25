import requests
import json
import base64
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5


class RSALoginSimulator:
    def __init__(self):
        self.base_url = "https://testzshq-os.zuiyouliao.com"  # 替换为实际网站
        self.public_key = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCXWfM/4K1K0M55Ol+ynZTefBBV
Rtmzg96RPjNOADVDjCVeljil6pQO6cYyItCUmtA4vfN+1nR5+3ZwfaaPWbxdfbsg
tkg0RDL/xhg1MiV4Wmss7i7JRaW8Ay5xC2FDJCoy/lvV5VHtMvbFnrkpmLKdPnqT
bisejvqBkuyfTtzlPQIDAQAB
-----END PUBLIC KEY-----"""

    def format_public_key(self, key_str):
        """格式化公钥为PEM格式"""
        if not key_str.startswith('-----BEGIN PUBLIC KEY-----'):
            return f"-----BEGIN PUBLIC KEY-----\n{key_str}\n-----END PUBLIC KEY-----"
        return key_str

    def encrypt_password(self, password):
        """使用RSA加密密码"""
        try:
            rsa_key = RSA.importKey(self.public_key)
            cipher = PKCS1_v1_5.new(rsa_key)
            encrypted = cipher.encrypt(password.encode('utf-8'))
            return base64.b64encode(encrypted).decode('utf-8')
        except Exception as e:
            print(f"加密失败: {str(e)}")
            return None

    def simulate_login(self, phone, password, country_code="+86"):
        """模拟登录流程"""
        # 加密密码
        encrypted_pwd = self.encrypt_password(password)
        if not encrypted_pwd:
            return False

        # 准备登录数据
        login_data = {
            "communicationWay": "phone",
            "countryCode": country_code,
            "phoneNumber": phone,
            "password": encrypted_pwd
        }

        # 发送登录请求
        try:
            response = requests.post(
                f"{self.base_url}/user/login",
                headers={'Content-Type': 'application/json'},
                data=json.dumps(login_data),
                timeout=10
            )

            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print("登录成功!")
                    print("响应数据:", json.dumps(result, indent=2))
                    return True
                else:
                    print("登录失败:", result.get('message', '未知错误'))
            else:
                print(f"请求失败，状态码: {response.status_code}")
        except Exception as e:
            print(f"请求异常: {str(e)}")

        return False


# 使用示例
if __name__ == "__main__":
    simulator = RSALoginSimulator()

    # 测试数据
    test_phone = "13950553595"
    test_password = "win8659008"

    # 执行模拟登录
    print("开始模拟登录...")
    success = simulator.simulate_login(test_phone, test_password)

    if success:
        print("模拟登录流程完成！")
    else:
        print("模拟登录失败，请检查参数和网络连接")