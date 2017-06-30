#!/Python27/python
# coding=utf-8

import codecs
from lxml import html,etree
import os, sys, re
import collections
import json,random
import wenda_proc, util

reload(sys)
sys.setdefaultencoding( "utf-8" )
DATA_ROOT = "/randy/Workspace/data/wenda/"

gb_default_encoding = "gbk"
dir_name1 = DATA_ROOT + "crawler/1/"
dir_name2 = DATA_ROOT +"crawler/2/"
dir_name3 = DATA_ROOT +"crawler/3/"


def process(dir=dir_name1):
    allfiles = os.listdir(dir)
    for one in allfiles:
        process_doc(one)

def get_single_elem(tree, path):
    node = tree.xpath(path)
    if node == None or len(node) == 0:
        return "na"
    return cleanup(node[0].text)

def get_elems(tree, path):
    node = tree.xpath(path)
    if node == None or len(node) == 0:
        return []
    return node

def get_text(elem):
    pass

def process_doc(one):
    res = collections.OrderedDict()
    with open(one, "r") as fp:
        content = fp.read()
    try:
        tree = html.fromstring(content)
    except Exception as e:
        print("excep parsing " + e.message)
        #sys.exit(0)
        return res
    title = get_single_elem(tree, "//title").replace("_百度知道", "")
    res["title"] = title
    sim_q = get_elem_text(tree, "//div[@id='wgt-related']/div/ul/li/a", title)
    #print("sim " + "##".join(sim_q))
    res["sim"] = sim_q
    related = get_elem_text(tree, "//div[@id='wgt-topic']/ul/li/a", title)
    res["rel"] = related

    category = get_elem_text(tree, "//*[@id='body']/div/div/nav[@class='wgt-nav f-12']/a", "百度知道")
    if len(category) > 0:
        res["category"] = category

    #print_list("related", related)
    topic = get_single_elem(tree, "//*[@id='wgt-topic']/h2/em")
    res["topic"] = topic
    return res

def print_list(str, arr):
    print(str)
    for s in arr:
        print s


def get_elem_text(tree, path, title):
    nodes = tree.xpath(path)
    questions = []
    for node in nodes:
        allnodes = node.xpath("node()")
        oneq = ""
        for nd in allnodes:
            if isinstance(nd, basestring):
                tx = nd
            elif nd.tag == "span" and "f-red in nd.attrib":
                continue
            else:
                tx = nd.text
            tx = cleanup(tx)
            if len(tx) == 0:
                continue
            oneq += tx
        if len(oneq) == 0 or oneq in questions or title == oneq or oneq == '[百度经验]':
            continue
        questions.append((oneq))
    return questions


def cleanup(tx):
    if tx is None:
        return ""
    tx = tx.strip().replace("\n", "").replace("\t", ",").replace("？", " ").replace("！", "").replace("?", "") \
        .replace("!", "").strip()
    tx = re.sub(",+", ",", tx)
    return tx


def process_docs(BASE, fws, fwr):
    files = os.listdir(BASE)
    i = 1
    for fname in files:
        if i % 1000 == 0:
            print("proc " + str(i))
            #break
        i += 1
        res = process_doc(BASE+fname)

        if len(res) == 0:
            continue
        res["id"] = fname
        cat = []
        if "category" in res:
            cat = res["category"]
        if "title" in res and "sim" in res:
            q1=res["title"]
            simq = res["sim"]
            for q2 in simq:
                line = q1+"\t" + q2 +"\t" + " ".join(cat)
                if should_drop(line):
                    continue
                #line = wenda_proc.change_encoding(line, "utf-8", gb_default_encoding)
                write( line + "\n", fws, fname )
        if "title" in res and "rel" in res and "topic" in res:
            topic = res["topic"]
            if len(topic) > 3:
                continue
            q1=res["title"]
            rels = res["rel"]
            for q2 in rels:
                line = q1+"\t" + q2 + "\t" + " ".join(cat)
                if should_drop(line):
                    continue
                write( line + "\n", fwr, fname )


def write(content, fw, name):
    try:
        fw.write(content)
    except Exception as e:
        print(e.message, content, name)

def get_result_jsonv2(dir):
    fws = codecs.open(DATA_ROOT + "filtered/baidu_sim.tsv", "w")
    fwr = codecs.open(DATA_ROOT +"filtered/baidu_rel.tsv", "w")
    # too big to combine and save together
    #process_docs(dir_name1, fws, fwr)
    process_docs(dir, fws, fwr)
    fws.close()
    fwr.close()

