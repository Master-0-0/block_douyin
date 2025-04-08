# block_douyin
自律学习抖音防沉迷工具

##前言
经常看抖音下饭一不小心就看过头了耽误学习时间所以写个工具用来强制戒断
##原理
利用hosts 将www.douyin.com 域名解析到本地即可无法访问，接着关闭浏览器用于刷新hosts状态
##工具使用：
```pyinstaller --onefile --windowed --icon=app.ico block_douyin-gui.py```
使用管理员权限运行输入看多少分钟关闭抖音即可
![image](https://github.com/user-attachments/assets/2bd62f66-d505-4463-a86b-d42b08bcd453)

