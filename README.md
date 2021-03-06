声明：仅用于学习之用，请不要用于任何商业用途，否则后果自负

# 初衷
* 抖音视频无水印下载。刷抖音时，看到有些不错的素材，想用于短视频剪辑。遇到两个麻烦，一是有些视频无法下载，二是下载下来会有水印。

* 从视频提取音频，音频识别为文字。在短视频盛行的时代，有些“鸡汤”类的内容也是通过视频的方式来承载了。比如，我在某个地方看到了一个视频里讲的段子很有意思，想整理成文字，就需要把视频完整看完并手动把文字敲下来。此时，自然就会有一个想法，能不能程序帮我从视频中提取音频，再把音频识别为文字。

# 功能
1、视频提取音频。支持直接给出视频，或给出抖音视频下载地址

2、视频提取音频，并识别文字

3、音频识别文字

4、抖音视频无水印下载

其中 ：
* 2和3的文字识别，用到了 [腾讯云语音识别（Automatic Speech Recognition，ASR）](https://cloud.tencent.com/document/product/1093/35680) ，需要开通ASR服务并获取 [SDK秘钥](https://console.cloud.tencent.com/cam/capi)

* 1和2支持直接从抖音提取

# 工程依赖

* [moviepy](https://pypi.org/project/moviepy/)
    ```
    python pip install moviepy
* [BeautifulSoup](https://pypi.org/project/beautifulsoup4/)
    ```
    python pip install beautifulsoup4
* [腾讯云ASR](https://github.com/TencentCloud/tencentcloud-speech-sdk-python/)


# 文件说明
* do.py 支持功能较多，依赖腾讯云ASR
* d.py 仅用于下载抖音无水印视频

本人写python不多，现学现用并没有对代码结构做过多考究，大家取之精华用即可。

# 运行效果

    python do.py

 <img src='https://github.com/hellojammy/media/blob/main/run.png' alt='运行效果' width=800> 
 
 * 抖音视频下载地址的获取方法：在视频播放页面，点击右下角分享按钮 → 复制链接，在复制的内容中找到类似于`https://v.douyin.com/eCAHg8o/`这样的地址，就是可用于下载的地址
 
 # 鸣谢
 
本工程借鉴了网络上[研究成果](https://cloud.tencent.com/developer/article/1583955)，不过此文章的方法已不可用，本人经过抓包研究后重新进行了改良。
