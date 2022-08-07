import requests
import os
import time
import json
import pprint

# 设置开始 #

# cookie
cookie = "buvid3=63B1C902-3DD5-CD46-85D8-9A69679BC65665004infoc; CURRENT_FNVAL=80; blackside_state=1; sid=6aaqymp9; rpdid=|(u)mJ~Rlll~0J'uYkR||uuYm; fingerprint=33bf6967b63128e997c2ee0e3659a990; buvid_fp=63B1C902-3DD5-CD46-85D8-9A69679BC65665004infoc; buvid_fp_plain=63B1C902-3DD5-CD46-85D8-9A69679BC65665004infoc"
# 结果数据保存路径(默认留空为'./')
file_dir = ""
# 仅爬取楼主
parentOnly = False
# 1,2最新评论(时间);3热门评论(热度)
comment_mode = 2
# 调试模式,在目录生成一个log文件,存放json原始内容
DebugMode = False

# 设置结束 #

def visit(bv):
	''' 访问av/BV对应的网页,查看是否存在 '''

	if bv[:2] == 'BV' or bv[:2] == 'av':	# 过滤av/BV号
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
		return False
	if response.status_code == 404 or """<div class="error-text">啊叻？视频不见了？</div>""" in response.text:
		print('视频不存在!')
		return False
	else:
		return True

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

def parseContent(js, parent=True):
	''' 解析评论json  \n js: 单条评论json  \n parent: 是否为楼主 '''
	try:
		content = {
			# 'floor': js['floor'] if('floor' in js) else '',	# 楼层
			'floor': '---' if(parent) else '  |',	# 是否楼主
			'time': str(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(js['ctime']))),# 时间
			'like': str(js['like']),		# 赞数
			'uid': js['member']['mid'],		# uid
			'name': js['member']['uname'],	# 用户名
			'sex': '-' if(js['member']['sex']=='保密')else js['member']['sex'],	# 性别
			'level': str(js['member']['level_info']['current_level']),	# 用户等级
			'location': js['reply_control']['location'].split('：')[1] if('location' in js['reply_control'])else '',	# IP属地,仅登录状态包含
			'content': '"' + js['content']['message'] + '"'# 评论内容
			}
	except KeyError:
		print('读取评论详情错误!')
		exit()
	return content

def get(bv, page=0, id=3, parent=True):
	''' 获取父评论或子评论json  \n bv: 全bv号  \n page: pn/next页码  \n id共用参数: 父评论mode:1楼层,2时间,3热门;子评论为rpid  \n parent: 是否为父评论 '''

	if(parent):
		# 父评论url
		r_url = 'https://api.bilibili.com/x/v2/reply/main'
	else:
		# 子评论url
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
		# 'callback': 'jQuery172030289933285891424_' + str(time.time()*1000)[:13],
		'jsonp': 'jsonp',
		'next': page,	# 页码next
		'type': '1',
		'oid': av,	# av号数字
		'mode': id,	# 1:楼层大前小后, 2:时间晚前早后, 3:热门评论先后
		'plat': '1',
		'_': str(time.time()*1000)[:13],	# 时间戳
	}if(parent) else{
		# 'callback': 'jQuery172030289933285891424_' + str(time.time()*1000)[:13],
		'jsonp': 'jsonp',
		'pn': page,	# pn,pagenumber
		'type': '1',
		'oid': av,	# av号数字
		'ps': '10',
		'root': id,	# 父评论的rpid
		'_': str(time.time()*1000)[:13],	# 时间戳
	}
	response = requests.get(r_url, headers = headers, params=data)
	response.encoding = 'utf-8'

	if DebugMode:
		with open('./log.txt', 'a', encoding='utf-8') as fp:
				fp.write(response.text + '\n\n')

	if('\"code\":0,' in response.text):
		# 将得到的json文本转化为可读json
		cr_json = json.loads(response.text)
	else:
		print('获取评论json错误!')
		print(response.status_code)
		print(response.text)
		exit()

	return cr_json

def parse_comment_r(bv, rpid):
	''' 解析子评论json  \n bv: 全bv号  \n rpid: reply_id '''

	cr_json = get(bv, id=rpid, parent=False)['data']
	count = cr_json['page']['count']
	replyCsv = ''

	for pn in range(1,count//10+2):
		print('p%d %d  ' % (pn,count), end='\r')
		cr_json = get(bv, id=rpid, page=pn, parent=False)['data']
		time.sleep(0.1)
		cr_list = cr_json['replies']
		if cr_list:	# 有时'replies'为'None'
			for i in range(len(cr_list)):
				# 添加评论
				replyCsv += ','.join(parseContent(cr_list[i], False).values()) + '\n'
	return replyCsv

def parse_comment(bv):
	''' 解析父评论json '''

	c_json = get(bv, id=comment_mode)
	csv = ''

	try:
		# 总评论数
		count_all = c_json['data']['cursor']['all_count']
		print('comments:%d' % count_all)
	except KeyError:
		print('KeyError, 该视频可能没有评论!')
		return '0', '2'	# 找不到键值

	# 置顶评论
	if c_json['data']['top']['upper']:
		comment_top = c_json['data']['top']['upper']
		csv += ','.join(parseContent(comment_top, parent=True).values()) + '\n'
		if((not parentOnly) and (comment_top['rcount'] or ('replies' in comment_top and comment_top['replies']))):
			rpid_f = comment_top['rpid']	# 父评论的rpid
			csv += parse_comment_r(bv, rpid_f)

	# 开始序号
	count_next = 0

	for page in range(count_all //20 +1):
		print('page:%d' % (page+1))

		c_json = get(bv, page=count_next, id=comment_mode)
		time.sleep(0.1)
		if not c_json:
			return 1	# json错误
		count_next = c_json['data']['cursor']['next']	# 下一个的序号

		# 评论列表
		c_list = c_json['data']['replies']

		# 有评论,就进入下面的循环保存
		if c_list:
			for i in range(len(c_list)):
				# 添加楼主评论
				csv += ','.join(parseContent(c_list[i], parent=True).values()) + '\n'

				# 若有子评论且要爬取子评论,记录rpid,爬取子评论
				if((not parentOnly) and (c_list[i]['rcount'] or ('replies' in c_list[i] and c_list[i]['replies']))):
					rpid = c_list[i]['rpid']
					csv += parse_comment_r(bv, rpid)

			if c_json['data']['cursor']['is_end']:
				print('读取完毕,结束')
				# 为最后一个json,结束爬取
				break
		else:
			print('评论为空,结束!')
			break
	return 	csv

def main():
	global file_dir

	bv = input('input av/BV/url:')
	if '/' in bv or '?' in bv:
		# 分解链接
		bv = bv.split('?')[0].split('/')[-1]
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

	# 获取处理好的csv文件和原始json
	csv= parse_comment(bv)

	# 保存评论csv,若csv文件不存在,创建并写入标题行
	csv_dir = file_dir + 'V_' + bv + '.csv'
	if not os.path.exists(csv_dir):
		with open(csv_dir, 'w', encoding='utf-8-sig') as fp:
			fp.write('楼层,评论时间,点赞数,uid,用户名,性别,等级,IP属地,评论内容\n')
	while True:
		try:
			with open(csv_dir, 'a', encoding='utf-8') as fp:
				fp.write(csv)
			break
		except PermissionError:
			input('文件被占用!!! (关闭占用的程序后,回车重试)')

if __name__ == "__main__":
	main()
	print('=== over! ===')
