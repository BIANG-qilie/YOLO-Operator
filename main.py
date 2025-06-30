#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YOLOv11目标识别与跟踪可视化界面
主程序入口
"""

import sys
import os
from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow

def main():
    """主函数"""
    app = QApplication(sys.argv)
    app.setApplicationName("YOLO目标识别与跟踪系统")
    app.setApplicationVersion("1.0.0")
    
    # 创建主窗口
    window = MainWindow()
    window.show()
    
    # 运行应用
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 