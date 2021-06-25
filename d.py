# -*- coding: utf-8 -*-
import sys
import requests
import re
import os
import time
import json
from datetime import datetime
from bs4 import BeautifulSoup
from moviepy.editor import AudioFileClip

BASE_PATH = ""

#下载抖音无水印视频
def main():
    #设定文件名
    global BASE_PATH
    BASE_PATH = "./file/result/file_" + str(int(round(time.time() * 1000)))

    while True:
        r = get_dy_video()
        if(r == 0):
            break

#下载抖音视频
def get_dy_video():
    url = input("请输入视频链接地址(输入0退出)：")
    if(url == "0"):
        return 0

    v_info = get_dy_video_info(url)
    v_id = v_info["video"]["play_addr"]["uri"]
    # 拼合链接
    video_url = 'https://aweme.snssdk.com/aweme/v1/play/?video_id=%s&line=0&ratio=720p' % v_id
    res_url = get_redirect_url(video_url)
    # 进行下载
    print("下载中 %s ..." %res_url)
    download_media(res_url, BASE_PATH + ".mp4")
    #print("下载完成")

    print("------ 🍺 下载视频成功 ------\n")
    return 1

#获取抖音视频的id
def get_dy_video_info(url):
    if not url:
        url = input("请输入正确的链接地址：")
    #url = "https://v.douyin.com/exA9M4Y/"  
    redirect_url = get_redirect_url(url)
    #获取视频id：6920107155437800719
    #https://www.iesdouyin.com/share/video/6920107155437800719/?region=CN&mid=6870791761040508930&u_code=mjmjiima&titleType=title&did=MS4wLjABAAAAHbiKEdYxtDwYiZyjoJ5oLtRHlfYV2sACf6DNknbysiw&iid=MS4wLjABAAAAi2PmpvzIFBJZPZ0B09KeS4w52_1SfvGSFRtMfGmWZXU&with_sec_did=1&timestamp=1623570095&app=aweme&utm_campaign=client_share&utm_medium=ios&tt_from=copy&utm_source=copy
    #2021/06/25 抖音视频链接更换为这种格式https://www.douyin.com/video/6920107155437800719
    pattern = re.compile('douyin.com/video/([a-z0-9]+)')  
    video_id = pattern.search(redirect_url).group(1)

    #获取视频元数据 https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/?item_ids=6920107155437800719
    url = "https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/?item_ids=%s" % video_id
    res = requests.get(url)
    code = res.status_code
    if code != 200:
        print('请求错误:' + url)
    
    headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36",
    #"Cookie": "anonymid=j3jxk555-nrn0wh; _r01_=1; _ga=GA1.2.1274811859.1497951251; _de=BF09EE3A28DED52E6B65F6A4705D973F1383380866D39FF5; ln_uact=mr_mao_hacker@163.com; depovince=BJ; jebecookies=54f5d0fd-9299-4bb4-801c-eefa4fd3012b|||||; JSESSIONID=abcI6TfWH4N4t_aWJnvdw; ick_login=4be198ce-1f9c-4eab-971d-48abfda70a50; p=0cbee3304bce1ede82a56e901916d0949; first_login_flag=1; ln_hurl=http://hdn.xnimg.cn/photos/hdn421/20171230/1635/main_JQzq_ae7b0000a8791986.jpg; t=79bdd322e760beae79c0b511b8c92a6b9; societyguester=79bdd322e760beae79c0b511b8c92a6b9; id=327550029; xnsid=2ac9a5d8; loginfrom=syshome; ch_id=10016; wp_fold=0"
    }  
    content = requests.get(url, headers=headers, timeout=3000)
    resp = json.loads(content.text)

    return resp["item_list"][0]
    #return resp["item_list"][0]["video"]["play_addr"]["uri"]

# 下载视频
def download_media(url, save_path):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36'}
        pre_content_length = 0
        # 循环接收视频数据
        while True:
            # 若文件已经存在，则断点续传，设置接收来需接收数据的位置
            if os.path.exists(save_path):
                headers['Range'] = 'bytes=%d-' % os.path.getsize(save_path)
            res = requests.get(url, stream=True, headers=headers)

            content_length = int(res.headers['content-length'])
            # 若当前报文长度小于前次报文长度，或者已接收文件等于当前报文长度，则可以认为视频接收完成
            if content_length < pre_content_length or (
                    os.path.exists(save_path) and os.path.getsize(save_path) == content_length) or content_length == 0:
                break
            pre_content_length = content_length

            # 写入收到的视频数据
            with open(save_path, 'ab') as file:
                file.write(res.content)
                file.flush()
                print('下载成功：文件大小 : %s  总下载大小:%s' % (format_size(os.path.getsize(save_path)), format_size(content_length)))
    except Exception as e:
        print(e)

# 格式化文件
def format_size(size):
    def strofsize(integer, remainder, level):
        if integer >= 1024:
            remainder = integer % 1024
            integer //= 1024
            level += 1
            return strofsize(integer, remainder, level)
        else:
            return integer, remainder, level

    units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    integer, remainder, level = strofsize(size, 0, 0)
    if level + 1 > len(units):
        level = -1
    return ('{}.{:>02d} {}'.format(integer, remainder, units[level]))

# 获取重定向的链接
def get_redirect_url(url):
    header = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36',
        'Upgrade-Insecure-Requests': '1',
    }
    data = requests.get(headers=header, url=url, timeout=5)
    return data.url

if __name__ == '__main__':
    main()
