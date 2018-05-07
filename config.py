##### 用户自定义配置 #####

# 网络抓包镜像的文件夹名称，请将此文件夹放在与本文件同目录下
MIRROR_PATH = 'charles'
# 是否使用数据库
USE_DB = True
# 数据库名称
DB_NAME = 'TouNaoWangZhe'
# 表格名称
TABLE_NAME = 'questions'
# 是否打开浏览器显示百度搜索结果
USE_BROWSER = True
# 是否在浏览器搜索时只搜索题目关键词 (jieba 提取)
BROWSER_KEYWORDS_ONLY = False
# 朗读什么置信度的题目答案，若设置为大于4的值则不朗读任何答案
SAY_ANSWER = 2
# 程序在百度搜索结果里提取的关键词数量
NUM_SEARCH_KEYWORDS = 10
# 在程序不确定答案时返回的其他可能答案的数量
NUM_POSSIBLE_KEYWORDS = 5


##### 程序设置 (一般无需更改) #####

# 头脑王者题目的根域名，定位文件夹用
ROOT_URL = 'question-zh.hortor.net'
# 访问百度的请求头 (Request Headers)
HEADERS = {'User-Agent': 'Mozilla/5.0'}


##### 程序自动生成设置（无需更改） #####

ROOT_DIR = '{}/{}'.format(MIRROR_PATH, ROOT_URL)
