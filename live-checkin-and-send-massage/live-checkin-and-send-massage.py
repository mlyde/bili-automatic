import requests, random, time, os
# import brotli		# br压缩模块, pip安装后, request可自动使用
from collections import OrderedDict
from urllib3 import encode_multipart_formdata

cookie = """"""

# 房间号(小概率不是,可自行抓包)
room_id = []
# 房间号对应up名称,方便读log,数量应与'room_id'长度相等
room_name=[]
# 打卡弹幕,数量不限,会随机选择内容进行发送弹幕
room_massage=['打卡']

def Dosign():
	""" 每日签到 """
	url = 'https://api.live.bilibili.com/xlive/web-ucenter/v1/sign/DoSign'
	headers = {
		'accept': 'application/json, text/plain, */*',
		'accept-encoding': 'gzip, deflate, br',
		'accept-language': 'zh-CN,zh;q=0.9',
		'cache-control': 'no-cache',
		'cookie': cookie,
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
	response = requests.get(url, headers = headers)
	# print(response.text)
	if response.status_code == 200:
		# 成功提交
		print('提交成功!\t',end='')
	else:
		print('提交失败!\t',end='')
	if '已' in response.text:
		print('已经签到过啦!\n')
	else:
		print('签到成功!\n')

def random_boundary():
	factor = 'ABCDEFGHIGKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
	boundary = "----WebKitFormBoundary{}".format("".join(random.choices(factor, k=16)))
	# print(boundary)
	return boundary

def Checkin(id, msg):
	""" 弹幕签到 (房间id, 弹幕)"""
	url = 'https://api.live.bilibili.com/msg/send'
	bili_jct = cookie.split('bili_jct=')[-1].split(';')[0]
	timestamp = time.time()
	boundary = random_boundary()
	headers = {
		'accept': '*/*',
		'accept-encoding': 'gzip, deflate, br',
		'accept-language': 'zh-CN,zh;q=0.9',
		'cache-control': 'no-cache',
		# content-length: 980,
		'content-type': 'multipart/form-data; boundary=' + boundary,
		'cookie': cookie,
		'origin': 'https://live.bilibili.com',
		'pragma': 'no-cache',
		'referer': 'https://live.bilibili.com/' + id,
		'sec-ch-ua': 'Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90',
		'sec-ch-ua-mobile': '?0',
		'sec-fetch-dest': 'empty',
		'sec-fetch-mode': 'cors',
		'sec-fetch-site': 'same-site',
		'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
	}
	params = OrderedDict([("bubble", '0'),
		("msg", msg),
		('color', '16777215'),	#'16777215'为普通颜色; '5566168'为5级粉丝牌可领取颜色...
		('mode', '1'),
		('fontsize', '25'),
		('rnd', str(timestamp)),
		('roomid', id),
		('csrf', bili_jct),
		('csrf_token', bili_jct)
	])
	data = encode_multipart_formdata(params, boundary=boundary)
	# print(data[0])
	response = requests.post(url = url, headers = headers, data = data[0])
	# print(response.text)	#post返回一个json,可用response.json()调用
	return response

if __name__ == "__main__":
	# global room_id, room_name, room_massage
	print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
	# 签到
	Dosign()
	# 发送弹幕
	print('up_name\tstate')
	for num in range(len(room_id)):
		print(room_name[num])
		time.sleep(0.001 * random.randint(8000,20000))	#产生一个8到20秒的延时
		# 打卡函数
		response = Checkin(room_id[num], random.choice(room_massage))
		if '"code":0' in response.text:	# 判断是否发送成功
			print('\t' + 'Success!')
		else:
			print('\t' + 'Error!')
	print('打卡完毕!\n', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), sep='')
	os.system('pause')
