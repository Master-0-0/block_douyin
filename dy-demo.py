import os
import time
import schedule
import psutil
from datetime import datetime

#重启浏览器
def close_firefox():
    # 查找所有 Firefox 进程
    firefox_processes = []
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            # 检查进程名是否包含 'firefox'（不区分大小写）
            if 'firefox' in proc.info['name'].lower():
                firefox_processes.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied, KeyError):
            continue
    
    if not firefox_processes:
        print("没有找到 Firefox 进程")
        return
    
    print(f"找到 {len(firefox_processes)} 个 Firefox 进程:")
    for proc in firefox_processes:
        print(f"PID: {proc.info['pid']}, 名称: {proc.info['name']}")
    
    # 确认是否关闭
    # confirm = input("确定要关闭这些 Firefox 进程吗？(y/n): ").strip().lower()
    # if confirm != 'y':
    #     print("取消操作")
    #     return
    
    # 关闭进程
    for proc in firefox_processes:
        try:
            proc.kill()
            print(f"已关闭 Firefox 进程 (PID: {proc.info['pid']})")
        except Exception as e:
            print(f"关闭进程 {proc.info['pid']} 失败: {str(e)}")


def block_douyin():
    close_firefox() #重启浏览器才能刷新hosts
    """将抖音域名指向本地并取消后续任务"""
    hosts_path = r"C:\Windows\System32\drivers\etc\hosts"  # Windows系统
    # hosts_path = "/etc/hosts"  # Linux/macOS系统
    
    douyin_domain = "www.douyin.com"
    block_entry = f"127.0.0.1 {douyin_domain}"
    
    try:
        with open(hosts_path, 'r',encoding="utf-8") as f:
            if block_entry in f.read():
                print(f"[{datetime.now()}] 抖音已在屏蔽列表中")
                return
        
        with open(hosts_path, 'a',encoding="utf-8") as f:
            f.write(f"\n{block_entry}\n")
            print(f"[{datetime.now()}] 已成功屏蔽抖音")

    except PermissionError:
        print(f"[{datetime.now()}] 错误: 需要管理员权限")
    except Exception as e:
        print(f"[{datetime.now()}] 发生错误: {str(e)}")
    
    return schedule.CancelJob  # 关键修改：执行一次后终止任务

def unblock_douyin():
    """解除屏蔽"""
    hosts_path = r"C:\Windows\System32\drivers\etc\hosts"
    douyin_domain = "www.douyin.com"
    block_entry = f"127.0.0.1 {douyin_domain}"
    
    try:
        with open(hosts_path, 'r',encoding="utf-8") as f:
            lines = f.readlines()
        
        new_lines = [line for line in lines if douyin_domain not in line]
        
        if len(new_lines) != len(lines):
            with open(hosts_path, 'w',encoding="utf-8") as f:
                f.writelines(new_lines)
            print(f"[{datetime.now()}] 已解除屏蔽")
        else:
            print(f"[{datetime.now()}] 未被屏蔽")
            
    except PermissionError:
        print(f"[{datetime.now()}] 错误: 需要管理员权限")
    except Exception as e:
        print(f"[{datetime.now()}] 发生错误: {str(e)}")

def schedule_blocking(minutes):
    """安排定时任务"""
    print(f"[{datetime.now()}] 将在 {minutes} 分钟后屏蔽抖音")
    schedule.every(minutes).minutes.do(block_douyin)  # 修改：仅注册定时任务
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n检测到用户中断，正在解除屏蔽...")
        unblock_douyin()

if __name__ == "__main__":
    print("抖音定时屏蔽工具 (Ctrl+C退出)")
    try:
        minutes = int(input("请输入屏蔽延迟分钟数: "))
        if minutes <= 0:
            raise ValueError("请输入正整数")
        schedule_blocking(minutes)
    except ValueError as e:
        print(f"输入错误: {str(e)}")