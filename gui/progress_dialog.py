#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
进度对话框
显示YOLO检测进度的模态对话框
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QProgressBar, QPushButton, QTextEdit)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

class ProgressDialog(QDialog):
    """进度对话框类"""
    
    # 信号
    cancel_requested = pyqtSignal()  # 取消请求信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.setup_connections()
    
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("YOLO检测进度")
        self.setModal(True)  # 设置为模态对话框
        self.setFixedSize(500, 300)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowTitleHint)
        
        # 主布局
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        title_label = QLabel("正在进行目标检测与跟踪")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid grey;
                border-radius: 5px;
                text-align: center;
                font-size: 12px;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # 状态文本
        self.status_label = QLabel("准备开始...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_font = QFont()
        status_font.setPointSize(11)
        self.status_label.setFont(status_font)
        layout.addWidget(self.status_label)
        
        # 详细信息区域
        info_label = QLabel("检测信息:")
        info_font = QFont()
        info_font.setPointSize(10)
        info_font.setBold(True)
        info_label.setFont(info_font)
        layout.addWidget(info_label)
        
        self.info_text = QTextEdit()
        self.info_text.setMaximumHeight(80)
        self.info_text.setReadOnly(True)
        self.info_text.setStyleSheet("""
            QTextEdit {
                background-color: #f0f0f0;
                color: #333333;
                border: 1px solid #ccc;
                border-radius: 3px;
                font-family: Consolas, monospace;
                font-size: 9px;
            }
        """)
        layout.addWidget(self.info_text)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_btn = QPushButton("取消检测")
        self.cancel_btn.setFixedSize(100, 30)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
            QPushButton:pressed {
                background-color: #b71c1c;
            }
        """)
        button_layout.addWidget(self.cancel_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
    
    def setup_connections(self):
        """设置信号连接"""
        self.cancel_btn.clicked.connect(self.on_cancel_clicked)
    
    def on_cancel_clicked(self):
        """取消按钮点击事件"""
        self.cancel_requested.emit()
    
    def update_progress(self, value):
        """更新进度条"""
        self.progress_bar.setValue(value)
        if value == 100:
            self.status_label.setText("检测完成！")
            self.cancel_btn.setText("关闭")
            self.cancel_btn.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
            """)
    
    def update_status(self, status_text):
        """更新状态文本"""
        self.status_label.setText(status_text)
    
    def add_info(self, info_text):
        """添加信息到详细信息区域"""
        self.info_text.append(info_text)
        # 滚动到底部
        scrollbar = self.info_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def reset(self):
        """重置对话框状态"""
        self.progress_bar.setValue(0)
        self.status_label.setText("准备开始...")
        self.info_text.clear()
        self.cancel_btn.setText("取消检测")
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
            QPushButton:pressed {
                background-color: #b71c1c;
            }
        """)
    
    def closeEvent(self, event):
        """对话框关闭事件"""
        # 发送取消信号
        self.cancel_requested.emit()
        event.accept() 