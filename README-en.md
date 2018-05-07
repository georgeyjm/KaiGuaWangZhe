# Cheat King

[:cn: 中文](README.md)

***This program is only for educational purposes.***

## Introduction

Quoted from Baidu Baike:
> "Mind King" is a WeChat Mini Program. There are two players in each game, five questions, without special addons, choosing the correct answer for a question can get a player up to 200 points, the slower the player answers, the fewer the points, wrong answers are not penalized, the player with high score wins the game.

This program is a helper program for the WeChat Mini Program "Mind King", its functionalities are to search, display and store the answer to a question, and it cannot auto-select the answer.


## Principle

首先，通过网络抓包，我们能够获取到头脑王者题目的网络请求，从而获取到题目和答案选项。通过简单的百度搜索和提取关键词，并根据已有的答案选项，寻找可能的答案。判断答案是否正确，并将正确答案加入数据库，以备下次使用。

## Features

- 快速地查找并显示出答案（网络条件允许下，可以达到题目未显示，答案已出的速度）
- 将题目存储到数据库，允许未来该题目答案 100% 的准确性
- 在浏览器中打开问题的搜索结果，在答案不确定的情况下人为寻找答案
- 朗读答案，用户可以只专注于手机屏幕
- 支持任何品牌、系统的手机，只需支持网络代理即可


## Installation and Usage

### Environment

#### OS

:white_check_mark: macOS  
:grey_question:    Windows (Not tested)  
:grey_question:    Linux (Not tested)

#### Python

:white_check_mark: Python 3.X  
:grey_question:    Python 2.X  

### Installation

1. Install proxy for traffic monitoring (Charles is recommended)

2. *(Optional)* Install MongoDB

3. Install Python modules:

```shell
pip install requests jieba bs4 watchdog selenium pymongo
```

4. Clone this repository:

```shell
git clone https://github.com/yu-george/KaiGuaWangZhe.git
```

### Usage

1. *(Optional)* If you are using a database, please run the database first:

```shell
mongod --dbpath <DB_PATH>
```

2. Open your traffic monitoring software and set up a mirror

3. Configure your network proxy on your phone to your computer

4. `cd` to the program's path, and run the program:

```shell
python KaiGuaWangZhe.py
```

### Configuration

Configurations are found in the `config.py` file.


## To-Do's

- [ ] Setup a proxy server within the Python script itself, thus removing the need to install extra softwares
- [ ] Optimize the algorithm to extract answer for unknown questions, increasing the accuracy
- [ ] Optimize the algorithm to extract answer for questions like "Which of the following is not…"
- [ ] Implement Natural Language Processing and semantic analysis to increase the accuracy of searching