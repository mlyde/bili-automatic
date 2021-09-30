import requests
import os
import time
import json

# 设置 #

# cookie 与 数据保存路径(默认留空为'./')
cookie = "buvid3=63B1C902-3DD5-CD46-85D8-9A69679BC65665004infoc; CURRENT_FNVAL=80; blackside_state=1; sid=6aaqymp9; rpdid=|(u)mJ~Rlll~0J'uYkR||uuYm; fingerprint=33bf6967b63128e997c2ee0e3659a990; buvid_fp=63B1C902-3DD5-CD46-85D8-9A69679BC65665004infoc; buvid_fp_plain=63B1C902-3DD5-CD46-85D8-9A69679BC65665004infoc"
file_dir = ""
# 1:评论(楼层);2:最新评论(时间);3:热门评论(热度)
comment_mode = 3

# 设置 #

def visit(bv):
    ''' 访问av/BV对应的网页,查看是否存在 '''

    if bv[:2] == 'BV' or bv[:2] == 'av':
        url = 'https://www.bilibili.com/video/' + bv
        headers = {
        #	'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-encoding': 'gzip, deflate',
            'accept-language': 'zh-CN,zh;q=0.9',
            'referer': 'https://www.bilibili.com/',
            'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.106 Safari/537.36',
        }
        response = requests.get(url, headers = headers)
    else:
        print('视频不存在!')
        return 0
    if response.status_code == 404 or """<div class="error-text">啊叻？视频不见了？</div>""" in response.text:
        print('视频不存在!')
        return 0
    else:
        return 1

def Bta(bv):
    ''' 将BV号转化为av号,如果已经是av号,直接返回数字部分(文本类型),方法参考cv9646821 '''

    if bv[:2] == 'av':
        return bv[2:]
    bv = list(bv[2:])
    keys = {'1': 13, '2': 12, '3': 46, '4': 31, '5': 43, '6': 18, '7': 40, '8': 28, '9': 5,
            'A': 54, 'B': 20, 'C': 15, 'D': 8, 'E': 39, 'F': 57, 'G': 45, 'H': 36, 'J': 38, 'K': 51, 'L': 42, 'M': 49, 'N': 52, 'P': 53, 'Q': 7, 'R': 4, 'S': 9, 'T': 50, 'U': 10, 'V': 44, 'W': 34, 'X': 6, 'Y': 25, 'Z': 1,
            'a': 26, 'b': 29, 'c': 56, 'd': 3, 'e': 24, 'f': 0, 'g': 47, 'h': 27, 'i': 22, 'j': 41, 'k': 16, 'm': 11, 'n': 37, 'o': 2, 'p': 35, 'q': 21, 'r': 17, 's': 33, 't': 30, 'u': 48, 'v': 23, 'w': 55, 'x': 32, 'y': 14, 'z': 19}
    for i in range(len(bv)):
        bv[i] = keys[bv[i]]
    bv[0] *= (58 ** 6)
    bv[1] *= (58 ** 2)
    bv[2] *= (58 ** 4)
    bv[3] *= (58 ** 8)
    bv[4] *= (58 ** 5)
    bv[5] *= (58 ** 9)
    bv[6] *= (58 ** 3)
    bv[7] *= (58 ** 7)
    bv[8] *= 58
    return str((sum(bv) - 100618342136696320) ^ 177451812)

