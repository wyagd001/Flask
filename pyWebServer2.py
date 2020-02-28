#!/data/data/com.termux/files/usr/bin/python
# -*- coding: utf-8 -*-
# 说明
#   启动web服务器
# 参考
#   https://flask.palletsprojects.com/en/1.1.x/
#   https://blog.csdn.net/u014793102/article/details/80372815
# external
#   date       2019-09-07 19:02:50
#   face       (>_<)
#   weather    Shanghai Clear 28℃
# 其他
#   用命令行启动server时，在app.run中配置的参数无效，需要在flask run后增加参数
#   win:    set FLASK_APP=server.py 
#   win:    set FLASK_ENV=development
#   linux:  export FLASK_APP=/sdcard/software_me/tasker/termux/pyWebServer.py
#   linux:  export FLASK_ENV=development
#   flask run -h '0.0.0.0' -p 10000
from flask import Flask, request, send_from_directory, render_template, Response, redirect, url_for
import subprocess, time, os
app = Flask(__name__)
app.secret_key = '123456'

#建立路由，通过路由可以执行其覆盖的方法，可以多个路由指向同一个方法。
@app.route('/')
@app.route('/index')
def index():
    base_dir = os.path.dirname(__file__)
    with open(base_dir + '/test.txt') as read_file:
      textcontent = read_file.read()
    html = render_template('index.html', textcontent=textcontent)
    return html
    
# 定义网站页面图标
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


# ahk[httpClient] -> termux -> python[WebServer] -> tasker[remoteCtlPC-setClip] -> ahk[httpServer] -> ahk[设置clip值]
@app.route('/clip', methods=['GET'])
def setPCClipFromMobile():
    subprocess.call("am broadcast -a net.dinglisch.android.tasker.ACTION_TASK --es task_name 'remoteCtlPC-setClip'", shell=True)
    return redirect(url_for('index'))
@app.route('/clip', methods=['POST'])
def setMobileClipFromPC():
    subprocess.call("am broadcast -a net.dinglisch.android.tasker.ACTION_TASK --es task_name 'remoteCtlPC-getClip'", shell=True)
    return redirect(url_for('index'))

# 自动下载AhkHttp分享的文件
@app.route('/ahkhttpupload', methods=['GET', 'POST'])
def ahkhttpuploadFile():
    subprocess.call("am broadcast -a net.dinglisch.android.tasker.ACTION_TASK --es task_name 'remoteCtlPC-downFile'", shell=True)
    return redirect(url_for('index'))

# 调用tasker使用Jquick插件截图
@app.route("/screenshot", methods=['post', 'get'])
def screenshot():
    subprocess.call("am broadcast -a net.dinglisch.android.tasker.ACTION_TASK --es task_name 'screenshot'", shell=True)
    time.sleep(4)
    path = "/storage/emulated/0/.termux/tasker2/screenshot/1.jpg"
    resp = Response(open(path, 'rb'), mimetype="image/jpeg")
    return resp

@app.route('/upload',methods=['GET','POST'])
def settings():
    if request.method == 'GET':
        return redirect(url_for('index'))
    else:
        avatar = request.files.get('file')
        # 对文件名进行包装，为了安全,不过对中文的文件名显示有问题
#        filename = secure_filename(avatar.filename)
        UPLOAD_PATH = "/storage/emulated/0/download"
        avatar.save(os.path.join(UPLOAD_PATH,avatar.filename))
        print(avatar.filename)
        return redirect(url_for('index'))


# 下载文件
@app.route('/download', methods=['GET', 'POST'])
def downloadFileSetPath():
    filePath = None
    if request.method=='GET':
        filePath = request.args.get("path")
    elif request.method=='POST':
        filePath = request.form['path']
        
    if (filePath == None) or (filePath == ""):
        return "=> 请配置path参数"
    if not os.path.exists(filePath):
        return "=> 指定的文件不存在: " + filePath
        
    (fileDir, fileName) = os.path.split(filePath)
    return send_from_directory(fileDir, fileName, as_attachment=True, attachment_filename=fileName,)


# 提交字符串然后写入文本文件
@app.route("/submittext", methods=['post', 'get'])
def submittext():
    mytext = request.args.get('mytext')
    base_dir = os.path.dirname(__file__)
    f1 = open(base_dir + '/test.txt','w')
    f1.write(str(mytext))
    f1.close()
    html = render_template('index.html', textcontent=mytext)
    return html


if __name__=='__main__':
    app.run(host='0.0.0.0', port= 10000, debug=True)