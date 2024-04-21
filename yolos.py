#存储目标检测的相关内容
#对yolov8的目标检测能力进行测试
from PIL import Image
import cv2 as cv
from facenet_pytorch import MTCNN, InceptionResnetV1
from torchvision import transforms
import matplotlib.pyplot as plt
import torch
import datatask
import argparse
import sys
sys.path.insert(0,r'D:/Graduate Design/project')
sys.path.insert(0,r'D:/Graduate Design/project/face-cluster-framework')
from face_feature_extract import models
import face_feature_extract.extract_feature
import face_cluster.face_cluster_by_infomap

parser = argparse.ArgumentParser(description='Face Cluster')#解析器
parser.add_argument('--is_cuda', default='False', type=str)
model_names = sorted(name for name in models.__dict__
                     if name.islower() and not name.startswith("__")
                     and callable(models.__dict__[name]))
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

def first_defection(p,model):
    #对输入的图片进行第一次目标检测，输出框坐标、目标标签以及置信度
    first_result=[]#列表，保存第一次检测后的结果：保存检测到的物体的种类和对应位置
    results=model.predict(source=p)[0].numpy()
    boxes=results.boxes.data.tolist()
    
    for box in boxes:
        first_result.append({
            "x0":box[0],
            "y0":box[1],
            "x1":box[2],
            "y1":box[3],
            "confidence":box[4],
           "class_id":box[5]
        })
    return first_result
def first_defections(p,model):
    #对输入的一组图片进行第一次目标检测，输出框坐标、目标标签以及置信度
    #输入应为一个各图片存储路径的列表
    results=model(p,conf=0.5)
    conn=datatask.open('album')#打开数据库
    pagelist=[]#记录含人体的照片
    for r in results:
        boxes=r.boxes.data.tolist()
        
        if not boxes:#没有检测到任何物体
            datatask.update_p_class(conn,r.path,'others')#归类为其他类型的图片
            continue
        else :
            datatask.update_p_class(conn,r.path,'things')
        i=0#
        p=0
        for box in boxes:#检测到物体
            if int(box[5])==0 and p==0:#检测到人脸且是第一次检测到
                datatask.update_p_class(conn,r.path,"person")
                pagelist.append(r.path)
                p+=1
            datatask.insert_dthings(conn,r.path,i,int(box[5]),box[0],box[1],box[2],box[3])                
            i+=1#下一个
        i=0#恢复
        p=0    
    datatask.close(conn)
    print(pagelist)
    return pagelist  

def image_cut(m):
    for r in m:#m存储的是这张图片的存储结果
        i=0
        for b in r:#对每一个框
            if b.get('class_id') == 0.0:#检测到的是人体
                i=i+1
                s=b.get('source')#路径
                im=Image.open(s)#打开对应图片
                imgcut=im.crop((int(b.get('x0')),int(b.get('y0')),int(b.get('x1')),int(b.get('y1'))))
                imgcut.save(s.rstrip(".jpg")+"_"+str(i)+"_person.jpg")

def image_cut_person(plist):#plist存储的是从数据库中查询到的图片位置、在图片中的排序、人体范围等信息
    mtcnn = MTCNN(select_largest=False,post_process=False)
    filename=[]
    facelist=[]
    for row in plist:
        im=Image.open(row[0])
        
        imgcut=im.crop((float(row[3]),float(row[4]),float(row[5]),float(row[6])))#裁剪出人体区域
        face=mtcnn(imgcut)
        if face!=None:#如果检测到了人脸
             facelist.append(face)#存储识别到的人脸的tensor对象
             filename.append([row[0],row[1]])#存储文件名称和该人体在图片中的次序
    return filename,facelist#这两者中的记录在次序上是对应的


def facesearch(im):#im为一个包含待搜索图像的列表
    mtcnn = MTCNN(select_largest=False,post_process=False)
    facelist=[]
    filename=[]
    global args
    args = parser.parse_args()#设置参数
    for row in im:
        face=mtcnn(row)
        if face!=None:
            facelist.append(face)
    features=face_feature_extract.extract_feature.extract_fature(args,filename,facelist)
    a=face_cluster.face_cluster_by_infomap.search_cluster(args,features)
    return a


def imshow(tensor, title=None):
    image = tensor.cpu().clone()  # we clone the tensor to not do changes on it
    image = image.squeeze(0)  # remove the fake batch dimension
    unloader = transforms.ToPILImage()
    image = unloader(image)
    plt.imshow(image)
    if title is not None:
        plt.title(title)
    plt.pause(90)  # pause a bit so that plots are updated
'''
normalize = transforms.Normalize(mean=[0.5, 0.5, 0.5],
                                     std=[0.25, 0.25, 0.25])
t=transforms.Compose([
            transforms.ToPILImage(),
            transforms.Resize([112,112]),
            transforms.ToTensor(),
            normalize     
        ])
conn=datatask.open('album')
fi,fl=image_cut_person(datatask.select_dthings_kind(conn,0))
for i in fl:
    img=t(i)
    imshow(img.resize(3,112,112))'''