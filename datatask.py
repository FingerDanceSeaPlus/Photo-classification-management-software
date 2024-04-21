#数据库相关操作
import sqlite3
import numpy as np
def open(d):
    #打开数据库，若不存在，会创建，d是数据库的名称
    conn=sqlite3.connect(d)
    print("数据库打开成功")
    return conn

def ctable_alarm(conn):
    #创建相册表，c是数据库对象
    c=conn.cursor()#创建游标
    c.execute("""create table palarm
    (loc char(50) not null,
     form char(50) not null,
     class char(50),
     primary key(loc)                );
    """)
    conn.commit()

def ctable_dthings(conn):
    c=conn.cursor()
    c.execute("""create table dthings
              (source char(50) not null,
               paixv int not null,
               kind int not null,
              x0 float not null,
              y0 float not null,
              x1 float not null,
              y1 float not null,
              primary key(source,paixv));
    """)
    conn.commit()

def ctable_facefeature(conn):#创建人脸特征表
    c=conn.cursor()
    c.execute("""create table facefeature(source char(50) not null,paixv int not null,feature blob not null,cluster char(50))
    """)
    conn.commit()


def insert_p(conn,loc):#对图片库新增一张图片的记录
    c=conn.cursor()
    form=loc.split(".")[1]
    s="insert into palarm values('"+loc+"','"+form+"',null"+");"
    c.execute(s)
    conn.commit()

def insert_dthings(conn,source,order,kind,x0,yo,x1,y1):
    c=conn.cursor()
    s="insert into dthings values('"+source+"',"+str(order)+","+str(kind)+","+str(x0)+","+str(yo)+","+str(x1)+","+str(y1)+");"
    c.execute(s)
    conn.commit()

def insert_face_feature(conn,infors,arrs):#新增含特征向量的人脸记录，infor记录了人脸所属图片的路径和序号
    c=conn.cursor()
    bytes_features=[]
    for feature in arrs:
        b=feature.tostring()
        bytes_features.append(b)
    i=0
    for infor in infors:
        infor.append(bytes_features[i])
        i+=1
    return infors


def bulk_insert_with_transaction(conn,infors,arrs):#新增含特征向量的人脸记录，infor记录了人脸所属图片的路径和序号
    cursor = conn.cursor()
    bytes_features=[]
    for feature in arrs:#将特征向量转换为二进制形式
        b=feature.tostring()
        bytes_features.append(b)
    i=0
    for infor in infors:
        infor.append(bytes_features[i])
        i+=1
    try:
        # 开始事务
        cursor.execute('BEGIN TRANSACTION')

        # 批量插入数据
        for d in infors:
            cursor.execute('INSERT INTO facefeature (source, paixv, feature) VALUES (?, ?, ?)', d)

        # 提交事务
        cursor.execute('COMMIT')

        print('批量插入成功')

    except Exception as e:
        # 回滚事务
        cursor.execute('ROLLBACK')
        print('批量插入失败：', str(e))

    finally:
        cursor.close()
        


def show_p(conn):#显示palarm表中的所有记录
    c=conn.cursor()
    r = c.execute("SELECT loc,form,class from palarm")
    for row in r:
        print(row)
def show(conn,tname):
    c=conn.cursor()
    r=c.execute("select * from %s"%(tname))
    for row in r:
        print(row)

def getloc_p(conn):#返回含有所有图片存储路径的列表
    c=conn.cursor()
    listf=[]
    r = c.execute("SELECT loc from palarm")
    
    for row in r:
        row_str=" ".join([str(cell) for cell in row])
        listf.append(row_str)
    return listf

def delete_p(conn,loc):
    c=conn.cursor()
    s="delete from palarm where loc='"+loc+"';"
    c.execute(s)
    conn.commit()

def delete_dthings(conn,source):
    c=conn.cursor()
    s="delete from dthings where source='"+source+"';"
    c.execute(s)
    conn.commit()

def delete_allface(conn):#删除人脸特征表中的所有记录
    c=conn.cursor()
    s="delete from facefeature"
    c.execute(s)
    conn.commit()

def delete_face(conn,source):
    c=conn.cursor()
    s="delete from facefeature where source='"+source+"';"
    c.execute(s)
    conn.commit()

def select_p(conn):#搜索palarm中所有完全没被分类的记录，返回一个含有其搜索路径的列表
    c=conn.cursor()
    r=c.execute("select loc from palarm where class is null;")
    listf=[]
    for row in r:
        row_str=" ".join([str(cell) for cell in row])
        listf.append(row_str)
    return listf
def select_p_class(conn,cl):#按类别在palarm中搜索记录
    c=conn.cursor()
    s="select * from palarm where class='"+cl+"';"
    r=c.execute(s)
    listf=[]
    for row in r:
        row_str=" ".join([str(cell) for cell in row])
        listf.append(row_str)
    return listf
