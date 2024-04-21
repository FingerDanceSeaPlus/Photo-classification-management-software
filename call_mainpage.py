from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from pages.Ui_mainpage import Ui_MainWindow
from PyQt5.QtCore import *
import sys
import datatask
import os
from PyQt5.QtGui import *
import Pthread
import cv2
from PIL import ImageQt,Image
from pages.Ui_face import Ui_Dialog
import yolos
class MainPageWindow(QMainWindow,Ui_MainWindow):
    chooseSignal=pyqtSignal(str)
    conn=0
    display_image_size=150
    display_image_size_things=120

    def __init__(self, parent=None):
        super(MainPageWindow,self).__init__(parent)
        self.setupUi(self)
        self.initUI()
        self.vertocall = QVBoxLayout()
        self.vertocall.addWidget(self.scrollArea)
        i=0
        self.CAM_NUM = 0
        self.cap = cv2.VideoCapture()
        if os.path.exists("album"):
            i=1
        if i==0:
            conn=datatask.open("album")
            datatask.ctable_alarm(conn)#假如是第一次启动的话，需要新建表
            datatask.ctable_dthings(conn)
            datatask.ctable_facefeature(conn)
        else:
            conn=datatask.open("album")
        
        

    def th(self):#设置图像处理线程
        self.thread=QThread()
        #实例化线程类
        self.work_thread=Pthread.workThread()
        #把实例化线程移动到thread管理
        self.work_thread.moveToThread(self.thread)
        #线程开始执行之前，从相关线程发射信号
        self.thread.started.connect(self.work_thread.work)
        #接受子线程信号发来的数据
        self.work_thread.to_show_img_signal.connect(self.notice)
        self.work_thread.to_show_img_signal.connect(self.thread.quit)#执行线程退出操作
        self.thread.finished.connect(self.threadStop)#收到退出信号后的操作
        #线程执行完毕关闭线程
        #self.thread.finished.connect(self.work_thread.deleteLater)
        #self.thread.finished.connect(self.thread.deleteLater)   

    def th2(self):#设置人脸聚类线程
        self.thread=QThread()
        #实例化线程类
        self.work_thread=Pthread.workThread()
        #把实例化线程移动到thread管理
        self.work_thread.moveToThread(self.thread)
        #线程开始执行之前，从相关线程发射信号
        self.thread.started.connect(self.work_thread.work_2)#连接的是另一个函数
        #接受子线程信号发来的数据
        self.work_thread.to_show_img_signal.connect(self.notice)
        self.work_thread.to_show_img_signal.connect(self.thread.quit)#执行线程退出操作
        self.thread.finished.connect(self.threadStop)#收到退出信号后的操作
    
    def th3(self):
        self.thread=QThread()
        #实例化线程类
        self.work_thread=Pthread.workThread()
        #把实例化线程移动到thread管理
        self.work_thread.moveToThread(self.thread)
        #线程开始执行之前，从相关线程发射信号
        self.thread.started.connect(self.work_thread.work_3)#连接的是另一个函数
        #接受子线程信号发来的数据
        self.work_thread.to_show_img_signal.connect(self.notice)
        self.work_thread.to_show_img_signal.connect(self.thread.quit)#执行线程退出操作
        self.thread.finished.connect(self.threadStop)#收到退出信号后的操作
    


    def threadStart(self):
        #开启线程
        self.thread.start()

    def threadStop(self):
        
        self.thread.wait()#等待，确保线程完全退出
        print("ok")


    def initUI(self):#初始化UI
        #设置左侧工具栏按钮的信号值与槽
        self.b_allp.clicked.connect(self.frameController)
        self.b_things.clicked.connect(self.frameController)
        self.b_face.clicked.connect(self.frameController)
        self.b_g.clicked.connect(self.frameController)
        #设置菜单栏中“文件”选项所属的选项的信号值与槽
        self.actionadd_folder.triggered.connect(self.sel_directory)
        self.actionadd_one.triggered.connect(self.sel_single_file)
        self.actionadd_pl.triggered.connect(self.sel_mul_files)
        #设置事物界面中各种类按钮的信号值与槽
        self.B_transport.clicked.connect(self.frameController_2)
        self.B_aminals.clicked.connect(self.frameController_2)
        self.B_sthings.clicked.connect(self.frameController_2)
        self.B_sports.clicked.connect(self.frameController_2)
        self.B_home.clicked.connect(self.frameController_2)
        #设置人脸分离界面中各种按钮的信号值与槽
        self.cluster_all.clicked.connect(self.clusterall)
        self.cluster_newadd.clicked.connect(self.clusternewadd)
        #设置搜索界面相关按钮
        self.openca.clicked.connect(self.open_camera)
        self.closeca.clicked.connect(self.close_camera)
        self.openca.setEnabled(True)
        self.starts.clicked.connect(self.start_search)
        # 初始状态不能关闭摄像头
        self.closeca.setEnabled(False)


   #初始化滚动栏
    def clear_layout(self,gl):
        for i in range(gl.count()):
            gl.itemAt(i).widget().deleteLater()


    def start_img_viewer(self,gl):
        self.clear_layout(gl)
        conn=datatask.open("album")
        plist=datatask.getloc_p(conn)
        pnum=len(plist)
        col=0
        row=0
        if pnum !=0:
            for i in range(pnum):
                image_id = plist[i]
                print(image_id)
                pixmap = QPixmap(image_id)
                col,row=self.addImage(gl,pixmap, image_id,col,row)
                QApplication.processEvents()##实时加载，可能图片加载数量比较多
        else:
                QMessageBox.information(self, '提示', '尚未添加照片')
        datatask.close(conn)
    def start_img_viewer_things(self,gl,i):#i决定了显示模式
        self.clear_layout(gl)
        conn=datatask.open("album")
        trans=[1,13]
        ani=[14,23]
        bt=[24,28]
        st=[29,38]
        ft=[39,79]
        if i==0:#交通市政
            p_list=datatask.select_dthings_range(conn,trans[0],trans[1])
        elif i==1:#飞禽走兽
            p_list=datatask.select_dthings_range(conn,ani[0],ani[1])
        elif i==2:#随身物品
            p_list=datatask.select_dthings_range(conn,bt[0],bt[1])
        elif i==3:#运动相关
            p_list=datatask.select_dthings_range(conn,st[0],st[1])
        else:#家居美食
            p_list=datatask.select_dthings_range(conn,ft[0],ft[1])
        pnum=len(p_list)
        col=0
        row=0
        if pnum!=0:
            for record in p_list:
                image_id=record[0]
                pixmap=QPixmap(image_id)
                col,row=self.addImage(gl,pixmap.copy(float(record[2]),float(record[3]),float(record[4])-float(record[2]),float(record[5])-float(record[3])),image_id,col,row)
                QApplication.processEvents()
        else:
            QMessageBox.information(self,"提示","尚未识别到含此类事物的图片")
        datatask.close(conn)

    def start_img_viewer_faces(self,gl):
        self.clear_layout(gl)
        conn=datatask.open("album")
        plist=datatask.select_faceclustered_represant(conn)
        pnum=len(plist)
        col=0
        row=0
        if pnum !=0:
            for record in plist:
                image_id=record[0]
                pixmap=QPixmap(image_id)
                col,row=self.addfaceImage(gl,pixmap.copy(float(record[3]),float(record[4]),float(record[5])-float(record[3]),float(record[6])-float(record[4])),record[2],col,row)
                QApplication.processEvents()
        else:
                QMessageBox.information(self, '提示', '尚未添加照片')
        datatask.close(conn)

    def clusterall(self):
        # 询问用户是否保存更改
        reply = QMessageBox.question(None, '警告！', '继续操作将重置之前所有聚类结果！',
                             QMessageBox.Yes | QMessageBox.Cancel)
        if reply == QMessageBox.Yes:#用户选择重新聚类
            self.th2()
            self.threadStart()
            
    def clusternewadd(self):
        reply = QMessageBox.question(None, '说明！', '仅对新增照片进行分类！',
                             QMessageBox.Yes | QMessageBox.Cancel)
        if reply == QMessageBox.Yes:#用户选择继续
            self.th3()
            self.threadStart()  



    def get_nr_of_image_columns(self):
        #展示图片的区域，计算每排显示图片数。返回的列数-1是因为我不想频率拖动左右滚动条，影响数据筛选效率
        scroll_area_images_width = int(0.68*self.page_0.width())
        if scroll_area_images_width > self.display_image_size:
 
            pic_of_columns = scroll_area_images_width // self.display_image_size  #计算出一行几列；
        else:
            pic_of_columns = 1
 
        return pic_of_columns-1
 
    #对指定的布局添加一个含图片的组件。
    def addImage(self,s_g, pixmap, image_id,col,row):#s_g表示存入的布局的名字
        ##获取图片列数
        nr_of_columns = self.get_nr_of_image_columns()
        #nr_of_widgets = self.page_0.gridLayout.count()
        self.max_columns = nr_of_columns
        if col < self.max_columns:
            col += 1
        else:
            col = 0
            row += 1
        clickable_image = QClickableImage(self.display_image_size, self.display_image_size, pixmap, image_id)
        #clickable_image.clicked.connect(self.on_left_clicked)
        #clickable_image.rightClicked.connect(self.on_right_clicked)
        s_g.addWidget(clickable_image, row,col)
        return col,row
    
    #对指定的布局添加一个含图片的组件。
    def addfaceImage(self,s_g, pixmap, image_id,col,row):#s_g表示存入的布局的名字
        ##获取图片列数
        nr_of_columns = self.get_nr_of_image_columns()
        #nr_of_widgets = self.page_0.gridLayout.count()
        self.max_columns = nr_of_columns
        if col < self.max_columns:
            col += 1
        else:
            col = 0
            row += 1
        clickable_image = QClickableImageface(self.display_image_size, self.display_image_size, pixmap, image_id)
        #clickable_image.clicked.connect(self.on_left_clicked)
        #clickable_image.rightClicked.connect(self.on_right_clicked)
        s_g.addWidget(clickable_image, row,col)
        return col,row

    
    def frameController(self):#页面控制函数
        sender=self.sender().objectName()#获取当前信号发送者
        index={
            "b_allp":0,#page_0
            "b_things":1,
            "b_face":2,
            "b_g":3
        }
        if sender=="b_allp":
            self.start_img_viewer(self.gridLayout0)
        elif sender=="b_face":
            self.start_img_viewer_faces(self.gridLayout_faces)
        elif sender=="b_g":
            self.init_timer()
             
        self.stackedWidget.setCurrentIndex(index[sender])


    def frameController_2(self):#事物界面所属页面控制函数
        sender=self.sender().objectName()#获取当前信号发送者
        index={
            "B_transport":0,#page_0
            "B_aminals":1,
            "B_sthings":2,
            "B_sports":3,
            "B_home":4
        }
        i=index[sender]
        if i==0:
            self.start_img_viewer_things(self.gridLayout_transports,i)
        elif i==1:
            self.start_img_viewer_things(self.gridLayout_animals,i)
        elif i==2:
            self.start_img_viewer_things(self.gridLayout_bthings,i)
        elif i==3:
            self.start_img_viewer_things(self.gridLayout_sthings,i)
        else:
            self.start_img_viewer_things(self.gridLayout_fthings,i)
        self.stackedWidget_2.setCurrentIndex(i)

    #选择单张照片
    def sel_single_file(self):
        conn=datatask.open("album")
        file_path,_=QFileDialog.getOpenFileName(self,"选择照片","/","All Files(*)")
        datatask.insert_p(conn,file_path)
        datatask.show_p(conn)
        datatask.close(conn)
        self.th()
        self.threadStart()
    #选择多张照片
    def sel_mul_files(self):
        conn=datatask.open("album")
        file_paths,_=QFileDialog.getOpenFileNames(self,"选择照片","/","All Files(*)")
        for f in file_paths:
            datatask.insert_p(conn,f)
            datatask.show_p(conn)
        datatask.close(conn)
        self.th()
        self.threadStart()
    #选择一个文件夹
    def sel_directory(self):
        conn=datatask.open("album")
        dir_path=QFileDialog.getExistingDirectory(self,"选择目录","/",QFileDialog.ShowDirsOnly)
        filenames=os.listdir(dir_path)#获取该文件夹下的所有文件（假设它们都是照片吧）
        for f in filenames:
            datatask.insert_p(conn,dir_path+"/"+f)
            datatask.show_p(conn)
        datatask.close(conn)
        self.th()
        self.threadStart()
    
    def notice(self):
        reply=QMessageBox.information(self,"提示","图片已处理完成！",QMessageBox.Yes)
        int(reply)
    
    CAM_NUM=0
    cap=cv2.VideoCapture()
    def open_camera(self):
        index = self.comboBox.currentIndex()# 获取选择的设备名称
        self.CAM_NUM = index
        flag = self.cap.open(self.CAM_NUM)# 检测该设备是否能打开
        if flag is False:
            QMessageBox.information(self, "警告", "该设备未正常连接", QMessageBox.Ok)
        else:
            # 幕布可以播放
            self.showspace.setEnabled(True)
            # 打开摄像头按钮不能点击
            self.openca.setEnabled(False)
            # 关闭摄像头按钮可以点击
            self.closeca.setEnabled(True)
            self.timer.start()
            self.timer.blockSignals(False)
    def close_camera(self):

        self.cap.release()
        self.openca.setEnabled(True)
        self.closeca.setEnabled(False)
        self.timer.stop()
        

     # 播放视频画面
    def init_timer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.show_pic)

        # 显示视频图像
    def show_pic(self):
        ret, self.img = self.cap.read()
        photo=0
        if ret:
            cur_frame = cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB)
            # 视频流的长和宽
            height, width = cur_frame.shape[:2]
            pixmap = QImage(cur_frame, width, height, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(pixmap)
            # 获取是视频流和label窗口的长宽比值的最大值，适应label窗口播放，不然显示不全
            ratio = max(width/self.showspace.width(), height/self.showspace.height())
            pixmap.setDevicePixelRatio(ratio)
            # 视频流置于label中间部分播放
            self.showspace.setAlignment(Qt.AlignCenter)
            self.showspace.setPixmap(pixmap)

    def start_search(self):
        images=[]
        #开始搜索
        cv2.imwrite('search.png',self.img)
        face=cv2.imread('search.png')
        pil_img = Image.fromarray(cv2.cvtColor(face,cv2.COLOR_BGR2RGB))
        
        #image = ImageQt.fromqimage(showImage)
        images.append(pil_img)
        plist=yolos.facesearch(images)
        resultshow=facemoreWindow2(plist)
        resultshow.show()
        resultshow.exec_()

class QClickableImage(QWidget):#定义图片类
    image_id =''
    def __init__(self,width =0,height =0,pixmap =None,image_id = ''):
        QWidget.__init__(self)
 
        self.width =width
        self.height = height
        self.pixmap =pixmap
 
        self.layout =QVBoxLayout(self)
        self.lable2 =QLabel()
        self.lable2.setObjectName('label2')
 
        if self.width and self.height:
            self.resize(self.width,self.height)
        if self.pixmap and image_id:
            pixmap = self.pixmap.scaled(QSize(self.width,self.height),Qt.KeepAspectRatio,Qt.SmoothTransformation)
            self.label1 = MyLabel(pixmap, image_id)
            self.label1.setObjectName('label1')
            self.layout.addWidget(self.label1)
 
        if image_id:
            self.image_id =image_id
            self.lable2.setText(image_id.split('/')[-1])
            self.lable2.setAlignment(Qt.AlignCenter)
            ###让文字自适应大小
            self.lable2.adjustSize()
            self.layout.addWidget(self.lable2)
        self.setLayout(self.layout)
 
    clicked = pyqtSignal(object)#左键点击
    rightClicked = pyqtSignal(object)#右键点击
 
    def imageId(self):
        return self.image_id


class MyLabel(QLabel):
    global NOP_value, NOP_dict
    def __init__(self, pixmap =None, image_id = None):
        QLabel.__init__(self)
        self.pixmap = pixmap
        self.image_id = image_id
        self.setPixmap(pixmap)
 
        self.setAlignment(Qt.AlignCenter)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.rightMenuShow)  # 开放右键策略
    
    def lmouseevent(self):
        id=self.image_id
        dialog_fault = QDialog()
        url_father = os.path.dirname(os.path.abspath(__file__))
        pic = QPixmap(id)
        label_pic = QLabel("show", dialog_fault)
        label_pic.setPixmap(pic)
        label_pic.setGeometry(10,10,1019,537)
        dialog_fault.exec_()

    def rightMenuShow(self, point):
        # 添加右键菜单
        self.popMenu = QMenu()
        fd = QAction(u'放大查看', self)
        sc = QAction(u'删除', self)
        xs = QAction(u'详情', self)
        self.popMenu.addAction(fd)
        self.popMenu.addAction(sc)
        self.popMenu.addAction(xs)
        # 绑定事件
        fd.triggered.connect(self.larger)
        sc.triggered.connect(self.delete)
        xs.triggered.connect(self.rshow)
        self.showContextMenu(QCursor.pos())
 
    def rshow(self):
        '''
        do something
        '''
 
    def delete(self):
        '''
        do something
        '''
        conn=datatask.open('album')
        datatask.delete_p(conn,self.image_id)#删除基础信息表中的相关记录
        datatask.delete_dthings(conn,self.image_id)#删除物体表中的相关记录
        datatask.delete_face(conn,self.image_id)#删除人脸记录
        datatask.close(conn)


 
    def larger(self):
        '''
        do something
        '''
        id=self.image_id
        dialog_fault = QDialog()
        #url_father = os.path.dirname(os.path.abspath(__file__))
        pic = QPixmap(id)
        label_pic = QLabel("show", dialog_fault)
        label_pic.setScaledContents(True)
        label_pic.setPixmap(pic)
        label_pic.adjustSize()
        dialog_fault.exec_()
 
    def showContextMenu(self, pos):
        # 调整位置
        '''''
        右键点击时调用的函数
        '''
        # 菜单显示前，将它移动到鼠标点击的位置
 
        self.popMenu.move(pos)
        self.popMenu.show()
 
    def menuSlot(self, act):
        print(act.text())



