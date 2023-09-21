import requests, random, time, os
import json
# import brotli		# br压缩模块, pip安装后, request可自动使用
from collections import OrderedDict
from urllib3 import encode_multipart_formdata

class BlLiveSendMassage():

	def __init__(self, cookie:str=None, blackList:[int]=[], message:[str]=["Hello"]):

		self.cookie = cookie
		self.blackList = blackList
		self.message = message

		self.medals:list = []
		self.timeout = (20,40)
		self.proxies = {"http":None, "https":None}
		# self.proxies = {	# 代理
		# 	"http":"//127.0.0.1:10809",
		# 	"https":"//127.0.0.1:10809"
		# }

	def log(self, log:str = None):
		""" 输出日志信息 """
		if(log):
			print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) + '\t' + log)

	def doSign(self):
		""" 签到 """

		url = 'https://api.live.bilibili.com/xlive/web-ucenter/v1/sign/DoSign'
		headers = {
			'accept': 'application/json, text/plain, */*',
			'accept-encoding': 'gzip, deflate, br',
			'accept-language': 'zh-CN,zh;q=0.9',
			'cache-control': 'no-cache',
			'cookie': self.cookie,
			'origin': 'https://live.bilibili.com',
			'pragma': 'no-cache',
			'referer': 'https://live.bilibili.com/',
			'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
			'sec-ch-ua-mobile': '?0',
			'sec-fetch-dest': 'empty',
			'sec-fetch-mode': 'cors',
			'sec-fetch-site': 'same-site',
			'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
		}
		response = requests.get(url, headers=headers, timeout=self.timeout, proxies=self.proxies)
		message = json.loads(response.text)['message']
		self.log(message)

	def send(self,
		id:int = None,		# 直播间ID
		msg:str = None,		# 要发送的内容
		color:str = '16777215'	#'16777215'为普通颜色; '5566168'为5级粉丝牌可领取颜色...
	):
		""" 发送弹幕 """

		def randomBoundary():
			""" 生成随机的.. """

			factor = 'ABCDEFGHIGKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
			boundary = "----WebKitFormBoundary{}".format("".join(random.choices(factor, k=16)))
			# print(boundary)
			return boundary

		url = 'https://api.live.bilibili.com/msg/send'
		bili_jct = self.cookie.split('bili_jct=')[-1].split(';')[0]
		timestamp = time.time()
		boundary = randomBoundary()
		headers = {
			'accept': '*/*',
			'accept-encoding': 'gzip, deflate, br',
			'accept-language': 'zh-CN,zh;q=0.9',
			'cache-control': 'no-cache',
			# content-length: 980,
			'content-type': 'multipart/form-data; boundary=' + boundary,
			'cookie': self.cookie,
			'origin': 'https://live.bilibili.com',
			'pragma': 'no-cache',
			'referer': 'https://live.bilibili.com/' + str(id),
			'sec-ch-ua': 'Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90',
			'sec-ch-ua-mobile': '?0',
			'sec-fetch-dest': 'empty',
			'sec-fetch-mode': 'cors',
			'sec-fetch-site': 'same-site',
			'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
		}
		params = OrderedDict([
			("bubble", '0'),
			("msg", msg),
			('color', color),
			('mode', '1'),
			('fontsize', '25'),
			('rnd', str(timestamp)),
			('roomid', id),
			('csrf', bili_jct),
			('csrf_token', bili_jct)
		])
		data = encode_multipart_formdata(params, boundary=boundary)
		# self.log(data[0])
		response = requests.post(url=url, headers=headers, data=data[0], timeout=self.timeout, proxies=self.proxies)

		# post返回一个json,可用response.json()调用
		# self.log(response.text)

		# if '"code":0' in response.text:	# 判断是否发送成功
		# 	print('\t' + 'Success!')
		# else:
		# 	print('\t' + 'Error!')
		return response

	def getFansMedal(self):
		""" 获取粉丝勋章信息 """

		url = 'https://api.live.bilibili.com/xlive/app-ucenter/v1/fansMedal/panel?page=1&page_size=20'
		headers = {
			'accept': 'application/json, text/plain, */*',
			'accept-encoding': 'gzip, deflate, br',
			'accept-language': 'zh-CN,zh;q=0.9',
			'cache-control': 'no-cache',
			'cookie': self.cookie,
			'origin': 'https://live.bilibili.com',
			'referer': 'https://live.bilibili.com/',
			'sec-ch-ua': 'Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90',
			'sec-ch-ua-mobile': '?0',
			'sec-fetch-dest': 'empty',
			'sec-fetch-mode': 'cors',
			'sec-fetch-site': 'same-site',
			'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
		}

		response = requests.get(url=url, headers=headers, timeout=self.timeout, proxies=self.proxies)
		data = json.loads(response.text)['data']
		self.medals = data['special_list'] + data['list']
		# self.log(str(self.medals))

	def sendMedalsMessage(self, sleep=5):
		""" 向有粉丝牌的直播间发送弹幕进行打卡 """

		if not self.medals:
			self.getFansMedal()
		for i in self.medals:
			name = i['anchor_info']['nick_name']
			roomId = i['room_info']['room_id']
			# 跳过直播间
			if roomId in self.blackList:
				continue
			msg = random.choice(self.message)
			self.send(roomId, msg)
			self.log(name + ':' + msg)
			time.sleep(sleep * 0.001 * random.randint(500,1500))

if __name__ == "__main__":

	cookie = """COOKIES"""
	Account = BlLiveSendMassage(cookie=cookie, blackList=[123,456], message=['0', '1', 'hello', '打卡'])
	Account.doSign()
	Account.sendMedalsMessage(sleep=5)
