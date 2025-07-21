## 📄 项目名称

YOLOv11目标识别与跟踪可视化界面

## 🎯 项目目标

开发一个支持导入视频，基于YOLOv11进行目标识别，结合Ultralytics跟踪算法进行多目标跟踪的可视化操作工具，用于演示和测试识别与跟踪效果。

---

## ✅ 功能需求

### 1. 视频导入功能

* 支持格式：MP4、AVI、MOV
* 支持拖拽导入或按钮上传
* 可播放、暂停、跳转进度

### 2. YOLOv11模型加载与目标识别

* 使用Ultralytics YOLOv11 模型（调用本地模型）
* 实时/逐帧显示识别结果（边框、标签、置信度）

### 3. 跟踪功能

* 提供两种Ultralytics跟踪算法选择（如：ByteTrack、BoT-SORT）
* 跟踪ID持续显示（不同颜色、标签）
* 可选开启/关闭跟踪功能

### 4. 视频处理结果展示

* 上方视频+下方日志区域展示检测数量、帧率等信息
* 支持帧步进查看处理细节

### 5. 导出结果

* 支持导出识别+跟踪后的视频（MP4）
* 支持导出检测/跟踪日志（JSON / CSV格式，包括frame\_id, object\_id, class, bbox等）

---

## 🖥️ 界面需求

### 主界面布局（PyQt实现）：

* **顶部菜单栏**：导入视频 / 开始检测 / 选择跟踪算法 / 导出结果
* **中央视频区域**：

  * 左侧：原始视频
  * 右侧：处理后视频（可选识别/跟踪切换）
* **底部操作栏**：

  * 播放/暂停、帧跳转、识别开关、跟踪开关、帧率显示等

---

## ⚙️ 技术要求

| 模块     | 技术选型                            |
| -------- | ----------------------------------- |
| 模型     | YOLOv11 (Ultralytics库)             |
| 跟踪算法 | ByteTrack / BoT-SORT（Ultralytics） |
| 视频处理 | OpenCV                              |
| 界面     | PyQt6                               |
| 导出     | FFmpeg（视频），pandas（日志）      |

---

## 🚀 快速开始

### 1. 环境安装

```bash
# 克隆项目
git clone https://github.com/BIANG-qilie/YOLO-Operator.git
cd YOLO-Operator

# 安装依赖
pip install -r requirements.txt
```

### 2. 模型权重文件

本项目使用YOLO11 OBB（有向边界框）模型进行目标检测。为了避免在Git仓库中存储大文件，模型权重文件将在首次运行时自动下载。

#### 自动下载（推荐）
- 程序首次运行时会自动检测并下载所需的模型文件
- 默认下载 `yolo11x-obb.pt`（113MB）到 `weights/` 目录

#### 手动下载
如果需要手动下载或选择其他模型，可以使用提供的下载脚本：

```bash
# 下载所有可用模型
python download_weights.py

# 下载指定模型
python download_weights.py --model yolo11n-obb.pt

# 查看可用模型列表
python download_weights.py --list
```

#### 可用模型

| 模型文件 | 大小 | 描述 | 下载地址 |
|---------|------|------|----------|
| yolo11n-obb.pt | 5.6MB | 轻量版OBB模型 | [下载](https://github.com/ultralytics/assets/releases/download/v8.3.0/yolo11n-obb.pt) |
| yolo11s-obb.pt | 19.8MB | 小型OBB模型 | [下载](https://github.com/ultralytics/assets/releases/download/v8.3.0/yolo11s-obb.pt) |
| yolo11m-obb.pt | 42.9MB | 中型OBB模型 | [下载](https://github.com/ultralytics/assets/releases/download/v8.3.0/yolo11m-obb.pt) |
| yolo11l-obb.pt | 54.3MB | 大型OBB模型 | [下载](https://github.com/ultralytics/assets/releases/download/v8.3.0/yolo11l-obb.pt) |
| yolo11x-obb.pt | 113MB | 超大型OBB模型（默认） | [下载](https://github.com/ultralytics/assets/releases/download/v8.3.0/yolo11x-obb.pt) |

> 📝 **注意**: 所有模型文件都来自 [Ultralytics 官方发布](https://docs.ultralytics.com/tasks/obb/#models)

### 3. 运行程序

```bash
python main.py
```

---

## 📚 使用说明

1. **导入视频**: 点击"导入视频"按钮或拖拽视频文件到界面
2. **模型加载**: 程序会自动加载YOLO模型（首次运行会自动下载）
3. **开始检测**: 点击"开始检测"按钮开始处理视频
4. **查看结果**: 在界面中实时查看检测和跟踪结果
5. **导出结果**: 处理完成后可导出结果视频和检测日志

