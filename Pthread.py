#包含图片分类的线程的相关内容
import argparse
import sys
sys.path.insert(0,r'D:/Graduate Design/project')
sys.path.insert(0,r'D:/Graduate Design/project/face-cluster-framework')
from ultralytics import YOLO 
from PIL import Image
import cv2 as cv
from facenet_pytorch import MTCNN, InceptionResnetV1
from torchvision import transforms
import matplotlib.pyplot as plt
import torch
import datatask
import yolos
from face_feature_extract import models,extract_feature
from face_cluster.face_cluster_by_infomap import cluster_main,new_cluster
import numpy as np
from qtpy.QtCore import QObject, QThread
from qtpy import QtCore, QtGui

CLASSES = [
    'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck', 'boat', 'traffic light',
    'fire hydrant',
    'stop sign', 'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra',
    'giraffe', 'backpack', 'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball',
    'kite',
    'baseball bat', 'baseball glove', 'skateboard', 'surfboard', 'tennis racket', 'bottle', 'wine glass', 'cup', 'fork',
    'knife', 'spoon', 'bowl', 'banana', 'apple', 'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza',
    'donut',
    'cake', 'chair', 'couch', 'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop', 'mouse', 'remote',
    'keyboard', 'cell phone', 'microwave', 'oven', 'toaster', 'sink', 'refrigerator', 'book', 'clock', 'vase',
    'scissors',
    'teddy bear', 'hair drier', 'toothbrush']#输出序号和类别对应的列表



def setparser():
    parser = argparse.ArgumentParser(description='Face Cluster')#解析器
    parser.add_argument('--is_cuda', default='False', type=str)

# feature-extract config
    model_names = sorted(name for name in models.__dict__
                     if name.islower() and not name.startswith("__")
                     and callable(models.__dict__[name]))


    parser.add_argument('--arch',
                    '-a',
                    metavar='ARCH',
                    default='resnet50',
                    choices=model_names,
                    help='model architecture: ' + ' | '.join(model_names) +
                    ' (default: resnet18)')
    parser.add_argument('-j', '--workers', default=1, type=int)
    parser.add_argument('-b', '--batch-size', default=128, type=int)
    parser.add_argument('--input-size', default=112, type=int)
    parser.add_argument('--feature-dim', default=256, type=int)
    parser.add_argument('--load-path', default='./face-cluster-framework/pretrain_models/res50_softmax.pth.tar', type=str)
    parser.add_argument('--strict', dest='strict', action='store_true')
    parser.add_argument('--output-path', default='./bin/test.bin', type=str)

# cluster config
    parser.add_argument('--input_picture_path', default='./face-cluster-framework/data/input_pictures/', type=str)
    parser.add_argument('--output_picture_path', default='./face-cluster-framework/data/output_pictures/', type=str)
    parser.add_argument('--knn_method', default='faiss-cpu', type=str)
    parser.add_argument('--is_evaluate', default='False', type=str)
    parser.add_argument('--k', default=80, type=int)
    parser.add_argument('--min_sim', default=0.5, type=float)
    parser.add_argument('--metrics', default=['pairwise', 'bcubed', 'nmi'], type=list)
    parser.add_argument('--label_path', default='./face-cluster-framework/data/tmp/test.meta', type=str)
    parser.add_argument('--save_result', default='False', type=str)
    return parser

class workThread(QObject):
    #图像处理完成信号
    to_show_img_signal = QtCore.Signal(str)#对图像处理完成后，会发送一个信号
    #finished=QtCore.Signal()
    model = YOLO('yolov8n.pt')
    global args
    parser=setparser()
    args = parser.parse_args()#设置参数
    def __init__(self):
        super(workThread, self).__init__()
       
    def work(self):#添加照片后的自动处理操作
        conn=datatask.open('album')#打开数据库
        pa=datatask.select_p(conn)#选择未被分类的图片
        photolist=yolos.first_defections(pa,self.model)#初次分类，主要是将照片分类为人像、事物和其他三类，并返回新增图像中含人脸图像的路径
        #提取特征向量相关操作
        conn=datatask.open('album')#打开数据库
        plist=datatask.select_dthings_name(conn,photolist)
        filelist,facelist=yolos.image_cut_person(plist)
        features = extract_feature.extract_fature(args,filelist,facelist)#得到特征向量
        datatask.bulk_insert_with_transaction(conn,filelist,features)#存入数据库
        datatask.close(conn)#关闭数据库
        #处理完成发送信号
        self.to_show_img_signal.emit("done!")

    def work_2(self):
        print("原神，启动！")
        conn=datatask.open("album")
        listf=datatask.select_face_null(conn)
        features=[]
        feature_infos=[]
        for l in listf:
            feature=np.frombuffer(l[2],dtype=np.float32)
            print(feature)
            features.append(feature)
            info=[]
            info.append(l[0])
            info.append(l[1])
            feature_infos.append(info)
        features=np.vstack(features)
        cluster_main(args,features,feature_infos)    
        self.to_show_img_signal.emit("done!")
    def work_3(self):
        print("王者，启动！")
        new_cluster(args)
        self.to_show_img_signal.emit("done!")                          