def select_dthings_kind(conn,kd):
    c=conn .cursor()
    s="select * from dthings where kind='"+str(kd)+"';"
    r=c.execute(s)
    listf=[]
    for row in r:
        rlist=[]
        for cell in row:
            rlist.append(str(cell))        
        listf.append(rlist)
    return listf

def select_dthings_name(conn,names):#根据照片的名称选择物体记录
    c=conn .cursor()
    for name in names:
       s="select * from dthings where source='"+str(name)+"';"
       r=c.execute(s)
       listf=[]
       for row in r:
            rlist=[]
            for cell in row:
                rlist.append(str(cell))        
            listf.append(rlist)
    return listf

def select_dthings_range(conn,min,max):#返回一个包含每张图片信息的列表的列表
    c=conn .cursor()
    s="select source,kind,x0,y0,x1,y1 from dthings where kind>='"+str(min)+"' and kind<='"+str(max)+"';"
    r=c.execute(s)
    listf=[]
    for row in r:
        rlist=[]
        for cell in row:
            rlist.append(str(cell))        
        listf.append(rlist)
    return listf

def select_face_null(conn):
    c=conn.cursor()
    s="select * from facefeature where cluster is null;"
    r=c.execute(s)
    listf=[]
    for row in r:
        rlist=[]
        for cell in row:
            rlist.append(cell)        
        listf.append(rlist)
    return listf

def select_faceclustered_average(conn):#返回已聚类的人脸的特征向量所属聚类以及它们的平均值
    c=conn.cursor()
    s1="select distinct cluster from facefeature where cluster is not null;"
    r=c.execute(s1)
    listaf=[]
    for row in r:
        pair=[]
        for cell in row:
            pair.append(str(cell))
            listaf.append(pair)
    for l in listaf:
        af=[]
        s2="select feature from facefeature where cluster ='"+l[0]+"';"
        r=c.execute(s2)#得到一连串属于此类的特征向量
        for row in r:
            for fea in row:
                feature=np.frombuffer(fea,dtype=np.float32)
                af.append(feature)
        average=np.mean(af,axis=0)
        l.append(average)
    print(listaf)
    return listaf

def select_faceclustered_represant(conn):#返回已聚类的人脸的特征向量所属聚类以及它们的平均值
    c=conn.cursor()
    s1="select distinct cluster from facefeature where cluster is not null;"
    r=c.execute(s1)
    listaf=[]#每个类的信息
    infos=[]
    for row in r:
        for cell in row:
            listaf.append(str(cell))
    for l in listaf:
        af=[]
        s2="select source,paixv from facefeature where cluster ='"+l+"' limit 0,1;"
        r=c.execute(s2)#得到一连串属于此类的特征向量
        for row in r:
            for cell in row:
                af.append(str(cell))
        af.append(l)
        infos.append(af)
    for record in infos:
        s3="select x0,y0,x1,y1 from dthings where source='"+record[0]+"' and paixv='"+record[1]+"';"
        r=c.execute(s3)
        for row in r:
            for cell in row:
                record.append(cell)
    return infos
        
def select_facesource_cluster(conn,cluster):
    c=conn.cursor()
    s1="select distinct source from facefeature where cluster='"+str(cluster)+"';"
    r=c.execute(s1)
    plist=[]
    for row in r:
        for cell in row:
            plist.append(str(cell))
    return plist

def update_p_class(conn,loc,cl):#修改指定图片的类别
    c=conn.cursor()
    s="update palarm set class='"+cl+"' where loc='"+loc+"';"
    c.execute(s)
    conn.commit()

def update_face_cluster(conn,loc,paixv,cluster):#将指定的人脸特征修改为指定的类别
    c=conn.cursor()
    s="update facefeature set cluster='"+str(cluster)+"' where source='"+loc+"' and paixv='"+str(paixv)+"';"
    c.execute(s)
    conn.commit()

def updata_face_rename_cluster(conn,oldn,newn):#重命名指定的簇
    c=conn.cursor()
    s="update facefeature set cluster='"+str(newn)+"' where cluster='"+str(oldn)+"';"
    c.execute(s)
    conn.commit()

def updata_face_cluster_source(conn,source,cluster,nc):
    c=conn.cursor()
    s="update facefeature set cluster='"+str(nc)+"' where cluster='"+str(cluster)+"' and source='"+str(source)+"';"
    c.execute(s)
    conn.commit()

def close(conn):
    #关闭数据库
    conn.close()
#conn=open('album')
#select_facesource_cluster(conn,"0")
#select_faceclustered_represant(conn)
#show(conn,'facefeature')
#l=select_face_null(conn)
#print(l)
#delete_allface(conn)
#show(conn,"facefeature")
#ctable_facefeature(conn)
#insert_dthings(conn,"test.jpg",1,1,0.1,0.1,2.3,4.0)
#s=select_dthings_kind(conn,1)
#print(s)
#delete_dthings(conn,"test.jpg")
#close(conn)
#c=conn.cursor()
#c.execute("delete from palarm where class is null;")
#conn.commit()
#show_p(conn)
