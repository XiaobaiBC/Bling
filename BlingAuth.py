import requests
import base64
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlparse, parse_qs
import time

class BlingAuth:
    def __init__(self):
        self.client_id = "a11343ab9c5401c3fb599d3131888bbffcc7efd3"
        self.client_secret = "5a8693d9911a2e297c90703c9136d71d956ec74492326951eb33ee760953"
        self.redirect_uri = "https://www.bodor.cn/"
        self.auth_url = "https://bling.com.br/Api/v3/oauth/authorize"
        self.token_url = "https://bling.com.br/Api/v3/oauth/token"
        self.state = "21"
        self.username = "zhengzaiga@gmail.com"
        self.password = "nap_gqh*apm4jhe!ZXQ"

    def check_url_change(self, driver, original_url, max_attempts=100, delay=0.1):
        """检查URL变化，使用轮询方式"""
        for _ in range(max_attempts):
            current_url = driver.current_url
            if current_url != original_url and 'bodor.cn' in current_url:
                return current_url
            time.sleep(delay)
        return None

    def get_authorization_code(self):
        """使用Selenium自动获取授权码"""
        auth_params = {
            "response_type": "code",
            "client_id": self.client_id,
            "state": self.state,
            "redirect_uri": self.redirect_uri
        }
        auth_url = f"{self.auth_url}?{'&'.join(f'{k}={v}' for k, v in auth_params.items())}"

        # 配置Chrome选项
        chrome_options = webdriver.ChromeOptions()
        chrome_options.page_load_strategy = 'none'  # 不等待页面加载完成
        
        driver = webdriver.Chrome(options=chrome_options)
        try:
            # 访问授权页面
            driver.get(auth_url)
            original_url = driver.current_url

            # 等待用户名输入框加载
            username_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "/html/body/div/div/div/form/div[2]/input"))
            )
            
            # 找到密码输入框和登录按钮
            password_input = driver.find_element(By.XPATH, "/html/body/div/div/div/form/div[3]/input")
            login_button = driver.find_element(By.XPATH, "/html/body/div/div/div/form/div[6]/button")

            # 输入登录信息
            username_input.send_keys(self.username)
            password_input.send_keys(self.password)

            # 点击登录按钮
            login_button.click()

            # 检查URL变化
            current_url = self.check_url_change(driver, original_url)
            if not current_url:
                raise Exception("URL未发生预期变化")
                
            print(f"当前URL: {current_url}")
            
            # 解析URL获取授权码
            parsed_url = urlparse(current_url)
            query_params = parse_qs(parsed_url.query)
            auth_code = query_params.get('code', [None])[0]

            if not auth_code:
                print("警告：未能在URL中找到授权码")
            
            return auth_code

        finally:
            driver.quit()

    def get_access_token(self, auth_code):
        """使用授权码获取访问令牌"""
        credentials = f"{self.client_id}:{self.client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        headers = {
            'Authorization': f'Basic {encoded_credentials}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        data = {
            "grant_type": "authorization_code",
            "code": auth_code,
            "redirect_uri": self.redirect_uri
        }

        response = requests.post(
            self.token_url, 
            data=data,
            headers=headers
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"获取访问令牌失败: {response.text}")

def main():
    auth = BlingAuth()
    
    try:
        print("正在获取授权码...")
        auth_code = auth.get_authorization_code()
        if not auth_code:
            raise Exception("无法获取授权码")

        print(f"获取到的授权码: {auth_code}")

        print("正在获取访问令牌...")
        token_info = auth.get_access_token(auth_code)
        print("\n成功获取访问令牌:")
        print(f"Access Token: {token_info.get('access_token')}")
        print(f"Token Type: {token_info.get('token_type')}")
        print(f"Expires In: {token_info.get('expires_in')} seconds")
        if 'refresh_token' in token_info:
            print(f"Refresh Token: {token_info.get('refresh_token')}")
    except Exception as e:
        print(f"错误: {str(e)}")

if __name__ == "__main__":
    main() 