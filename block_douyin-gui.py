import os
import sys
import time
import schedule
import psutil
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                            QTextEdit, QMessageBox, QSpinBox)
from PyQt5.QtCore import QTimer, Qt

class DouyinBlockerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("抖音定时屏蔽工具")
        self.setGeometry(100, 100, 500, 400)
        
        self.init_ui()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_schedule)
        self.timer.start(1000)  # 每秒检查一次计划任务
        
    def init_ui(self):
        # 主窗口部件
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        
        # 标题
        title_label = QLabel("抖音定时屏蔽工具")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 20px;")
        
        # 输入区域
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("屏蔽延迟分钟数:"))
        
        self.minutes_input = QSpinBox()
        self.minutes_input.setMinimum(1)
        self.minutes_input.setMaximum(1440)  # 最多24小时
        self.minutes_input.setValue(30)
        
        input_layout.addWidget(self.minutes_input)
        input_layout.addStretch()
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        self.block_button = QPushButton("立即屏蔽")
        self.block_button.clicked.connect(self.block_now)
        
        self.schedule_button = QPushButton("定时屏蔽")
        self.schedule_button.clicked.connect(self.schedule_block)
        
        self.unblock_button = QPushButton("解除屏蔽")
        self.unblock_button.clicked.connect(self.unblock_now)
        
        button_layout.addWidget(self.block_button)
        button_layout.addWidget(self.schedule_button)
        button_layout.addWidget(self.unblock_button)
        
        # 日志区域
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setStyleSheet("background-color: #f0f0f0;")
        
        # 添加到主布局
        main_layout.addWidget(title_label)
        main_layout.addLayout(input_layout)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.log_output)
        
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # 初始状态
        self.log_message("抖音定时屏蔽工具已启动")
        
    def log_message(self, message):
        timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
        self.log_output.append(f"{timestamp} {message}")
        
    def close_firefox(self):
        firefox_processes = []
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if 'firefox' in proc.info['name'].lower():
                    firefox_processes.append(proc)
            except (psutil.NoSuchProcess, psutil.AccessDenied, KeyError):
                continue
        
        if not firefox_processes:
            self.log_message("没有找到 Firefox 进程")
            return
        
        self.log_message(f"找到 {len(firefox_processes)} 个 Firefox 进程")
        
        for proc in firefox_processes:
            try:
                proc.kill()
                self.log_message(f"已关闭 Firefox 进程 (PID: {proc.info['pid']})")
            except Exception as e:
                self.log_message(f"关闭进程 {proc.info['pid']} 失败: {str(e)}")
    
    def block_douyin(self):
        self.close_firefox()  # 重启浏览器才能刷新hosts
        hosts_path = r"C:\Windows\System32\drivers\etc\hosts"
        douyin_domain = "www.douyin.com"
        block_entry = f"127.0.0.1 {douyin_domain}"
        
        try:
            with open(hosts_path, 'r', encoding="utf-8") as f:
                if block_entry in f.read():
                    self.log_message("抖音已在屏蔽列表中")
                    return
            
            with open(hosts_path, 'a', encoding="utf-8") as f:
                f.write(f"\n{block_entry}\n")
                self.log_message("已成功屏蔽抖音")
                
            # 显示成功消息
            QMessageBox.information(self, "成功", "抖音已成功屏蔽")

        except PermissionError:
            self.log_message("错误: 需要管理员权限")
            QMessageBox.critical(self, "错误", "需要管理员权限才能修改hosts文件")
        except Exception as e:
            self.log_message(f"发生错误: {str(e)}")
            QMessageBox.critical(self, "错误", f"发生错误: {str(e)}")
        
        return schedule.CancelJob
    
    def unblock_douyin(self):
        hosts_path = r"C:\Windows\System32\drivers\etc\hosts"
        douyin_domain = "www.douyin.com"
        block_entry = f"127.0.0.1 {douyin_domain}"
        
        try:
            with open(hosts_path, 'r', encoding="utf-8") as f:
                lines = f.readlines()
            
            new_lines = [line for line in lines if douyin_domain not in line]
            
            if len(new_lines) != len(lines):
                with open(hosts_path, 'w', encoding="utf-8") as f:
                    f.writelines(new_lines)
                self.log_message("已解除屏蔽")
                QMessageBox.information(self, "成功", "已解除抖音屏蔽")
            else:
                self.log_message("未被屏蔽")
                
        except PermissionError:
            self.log_message("错误: 需要管理员权限")
            QMessageBox.critical(self, "错误", "需要管理员权限才能修改hosts文件")
        except Exception as e:
            self.log_message(f"发生错误: {str(e)}")
            QMessageBox.critical(self, "错误", f"发生错误: {str(e)}")
    
    def block_now(self):
        self.log_message("立即屏蔽抖音...")
        self.block_douyin()
    
    def unblock_now(self):
        self.log_message("解除抖音屏蔽...")
        self.unblock_douyin()
    
    def schedule_block(self):
        minutes = self.minutes_input.value()
        self.log_message(f"将在 {minutes} 分钟后屏蔽抖音")
        schedule.every(minutes).minutes.do(self.block_douyin)
        QMessageBox.information(self, "计划设置", f"已设置 {minutes} 分钟后自动屏蔽抖音")
    
    def check_schedule(self):
        schedule.run_pending()
    
    def closeEvent(self, event):
        # 关闭前确认
        reply = QMessageBox.question(
            self, '确认退出', 
            '确定要退出吗？退出前会自动解除屏蔽。',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.unblock_now()
            event.accept()
        else:
            event.ignore()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 检查管理员权限
    try:
        test_path = r"C:\Windows\System32\drivers\etc\hosts"
        with open(test_path, 'a', encoding="utf-8") as f:
            pass
    except PermissionError:
        QMessageBox.critical(None, "错误", "请以管理员身份运行此程序")
        sys.exit(1)
    
    window = DouyinBlockerGUI()
    window.show()
    sys.exit(app.exec_())