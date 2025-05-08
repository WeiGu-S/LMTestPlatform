import sys
import os
import subprocess
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# 将项目根目录添加到 Python 路径中，以便能够正确导入 app.py
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# 要运行的主应用程序脚本
APP_SCRIPT = os.path.join(os.path.dirname(PROJECT_ROOT), 'app.py')
# 要监控的文件夹，这里是项目根目录及其父目录
WATCH_PATHS = [os.path.dirname(PROJECT_ROOT)]
# 要监控的文件扩展名
WATCH_EXTENSIONS = ['.py']
# 要排除的目录
EXCLUDE_DIRS = ['.venv', 'log']

# 全局变量，用于存储当前运行的子进程
current_process = None

def start_application():
    """启动应用程序子进程"""
    global current_process
    print("正在启动应用程序...")
    # 使用 Popen 启动应用，这样主脚本不会被阻塞
    current_process = subprocess.Popen([sys.executable, APP_SCRIPT])

def restart_application():
    """重启应用程序"""
    global current_process
    if current_process:
        print("正在终止当前应用程序...")
        try:
            current_process.terminate() # 尝试正常终止
            current_process.wait(timeout=5) # 等待最多5秒
        except subprocess.TimeoutExpired:
            print("正在强制终止应用程序...")
            current_process.kill() # 如果无法正常终止，则强制杀死
        except Exception as e:
            print(f"终止进程时出错：{e}")
        current_process = None
    
    # 等待一小段时间确保端口等资源已释放
    time.sleep(1)
    start_application()

class ChangeHandler(FileSystemEventHandler):
    """文件系统事件处理器"""
    def on_modified(self, event):
        if event.is_directory:
            return
        
        file_path = event.src_path
        _, ext = os.path.splitext(file_path)
        
        # 检查文件路径是否在排除目录中
        for exclude_dir in EXCLUDE_DIRS:
            if exclude_dir in file_path.split(os.path.sep):
                return
                
        # 检查是否是需要监控的文件类型，并且不是 debug_runner.py 本身
        if ext.lower() in WATCH_EXTENSIONS and os.path.basename(file_path) != os.path.basename(__file__):
            print(f"文件已修改：{file_path}。正在重启应用程序...")
            restart_application()

if __name__ == "__main__":
    # 首次启动应用程序
    start_application()

    # 创建并启动观察者
    event_handler = ChangeHandler()
    observer = Observer()
    for path in WATCH_PATHS:
        observer.schedule(event_handler, path, recursive=True)
    observer.start()
    print(f"正在监视以下目录的文件变化：{', '.join(WATCH_PATHS)}")
    print(f"已排除以下目录：{', '.join(EXCLUDE_DIRS)}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("正在停止监视器...")
        observer.stop()
        if current_process:
            print("正在终止应用程序...")
            current_process.terminate()
            current_process.wait()
    observer.join()
    print("调试运行器已结束。")