class QClickableImageface(QWidget):#定义人脸图片类
    def __init__(self,width =0,height =0,pixmap =None,image_id = ''):
        QWidget.__init__(self)
 
        self.width =width
        self.height = height
        self.pixmap =pixmap
        self.image_id=image_id
        self.layout =QVBoxLayout(self)
        self.lable2 =QLabel()
        self.lable2.setObjectName('label2')
 
        if self.width and self.height:
            self.resize(self.width,self.height)
        if self.pixmap and image_id:
            pixmap = self.pixmap.scaled(QSize(self.width,self.height),Qt.KeepAspectRatio,Qt.SmoothTransformation)
            self.label1 = MyLabel2(pixmap, image_id)
            self.label1.setObjectName('label1')
            self.layout.addWidget(self.label1)
 
        if image_id:
            self.image_id =image_id
            self.lable2.setText(image_id)
            self.lable2.setAlignment(Qt.AlignCenter)
            ###让文字自适应大小
            self.lable2.adjustSize()
            self.layout.addWidget(self.lable2)
        self.setLayout(self.layout)
 
    clicked = pyqtSignal(object)#左键点击
    rightClicked = pyqtSignal(object)#右键点击
 
    def imageId(self):
        return self.image_id


class MyLabel2(QLabel):
    global NOP_value, NOP_dict
    def __init__(self, pixmap =None, image_id = None):
        QLabel.__init__(self)
        self.pixmap = pixmap
        self.image_id = image_id
        self.setPixmap(pixmap)
 
        self.setAlignment(Qt.AlignCenter)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.rightMenuShow)  # 开放右键策略
    
    def lmouseevent(self):
        id=self.image_id
        dialog_fault = QDialog()
        url_father = os.path.dirname(os.path.abspath(__file__))
        pic = QPixmap(id)
        label_pic = QLabel("show", dialog_fault)
        label_pic.setPixmap(pic)
        label_pic.setGeometry(10,10,1019,537)
        dialog_fault.exec_()

    def rightMenuShow(self, point):
        # 添加右键菜单
        self.popMenu = QMenu()
        seeall = QAction(u'查看所有', self)
        detail = QAction(u'详情', self)
        rename=QAction(u'重命名',self)
        self.popMenu.addAction(seeall)
        self.popMenu.addAction(detail)
        self.popMenu.addAction(rename)
        # 绑定事件
        seeall.triggered.connect(self.seeall)
        detail.triggered.connect(self.detail)
        rename.triggered.connect(self.rename)
        self.showContextMenu(QCursor.pos())
    
    def seeall(self):#展示这类人脸照片的所有
        facepage=facemoreWindow(self.image_id)
        facepage.show()
        facepage.exec_()
        
    def detail(self):
        conn=datatask.open('album')
        plist=datatask.select_facesource_cluster(conn,self.image_id)
        num=len(plist)
        datatask.close(conn)
        QMessageBox.information(self, '详情', '该人脸共有'+str(num)+'张照片')

    def rename(self):
        name,ok=QInputDialog.getText(self, 'Text Input Dialog', '输入姓名：')
        if ok and name:
            conn=datatask.open('album')
            datatask.updata_face_rename_cluster(conn,self.image_id,name)
            datatask.close(conn)
            QMessageBox.information(self,'提示', '重命名完成！')

    def larger(self):
        '''
        do something
        '''
        id=self.image_id
        dialog_fault = QDialog()
        #url_father = os.path.dirname(os.path.abspath(__file__))
        pic = QPixmap(id)
        label_pic = QLabel("show", dialog_fault)
        label_pic.setScaledContents(True)
        label_pic.setPixmap(pic)
        label_pic.adjustSize()
        dialog_fault.exec_()
 
    def showContextMenu(self, pos):
        # 调整位置
        '''''
        右键点击时调用的函数
        '''
        # 菜单显示前，将它移动到鼠标点击的位置
 
        self.popMenu.move(pos)
        self.popMenu.show()
 
    def menuSlot(self, act):
        print(act.text())


