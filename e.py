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

sys.path.append("./qc-speech-sdk")
from common import credential
from asr import flash_recognizer


#腾讯云API秘钥，假如不用语音转文字，可以不用配置
APPID = ""
SECRET_ID = ""
SECRET_KEY = ""
ENGINE_TYPE = "16k_zh"

#文件存储的全局路径，在main中初始化
BASE_PATH = ""

def main():
    #设定文件名
    global BASE_PATH
    BASE_PATH = "./file/result/file_" + str(int(round(time.time() * 1000)))

    print("------------- 请选择 -------------")
    print("----------------------------------")
    print("------ 1:抖音视频无水印下载 -----")
    print("------ 2:抖音视频提取音频 ------")
    print("------ 3:抖音视频提取文字 ------")
    print("------ 4:mp4视频提取音频 --------")
    print("------ 5:mp4视频提取文字 --------")
    print("------ 6:mp3音频提取文字 --------")
    print("---------------------------------")
    print("---------------------------------")
    print("------ 0:退出 -------------------")
    print("---------------------------------")

    while True:
        sel = input("\n ==> 请选择:")
        if(sel == "1"):
            get_dy_video()
        elif(sel == "2"):
            get_dy_video()
            get_audio()
        elif(sel == "3"):
            get_dy_video()
            get_audio()
            audio_recognise()            
        elif(sel == "4"):
            v_path = input("请输入视频的本地绝对地址（只支持mp4格式视频，如 /User/xx/Downloads/my.mp4)：")
            get_audio(v_path)
        elif(sel == "5"):
            v_path = input("请输入视频的本地绝对地址（只支持mp4格式视频，如 /User/xx/Downloads/my.mp4)：")
            get_audio(v_path)
            audio_recognise()
        elif(sel == "6"):
            a_path = input("请输入音频的本地绝对地址（只支持mp3格式音频，如 /User/xx/Downloads/my.mp3)：") 
            audio_recognise(a_path)    
        elif(sel == "0"):
            break
        else:
            print("无效选项")

# 从视频中提取音频
def get_audio(video_path= ""):
    if(video_path == ""):
        video_path = BASE_PATH + ".mp4"
    #把视频转换为音频
    my_audio = AudioFileClip(video_path)
    print("------ 从视频提取音频开始 ------")
    my_audio.write_audiofile(BASE_PATH + ".mp3")
    print("------ 🍺 从视频提取音频成功 ------\n")

#识别视频文件中的语音识别
def audio_recognise(audio_path = ""):
    # if(video_path == ""):
    #     video_path = BASE_PATH + ".mp4"

    # #把视频转换为音频
    # my_audio = AudioFileClip(video_path)
    # print("------ 从视频提取音频开始 ------")
    # my_audio.write_audiofile(BASE_PATH + ".mp3")
    # print("------ 🍺 从视频提取音频成功 ------\n")

    # get_audio(video_path)

    print("------ 语音识别开始 ------")
    credential_var = credential.Credential(SECRET_ID, SECRET_KEY)
    # 新建FlashRecognizer，一个recognizer可以执行N次识别请求
    recognizer = flash_recognizer.FlashRecognizer(APPID, credential_var)

    # 新建识别请求
    req = flash_recognizer.FlashRecognitionRequest(ENGINE_TYPE)
    req.set_filter_modal(0)
    req.set_filter_punc(0)
    req.set_filter_dirty(0)
    req.set_voice_format("mp3")
    req.set_word_info(0)
    req.set_convert_num_mode(1)
    # 音频路径
    if(audio_path == ""):
         audio_path = BASE_PATH + ".mp3"

    with open(audio_path, 'rb') as f:
        #读取音频数据
        data = f.read()
        #执行识别
        resultData = recognizer.recognize(req, data)
        # print("response raw: ", resultData , "\n")
        resp = json.loads(resultData)
        request_id = resp["request_id"]
        code = resp["code"]
        if code != 0:
            print("recognize faild! request_id: ", request_id, " code: ", code, ", message: ", resp["message"])
            exit(0)

        # print("request_id: ", request_id)
        #一个channl_result对应一个声道的识别结果
        #大多数音频是单声道，对应一个channl_result
        file_txt_obj = open(BASE_PATH + ".txt", "w")
        for channl_result in resp["flash_result"]:
            file_txt_obj.write("\n-------channel_id: [" + str(channl_result["channel_id"]) + "] -------\n\n")
            file_txt_obj.write(channl_result["text"])
            #print("channel_id: ", channl_result["channel_id"])
            #print(channl_result["text"])

        file_txt_obj.close()

    print("------ 🍺 语音识别成功 ------\n")

#下载抖音视频
def get_dy_video():
    print("\n------ 下载视频 ------")
    url = input("请输入视频链接地址：")
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
        #接收视频数据
        while True:
            # 文件已经存在则断点续传 设置接收来需接收数据的位置
            if os.path.exists(save_path):
                headers['Range'] = 'bytes=%d-' % os.path.getsize(save_path)
            res = requests.get(url, stream=True, headers=headers)

            content_length = int(res.headers['content-length'])
            #若当前报文长度小于上次报文长度，或者已接收文件等于当前报文长度，则可以认为视频接收完成
            if content_length < pre_content_length or (
                    os.path.exists(save_path) and os.path.getsize(save_path) == content_length) or content_length == 0:
                break
            pre_content_length = content_length

            # 写入视频数据
            with open(save_path, 'ab') as file:
                file.write(res.content)
                file.flush()
                #print('下载成功：文件大小 : %s  总下载大小:%s' % (format_size(os.path.getsize(save_path)), format_size(content_length)))

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
    return ('{}.{:>03d} {}'.format(integer, remainder, units[level]))

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
