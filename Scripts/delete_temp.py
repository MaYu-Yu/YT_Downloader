import os
import time

def delDir(dir, t=259200):
    if os.path.exists(dir):
        # 獲取文件夾下所有文件和文件夾
        files = os.listdir(dir)
        now = int(time.time())  # 只需獲取一次當前時間

        for file in files:
            filePath = os.path.join(dir, file)  # 使用os.path.join來拼接路徑
            if os.path.isfile(filePath):
                # 獲取文件的最後一次修改時間
                last_modified_time = int(os.stat(filePath).st_mtime)

                # 判斷是否過期
                if now - last_modified_time >= t:
                    os.remove(filePath)
                    print(filePath + " was removed!")
            elif os.path.isdir(filePath):
                # 如果是文件夾，繼續遞迴刪除
                delDir(filePath, t)

                # 如果是空文件夾，刪除空文件夾
                if not os.listdir(filePath):
                    os.rmdir(filePath)
                    print(filePath + " was removed!")
    else:
        os.mkdir(dir)