def output_qq(results, fws, fwr):
    for res in results:
        if "title" in res and "sim" in res:
            q1=res["title"]
            simq = res["sim"]
            for q2 in simq:
                line = q1+"\t" + q2
                if should_drop(line):
                    continue
                #line = wenda_proc.change_encoding(line, "utf-8", gb_default_encoding)
                fws.write( line + "\n" )
        if "title" in res and "rel" in res and "topic" in res:
            topic = res["topic"]
            if len(topic) > 3:
                continue
            q1=res["title"]
            rels = res["rel"]
            for q2 in rels:
                line = q1+"\t" + q2
                if should_drop(line):
                    continue
                fwr.write( line + "\n" )


def get_result_json():
    res1 = process_docs(dir_name1)
    res2 = process_docs(dir_name1)
    res = res1 + res2
    output_qq(res)
    res = json.dumps(res, indent=2)
    # just to read. don't process. there may be double quotes eg "a"b""
    str_symptom = str(res).replace('u\'','\'')
    decoded = str_symptom.decode("unicode-escape")
    with open("result_read.json", "w") as fw:
        fw.write(decoded)
    with open("result.json", "w") as fw:
        fw.write(res)


def output_qq(results):
    with codecs.open(DATA_ROOT + "filtered/baidu_sim.tsv", "w",) as fws, codecs.open(DATA_ROOT +"filtered/baidu_rel.tsv", "w") as fwr:
        for res in results:
            if "title" in res and "sim" in res:
                q1=res["title"]
                simq = res["sim"]
                for q2 in simq:
                    line = q1+"\t" + q2
                    if should_drop(line):
                        continue
                    #line = wenda_proc.change_encoding(line, "utf-8", gb_default_encoding)
                    fws.write( line + "\n" )
            if "title" in res and "rel" in res and "topic" in res:
                topic = res["topic"]
                if len(topic) > 3:
                    continue
                q1=res["title"]
                rels = res["rel"]
                for q2 in rels:
                    line = q1+"\t" + q2
                    if should_drop(line):
                        continue
                    fwr.write( line + "\n" )


def cleanup_qq():
    # json load failed wrong with "成语"狐假虎威"的寓意",
    with open("filtered/wenda_qq_pagesim.tsv", "w") as fw:
        with codecs.open("filtered/baidu_simq.tsv", "r", encoding="utf-8") as fp:
            lines = fp.readlines()
            for line in lines:
                if should_drop(line):
                    continue
                #line = wenda_proc.change_encoding(line, "utf-8", "GB18030")
                fw.write(line.strip() +"\n")


def should_drop(line):
    for st in wenda_proc.STOP:
        if st in line:
            return True
    ww = line.split("\t")
    if len(ww) <= 1:
        return True
    try:
        if len(ww[0]) > wenda_proc.MAX_COUNT_Q or len(ww[1]) > wenda_proc.MAX_COUNT_Q or \
                        len(ww[0]) < wenda_proc.MIN_COUNT_Q or len(ww[1]) < wenda_proc.MIN_COUNT_Q:
            return True
    except Exception as e:
        print (e.message, line)

    return False


def combine_labeled_data():
    fname_neg = DATA_ROOT + "filtered/bdv2/baidu_rel.tsvwb"
    fname_pos = DATA_ROOT +  "filtered/bdv2/baidu_sim.tsvwb"
    fname_all = DATA_ROOT + "filtered/bdv2/baidu_qq.tsv"
    result = []
    dict = set()

    cont1 = util.readlines_from_file(fname_neg)
    idx, tot = 0, 0
    while idx < (len(cont1) - 1):
        vals = cont1[idx].split("\t")
        idx += 1
        if not len(vals) == 2:
            continue
        w1 = cleanup(vals[0])
        w2 = cleanup(vals[1])
        if not check_negative(w1, w2):
            continue
        dict.add(w1)
        dict.add(w2)
        result.append(w1 + "\t" + w2 + "\t0\n")
        tot += 1

    cont2 = util.readlines_from_file(fname_pos)
    idx = 0
    while idx < min(len(cont2), tot):  # not too many pos
        vals = cont2[idx].split("\t")
        idx += 1
        if not len(vals) == 2:
            continue

        w1 = cleanup(vals[0])
        w2 = cleanup(vals[1])
        idx += 1
        #if not w1 in dict and not w2 in dict:
        #    continue
        result.append(w1 + "\t" + w2+ "\t1\n")

    random.shuffle(result)

    with codecs.open(fname_all, "w", "gbk") as fw:
        for res in result:
            fw.write(res)

    idx = 0
    with codecs.open(fname_all+".new", "w", "gbk") as f1:
        while idx < 1*len(result):
            f1.write(result[idx])
            idx += 1

    '''with codecs.open(fname_all+".2", "w", "gbk") as f1:
        while idx < 0.66*len(result):
            f1.write(result[idx])
            idx += 1

    with codecs.open(fname_all+".3", "w", "gbk") as f1:
        while idx < len(result):
            f1.write(result[idx])
            idx += 1'''