def send_f(bv, nexts=0, mode=3):
    ''' 返回父评论json  \n bv: 全bv号  \n nests: json页码  \n mode: 1楼层,2时间,3热门 '''

    r_url = 'https://api.bilibili.com/x/v2/reply/main'
    url = 'https://www.bilibili.com/video/' + bv
    av = Bta(bv)
    headers = {
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9',
        'cache-control': 'no-cache',
        'cookie': cookie,
        'pragma': 'no-cache',
        'referer': url,
        'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
        'sec-ch-ua-mobile': '?0',
        'sec-fetch-dest': 'script',
        'sec-fetch-mode': 'no-cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.106 Safari/537.36',
    }
    data = {
        # 'callback': 'jQuery172030289933285891424_' + str(time.time()*1000)[:13],
        'jsonp': 'jsonp',
        'next': nexts,	# 页码
        'type': '1',
        'oid': av,		# av号
        'mode': mode,	# 1:楼层大前小后, 2:时间晚前早后, 3:热门评论
        'plat': '1',
        '_': str(time.time()*1000)[:13],	# 时间戳
    }
    response = requests.get(r_url, headers = headers, params = data)
    response.encoding = 'utf-8'

    # 将得到的json文本转化为可读json
    if 'code' in response.text:
        c_json = json.loads(response.text)
    else:
        c_json = {'code': -1}
    if c_json['code'] != 0:
        print('json error!')
        print(response.status_code)
        print(response.text)
        return 0	# 读取错误
    return c_json

def send_r(bv, rpid, pn=1):
    ''' 返回子评论json  \n bv: 全bv号  \n rpid: 父评论的id  \n pn: 子评论的页码 '''

    r_url = 'https://api.bilibili.com/x/v2/reply/reply'
    url = 'https://www.bilibili.com/video/' + bv
    av = Bta(bv)
    headers = {
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9',
        'cache-control': 'no-cache',
        'cookie': cookie,
        'pragma': 'no-cache',
        'referer': url,
        'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
        'sec-ch-ua-mobile': '?0',
        'sec-fetch-dest': 'script',
        'sec-fetch-mode': 'no-cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.106 Safari/537.36',
    }
    data = {
        # 'callback': 'jQuery172040348849791483166_' + str(time.time()*1000)[:13],
        'jsonp': 'jsonp',
        'pn': pn,	# pagenumber
        'type': '1',
        'oid': av,
        'ps': '10',
        'root': rpid,	# 父评论的rpid
        '_': str(time.time()*1000)[:13],	# 时间戳
    }
    response = requests.get(r_url, headers = headers, params=data)
    response.encoding = 'utf-8'

    # 将得到的json文本转化为可读json
    if 'code' in response.text:
        cr_json = json.loads(response.text)
    else:
        cr_json = {'code': -1}
    if cr_json['code'] != 0:
        print('error!')
        print(response.status_code)
        print(response.text)
        return 0	# 读取错误
    return cr_json

def parse_comment_r(bv, rpid):
    ''' 解析子评论json  \n bv: 全bv号  \n rpid: reply_id '''

    cr_json = send_r(bv, rpid)['data']
    count = cr_json['page']['count']
    csv_temp = ''
    for pn in range(1,count//10+2):
        print('p%d %d  ' % (pn,count), end='\r')
        cr_json = send_r(bv, rpid, pn=pn)['data']
        cr_list = cr_json['replies']
        if cr_list:	# 有时'replies'为'None'
            for i in range(len(cr_list)):
                comment_temp = {
                    'floor': '',
                    'time': time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(cr_list[i]['ctime'])),# 时间
                    'like': cr_list[i]['like'],				# 赞数
                    'uid': cr_list[i]['member']['mid'],		# uid
                    'name': cr_list[i]['member']['uname'],	# 用户名
                    'sex': cr_list[i]['member']['sex'],		# 性别
                    'content': '"' + cr_list[i]['content']['message'] + '"',	# 子评论
                }# 保留需要的内容
                for i in comment_temp:
                    csv_temp += str(comment_temp[i]) + ','
                csv_temp += '\n'
        time.sleep(0.1)
    return csv_temp

