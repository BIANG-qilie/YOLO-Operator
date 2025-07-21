#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
标签导出选项对话框
用于在开始检测前选择标签导出选项
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QCheckBox, 
                            QPushButton, QLabel, QGroupBox, QLineEdit, QFileDialog)
from PyQt6.QtCore import Qt
import os

class LabelExportDialog(QDialog):
    """标签导出选项对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.save_txt = False
        self.save_conf = False
        self.output_dir = None
        self.init_ui()
        self.init_connections()
    
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("标签导出选项")
        self.setModal(True)
        self.setFixedSize(450, 280)
        
        # 主布局
        main_layout = QVBoxLayout(self)
        
        # 说明标签
        info_label = QLabel("请选择标签导出选项：")
        main_layout.addWidget(info_label)
        
        # 导出选项组
        options_group = QGroupBox("导出选项")
        options_layout = QVBoxLayout(options_group)
        
        # 保存检测框坐标到txt文件选项
        self.save_txt_check = QCheckBox("保存检测框坐标到txt文件")
        self.save_txt_check.setToolTip("将检测到的边界框坐标保存为YOLO格式的txt文件")
        options_layout.addWidget(self.save_txt_check)
        
        # 检测框结果包含置信度选项
        self.save_conf_check = QCheckBox("检测框结果包含置信度")
        self.save_conf_check.setToolTip("在保存的结果中包含检测的置信度分数")
        self.save_conf_check.setEnabled(False)  # 初始状态禁用
        options_layout.addWidget(self.save_conf_check)
        
        main_layout.addWidget(options_group)
        
        # 输出目录选择组
        dir_group = QGroupBox("输出设置")
        dir_layout = QVBoxLayout(dir_group)
        
        # 输出目录选择
        dir_select_layout = QHBoxLayout()
        dir_select_layout.addWidget(QLabel("输出目录:"))
        
        self.output_dir_edit = QLineEdit()
        self.output_dir_edit.setPlaceholderText("选择输出目录...")
        self.output_dir_edit.setReadOnly(True)
        self.output_dir_edit.setEnabled(False)  # 初始状态禁用
        dir_select_layout.addWidget(self.output_dir_edit)
        
        self.browse_btn = QPushButton("浏览...")
        self.browse_btn.setFixedWidth(80)
        self.browse_btn.setEnabled(False)  # 初始状态禁用
        dir_select_layout.addWidget(self.browse_btn)
        
        dir_layout.addLayout(dir_select_layout)
        
        main_layout.addWidget(dir_group)
        
        # 添加弹性空间
        main_layout.addStretch()
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        # 确认按钮
        self.confirm_btn = QPushButton("确认")
        self.confirm_btn.setDefault(True)
        button_layout.addWidget(self.confirm_btn)
        
        # 取消按钮
        self.cancel_btn = QPushButton("取消")
        button_layout.addWidget(self.cancel_btn)
        
        main_layout.addLayout(button_layout)
    
    def init_connections(self):
        """初始化信号连接"""
        # 第一个复选框状态变化时，控制第二个复选框的启用状态
        self.save_txt_check.stateChanged.connect(self.on_save_txt_changed)
        
        # 浏览按钮连接
        self.browse_btn.clicked.connect(self.browse_output_dir)
        
        # 按钮连接
        self.confirm_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
    
    def on_save_txt_changed(self, state):
        """处理保存txt选项状态变化"""
        # 只有勾选了保存txt选项，才能勾选置信度选项和选择输出目录
        is_checked = (state == Qt.CheckState.Checked.value)
        self.save_conf_check.setEnabled(is_checked)
        self.output_dir_edit.setEnabled(is_checked)
        self.browse_btn.setEnabled(is_checked)
        
        # 如果取消勾选保存txt选项，同时取消勾选置信度选项，并清空输出目录
        if not is_checked:
            self.save_conf_check.setChecked(False)
            self.output_dir_edit.clear()
            self.output_dir = None
    
    def browse_output_dir(self):
        """浏览选择输出目录"""
        directory = QFileDialog.getExistingDirectory(
            self, 
            "选择标签输出目录",
            os.getcwd(),  # 默认当前工作目录
            QFileDialog.Option.ShowDirsOnly
        )
        
        if directory:
            self.output_dir = directory
            self.output_dir_edit.setText(directory)
    
    def get_export_options(self):
        """获取导出选项"""
        return {
            'save_txt': self.save_txt_check.isChecked(),
            'save_conf': self.save_conf_check.isChecked(),
            'output_dir': self.output_dir if self.save_txt_check.isChecked() else None
        }
    
    def accept(self):
        """确认按钮处理"""
        self.save_txt = self.save_txt_check.isChecked()
        self.save_conf = self.save_conf_check.isChecked()
        super().accept()
    
    def reject(self):
        """取消按钮处理"""
        self.save_txt = False
        self.save_conf = False
        super().reject() 