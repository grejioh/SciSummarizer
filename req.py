import requests

url = "https://export.arxiv.org/api/query?search_query=&id_list=2410.03537&sortBy=submittedDate&sortOrder=descending&start=0&max_results=100"

# proxies = {
#     'http': 'http://127.0.0.1:7890',
#     'https': 'http://127.0.0.1:7890',
# }
response = requests.get(url)

if response.status_code == 200:
    print(response.text)
else:
    print(f"请求失败，状态码：{response.status_code}")