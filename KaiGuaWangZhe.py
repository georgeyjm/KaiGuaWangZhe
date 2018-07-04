import json
import os
from pathlib import Path
from threading import Thread

import requests
import jieba
import jieba.analyse
from bs4 import BeautifulSoup
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from selenium import webdriver
from pymongo import MongoClient

from config import *

jieba.setLogLevel(20)

class Handler(FileSystemEventHandler):
    '''监听文件变动的句柄。'''
    def __init__(self):
        super().__init__()

    def on_created(self, event):
        '''一旦有文件变动，该函数就会被调用。'''
        if USE_DB:
            global newQuestion
        if event.src_path == (ROOT_DIR / 'question/bat/findQuiz').as_posix():
            # 新的题目
            # 获取相应的数据
            data = json.load((ROOT_DIR / 'question/bat/findQuiz').open())['data']
            questionNum = data['num']
            question = data['quiz']
            options = data['options']
            print(MSGS['QUESTION'].format(questionNum, question))
            # 查询答案
            answer, possibles, confidence = get_answer(question, options)
            # 根据返回置信度输出答案
            if confidence == 4:
                print(MSGS['ANSWER_DB'].format(answer))
            elif confidence == 3:
                print(MSGS['ANSWER_BAIKE'].format(answer))
            elif confidence == 2:
                print(MSGS['ANSWER_KEYWORD'].format(answer))
            elif confidence == 1:
                print(MSGS['ANSWER_FREQ'].format(answer, ', '.join(possibles)))
            if confidence >= SAY_ANSWER:
                os.system('say -v {} {}'.format(READ_VOICE, answer))

        elif USE_DB and event.src_path == (ROOT_DIR / 'question/bat/choose').as_posix():
            # 玩家选择结果
            # 获取相应数据
            chooseData = json.load((ROOT_DIR / 'question/bat/choose').open())['data']
            if newQuestion:
                # 未被记录过的问题
                # 获取相应数据
                correctIndex = chooseData['answer'] - 1
                quizData = json.load((ROOT_DIR / 'question/bat/findQuiz').open())['data']
                record = {'question': quizData['quiz'], 'answer': quizData['options'][correctIndex]}
                # 更新数据库
                questions.insert_one(record)
                print(MSGS['DB_INSERT'].format(quizData['quiz'], quizData['options'][correctIndex]))
                newQuestion = False
            elif chooseData['yes'] == False:
                # 被错误记录的问题（有些重复代码）
                # 获取相应数据
                correctIndex = chooseData['answer'] - 1
                quizData = json.load((ROOT_DIR / 'question/bat/findQuiz').open())['data']
                record = {'question': quizData['quiz'], 'answer': quizData['options'][correctIndex]}
                incorrectAnswer = questions.find_one({'question': quizData['quiz']})['answer']
                # 更新数据库
                questions.delete_one({'question': quizData['quiz']})
                questions.insert_one(record)
                print(MSGS['DB_CHANGE'].format(quizData['quiz'], incorrectAnswer, quizData['options'][correctIndex]))

def get_answer(question, options):
    '''根据百度搜索结果提取答案。'''
    if USE_DB:
        global newQuestion
    if USE_BROWSER:
        # 打开浏览器搜索页面
        Thread(target=open_browser, args=(question,)).start()

    # 首先查找该问题是否存在于数据库中
    if USE_DB:
        dbAnswer = questions.find_one({'question': question})
        if dbAnswer:
            return dbAnswer['answer'], [], 4
        newQuestion = True

    # 获取百度搜索结果
    web = requests.get('http://www.baidu.com/s?wd={}'.format(question), headers=HEADERS)
    soup = BeautifulSoup(web.text, 'lxml')

    # 查找是否有百度百科答案
    try:
        answer = soup.select('div.op_exactqa_s_answer')[0].get_text().strip().split('\n')[0]
        return answer, [], 3
    except IndexError:
        pass

    # 提取网页中关键词
    abstracts = '\n'.join(list(map(lambda x: x.get_text().replace('...', ''), soup.select('div.c-abstract'))))
    keywords = jieba.analyse.extract_tags(abstracts, NUM_SEARCH_KEYWORDS)
    for keyword in keywords:
        if keyword in options:
            return keyword, keywords[:NUM_POSSIBLE_KEYWORDS], 2

    # 返回词频最高的答案
    counts = [abstracts.count(i) for i in options]
    mostCount = options[counts.index(max(counts))] if max(counts) > 0 else MSGS['NO_ANSWER']
    return mostCount, keywords[:NUM_POSSIBLE_KEYWORDS], 1

def open_browser(search):
    '''在浏览器中打开传入参数的百度搜索结果。'''
    try:
        if BROWSER_KEYWORDS_ONLY:
            search = ' '.join(jieba.analyse.extract_tags(search, 3))
        driver.get('https://www.baidu.com/s?wd={}'.format(search))
    except Exception:
        pass

if USE_DB:
    # 连接数据库
    client = MongoClient()
    db = client[DB_NAME]
    questions = db[TABLE_NAME]
    newQuestion = False

if USE_BROWSER:
    # 初始化浏览器
    driver = webdriver.Chrome()
    driver.set_window_size(1440, 900)
    driver.set_window_position(0, 0)

# 初始化程序
handler = Handler()
observer = Observer()
(ROOT_DIR / 'question').mkdir(parents=True, exist_ok=True)
observer.schedule(handler, path=(ROOT_DIR / 'question').as_posix(), recursive=True)
observer.start()

try:
    input(MSGS['START'])
    observer.stop()
except KeyboardInterrupt:
    observer.stop()
observer.join()

if USE_BROWSER:
    driver.quit()
