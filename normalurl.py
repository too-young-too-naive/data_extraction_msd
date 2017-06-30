from urllib2 import quote

x = 'https://www.msdmanuals.com/zh/%E9%A6%96%E9%A1%B5/%E5%A4%96%E4%BC%A4%E5%92%8C%E4%B8%AD%E6%AF%92/%E5%92%AC%E4%BC%A4%E5%92%8C%E8%9E%AB%E4%BC%A4/%E5%8A%A8%E7%89%A9%E5%92%AC%E4%BC%A4?sc_camp='
fullurl = quote(x.encode('utf-8'), safe="%/:=&?~#+!$,;'@()*[]")
print fullurl
