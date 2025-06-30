#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YOLO处理器
实现YOLOv11目标检测和多目标跟踪功能
"""

import cv2
import numpy as np
from ultralytics import YOLO
from PyQt6.QtCore import QObject, QThread, pyqtSignal, QTimer
import time
import json
from pathlib import Path
import requests
import sys
import os

class YOLOProcessorThread(QThread):
    """YOLO处理线程"""
    
    # 信号
    frame_processed = pyqtSignal(np.ndarray, dict)  # 处理完成的帧和检测信息
    progress_updated = pyqtSignal(int, int, int)  # 处理进度更新：当前帧，总帧数，进度百分比
    fps_updated = pyqtSignal(float)  # FPS更新
    error_occurred = pyqtSignal(str)  # 错误信号
    processing_finished = pyqtSignal()  # 处理完成信号
    detection_info_updated = pyqtSignal(str)  # 检测信息更新信号
    
    def __init__(self, processor):
        super().__init__()
        self.processor = processor
        self.video_path = None
    
    def set_video_path(self, video_path):
        """设置要处理的视频路径"""
        self.video_path = video_path
    
    def run(self):
        """线程运行函数"""
        if self.video_path:
            # 连接处理器信号到线程信号
            self.processor.frame_processed.connect(self.frame_processed)
            self.processor.progress_updated.connect(self.progress_updated)
            self.processor.fps_updated.connect(self.fps_updated)
            self.processor.error_occurred.connect(self.error_occurred)
            self.processor.processing_finished.connect(self.processing_finished)
            self.processor.detection_info_updated.connect(self.detection_info_updated)
            
            # 开始处理
            self.processor.process_video(self.video_path)

class YOLOProcessor(QObject):
    """YOLO处理器类"""
    
    # 信号
    frame_processed = pyqtSignal(np.ndarray, dict)  # 处理完成的帧和检测信息
    progress_updated = pyqtSignal(int, int, int)  # 处理进度更新：当前帧，总帧数，进度百分比
    fps_updated = pyqtSignal(float)  # FPS更新
    error_occurred = pyqtSignal(str)  # 错误信号
    processing_finished = pyqtSignal()  # 处理完成信号
    detection_info_updated = pyqtSignal(str)  # 检测信息更新信号
    
    def __init__(self):
        super().__init__()
        self.model = None
        self.video_capture = None
        self.is_processing = False
        self.detection_enabled = True  # 默认启用检测
        self.tracking_enabled = True
        self.tracker_type = 'bytetrack.yaml'  # 默认跟踪器
        self.is_obb_model = False  # 是否为OBB模型
        
        # 帧率控制
        self.target_fps = 25  # 目标处理帧率，默认25FPS
        self.skip_frames = 1  # 跳帧数量，由target_fps计算得出
        
        # 检测结果存储
        self.detection_results = []
        
        # 性能统计
        self.frame_count = 0
        self.processed_frame_count = 0  # 实际处理的帧数
        self.start_time = None
        
        # 工作线程
        self.worker_thread = None
    
    def set_target_fps(self, fps):
        """设置目标处理帧率"""
        self.target_fps = max(1, fps)  # 最小1FPS
    
    def download_model_if_needed(self, model_path):
        """如果模型文件不存在，则自动下载"""
        if Path(model_path).exists():
            return True
        
        # 权重文件下载配置
        weights_config = {
            'weights/yolo11x-obb.pt': {
                'url': 'https://github.com/ultralytics/assets/releases/download/v8.3.0/yolo11x-obb.pt',
                'description': 'YOLO11x-OBB 模型权重文件',
                'size': '113MB'
            },
            'weights/yolo11n-obb.pt': {
                'url': 'https://github.com/ultralytics/assets/releases/download/v8.3.0/yolo11n-obb.pt',
                'description': 'YOLO11n-OBB 模型权重文件（轻量版）',
                'size': '5.6MB'
            },
            'weights/yolo11s-obb.pt': {
                'url': 'https://github.com/ultralytics/assets/releases/download/v8.3.0/yolo11s-obb.pt',
                'description': 'YOLO11s-OBB 模型权重文件（小型版）',
                'size': '19.8MB'
            },
            'weights/yolo11m-obb.pt': {
                'url': 'https://github.com/ultralytics/assets/releases/download/v8.3.0/yolo11m-obb.pt',
                'description': 'YOLO11m-OBB 模型权重文件（中型版）',
                'size': '42.9MB'
            },
            'weights/yolo11l-obb.pt': {
                'url': 'https://github.com/ultralytics/assets/releases/download/v8.3.0/yolo11l-obb.pt',
                'description': 'YOLO11l-OBB 模型权重文件（大型版）',
                'size': '54.3MB'
            }
        }
        
        if model_path not in weights_config:
            return False
        
        config = weights_config[model_path]
        
        try:
            # 确保weights目录存在
            weights_dir = Path("weights")
            weights_dir.mkdir(exist_ok=True)
            
            # 发送下载开始信号
            self.detection_info_updated.emit(f"正在下载 {config['description']} ({config['size']})...")
            
            # 下载文件
            response = requests.get(config['url'], stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0
            
            with open(model_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
                        downloaded_size += len(chunk)
                        
                        # 计算下载进度
                        if total_size > 0:
                            progress = int((downloaded_size / total_size) * 100)
                            self.detection_info_updated.emit(f"下载进度: {progress}% ({downloaded_size // 1024 // 1024}MB/{total_size // 1024 // 1024}MB)")
            
            self.detection_info_updated.emit(f"✅ {config['description']} 下载完成")
            return True
            
        except Exception as e:
            self.error_occurred.emit(f"模型下载失败: {str(e)}")
            return False
    
    def load_model(self, model_path=None):
        """加载YOLO模型"""
        try:
            if model_path is None:
                # 使用指定的YOLOv11x-OBB模型
                model_path = 'weights/yolo11x-obb.pt'
            
            # 检查模型文件是否存在，如果不存在则尝试下载
            if not Path(model_path).exists():
                self.detection_info_updated.emit(f"模型文件不存在，正在自动下载: {model_path}")
                if not self.download_model_if_needed(model_path):
                    raise FileNotFoundError(f"模型文件不存在且下载失败: {model_path}")
            
            self.detection_info_updated.emit(f"正在加载模型: {model_path}")
            self.model = YOLO(model_path)
            self.is_obb_model = 'obb' in model_path.lower()  # 检测是否为OBB模型
            self.detection_info_updated.emit(f"✅ 模型加载成功: {model_path}")
            return True
            
        except Exception as e:
            self.error_occurred.emit(f"模型加载失败: {str(e)}")
            return False
    
    def set_tracker(self, tracker_name):
        """设置跟踪算法"""
        tracker_map = {
            'ByteTrack': 'bytetrack.yaml',
            'BoT-SORT': 'botsort.yaml'
        }
        
        if tracker_name in tracker_map:
            self.tracker_type = tracker_map[tracker_name]
        else:
            self.tracker_type = 'bytetrack.yaml'  # 默认值
    
    def set_detection_enabled(self, enabled):
        """设置是否启用检测"""
        self.detection_enabled = enabled
    
    def set_tracking_enabled(self, enabled):
        """设置是否启用跟踪"""
        self.tracking_enabled = enabled
    
    def process_video(self, video_path):
        """处理视频文件"""
        try:
            # 确保模型已加载
            if self.model is None:
                if not self.load_model():
                    return False
            
            # 打开视频文件
            self.video_capture = cv2.VideoCapture(video_path)
            if not self.video_capture.isOpened():
                self.error_occurred.emit("无法打开视频文件")
                return False
            
            # 获取视频信息
            total_frames = int(self.video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
            original_fps = self.video_capture.get(cv2.CAP_PROP_FPS)
            
            # 计算跳帧数量
            self.skip_frames = max(1, int(original_fps / self.target_fps))
            
            self.is_processing = True
            self.frame_count = 0
            self.processed_frame_count = 0
            self.start_time = time.time()
            self.detection_results.clear()
            
            # 发送初始信息
            self.detection_info_updated.emit(f"视频信息: {total_frames}帧, {original_fps:.1f}FPS")
            self.detection_info_updated.emit(f"处理设置: 目标{self.target_fps}FPS, 每{self.skip_frames}帧处理1帧")
            
            # 逐帧处理
            while self.is_processing:
                ret, frame = self.video_capture.read()
                if not ret:
                    break
                
                # 根据跳帧设置决定是否处理当前帧
                should_process = (self.frame_count % self.skip_frames == 0)
                
                if should_process:
                    # 处理当前帧
                    processed_frame, detection_info = self.process_frame(frame, self.frame_count)
                    
                    # 发送处理结果
                    self.frame_processed.emit(processed_frame, detection_info)
                    
                    # 发送检测信息
                    count = detection_info.get('count', 0)
                    if count > 0:
                        info_text = f"帧 {self.frame_count + 1}/{total_frames}: 检测到 {count} 个对象"
                        self.detection_info_updated.emit(info_text)
                    
                    self.processed_frame_count += 1
                
                # 更新进度
                progress = int((self.frame_count / total_frames) * 100)
                self.progress_updated.emit(self.frame_count + 1, total_frames, progress)
                
                # 更新FPS（每10个处理帧更新一次）
                if self.processed_frame_count > 0 and self.processed_frame_count % 10 == 0:
                    elapsed_time = time.time() - self.start_time
                    current_fps = self.processed_frame_count / elapsed_time
                    self.fps_updated.emit(current_fps)
                
                self.frame_count += 1
            
            self.processing_finished.emit()
            return True
            
        except Exception as e:
            self.error_occurred.emit(f"视频处理失败: {str(e)}")
            return False
        
        finally:
            if self.video_capture:
                self.video_capture.release()
    
    def process_frame(self, frame, frame_index):
        """处理单帧"""
        processed_frame = frame.copy()
        detection_info = {
            'frame_id': frame_index,
            'objects': [],
            'count': 0
        }
        
        try:
            if self.detection_enabled and self.model is not None:
                # 进行目标检测
                if self.tracking_enabled:
                    # 使用跟踪
                    results = self.model.track(frame, tracker=self.tracker_type, persist=True)
                else:
                    # 仅检测
                    results = self.model(frame)
                
                # 处理检测结果
                if results and len(results) > 0:
                    result = results[0]
                    
                    # 处理OBB模型和普通模型的不同输出
                    if self.is_obb_model and hasattr(result, 'obb') and result.obb is not None:
                        # OBB模型处理
                        boxes = result.obb.xyxyxyxy.cpu().numpy()  # 8点坐标(旋转框)
                        confidences = result.obb.conf.cpu().numpy()  # 置信度
                        class_ids = result.obb.cls.cpu().numpy().astype(int)  # 类别ID
                        
                        # 获取跟踪ID（如果启用跟踪）
                        track_ids = None
                        if self.tracking_enabled and hasattr(result.obb, 'id') and result.obb.id is not None:
                            track_ids = result.obb.id.cpu().numpy().astype(int)
                            
                    elif result.boxes is not None:
                        # 普通模型处理
                        boxes = result.boxes.xyxy.cpu().numpy()  # 边界框坐标
                        confidences = result.boxes.conf.cpu().numpy()  # 置信度
                        class_ids = result.boxes.cls.cpu().numpy().astype(int)  # 类别ID
                        
                        # 获取跟踪ID（如果启用跟踪）
                        track_ids = None
                        if self.tracking_enabled and hasattr(result.boxes, 'id') and result.boxes.id is not None:
                            track_ids = result.boxes.id.cpu().numpy().astype(int)
                    else:
                        boxes = None
                    
                    # 绘制检测结果（如果有检测到对象）
                    if boxes is not None and len(boxes) > 0:
                        for i, (box, conf, class_id) in enumerate(zip(boxes, confidences, class_ids)):
                            # 获取类别名称
                            class_name = self.model.names[class_id] if class_id < len(self.model.names) else f"Class_{class_id}"
                            
                            # 获取跟踪ID
                            track_id = track_ids[i] if track_ids is not None and i < len(track_ids) else None
                            
                            # 获取颜色
                            color = self.get_color_for_class(class_id)
                            
                            if self.is_obb_model:
                                # OBB模型：绘制旋转边界框
                                # box是8个点的坐标：[x1,y1,x2,y2,x3,y3,x4,y4]
                                points = box.reshape(-1, 2).astype(int)
                                cv2.polylines(processed_frame, [points], True, color, 2)
                                
                                # 获取边界框用于标签位置
                                x1, y1 = points.min(axis=0)
                                x2, y2 = points.max(axis=0)
                                
                                # 保存检测信息（OBB格式）
                                obj_info = {
                                    'bbox': box.tolist(),  # 8个坐标点
                                    'bbox_type': 'obb',
                                    'confidence': float(conf),
                                    'class_id': int(class_id),
                                    'class_name': class_name,
                                    'track_id': int(track_id) if track_id is not None else None
                                }
                            else:
                                # 普通模型：绘制矩形边界框
                                x1, y1, x2, y2 = box.astype(int)
                                cv2.rectangle(processed_frame, (x1, y1), (x2, y2), color, 2)
                                
                                # 保存检测信息（普通格式）
                                obj_info = {
                                    'bbox': [int(x1), int(y1), int(x2), int(y2)],
                                    'bbox_type': 'xyxy',
                                    'confidence': float(conf),
                                    'class_id': int(class_id),
                                    'class_name': class_name,
                                    'track_id': int(track_id) if track_id is not None else None
                                }
                            
                            # 准备标签文本
                            label = f"{class_name}: {conf:.2f}"
                            if track_id is not None:
                                label = f"ID:{track_id} {label}"
                            
                            # 绘制标签背景
                            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
                            cv2.rectangle(processed_frame, (x1, y1 - label_size[1] - 10), 
                                        (x1 + label_size[0], y1), color, -1)
                            
                            # 绘制标签文本
                            cv2.putText(processed_frame, label, (x1, y1 - 5), 
                                      cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                            
                            detection_info['objects'].append(obj_info)
                        
                        detection_info['count'] = len(boxes)
            
            # 保存检测结果
            self.detection_results.append(detection_info)
            
        except Exception as e:
            print(f"处理帧 {frame_index} 时出错: {e}")
        
        return processed_frame, detection_info
    
    def get_color_for_class(self, class_id):
        """为不同类别生成不同颜色"""
        colors = [
            (255, 0, 0),    # 红色
            (0, 255, 0),    # 绿色
            (0, 0, 255),    # 蓝色
            (255, 255, 0),  # 黄色
            (255, 0, 255),  # 紫色
            (0, 255, 255),  # 青色
            (128, 0, 128),  # 紫色
            (255, 165, 0),  # 橙色
            (255, 192, 203), # 粉色
            (0, 128, 0),    # 深绿色
        ]
        return colors[class_id % len(colors)]
    
    def stop_processing(self):
        """停止处理"""
        self.is_processing = False
        if self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.quit()
            self.worker_thread.wait()
    
    def start_processing_thread(self, video_path):
        """在线程中启动处理"""
        if self.worker_thread and self.worker_thread.isRunning():
            return False
        
        # 创建工作线程
        self.worker_thread = YOLOProcessorThread(self)
        self.worker_thread.set_video_path(video_path)
        
        # 启动线程
        self.worker_thread.start()
        return True
    
    def export_results(self, output_path, format='json'):
        """导出检测结果"""
        try:
            if format.lower() == 'json':
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(self.detection_results, f, ensure_ascii=False, indent=2)
            
            elif format.lower() == 'csv':
                import pandas as pd
                
                # 将结果转换为DataFrame格式
                rows = []
                for frame_data in self.detection_results:
                    frame_id = frame_data['frame_id']
                    for obj in frame_data['objects']:
                        row = {
                            'frame_id': frame_id,
                            'object_id': obj['track_id'],
                            'class_id': obj['class_id'],
                            'class_name': obj['class_name'],
                            'confidence': obj['confidence'],
                            'bbox_x1': obj['bbox'][0],
                            'bbox_y1': obj['bbox'][1],
                            'bbox_x2': obj['bbox'][2],
                            'bbox_y2': obj['bbox'][3]
                        }
                        rows.append(row)
                
                df = pd.DataFrame(rows)
                df.to_csv(output_path, index=False, encoding='utf-8-sig')
            
            return True
            
        except Exception as e:
            self.error_occurred.emit(f"导出结果失败: {str(e)}")
            return False
    
    def get_detection_summary(self):
        """获取检测摘要信息"""
        if not self.detection_results:
            return {}
        
        total_detections = sum(frame['count'] for frame in self.detection_results)
        total_frames = len(self.detection_results)
        
        # 统计各类别数量
        class_counts = {}
        for frame_data in self.detection_results:
            for obj in frame_data['objects']:
                class_name = obj['class_name']
                class_counts[class_name] = class_counts.get(class_name, 0) + 1
        
        return {
            'total_frames': total_frames,
            'total_detections': total_detections,
            'average_detections_per_frame': total_detections / total_frames if total_frames > 0 else 0,
            'class_counts': class_counts
        } 