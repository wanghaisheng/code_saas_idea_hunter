import requests

headers = {
    "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1",
    "Accept":"video/webm,video/ogg,video/*;q=0.9,application/ogg;q=0.7,audio/*;q=0.6,*/*;q=0.5"
    }

url = "https://www.douyin.com/video/7068253884954791182"
# 禁止重定向，设置 allow_redirects=False
r = requests.get(url, headers=headers, allow_redirects=True)
print(r.text)