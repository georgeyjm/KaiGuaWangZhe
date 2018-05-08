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
        if USE_DB:
            global newQuestion
        if event.src_path == '{}/question/bat/findQuiz'.format(ROOT_DIR):
            data = json.load(open('{}/question/bat/findQuiz'.format(ROOT_DIR)))['data']
            questionNum = data['num']
            question = data['quiz']
            options = data['options']
            print(MSGS['QUESTION'].format(questionNum, question))
            answer, possibles, confidence = get_answer(question, options)
            if confidence == 4:
                print(MSGS['ANSWER_DB'].format(answer))
            elif confidence == 3:
                print(MSGS['ANSWER_BAIKE'].format(answer))
            elif confidence == 2:
                print(MSGS['ANSWER_KEYWORD'].format(answer))
            elif confidence == 1:
                print(MSGS['FREQ'].format(answer, ', '.join(possibles)))
            if confidence >= SAY_ANSWER:
                os.system('say -v {} {}'.format(READ_VOICE, answer))

        elif USE_DB and event.src_path == '{}/question/bat/choose'.format(ROOT_DIR):
            chooseData = json.load(open('{}/question/bat/choose'.format(ROOT_DIR)))['data']
            if newQuestion:
                correctIndex = chooseData['answer'] - 1
                quizData = json.load(open('{}/question/bat/findQuiz'.format(ROOT_DIR)))['data']
                record = {'question': quizData['quiz'], 'answer': quizData['options'][correctIndex]}
                questions.insert_one(record)
                print(MSGS[DB_INSERT].format(quizData['quiz'], quizData['options'][correctIndex]))
                newQuestion = False
            elif chooseData['yes'] == False: # Incorrect database record (some redundant code)
                correctIndex = chooseData['answer'] - 1
                quizData = json.load(open('{}/question/bat/findQuiz'.format(ROOT_DIR)))['data']
                record = {'question': quizData['quiz'], 'answer': quizData['options'][correctIndex]}
                incorrectAnswer = questions.find_one({'question': quizData['quiz']})['answer']
                questions.delete_one({'question': quizData['quiz']})
                questions.insert_one(record)
                print(MSGS[DB_CHANGE].format(quizData['quiz'], incorrectAnswer, quizData['options'][correctIndex]))

def get_answer(question, options):
    if USE_DB:
        global newQuestion
    if USE_BROWSER:
        Thread(target=open_browser, args=(question,)).start()

    if USE_DB:
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
    mostCount = options[counts.index(max(counts))] if max(counts) > 0 else MSGS['NO_ANSWER']
    return mostCount, keywords[:NUM_POSSIBLE_KEYWORDS], 1

def open_browser(search):
    try:
        if BROWSER_KEYWORDS_ONLY:
            search = ' '.join(jieba.analyse.extract_tags(search, 3))
        driver.get('https://www.baidu.com/s?wd={}'.format(search))
    except Exception:
        pass

if USE_DB:
    client = MongoClient()
    db = client[DB_NAME]
    questions = db[TABLE_NAME]
    newQuestion = False

if USE_BROWSER:
    driver = webdriver.Chrome()
    driver.set_window_size(1440, 900)
    driver.set_window_position(0, 0)

handler = Handler()
observer = Observer()
observer.schedule(handler, path='{}/question'.format(ROOT_DIR), recursive=True)
observer.start()

try:
    input(MSGS['START'])
    observer.stop()
except KeyboardInterrupt:
    observer.stop()
observer.join()

if USE_BROWSER:
    driver.quit()