class facemoreWindow(QDialog):#子界面相关逻辑
    display_image_size=150
    def __init__(self,cluster):
        QDialog.__init__(self)
        self.child=Ui_Dialog()
        self.child.setupUi(self)
        self.cluster=cluster
        self.start_img_viewer_detail(self.child.gridLayout_fphotos,self.cluster)
        

    def clear_layout(self,gl):
        for i in range(gl.count()):
            gl.itemAt(i).widget().deleteLater()

    def get_nr_of_image_columns(self):
        #展示图片的区域，计算每排显示图片数。返回的列数-1是因为我不想频率拖动左右滚动条，影响数据筛选效率
        scroll_area_images_width = int(0.68*self.child.scrollAreaWidgetContents.width())
        if scroll_area_images_width > self.display_image_size:
 
            pic_of_columns = scroll_area_images_width // self.display_image_size  #计算出一行几列；
        else:
            pic_of_columns = 1
 
        return pic_of_columns-1

    def addImage(self,s_g, pixmap, image_id,cluster,col,row):#s_g表示存入的布局的名字
        ##获取图片列数
        nr_of_columns = self.get_nr_of_image_columns()
        #nr_of_widgets = self.page_0.gridLayout.count()
        self.max_columns = nr_of_columns
        if col < self.max_columns:
            col += 1
        else:
            col = 0
            row += 1
        clickable_image = QClickableImageSame(self.display_image_size, self.display_image_size, pixmap, image_id,cluster)
        #clickable_image.clicked.connect(self.on_left_clicked)
        #clickable_image.rightClicked.connect(self.on_right_clicked)
        s_g.addWidget(clickable_image, row,col)
        return col,row

    def start_img_viewer_detail(self,gl,cluster):
        self.clear_layout(gl)
        conn=datatask.open("album")
        plist=datatask.select_facesource_cluster(conn,cluster)
        pnum=len(plist)
        col=0
        row=0
        if pnum !=0:
            for i in range(pnum):
                image_id = plist[i]
                print(image_id)
                pixmap = QPixmap(image_id)
                col,row=self.addImage(gl,pixmap, image_id,cluster,col,row)
                QApplication.processEvents()##实时加载，可能图片加载数量比较多
        else:
                QMessageBox.information(self, '提示', '尚未添加照片')
        datatask.close(conn)