def parse_comment_f(bv):
    ''' 解析父评论json '''

    c_json = send_f(bv, mode=comment_mode)
    if c_json:
        # 总评论数
        try:
            count_all = c_json['data']['cursor']['all_count']
            print('comments:%d' % count_all)
        except KeyError:
            print('KeyError, 该视频可能没有评论!')
            return '0', '2'	# 找不到键值
    else:
        print('json错误')
        return 1	# json错误

    # 置顶评论
    if c_json['data']['top']['upper']:
        comment_top = c_json['data']['top']['upper']
        # csv = '%s,%s,%s,%s,%s,%s,%s\n' % (comment_top['floor'], 	# 楼层
        csv = '%s,%s,%s,%s,%s,%s,%s\n' % ('0', 	# 楼层
        time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(comment_top['ctime'])),# 时间
        comment_top['like'],			# 赞数
        comment_top['member']['mid'],	# uid
        comment_top['member']['uname'],	# 用户名
        comment_top['member']['sex'],	# 性别
        '"' + comment_top['content']['message'] + '"')# 评论内容
        if comment_top['rcount'] or ('replies' in comment_top and comment_top['replies']):
            rpid_f = comment_top['rpid']	# 父评论的rpid
            csv += parse_comment_r(bv, rpid_f)
    else:
        csv = ''

    # 开始序号
    count_next = 0

    # 存放原始json
    all_json = ''

    for page in range(count_all //20 +1):
        print('page:%d' % (page+1))

        c_json = send_f(bv, count_next, mode=comment_mode)
        all_json += str(c_json) + '\n'
        if not c_json:
            return 1	# json错误
        count_next = c_json['data']['cursor']['next']	# 下一个的序号

        # 评论列表
        c_list = c_json['data']['replies']

        # 有评论,就进入下面的循环保存
        if c_list:
            for i in range(len(c_list)):
                comment_temp = {
                    # 'floor': c_list[i]['floor'],			# 楼层
                    'floor': '0',			# 楼层
                    'time':  time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(c_list[i]['ctime'])),# 时间
                    'like': c_list[i]['like'],				# 赞数
                    'uid': c_list[i]['member']['mid'],		# uid
                    'name': c_list[i]['member']['uname'], 	# 用户名
                    'sex': c_list[i]['member']['sex'],		# 性别
                    'content': '"' + c_list[i]['content']['message'] + '"',	# 评论内容
                }# 保留需要的内容
                # 若有子评论,记录rpid,爬取子评论
                replies = False
                if c_list[i]['rcount'] or ('replies' in c_list[i] and c_list[i]['replies']):
                    replies = True
                    rpid = c_list[i]['rpid']

                for i in comment_temp:
                    csv += str(comment_temp[i]) + ','
                csv += '\n'

                # 如果有回复评论,爬取子评论
                if replies:
                    csv += parse_comment_r(bv, rpid)

            if c_json['data']['cursor']['is_end']:
                print('读取完毕,结束')
                # 为最后一个json,结束爬取
                break
        else:
            print('评论为空,结束!')
            break
        time.sleep(0.2)
    return 	csv, all_json

def main():
    global file_dir

    bv = input('input av/BV/url:')
    if '/' in bv or '?' in bv:
        # 分解链接
        bv = bv.split('/')[-1].split('?')[0]
    if not visit(bv):
        return

    # 处理存储路径
    if file_dir == '':
        file_dir = './'
    elif file_dir[-1] != '/' or file_dir[-1] != '\\':
        file_dir += '/'
    if not os.path.exists(file_dir):
        print('存储路径不存在...', end='')
        os.mkdir(file_dir)
        print('已自动创建!')
    dir_csv = file_dir + 'V_' + bv + '.csv'
    dir_txt = file_dir + 'V_' + bv + '.txt'

    # 如果是第一次写入文件,创建并写入标题
    if not os.path.exists(dir_csv):
        with open(dir_csv, 'w', encoding='utf-8-sig') as fp:
            fp.write('楼层,时间,点赞数,uid,用户名,性别,评论内容\n')

    csv, all_json = parse_comment_f(bv)

    # 将返回的json保存为txt,原始内容存档
    # with open(dir_txt, 'a', encoding='utf-8') as fp:
    # 	fp.write(all_json + '\n\n')

    # 保存评论csv
    while True:
        try:
            with open(dir_csv, 'a', encoding='utf-8') as fp:
                fp.write(csv)
            break
        except PermissionError:
            input('文件被占用!!! (关闭占用的程序后,回车重试)')

if __name__ == "__main__":
    main()
    print('=== over! ===')