def check_negative(w1, w2):
    vals1 = w1.split(" ")
    vals2 = w2.split(" ")
    cnt  = 0.0
    for v in vals1:
        if v in vals2:
            cnt += 1
    if cnt/len(vals1) >= 0.5:
        return False
    return True

def data_vote():
    idx = []
    d1 = read_data(DATA_ROOT + "filtered/bdv2/pred1.tsv")
    d2 = read_data(DATA_ROOT + "filtered/bdv2/pred2.tsv")
    d3 = read_data(DATA_ROOT + "filtered/bdv2/pred3.tsv")
    fw = open(DATA_ROOT + "filtered/bdv2/pred.tsv", "w")
    for i in range(len(d1)):
        if d1[i] == d2[i]:
            toapp = d1[i]
        elif d1[i] == d3[i]:
            toapp = d1[i]
        elif d2[i] == d3[i]:
            toapp = d2[i]
        else:
            continue
        fw.write(toapp + "\n")
        idx.append(toapp)
    fw.close()
    return idx


def intercept():
    idx = data_vote()
    data = util.readlines_from_file(DATA_ROOT + "filtered/bdv2/baidu_qq.tsv.new")
    fw = open(DATA_ROOT + "filtered/bdv2/join.tsv", "w")
    for i in range(len(idx)):
        line = idx[i].strip().replace("__label__", "")
        if len(line) == 0:
            continue
        label = data[i].strip().split("\t")[2]
        if label == line:
            fw.write(data[i] +"\n")
    fw.close()


def read_data(fname):
    lines = util.readlines_from_file(fname)
    data = []
    for line in lines:
        vals = line.split(" ")
        data.append(vals[0].strip())
    return data


def proc_score():
    fname="C:\\Workspace\\Data\\wenda\\filtered\\bdv2\\odmodel_newdata\\pred.tsv"
    data = util.readlines_from_file(fname)
    with open(fname+"2", "w") as fw:
        for line in data:
            vals = line.split("\t")
            if len(vals) <= 1:
                continue
            lab = int(vals[0])
            if lab == 1:
                fw.write(line+"\n")
            else:
                s1 = (float)(vals[1])
                s2 = 1 - s1
                fw.write("0\t" + str(s2) + "\n")


def gen_label():
    fname1 = "C:\\Workspace\\Data\\wenda\\filtered\\bdv2\\odmodel_newdata\\baidu_qq.tsv.new"
    fname2="C:\\Workspace\\Data\\wenda\\filtered\\bdv2\\odmodel_newdata\\pred.tsv2"
    data1 = util.readlines_from_file(fname1)
    data2 = util.readlines_from_file(fname2)
    c1,c2=[],[]
    for d1 in data1:
        vals = d1.split("\t")
        if not len(vals) == 3 :
            continue
        c1.append(vals[2])

    for d2 in data2:
        vals = d2.split("\t")
        if not len(vals) == 2:
            continue
        c2.append(vals[1])
    if not len(c1) == len(c2):
        print "wrong"
    with open(fname1+".label", "w") as fw:
        for i in range(len(c1)):
            fw.write(c1[i] + "\t" + c2[i] + "\n")


def gen_questions():
    content = util.readlines_from_file(DATA_ROOT + "/qclick/wenda_q2q_v2.dat")
    dedup = set()
    with open(DATA_ROOT + "/qclick/wenda_questions.txt", "w") as fw:
        for line in content:
            vals = line.split("\t")
            if not len(vals) == 2:
                continue
            if len(vals[1]) <= wenda_proc.MIN_COUNT_Q or len(vals[1]) >= wenda_proc.MAX_COUNT_Q:
                continue
            if vals[1] in dedup:
                #print("dup " + vals[1])
                continue
            dedup.add(vals[1])
            fw.write(vals[1] + "\n")


def get_qq_es(fname):
    data = util.readlines_from_file(fname)
    with open(fname+".qq", "w") as fw:
        q1,q2="",""
        for line in data:
            line = line.strip()
            if line.startswith("input:"):
                q1 = line[len("input:"):]
            else:
                if len(line) == 0:
                    continue
                idx = line.rfind(" ")
                q2 = line[0:idx]
                fw.write(q1 + "\t" + q2+ "\t-1\n")


if __name__=="__main__":
    #get_qq_es(sys.argv[1])
    #fname = "crawler/409771957"
    #fname = "crawler/199191146.html"
    #get_result_jsonv2()
    #process_docs(dir_name3)
    #expand_qq()
    #get_result_json("crawler/1/")
    get_result_jsonv2(dir_name3)
    #combine_labeled_data()
    #intercept()
    #gen_label()
    #gen_questions()
    #print("\n".join(idx))