class facemoreWindow2(QDialog):#子界面相关逻辑
    display_image_size=150
    def __init__(self,plist):
        QDialog.__init__(self)
        self.child=Ui_Dialog()
        self.child.setupUi(self)
        self.plist=plist
        self.start_img_viewer_detail(self.child.gridLayout_fphotos,self.plist)
        

    def clear_layout(self,gl):
        for i in range(gl.count()):
            gl.itemAt(i).widget().deleteLater()

    def get_nr_of_image_columns(self):
        #展示图片的区域，计算每排显示图片数。返回的列数-1是因为我不想频率拖动左右滚动条，影响数据筛选效率
        scroll_area_images_width = int(0.68*self.child.scrollAreaWidgetContents.width())
        if scroll_area_images_width > self.display_image_size:
 
            pic_of_columns = scroll_area_images_width // self.display_image_size  #计算出一行几列；
        else:
            pic_of_columns = 1
 
        return pic_of_columns-1
    def addImage(self,s_g, pixmap, image_id,col,row):#s_g表示存入的布局的名字
        ##获取图片列数
        nr_of_columns = self.get_nr_of_image_columns()
        #nr_of_widgets = self.page_0.gridLayout.count()
        self.max_columns = nr_of_columns
        if col < self.max_columns:
            col += 1
        else:
            col = 0
            row += 1
        clickable_image = QClickableImage(self.display_image_size, self.display_image_size, pixmap, image_id)
        #clickable_image.clicked.connect(self.on_left_clicked)
        #clickable_image.rightClicked.connect(self.on_right_clicked)
        s_g.addWidget(clickable_image, row,col)
        return col,row
    def start_img_viewer_detail(self,gl,plist):
        self.clear_layout(gl)
        conn=datatask.open("album")

        pnum=len(plist)
        col=0
        row=0
        if pnum !=0:
            for i in range(pnum):
                image_id = plist[i]
                print(image_id)
                pixmap = QPixmap(image_id)
                col,row=self.addImage(gl,pixmap, image_id,col,row)
                QApplication.processEvents()##实时加载，可能图片加载数量比较多
        else:
                QMessageBox.information(self, '提示', '尚未找到照片')
        datatask.close(conn)



