#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频显示组件
用于显示视频帧的PyQt6组件
"""

import cv2
import numpy as np
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QImage, QPixmap

class VideoWidget(QWidget):
    """视频显示组件"""
    
    # 信号
    frame_changed = pyqtSignal(int)  # 帧位置改变信号
    
    def __init__(self):
        super().__init__()
        self.video_capture = None
        self.current_frame = None
        self.total_frames = 0
        self.current_frame_index = 0
        self.is_playing = False
        
        self.init_ui()
        self.init_timer()
    
    def init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout(self)
        
        # 视频显示标签
        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setStyleSheet("""
            QLabel {
                background-color: black;
                border: 1px solid gray;
                min-height: 300px;
            }
        """)
        self.video_label.setText("未加载视频")
        self.video_label.setMinimumSize(640, 480)
        
        layout.addWidget(self.video_label)
        layout.setContentsMargins(5, 5, 5, 5)
    
    def init_timer(self):
        """初始化定时器"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.fps = 30  # 默认帧率
    
    def load_video(self, video_path):
        """加载视频文件"""
        try:
            # 释放之前的视频
            if self.video_capture is not None:
                self.video_capture.release()
            
            # 打开新视频
            self.video_capture = cv2.VideoCapture(video_path)
            
            if not self.video_capture.isOpened():
                raise Exception("无法打开视频文件")
            
            # 获取视频信息
            self.total_frames = int(self.video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
            self.fps = int(self.video_capture.get(cv2.CAP_PROP_FPS))
            self.current_frame_index = 0
            
            # 显示第一帧
            self.show_frame(0)
            
            return True
            
        except Exception as e:
            print(f"加载视频失败: {e}")
            return False
    
    def show_frame(self, frame_index):
        """显示指定帧"""
        if self.video_capture is None or not self.video_capture.isOpened():
            return
        
        # 设置帧位置
        self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        
        # 读取帧
        ret, frame = self.video_capture.read()
        if ret:
            self.current_frame = frame
            self.current_frame_index = frame_index
            self.display_frame(frame)
            self.frame_changed.emit(frame_index)
    
    def display_frame(self, frame):
        """显示帧到标签"""
        if frame is None:
            return
        
        # 转换颜色空间 (BGR -> RGB)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # 获取帧尺寸
        height, width, channel = rgb_frame.shape
        bytes_per_line = 3 * width
        
        # 创建QImage
        q_image = QImage(rgb_frame.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
        
        # 缩放图像以适应标签大小
        label_size = self.video_label.size()
        scaled_pixmap = QPixmap.fromImage(q_image).scaled(
            label_size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
        )
        
        # 显示图像
        self.video_label.setPixmap(scaled_pixmap)
    
    def update_frame(self):
        """更新帧（用于播放）"""
        if self.video_capture is None or not self.is_playing:
            return
        
        next_frame = self.current_frame_index + 1
        if next_frame >= self.total_frames:
            self.stop_playback()
            return
        
        self.show_frame(next_frame)
    
    def play(self):
        """开始播放"""
        if self.video_capture is None:
            return
        
        self.is_playing = True
        self.timer.start(1000 // self.fps)  # 根据FPS设置定时器间隔
    
    def pause(self):
        """暂停播放"""
        self.is_playing = False
        self.timer.stop()
    
    def stop_playback(self):
        """停止播放"""
        self.is_playing = False
        self.timer.stop()
    
    def seek(self, frame_index):
        """跳转到指定帧"""
        if self.video_capture is None:
            return
        
        frame_index = max(0, min(frame_index, self.total_frames - 1))
        self.show_frame(frame_index)
    
    def get_current_frame(self):
        """获取当前帧"""
        return self.current_frame
    
    def get_frame_count(self):
        """获取总帧数"""
        return self.total_frames
    
    def get_current_frame_index(self):
        """获取当前帧索引"""
        return self.current_frame_index
    
    def get_fps(self):
        """获取帧率"""
        return self.fps
    
    def set_frame(self, frame):
        """设置显示的帧（用于显示处理后的帧）"""
        if frame is not None:
            self.display_frame(frame)
    
    def closeEvent(self, event):
        """组件关闭事件"""
        if self.video_capture is not None:
            self.video_capture.release()
        super().closeEvent(event) 