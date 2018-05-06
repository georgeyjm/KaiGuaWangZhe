# Remember to start MongoDB client with:
#   mongod --dbpath ~/db

import requests
import jieba
import jieba.analyse
from bs4 import BeautifulSoup
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import json
import os
from selenium import webdriver
from threading import Thread
from pymongo import MongoClient
from config import *

jieba.setLogLevel(20)

class Handler(FileSystemEventHandler):
    '''Handler for any file changes for the battle question.'''
    def __init__(self):
        super().__init__()

    def on_created(self, event):
        global newQuestion
        if event.src_path == 'charles/{}/question/bat/findQuiz'.format(ROOT_URL):
            data = json.load(open('charles/{}/question/bat/findQuiz'.format(ROOT_URL)))['data']
            questionNum = data['num']
            question = data['quiz']
            options = data['options']
            print('\n\n第{}题：{}'.format(questionNum, question))
            answer, possibles, confidence = get_answer(question, options)
            if confidence == 4:
                print('答案（数据库）：{}'.format(answer))
            elif confidence == 3:
                print('答案（百度百科）：{}'.format(answer))
            elif confidence == 2:
                print('答案（关键词提取）：{}'.format(answer))
                # print('答案：{}\n其他可能答案关键词：{}'.format(answer, ', '.join(possibles)))
            elif confidence == 1:
                print('答案（词频）：{}\n可能答案关键词：{}'.format(answer, ', '.join(possibles)))
            if confidence >= SAY_ANSWER:
                os.system('say -v ting-ting {}'.format(answer))

        elif event.src_path == 'charles/{}/question/bat/choose'.format(ROOT_URL):
            chooseData = json.load(open('charles/{}/question/bat/choose'.format(ROOT_URL)))['data']
            if newQuestion:
                # correctIndex = json.load(open('charles/{}/question/bat/choose'.format(ROOT_URL)))['data']['answer'] - 1
                # data = json.load(open('charles/{}/question/bat/findQuiz'.format(ROOT_URL)))['data']
                # record = {'question': data['quiz'], 'answer': data['options'][correctIndex]}
                # questions.insert_one(record)
                # # print('插入数据：{}，答案为：{}'.format(data['quiz'], data['options'][correctIndex]))
                # newQuestion = False

                correctIndex = chooseData['answer'] - 1
                quizData = json.load(open('charles/{}/question/bat/findQuiz'.format(ROOT_URL)))['data']
                # print('answer', quizData['options'][chooseData['answer'] - 1])
                # print('option', quizData['options'][chooseData['option'] - 1])
                record = {'question': quizData['quiz'], 'answer': quizData['options'][correctIndex]}
                questions.insert_one(record)
                print('插入数据：{}，答案为：{}'.format(quizData['quiz'], quizData['options'][correctIndex]))
                newQuestion = False
            elif chooseData['yes'] == False: # Incorrect database record (some redundant code)
                correctIndex = chooseData['answer'] - 1
                quizData = json.load(open('charles/{}/question/bat/findQuiz'.format(ROOT_URL)))['data']
                record = {'question': quizData['quiz'], 'answer': quizData['options'][correctIndex]}
                incorrectAnswer = questions.find_one({'question': quizData['quiz']})['answer']
                questions.delete_one({'question': quizData['quiz']})
                questions.insert_one(record)
                print('更改数据：{}，答案从：{}，更改为：{}'.format(quizData['quiz'], incorrectAnswer, quizData['options'][correctIndex]))

def get_answer(question, options):
    global newQuestion
    if BROWSER_PAGE:
        Thread(target=open_browser, args=(question,)).start()

    dbAnswer = questions.find_one({'question': question})
    if dbAnswer:
        return dbAnswer['answer'], [], 4
    newQuestion = True

    web = requests.get('https://www.baidu.com/s?wd={}'.format(question), headers=HEADERS)
    soup = BeautifulSoup(web.text, 'lxml')

    # Try to get answer from Baidu Baike
    try:
        answer = soup.select('div.op_exactqa_s_answer')[0].get_text().strip().split('\n')[0]
        return answer, [], 3
    except IndexError:
        pass

    # Keyword extract
    abstracts = '\n'.join(list(map(lambda x: x.get_text().replace('...', ''), soup.select('div.c-abstract'))))
    keywords = jieba.analyse.extract_tags(abstracts, NUM_SEARCH_KEYWORDS)
    for keyword in keywords:
        if keyword in options:
            return keyword, keywords[:NUM_POSSIBLE_KEYWORDS], 2
    counts = [abstracts.count(i) for i in options]
    mostCount = options[counts.index(max(counts))] if max(counts) > 0 else '无法找到答案！'
    return mostCount, keywords[:NUM_POSSIBLE_KEYWORDS], 1

def open_browser(search):
    try:
        if BROWSER_KEYWORDS_ONLY:
            search = ' '.join(jieba.analyse.extract_tags(search, 3))
        driver.get('https://www.baidu.com/s?wd={}'.format(search))
    except Exception:
        pass

client = MongoClient()
db = client['TouNaoWangZhe']
questions = db['questions']
newQuestion = False

if BROWSER_PAGE:
    driver = webdriver.Chrome()
    driver.set_window_size(1440, 900)
    driver.set_window_position(0, 0)

handler = Handler()
observer = Observer()
observer.schedule(handler, path='charles/{}/question'.format(ROOT_URL), recursive=True)
observer.start()

try:
    input('开挂开始！')
    observer.stop()
except KeyboardInterrupt:
    observer.stop()
observer.join()

if BROWSER_PAGE:
    driver.quit()
