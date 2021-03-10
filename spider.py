#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2021/3/5 9:31 下午
# @Author : duanbin

import csv
import os
import re
import time

import requests
from bs4 import BeautifulSoup


class Spider:
    def __init__(self):
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
            'Cookie': 'cna=3G/DGAa80UgCAW/L9AKPQiHg; _gscu_818434402=14578259x1ne1471; _gscbrs_818434402=1; GUID=384555549; firstTime=1614578259167; vjuids=43b065c21.177ecb8a731.0.784cdb8e96d75; vjlast=1614584260.1614584260.30; lastTime=1614952919932; cookie_url=http%3A%2F%2Fwww.12371.cn%2Fspecial%2Fdnfg%2F; cookie_pcode=S-002-000-000; cookie_title=%25E5%2585%259A%25E7%25AB%25A0%25E5%2585%259A%25E8%25A7%2584_%25E5%2585%25B1%25E4%25BA%25A7%25E5%2585%259A%25E5%2591%2598%25E7%25BD%2591; _gscs_818434402=t149523258g0yro17|pv:13'
        }

    def initialize(self):
        self.urls = self.get_all_urls() if self.page_num > 1 else [self.url_prefix]
        self.saved_path = os.path.join(os.getcwd(), "results", self.url_name + "_" + str(self.page_num) + ".csv")

    def create_saved_file(self):
        with open(self.saved_path, 'w', encoding='utf-8', newline='')as f:
            write = csv.writer(f)
            write.writerow(self.save_header)

    def insert_records(self, data):
        with open(self.saved_path, 'a', encoding='utf-8', newline='')as file:
            writer = csv.writer(file)
            writer.writerows(data)

    def get_all_urls(self):
        urls = []
        for i in range(self.page_num):
            if self.url_postfix != "":
                url = self.url_prefix + str(i + 1) + self.url_postfix
            else:
                url = self.url_prefix + str(i + 1)
            urls.append(url)
        return urls

    def url_request(self, url):
        r = requests.get(url, headers=self.headers)
        r.encoding = 'utf-8'
        html = r.text
        return BeautifulSoup(html, 'html.parser')


class GCD_search_Spider(Spider):
    def __init__(self):
        super(GCD_search_Spider, self).__init__()
        self.url_name = "共产党员网-党规党章图文搜索"
        self.url_prefix = "http://so.12371.cn/dangjian.htm?t=news&q=%e5%85%9a%e8%a7%84%e5%85%9a%e7%ab%a0&p="
        self.url_postfix = "&time=0&type=%e5%9b%be%e6%96%87&category=&videotype=&videocategory=&namechar=&sort="
        self.page_num = 50
        self.initialize()
        self.save_header = ['标题', "内容", "更新时间"]
        self.create_saved_file()

    def get_link_content(self, url):
        link_bs = self.url_request(url)
        word = link_bs.find("div", class_="word")
        if not word:
            word = link_bs.find("div", class_="font_area_mid")
        if not word:
            print(url)
            return None
        else:
            content = word.get_text()
            return content

    def get_content(self):
        start_time = time.time()
        cnt = 1
        for p in range(self.page_num):
            bs = self.url_request(self.urls[p])
            links = bs.find_all("a", class_="rstitle")
            page_data = []
            for a in links:
                link = a['href']
                title = a.get_text()
                date = a.parent.parent.table.tr.td.get_text()
                content = self.get_link_content(link)
                print(f"当前正在爬取第{p + 1}页第{cnt}个界面...")
                if content:
                    page_data.append([title, content, date])
                    cnt += 1
            self.insert_records(page_data)
        end_time = time.time()
        print("总共用时%.2f秒" % (end_time - start_time))
        print("总共爬虫{}个界面".format(cnt))


class GCD_Hot_QA_Spider(Spider):
    def __init__(self):
        super(GCD_Hot_QA_Spider, self).__init__()
        self.url_name = "共产党员网-热门问题"
        self.url_prefix = "http://wenda.12371.cn/liebiao.php?mod=wantanswer&action=hot&page="
        self.url_postfix = ""
        self.page_num = 414
        self.initialize()
        self.save_header = ['简单问题', "详细问题", "答案数目", '答案', "url"]
        self.create_saved_file()

    def get_link_content(self, url):
        link_bs = self.url_request(url)
        detail = link_bs.find("div", class_="qaSubtit")
        if detail is None:
            return "",""
        detail=detail.get_text()
        answer_div = link_bs.find("div", class_="otherAnswerBox").find_all("div", class_="qaSubtit")
        answers = []
        for div in answer_div:
            answers.append(div.get_text())
        answers = "(-.-)".join(answers)
        return detail, answers

    def get_content(self):
        start_time = time.time()
        cnt = 1
        link_prefix = "http://wenda.12371.cn/"
        for p in range(948,self.page_num):
            bs = self.url_request(self.urls[p])
            divs = bs.find_all("div", class_="classifyCon_con answerCon_con")
            page_data = []
            for div in divs:
                question_summary = div.h1.a.get_text()
                link = link_prefix + div.h1.a['href']
                answer_num = int(re.sub("\D", "", div.find("p", class_="answerNum").span.get_text()))
                print(f"当前正在爬取第{p + 1}页第{cnt}个界面共{answer_num}个答案...")
                question_detail, answers = self.get_link_content(link)
                page_data.append([question_summary, question_detail, answer_num, answers, link])
                cnt += 1
            self.insert_records(page_data)
        end_time = time.time()
        print("总共用时%.2f秒" % (end_time - start_time))
        print("总共爬虫{}个界面".format(cnt))

class GCD_New_QA_Spider(GCD_Hot_QA_Spider):
    def __init__(self):
        super(GCD_New_QA_Spider, self).__init__()
        self.url_name = "共产党员网-最新问题"
        self.url_prefix = "http://wenda.12371.cn/liebiao.php?mod=wantanswer&action=new&page="
        self.url_postfix = ""
        self.page_num = 2576
        self.initialize()
        self.save_header = ['简单问题', "详细问题", "答案数目", '答案', "url"]
        self.create_saved_file()


if __name__ == "__main__":
    spider = GCD_New_QA_Spider()
    spider.get_content()
