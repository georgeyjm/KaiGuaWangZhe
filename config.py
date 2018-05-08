##### 用户自定义配置 #####

# 程序提示信息语言
LANG = 'zh'
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
# 用什么声音朗读答案
READ_VOICE = 'ting-ting'
# 程序在百度搜索结果里提取的关键词数量
NUM_SEARCH_KEYWORDS = 10
# 在程序不确定答案时返回的其他可能答案的数量
NUM_POSSIBLE_KEYWORDS = 5


##### 程序设置 (一般无需更改) #####

# 头脑王者题目的根域名，定位文件夹用
ROOT_URL = 'question-zh.hortor.net'
# 访问百度的请求头 (Request Headers)
HEADERS = {'User-Agent': 'Mozilla/5.0'}


##### 程序设置（无需更改） #####

ROOT_DIR = '{}/{}'.format(MIRROR_PATH, ROOT_URL)

MSGS = {
    'zh': {
        'START': '开挂开始！',
        'QUESTION': '\n\n第{}题：{}',
        'NO_ANSWER': '无法找到答案！',
        'DB_INSERT': '插入数据：{}，答案为：{}',
        'DB_CHANGE': '更改数据：{}，答案从：{}，更改为：{}',
        'ANSWER_DB': '答案（数据库）：{}',
        'ANSWER_BAIKE': '答案（百度百科）：{}',
        'ANSWER_KEYWORD': '答案（关键词提取）：{}',
        'ANSWER_FREQ': '答案（词频）：{}\n可能答案关键词：{}'
    },
    'en': {
        'START': 'Start!',
        'QUESTION': '\n\nQuestion #{}: {}',
        'NO_ANSWER': 'Unable to find answer',
        'DB_INSERT': 'Inserted question: {}, with answer: {}',
        'DB_CHANGE': 'Changed answer for question: {} from {} to {}',
        'ANSWER_DB': 'Answer (database): {}',
        'ANSWER_BAIKE': 'Answer (baike): {}',
        'ANSWER_KEYWORD': 'Answer (keyword): {}',
        'ANSWER_FREQ': 'Answer (frequency): {}\nPossible answer keywords: {}'
    }
}[LANG]
