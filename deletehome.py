import re
import os
import json
import codecs

def extract_url(file_name):
    with codecs.open(file_name, 'rt', encoding='utf-8') as f:
        data = json.load(f)
        url = data['url']
    return url


def delete_file(word):
    for i in range(12000):
        file_zh = 'json_file/web' + str(i) + '.json'
        file_en = 'json_file/web' + str(i) + '_en.json'
        try:
            url_zh = extract_url(file_zh)
            if url_zh.split('/')[4] == word:
                os.remove(file_zh)
        except Exception as e:
            print 'Error: ' + str(e)
        else:
            print 'Delete zh-CN file succeed'

        try:
            url_en = extract_url(file_en)
            if url_en.split('/')[3] == 'home':
                os.remove(file_en)
        except Exception as e:
            print 'Error: ' + str(e)
        else:
            print 'Delete en-US file succeed'


if __name__ == '__main__':
    url = extract_url('web4312.json')
    _word = url.split('/')[4]
    delete_file(_word)