import requests
import os
import time
import json
from datetime import datetime
import re

class BiliVideoCommentCrawler():
	""" url: 链接或BV/av号  \n cookie  \n commentMode: 内容模式  \n dirF: 存储路径  \n child: 是否包含子评论  \n at: 是否包含@回复  \n debug: 调试模式 """

	def __init__(self, url, cookie, commentMode=2, dirF='./', child=True, at=True, debug=False):

		self.log('初始化')
		self.debug = debug
		self.dir = dirF if(dirF) else './'
		# 从输入中获取BV/av
		self.BV = url.split('?')[0].split('/')[-1]
		self.url = f'https://www.bilibili.com/video/{self.BV}'
		self.reqTimeout = (4, 10)
		self.timeSleep = 0.2
		if(not self.check()):
			self.log('BV Error!')
			return
		self.Bta()
		self.cookie = cookie
		self.child = child
		self.commentMode = commentMode
		self.at = at
		self.json = ''
		self.csv = '楼层,评论时间,点赞数,uid,用户名,性别,等级,IP属地,评论内容\n'

	def log(self, message, end='\n'):
		''' 输出信息 '''
		print(datetime.now().strftime('%y-%m-%d %H:%M:%S.%f')[:-3], message, sep='\t', end=end)

	def Bta(self):
		''' BV号转化为av号,如果已经是av号,直接返回数字部分,cv9646821方法 '''

		# self.BV BV+字母数字 或 av+数字; self.av 文本型纯数字
		bv = self.BV
		if(bv[:2] == 'av'):
			self.av = bv[2:]
		else:
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
			self.av = str((sum(bv) - 100618342136696320) ^ 177451812)

	def check(self):
		''' 访问av/BV对应的网页,查看是否存在 '''

		if(self.BV[:2] == 'BV' or self.BV[:2] == 'av'):	# 过滤av/BV号
			headers = {
			#	'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
				'accept-encoding': 'gzip, deflate',
				'accept-language': 'zh-CN,zh;q=0.9',
				'referer': 'https://www.bilibili.com/',
				'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
				'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.106 Safari/537.36',
			}
			response = requests.get(self.url, headers = headers, timeout=self.reqTimeout)
		else:
			self.log('视频不存在!')
			return False
		if(response.status_code == 404 or """<div class="error-text">啊叻？视频不见了？</div>""" in response.text):
			self.log('视频不存在!')
			return False
		else:
			self.log('视频存在')
			return True

	def save(self):
		""" 保存json, csv """

		# 处理存储路径
		if(self.dir[-1] != '/' or self.dir[-1] != '\\'):
			self.dir += '/'
		if(not os.path.exists(self.dir)):
			self.log('存储路径不存在...', end='\t')
			os.mkdir(self.dir)
			print('已自动创建!')

		# 保存返回的json
		if(self.debug and self.json):
			with open(f'{self.dir}V_{self.BV}.txt', 'w', encoding='utf-8') as fp:
				fp.write(self.json)
		self.log('json保存完成')

		# 保存评论csv
		if(self.csv):
			csv_dir = f'{self.dir}V_{self.BV}.csv'
			# (创建)并写入csv文件
			if(not os.path.exists(csv_dir)):
				with open(csv_dir, 'w', encoding='utf-8-sig') as fp:
					fp.write(self.csv)
			else:
				while True:
					try:
						with open(csv_dir, 'a', encoding='utf-8-sig') as fp:
							fp.write('\n' + self.csv)
						break
					except PermissionError:
						self.log('csv文件被占用!!! (关闭占用的程序后,回车重试)', end='')
						input()
		self.log('csv保存完成')

	def parseContent(self, js, parent=True):
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
				'content': '"' + js['content']['message'] + '"' if self.at else '"' + re.sub("^回复 @(.){0,16}? :", '', js['content']['message']) + '"'	# 评论内容
				}
		except KeyError:
			log('读取评论详情错误!')
			return
		return content

	def get(self, page=0, rpid=0, parent=True):
		''' 获取父评论或子评论json  \n page: pn/next页码  \n id共用参数: rpid:子评论id  \n parent: 是否为父评论	\n ps: 子评论每页条数 '''

		if(parent):
			# 父评论url
			r_url = 'https://api.bilibili.com/x/v2/reply/main'
		else:
			# 子评论url
			r_url = 'https://api.bilibili.com/x/v2/reply/reply'
		headers = {
			'accept': '*/*',
			'accept-encoding': 'gzip, deflate, br',
			'accept-language': 'zh-CN,zh;q=0.9',
			'cache-control': 'no-cache',
			'cookie': self.cookie,
			'pragma': 'no-cache',
			'referer': self.url,
			'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
			'sec-ch-ua-mobile': '?0',
			'sec-fetch-dest': 'script',
			'sec-fetch-mode': 'no-cors',
			'sec-fetch-site': 'same-site',
			'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.106 Safari/537.36',
		}
		data = {
			'jsonp': 'jsonp',
			'next': page,	# 页码next
			'type': '1',
			'oid': self.av,	# av号数字
			'mode': self.commentMode,	# 12时间,3热门
			'plat': '1',
			'_': str(time.time()*1000)[:13],	# 时间戳
		}if(parent) else{
			'jsonp': 'jsonp',
			'pn': page,	# pn,pagenumber
			'type': '1',
			'oid': self.av,	# av号数字
			'ps': 20,	# 最大20,默认10
			'root': rpid,
			'_': str(time.time()*1000)[:13],	# 时间戳
		}
		response = requests.get(r_url, headers = headers, params=data, timeout=self.reqTimeout)
		response.encoding = 'utf-8'

		if(self.debug):
			self.json += response.text + '\n\n'

		if('\"code\":0,' in response.text):
			# 文本转化为json
			cr_json = json.loads(response.text)
		else:
			self.log('获取评论json错误!')
			print(response.status_code)
			print(response.text)
			return
		return cr_json

	def parse_comment_r(self, rpid, count):
		''' 解析子评论json  \n rpid: replyid  \n count: 子评论数量 '''

		# cr_json = self.get(rpid=rpid, parent=False)['data']
		# count = cr_json['page']['count']

		for pn in range(1, count//20+1):
			print('p%d %d  ' % (pn,count), end='\r')
			cr_list = self.get(rpid=rpid, page=pn, parent=False)['data']['replies']
			time.sleep(self.timeSleep)
			if(cr_list):	# 有时'replies'为'None'
				for i in range(len(cr_list)):
					# 添加评论
					self.csv += ','.join(self.parseContent(cr_list[i], False).values()) + '\n'

	def parse_comment(self, count_next=0):
		''' 解析楼主评论json  \n count_next: 开始序号'''

		c_json = self.get()

		# 总评论数
		try:
			count_all = c_json['data']['cursor']['all_count']
			self.log('comments: %d' % count_all)
		except KeyError:
			self.log('KeyError, 该视频可能没有评论!')
			return

		# 置顶评论
		if(c_json['data']['top']['upper']):
			comment_top = c_json['data']['top']['upper']
			self.csv += ','.join(self.parseContent(comment_top, parent=True).values()) + '\n'
			if(self.child and (comment_top['count'] or ('replies' in comment_top and comment_top['replies']))):
				self.parse_comment_r(comment_top['rpid'], comment_top['count'])

		for page in range(count_all //20 +1):
			self.log('page: %d' % (page+1))

			c_json = self.get(page=count_next)
			time.sleep(self.timeSleep)
			if(not c_json):
				return
			count_next = c_json['data']['cursor']['next']	# 下一个的序号

			# 评论列表
			c_list = c_json['data']['replies']

			# 有评论,就进入下面的循环保存
			if(c_list):
				for i in range(len(c_list)):
					# 添加楼主评论
					self.csv += ','.join(self.parseContent(c_list[i], parent=True).values()) + '\n'

					# 若有子评论且要爬取子评论,记录rpid,爬取子评论
					if(self.child and (c_list[i]['count'] or ('replies' in c_list[i] and c_list[i]['replies']))):
						self.parse_comment_r(c_list[i]['rpid'], c_list[i]['count'])

				if(c_json['data']['cursor']['is_end']):
					# 为最后一个json,结束爬取
					self.log('读取完毕,结束')
					break
			else:
				self.log('评论为空,结束!')
				break

	def begin(self):
		''' 自动开始爬取并保存 '''

		if(self.debug):
			self.parse_comment()
			self.save()
		else:
			try:
				self.parse_comment()
			except Exception as e:
				self.log(e)
			finally:
				# 中断时保证将已处理的评论保存
				self.save()

if __name__ == "__main__":

	cookie = "buvid3=63B1C902-3DD5-CD46-85D8-9A69679BC65665004infoc; CURRENT_FNVAL=80; blackside_state=1; sid=6aaqymp9; rpdid=|(u)mJ~Rlll~0J'uYkR||uuYm; fingerprint=33bf6967b63128e997c2ee0e3659a990; buvid_fp=63B1C902-3DD5-CD46-85D8-9A69679BC65665004infoc; buvid_fp_plain=63B1C902-3DD5-CD46-85D8-9A69679BC65665004infoc"

	demo = BiliVideoCommentCrawler(input('输入链接或BV/av号: '), cookie)
	demo.debug = False
	demo.begin()
	print('=== over! ===')