class QClickableImageSame(QWidget):#定义人脸图片类
    def __init__(self,width =0,height =0,pixmap =None,image_id = '',cluster=''):
        QWidget.__init__(self)
 
        self.width =width
        self.height = height
        self.pixmap =pixmap
        self.image_id=image_id
        self.cluster=cluster
        self.layout =QVBoxLayout(self)
        self.lable2 =QLabel()
        self.lable2.setObjectName('label2')
 
        if self.width and self.height:
            self.resize(self.width,self.height)
        if self.pixmap and image_id:
            pixmap = self.pixmap.scaled(QSize(self.width,self.height),Qt.KeepAspectRatio,Qt.SmoothTransformation)
            self.label1 = MyLabel3(pixmap, image_id,cluster)
            self.label1.setObjectName('label1')
            self.layout.addWidget(self.label1)
 
        if image_id:
            self.image_id =image_id
            self.lable2.setText(image_id.split('/')[-1])
            self.lable2.setAlignment(Qt.AlignCenter)
            ###让文字自适应大小
            self.lable2.adjustSize()
            self.layout.addWidget(self.lable2)
        self.setLayout(self.layout)
 
    clicked = pyqtSignal(object)#左键点击
    rightClicked = pyqtSignal(object)#右键点击
 
    def imageId(self):
        return self.image_id


