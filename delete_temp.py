import os
import time

# 3天刪除 t=259200
def delDir(dir,t=259200):
    if os.path.exists(dir):
        #獲取文件夾下所有文件和文件夾
        files = os.listdir(dir)
        for file in files:
            filePath = dir + "/" + file
            #判斷是否是文件
            if os.path.isfile(filePath):
                #最後一次修改的時間
                last = int(os.stat(filePath).st_mtime)
                #上一次訪問的時間
                #last = int(os.stat(filePath).st_atime)
                #當前時間
                now = int(time.time())
                #刪除過期文件
                if (now - last >= t):
                    os.remove(filePath)
                    print(filePath + " was removed!")
            elif os.path.isdir(filePath):
                #如果是文件夾，繼續遍歷刪除
                delDir(filePath,t)
                #如果是空文件夾，刪除空文件夾
                if not os.listdir(filePath):
                    os.rmdir(filePath)
                    print(filePath + " was removed!")
    else:
        os.mkdir(dir)