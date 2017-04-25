#!/bin/python3
#-*-coding:utf-8-*-

import os, json, re
from flask import Flask, render_template, request, jsonify, abort
from flask_cors import CORS, cross_origin
from pymongo import MongoClient
from whoosh.fields import Schema, TEXT, ID, KEYWORD, STORED
from whoosh.index import create_in, open_dir
from whoosh.qparser import MultifieldParser
from jieba.analyse import ChineseAnalyzer

app = Flask(__name__)
CORS(app)
# app.config['JSON_AS_ASCII'] = False

client = MongoClient('localhost:27017')
db = client.search
co = db.search
analyzer = ChineseAnalyzer()
# PAGE_SIZE = 5

class WhooshSarch(object):
    """
    Object utilising Whoosh to create a search index of all
    crawled rss feeds, parse queries and search the index for related mentions.
    """

    def __init__(self, collection):
        self.collection = collection
        self.indexdir = "indexdir"
        self.indexname = "indexname"
        self.schema = self.get_schema()
        if not os.path.exists(self.indexdir):
            os.mkdir(self.indexdir)
            create_in(self.indexdir, self.schema, indexname=self.indexname)
        self.ix = open_dir(self.indexdir, indexname=self.indexname)

    def get_schema(self):
        return Schema(title=TEXT(stored=True, analyzer=analyzer),
                      url=ID(unique=True, stored=True),
                      content=TEXT(stored=True, analyzer=analyzer))

    def rebuild_index(self):
        ix = create_in(self.indexdir, self.schema, indexname=self.indexname)
        writer = ix.writer()
        for coll in self.collection.find():
            writer.update_document(title=coll["title"], url=coll["url"],
                            content=coll["content"])
        writer.commit() 

    def commit(self, writer):
        """ commit data to index """
        writer.commit()
        return True

    def parse_query(self, query):
        parser = MultifieldParser(["url", "title", "content"], self.ix.schema)
        return parser.parse(query)
                    
    # def search(self, query, page):
    #     """ 考虑使用后端分页还是前段分页 """
    #     results = []
    #     with self.ix.searcher() as searcher:
    #         result_page = searcher.search_page(
    #             self.parse_query(query), page, pagelen=PAGE_SIZE)
    #         for result in result_page:
    #         # for result in searcher.search(self.parse_query(query)):
    #             results.append(dict(result))
    #     return {'results': results, 'total': result_page.total}

    def search(self, query):
        results = []
        with self.ix.searcher() as searcher:
            result_origin = searcher.search(self.parse_query(query))
            #TODO 将查询结果中'content'字段内容改为html格式的摘要

            for result in result_origin:
                #Fragment size 的maxchars默认200，surround默认20
                # dict(result)
                # re.sub("[\t\r\n ]+", " ", result['content'])
                # 不用去掉这几个字符，在返回结果中他们会在浏览器中自动转化
                # results.append(result)
                results.append(dict(result))
        return results
            # result_len = len(result_origin)
            # for i in range(result_len):
            #     results.append(result_origin[i].fields)
            # keywords = [keyword for keyword, score in
            #     result_origin.key_terms("content", docs=10, numterms=5)]
            # print(keywords)

    def close(self):
        """
        Closes the searcher obj. Must be done manually.
        """
        self.ix.close()


nwsuaf = WhooshSarch(co)
nwsuaf.rebuild_index()
# query_one = "关于举办新西兰林肯大学土壤学专家系列学术报告的通知"
# pageshow = nwsuaf.search(query_one)
# print(pageshow)
# nwsuaf.close()


@app.route('/')
def index_page():
    return render_template('index.html')

@app.route('/results', methods=['GET', 'POST'])
def get_results():
    if not request.json or not 'keywords' in request.json:
        abort(400)
    query_keywords = request.json['keywords']
    pageshow = nwsuaf.search(query_keywords)
    print(query_keywords)
    print(pageshow)
    # TODO 此处添加完成搜索后的返回消息
    return jsonify({'results': pageshow}), 201

# @app.route('/keywords', method=['POST'])
# def post_keywords():
#     query_keywords = resquest.json['keywords']
#     pageshow = nwsuaf.search(query_keywords)
#     print(pageshow)
#     # TODO 此处添加完成搜索后的返回消息
#     return 200




if __name__ == "__main__":
    app.run(debug=True)
  