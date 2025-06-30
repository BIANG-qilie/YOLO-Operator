#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主窗口类
实现YOLOv11目标识别与跟踪可视化界面的主要GUI组件
"""

import os
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QMenuBar, QToolBar, QStatusBar, QLabel, QPushButton,
                            QComboBox, QCheckBox, QSlider, QTextEdit, QGroupBox,
                            QFileDialog, QMessageBox, QProgressBar, QSplitter)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QAction, QPixmap, QFont
from gui.video_widget import VideoWidget
from gui.progress_dialog import ProgressDialog
from core.yolo_processor import YOLOProcessor

class MainWindow(QMainWindow):
    """主窗口类"""
    
    def __init__(self):
        super().__init__()
        self.video_processor = None
        self.current_video_path = None
        self.progress_dialog = None
        self.init_ui()
        self.init_connections()
    
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("YOLO目标识别与跟踪系统 v1.0")
        self.setGeometry(100, 100, 1400, 900)
        
        # 创建菜单栏
        self.create_menu_bar()
        
        # 创建工具栏
        self.create_toolbar()
        
        # 创建中央窗口部件
        self.create_central_widget()
        
        # 创建状态栏
        self.create_status_bar()
    
    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu('文件(&F)')
        
        # 导入视频
        import_action = QAction('导入视频', self)
        import_action.setShortcut('Ctrl+O')
        import_action.triggered.connect(self.import_video)
        file_menu.addAction(import_action)
        
        file_menu.addSeparator()
        
        # 导出结果
        export_video_action = QAction('导出视频', self)
        export_video_action.triggered.connect(self.export_video)
        file_menu.addAction(export_video_action)
        
        export_log_action = QAction('导出日志', self)
        export_log_action.triggered.connect(self.export_log)
        file_menu.addAction(export_log_action)
        
        file_menu.addSeparator()
        
        # 退出
        exit_action = QAction('退出', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 设置菜单
        settings_menu = menubar.addMenu('设置(&S)')
        
        # 模型设置
        model_action = QAction('模型设置', self)
        model_action.triggered.connect(self.show_model_settings)
        settings_menu.addAction(model_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu('帮助(&H)')
        
        about_action = QAction('关于', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_toolbar(self):
        """创建工具栏"""
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        # 导入视频按钮
        self.import_btn = QPushButton('导入视频')
        self.import_btn.clicked.connect(self.import_video)
        toolbar.addWidget(self.import_btn)
        
        toolbar.addSeparator()
        
        # 开始检测按钮
        self.start_btn = QPushButton('开始检测')
        self.start_btn.clicked.connect(self.start_detection)
        self.start_btn.setEnabled(False)
        toolbar.addWidget(self.start_btn)
        
        # 停止检测按钮
        self.stop_btn = QPushButton('停止检测')
        self.stop_btn.clicked.connect(self.stop_detection)
        self.stop_btn.setEnabled(False)
        toolbar.addWidget(self.stop_btn)
        
        toolbar.addSeparator()
        
        # 跟踪算法选择
        toolbar.addWidget(QLabel('跟踪算法:'))
        self.tracker_combo = QComboBox()
        self.tracker_combo.addItems(['ByteTrack', 'BoT-SORT'])
        toolbar.addWidget(self.tracker_combo)
        
        toolbar.addSeparator()
        
        # 抽帧频率选择
        toolbar.addWidget(QLabel('处理帧率:'))
        self.fps_combo = QComboBox()
        self.fps_combo.addItems(['10', '15', '20', '25', '30'])
        self.fps_combo.setCurrentText('25')
        self.fps_combo.setToolTip('选择处理帧率(FPS)')
        toolbar.addWidget(self.fps_combo)
        
        toolbar.addSeparator()
        
        # 跟踪开关（识别默认启用，不可修改）
        self.tracking_check = QCheckBox('启用跟踪')
        self.tracking_check.setChecked(True)
        toolbar.addWidget(self.tracking_check)
    
    def create_central_widget(self):
        """创建中央窗口部件"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 创建水平分割器
        hsplitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(hsplitter)
        
        # 左侧视频区域
        left_group = QGroupBox('原始视频')
        left_layout = QVBoxLayout(left_group)
        self.original_video = VideoWidget()
        left_layout.addWidget(self.original_video)
        hsplitter.addWidget(left_group)
        
        # 右侧处理后视频区域
        right_group = QGroupBox('处理后视频')
        right_layout = QVBoxLayout(right_group)
        self.processed_video = VideoWidget()
        right_layout.addWidget(self.processed_video)
        hsplitter.addWidget(right_group)
        
        # 设置分割器比例
        hsplitter.setStretchFactor(0, 1)
        hsplitter.setStretchFactor(1, 1)
        
        # 底部控制面板
        self.create_control_panel(main_layout)
        
        # 日志区域
        self.create_log_panel(main_layout)
    
    def create_control_panel(self, parent_layout):
        """创建控制面板"""
        control_group = QGroupBox('控制面板')
        control_layout = QHBoxLayout(control_group)
        
        # 播放控制
        self.play_btn = QPushButton('播放')
        self.play_btn.clicked.connect(self.toggle_play)
        self.play_btn.setEnabled(False)
        control_layout.addWidget(self.play_btn)
        
        self.pause_btn = QPushButton('暂停')
        self.pause_btn.clicked.connect(self.pause_video)
        self.pause_btn.setEnabled(False)
        control_layout.addWidget(self.pause_btn)
        
        # 进度条
        control_layout.addWidget(QLabel('进度:'))
        self.progress_slider = QSlider(Qt.Orientation.Horizontal)
        self.progress_slider.valueChanged.connect(self.seek_video)
        self.progress_slider.setEnabled(False)
        control_layout.addWidget(self.progress_slider)
        
        # 帧率显示
        self.fps_label = QLabel('FPS: 0')
        control_layout.addWidget(self.fps_label)
        
        # 检测数量显示
        self.detection_count_label = QLabel('检测数量: 0')
        control_layout.addWidget(self.detection_count_label)
        
        parent_layout.addWidget(control_group)
    
    def create_log_panel(self, parent_layout):
        """创建日志面板"""
        log_group = QGroupBox('系统日志')
        log_layout = QVBoxLayout(log_group)
        
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(150)
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        
        parent_layout.addWidget(log_group)
    
    def create_status_bar(self):
        """创建状态栏"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # 添加进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)
        
        self.status_bar.showMessage('就绪')
    
    def init_connections(self):
        """初始化信号连接"""
        # 显示启动信息
        self.log_message("系统已启动")
        self.log_message("当前模型: YOLOv11x-OBB (weights/yolo11x-obb.pt)")
        self.log_message("支持旋转边界框检测")
    
    def log_message(self, message):
        """添加日志消息"""
        self.log_text.append(f"[{self.get_current_time()}] {message}")
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )
    
    def get_current_time(self):
        """获取当前时间字符串"""
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")
    
    # 槽函数
    def import_video(self):
        """导入视频文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            '选择视频文件', 
            '', 
            'Video Files (*.mp4 *.avi *.mov)'
        )
        
        if file_path:
            self.current_video_path = file_path
            self.log_message(f"导入视频: {os.path.basename(file_path)}")
            
            # 启用相关按钮
            self.start_btn.setEnabled(True)
            self.play_btn.setEnabled(True)
            
            # 加载视频到原始视频窗口
            self.original_video.load_video(file_path)
            
            self.status_bar.showMessage(f'已加载视频: {os.path.basename(file_path)}')
    
    def start_detection(self):
        """开始检测"""
        if not self.current_video_path:
            QMessageBox.warning(self, '警告', '请先导入视频文件！')
            return
        
        self.log_message('开始YOLO目标识别...')
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.progress_bar.setVisible(True)
        
        # 创建并显示进度对话框
        self.progress_dialog = ProgressDialog(self)
        self.progress_dialog.cancel_requested.connect(self.stop_detection)
        
        # 初始化YOLO处理器
        if self.video_processor is None:
            self.video_processor = YOLOProcessor()
            self.setup_processor_connections()
        
        # 设置处理器参数
        self.video_processor.set_detection_enabled(True)  # 默认启用检测
        self.video_processor.set_tracking_enabled(self.tracking_check.isChecked())
        self.video_processor.set_tracker(self.tracker_combo.currentText())
        self.video_processor.set_target_fps(int(self.fps_combo.currentText()))
        
        # 显示进度对话框
        self.progress_dialog.reset()
        self.progress_dialog.update_status("正在加载模型...")
        self.progress_dialog.add_info("开始初始化YOLO检测...")
        self.progress_dialog.show()
        
        # 在后台线程中启动处理
        if self.video_processor.start_processing_thread(self.current_video_path):
            self.progress_dialog.update_status("开始处理视频...")
            self.progress_dialog.add_info(f"视频文件: {os.path.basename(self.current_video_path)}")
            
            # 连接工作线程的信号
            if self.video_processor.worker_thread:
                self.video_processor.worker_thread.progress_updated.connect(self.on_progress_updated)
                self.video_processor.worker_thread.fps_updated.connect(self.on_fps_updated)
                self.video_processor.worker_thread.frame_processed.connect(self.on_frame_processed)
                self.video_processor.worker_thread.error_occurred.connect(self.on_processing_error)
                self.video_processor.worker_thread.processing_finished.connect(self.on_processing_finished)
                self.video_processor.worker_thread.detection_info_updated.connect(self.on_detection_info_updated)
        else:
            self.progress_dialog.add_info("启动处理失败！")
            self.stop_detection()
        
        self.status_bar.showMessage('正在处理...')
    
    def stop_detection(self):
        """停止检测"""
        self.log_message('停止检测')
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setVisible(False)
        
        # 停止YOLO处理
        if self.video_processor:
            self.video_processor.stop_processing()
        
        # 关闭进度对话框
        if self.progress_dialog:
            self.progress_dialog.close()
            self.progress_dialog = None
        
        self.status_bar.showMessage('检测已停止')
    
    def setup_processor_connections(self):
        """设置处理器信号连接"""
        if self.video_processor:
            # 连接处理器的信号
            self.video_processor.progress_updated.connect(self.on_progress_updated)
            self.video_processor.fps_updated.connect(self.on_fps_updated)
            self.video_processor.frame_processed.connect(self.on_frame_processed)
            self.video_processor.error_occurred.connect(self.on_processing_error)
            self.video_processor.processing_finished.connect(self.on_processing_finished)
            self.video_processor.detection_info_updated.connect(self.on_detection_info_updated)
    
    def on_progress_updated(self, current_frame, total_frames, progress):
        """处理进度更新"""
        if self.progress_dialog:
            self.progress_dialog.update_progress(progress)
            self.progress_dialog.update_status(f"正在处理... {current_frame}/{total_frames} ({progress}%)")
    
    def on_fps_updated(self, fps):
        """处理FPS更新"""
        self.fps_label.setText(f'FPS: {fps:.1f}')
        if self.progress_dialog:
            self.progress_dialog.add_info(f"处理速度: {fps:.1f} FPS")
    
    def on_frame_processed(self, processed_frame, detection_info):
        """处理帧处理完成"""
        # 更新处理后的视频显示
        self.processed_video.set_frame(processed_frame)
        
        # 更新检测数量
        count = detection_info.get('count', 0)
        self.detection_count_label.setText(f'检测数量: {count}')
    
    def on_detection_info_updated(self, info_text):
        """处理检测信息更新"""
        if self.progress_dialog:
            self.progress_dialog.add_info(info_text)
    
    def on_processing_error(self, error_message):
        """处理错误"""
        self.log_message(f"处理错误: {error_message}")
        if self.progress_dialog:
            self.progress_dialog.add_info(f"错误: {error_message}")
        QMessageBox.critical(self, '处理错误', error_message)
        self.stop_detection()
    
    def on_processing_finished(self):
        """处理完成"""
        self.log_message('检测处理完成')
        if self.progress_dialog:
            self.progress_dialog.update_progress(100)
            self.progress_dialog.add_info("检测处理已完成！")
        
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setVisible(False)
        self.status_bar.showMessage('检测完成')
    
    def toggle_play(self):
        """切换播放状态"""
        # TODO: 实现播放/暂停功能
        pass
    
    def pause_video(self):
        """暂停视频"""
        # TODO: 实现暂停功能
        pass
    
    def seek_video(self, position):
        """跳转视频位置"""
        # TODO: 实现视频跳转功能
        pass
    
    def export_video(self):
        """导出处理后的视频"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            '保存视频文件',
            '',
            'Video Files (*.mp4)'
        )
        
        if file_path:
            self.log_message(f"导出视频到: {file_path}")
            # TODO: 实现视频导出功能
    
    def export_log(self):
        """导出检测日志"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            '保存日志文件',
            '',
            'CSV Files (*.csv);;JSON Files (*.json)'
        )
        
        if file_path:
            self.log_message(f"导出日志到: {file_path}")
            # TODO: 实现日志导出功能
    
    def show_model_settings(self):
        """显示模型设置对话框"""
        QMessageBox.information(self, '模型设置', '模型设置功能待实现')
    
    def show_about(self):
        """显示关于对话框"""
        QMessageBox.about(self, '关于', 
                         'YOLO目标识别与跟踪系统 v1.0\n'
                         '基于YOLOv11和Ultralytics开发\n'
                         '支持实时目标检测和多目标跟踪')
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        reply = QMessageBox.question(self, '确认退出', 
                                   '确定要退出程序吗？',
                                   QMessageBox.StandardButton.Yes | 
                                   QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore() 