class MyLabel3(QLabel):
    global NOP_value, NOP_dict
    def __init__(self, pixmap =None, image_id = None,cluster=None):
        QLabel.__init__(self)
        self.pixmap = pixmap
        self.image_id = image_id
        self.cluster=cluster
        self.setPixmap(pixmap)
 
        self.setAlignment(Qt.AlignCenter)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.rightMenuShow)  # 开放右键策略
    
    def lmouseevent(self):
        id=self.image_id
        dialog_fault = QDialog()
        url_father = os.path.dirname(os.path.abspath(__file__))
        pic = QPixmap(id)
        label_pic = QLabel("show", dialog_fault)
        label_pic.setPixmap(pic)
        label_pic.setGeometry(10,10,1019,537)
        dialog_fault.exec_()

    def rightMenuShow(self, point):
        # 添加右键菜单
        self.popMenu = QMenu()
        fd = QAction(u'放大查看', self)
        sc = QAction(u'删除', self)
        re = QAction(u'更换分组', self)
        self.popMenu.addAction(fd)
        self.popMenu.addAction(sc)
        self.popMenu.addAction(re)
        # 绑定事件
        fd.triggered.connect(self.larger)
        sc.triggered.connect(self.delete)
        re.triggered.connect(self.re)
        self.showContextMenu(QCursor.pos())
 
    def re(self):
        name,ok=QInputDialog.getText(self, 'Text Input Dialog', '输入新组名：')
        if ok and name:
            conn=datatask.open('album')
            datatask.updata_face_cluster_source(conn,self.image_id,self.cluster,name)
            datatask.close(conn)
            QMessageBox.information(self,'提示', '更换完成！')
 
    def delete(self):
        '''
        do something
        '''
        conn=datatask.open('album')
        datatask.delete_p(conn,self.image_id)#删除基础信息表中的相关记录
        datatask.delete_dthings(conn,self.image_id)#删除物体表中的相关记录
        datatask.delete_face(conn,self.image_id)#删除人脸记录
        datatask.close(conn)


 
    def larger(self):
        '''
        do something
        '''
        id=self.image_id
        dialog_fault = QDialog()
        #url_father = os.path.dirname(os.path.abspath(__file__))
        pic = QPixmap(id)
        label_pic = QLabel("show", dialog_fault)
        label_pic.setScaledContents(True)
        label_pic.setPixmap(pic)
        label_pic.adjustSize()
        dialog_fault.exec_()
 
    def showContextMenu(self, pos):
        # 调整位置
        '''''
        右键点击时调用的函数
        '''
        # 菜单显示前，将它移动到鼠标点击的位置
 
        self.popMenu.move(pos)
        self.popMenu.show()
 
    def menuSlot(self, act):
        print(act.text())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainPageWindow()
    mainWindow.show()
    sys.exit(app.exec_())