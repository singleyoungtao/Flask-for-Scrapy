#!/bin/python3
#-*-coding:utf-8-*-

import os, json
from flask import Flask, render_template
from pymongo import MongoClient
from whoosh.fields import Schema, TEXT, ID, KEYWORD, STORED
from whoosh.index import create_in, open_dir
from whoosh.qparser import MultifieldParser
from jieba.analyse import ChineseAnalyzer


app = Flask(__name__)


client = MongoClient('localhost:27017')
db = client.search
collection = db.search

# class appSchema(SchemaClass):
#     url = ID(stored=True)
#     title = TEXT(stored=True)
#     content = TEXT


# class WhooshSarch(object):

# def open_writer(self):
analyzer = ChineseAnalyzer()
schema = Schema(title=TEXT(stored=True, analyzer=analyzer),
                    url=ID(unique=True, stored=True),
                    content=TEXT(stored=True, analyzer=analyzer))
if not os.path.exists("testindexdir"):
    os.mkdir("testindexdir")
ix = create_in("testindexdir", schema)
ix = open_dir("testindexdir")
# else:
#     ix = open_dir("testindexdir")
# ix = open_dir("testindexdir")
# return ix.writer()

    # def write_index(coll):
    # writer = open_writer(self)
    # 此处的timeout参数需要查询
writer = ix.writer()
# for coll in collection.find(timeout=False):
for coll in collection.find():
    writer.add_document(title=coll["title"], url=coll["url"],
                           content=coll["content"])
writer.commit()


# def search_data():
with ix.searcher() as searcher:
    query = MultifieldParser(["url", "title", "content"],
                             ix.schema).parse("关于举办新西兰林肯大学土壤学专家系列学术报告的通知")
    results = searcher.search(query)
    a = len(results)
    b = results[0:2]
    c = results[0].fields()
    d = json.dumps(c, ensure_ascii=False)
    e = results[1]
    f = results[0]
    print(type(results))
    print(len(results))
    print(results[0:2])
    print(results[0])
    g = []
    for i in range(a):
        g.append(results[i].fields())
    keywords = [keyword for keyword, score in
                results.key_terms("content", docs=10, numterms=5)]
    print(keywords)
    # 此处search_page及其参数需查明,考虑前段分页
    # searcher.search_page(query, 1, pagelen=20)

# ix.close()


@app.route('/')
def index_page():
    return render_template('index.html', a=a, c=c, g=g)


if __name__ == "__main__":
    app.run(debug=True)
