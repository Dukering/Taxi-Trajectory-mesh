#coding=utf-8
import os
import time
import numpy as np
from multiprocessing import Pool
#网格图的定义
class Gridgraph:
      def __init__(self,origin,size_cell,num_x,num_y):
          self.origin=origin
          self.size_cell=size_cell
          self.data_x=self.create_x(origin,size_cell,num_x)
          self.data_y=self.create_y(origin,size_cell,num_y)
      def create_x(self,origin,size_cell,num_x):
          return np.array(range(num_x+1))*size_cell+origin[0]
      def create_y(self,origin,size_cell,num_y):
          return  origin[1]-np.array(range(num_y+1)) * size_cell

#一条直线已知x或y求y或x
def cal_x_y(nodeA,nodeB,is_x,value):
    tan=(nodeB[1]-nodeA[1])*1.0/(nodeB[0]-nodeA[0])
    #print(tan)
    #求y
    if is_x==True:
       return round((value-nodeA[0])*tan+nodeA[1],10)
    else :
    #求x
       return round((value - nodeA[1])*1.0/tan + nodeA[0],10)

#交点的平均时间
def cal_time(nodeA,nodeB,is_x,value):
    #(time.经度，纬度)
    if is_x==True:
       return (nodeB[0]-nodeA[0])*((value-nodeA[1])*1.0/(nodeB[1]-nodeA[1]))+nodeA[0]
    else :

       return(nodeB[0]-nodeA[0])*((value-nodeA[2])*1.0/(nodeB[2]-nodeA[2]))+nodeA[0]

def merge(a,b,c,is_x):
    result=[]
    if is_x==True:
     for i in range(len(a)):
        result.append([a[i],np.array([b[i]]),c[i]])
    else:
     for i in range(len(a)):
        result.append([a[i], c[i], np.array([b[i]])])
    return result

def cmp_time(nodea,nodeb):
    if nodea[0]>=nodeb[0]:
        return 1
    else:
        return -1

#求俩俩轨迹点之间与网格的交点
def grid_point_single(node_xory_index,is_x,tripa,tripb,Graph):
    delete_y=[]

    if is_x==True:
       judge_x=[True] * len(node_xory_index)

       data=Graph.data_x[node_xory_index]

       orgin=Graph.origin[1]

    else:
        judge_x = [False] * len(node_xory_index)
        data = Graph.data_y[node_xory_index]
        orgin = Graph.origin[0]
    #print([(tripa[2], tripa[1])] * len(node_xory_index), [(tripb[2], tripb[1])] *len(node_xory_index), judge_x,data)

    node_other =map(cal_x_y,[(tripa[1], tripa[2])] * len(node_xory_index), [(tripb[1], tripb[2])] *len(node_xory_index), judge_x,data)

    node_time = map(cal_time,[(tripa[0], tripa[1], tripa[2])] * len(node_xory_index), [(tripb[0], tripb[1], tripb[2])] * len(node_xory_index), judge_x,data)
    #找出与网格的交点相交的y坐标并过滤不在网格内的点
    node_other=np.array(node_other)
    node_time=np.array(node_time)
    #print(node_other)
    if is_x==True:

       node_is_inside=(node_other<=orgin)&(node_other>=Graph.data_y[-1])
       #print(node_is_inside)
    else:
        node_is_inside = (node_other >= orgin) & (node_other <= Graph.data_x[-1])

    node_other = node_other[node_is_inside]
    #print(node_other)
    node_time = node_time[node_is_inside]

    #排除与网格交点相交的node
    node_other_iscon = ~(abs(node_other - orgin) % Graph.size_cell==0)

    #node_other = np.array(node_other).reshape(len(node_other), 1)
    node_time = np.array(node_time).reshape(len(node_time), 1)

    node_other_index = (abs(node_other - orgin) // Graph.size_cell).astype(np.int)
    if is_x==True:
        delete_y=node_other_index[np.where(node_other_iscon==False)]
    node_other_index_gap=node_other_index+node_other_iscon
    node_other_index=np.array(node_other_index).reshape(len(node_other),1)
    node_other_index_gap=np.array(node_other_index_gap).reshape(len(node_other),1)
    node_other_index = np.hstack((node_other_index, node_other_index_gap))

    return merge(node_time,node_xory_index[node_is_inside],node_other_index,is_x),delete_y
#判断一个点是否在网格内 node[1]为y,node[2]为x
def judgein(rangex,rangey,trip_node):
    return (trip_node[1] >= rangex[0]) &( trip_node[1]<=rangex[1])&(trip_node[2]>=rangey[0])&(trip_node[2]<=rangey[1])


#求整条trip与网格交点（time,x(0,1),y(1)）
def grid_point_informal(trip,
                        Graph
                        ):
    grid_point_all=[]
    #由于边界原因，有些trip会分为多个trip
    grid_point=[]
    y_range=(Graph.data_y[-1],Graph.data_y[0])
    x_range=(Graph.data_x[0],Graph.data_x[-1])
    #经度在前
    first_node=trip[0]

    if first_node[1]-Graph.origin[0]<0:
        index=-1
    elif first_node[1]>Graph.data_x[-1]:
        index=(Graph.data_x[-1]-Graph.origin[0])/Graph.size_cell
    else:
        index=int((first_node[1]-Graph.origin[0])//Graph.size_cell)

    if Graph.origin[1]-first_node[2]<0:
        indey=-1
    elif first_node[2]<Graph.data_y[-1]:
        indey=(Graph.origin[1]-Graph.data_y[-1])/Graph.size_cell
    else:
        indey=int((Graph.origin[1]-first_node[2])//Graph.size_cell)
    first_index=(index,indey)

    for i in range(1,len(trip)):
        next_node=trip[i]
        if next_node[1] - Graph.origin[0] < 0:
            index = -1
        elif next_node[1] > Graph.data_x[-1]:
            index = (Graph.data_x[-1] - Graph.origin[0]) / Graph.size_cell
        else:
            index = int((next_node[1] - Graph.origin[0]) // Graph.size_cell)
        if Graph.origin[1] - next_node[2] < 0:
            indey = -1
        elif next_node[2] < Graph.data_y[-1]:
            indey = (Graph.origin[1] - Graph.data_y[-1]) / Graph.size_cell
        else:
            indey = int((Graph.origin[1] - next_node[2]) // Graph.size_cell)
        #print(judgein(x_range,y_range,first_node))
        next_index = (index,indey)
        #print((first_node[1],first_node[2]),(next_node[1],next_node[2]),first_index,next_index)
        #print(x_range,y_range,first_node,next_node)
        if (judgein(x_range,y_range,first_node)|judgein(x_range,y_range,next_node)|(i==len(trip)-1))==0:
            #print(judgein(x_range,y_range,first_node)|judgein(x_range,y_range,next_node)|(i==len(trip)-1))
            first_node = next_node
            first_index=next_index
            if len(grid_point)!=0:
             grid_point_all.append(sorted(grid_point,cmp_time))
             grid_point=[]
            continue
        node_x_index=np.array(range(max(next_index[0],first_index[0]),min(next_index[0],first_index[0]),-1))
        node_y_index=np.array(range(max(next_index[1],first_index[1]),min(next_index[1],first_index[1]),-1))
        #print(node_x_index,node_y_index)
        #print(node_x_index,node_y_index)

        if len(node_x_index)!=0:
          result=grid_point_single(node_x_index,True,trip[i-1],trip[i],Graph)
          #print(result[0])
          #break
          for j in result[0]:
            grid_point.append(j)
          if len(result[1])!=0:
            np.delete(node_y_index,np.where(node_y_index,result[1]))
        if len(node_y_index)!=0:
          result=grid_point_single(node_y_index,False,trip[i-1],trip[i],Graph)
          for j in result[0]:
            grid_point.append(j)
        first_node=next_node
        first_index=next_index
    if len(grid_point) != 0:
      grid_point_all.append(sorted(grid_point, cmp_time))
    #print(grid_point_all)
    return grid_point_all

def ouput(trip_node,x_num,trip_index):
    result=[]
    if len(trip_node)==0:
        return result
    first_node=trip_node[0]
    for i in range(1,len(trip_node)):
        next_node=trip_node[i]
        x_index=np.max(np.append(first_node[1],next_node[1]))
        y_index=np.min(np.append(first_node[2],next_node[2]))
        #经过的方格编号
        index=y_index*x_num+x_index
        #进方格的方向
        if len(first_node[1])==1:
            if first_node[1]<np.max(next_node[1]):
              if first_node[2][0]!=first_node[2][1]:
                in_dir=4
              elif first_node[2][0]<np.max(next_node[2]):
                 in_dir=8
              else:
                 in_dir=7
            else:
              if first_node[2][0] != first_node[2][1]:
                 in_dir=2
              elif first_node[2][0]<np.max(next_node[2]):
                  in_dir=5
              else:
                  in_dir=6
        else :
            if first_node[2]<=np.min(next_node[2]):
                in_dir=1
            else: in_dir=3
         #出方格的方向
        if len(next_node[1]) == 1:
            #print(np.max(first_node[1]),next_node[1])
            if np.max(first_node[1])<=next_node[1]:
                out_dir=2
            else:
                out_dir=4
        else :
            if np.max(first_node[2])<=next_node[2]:
                out_dir=3
            else: out_dir=1
        result.append([trip_node[i-1][0],trip_node[i][0],index,in_dir,out_dir,
                       ])
        first_node=next_node
    return result


def grid_point_formal(dirname,
               savedir,
               logfile,
               day,
               Gridgraph
               ):
    start_time = time.clock()
    print 'begin of day ' + day

    trace_data_dir = dirname + day + "/"
    savedir_tmp = savedir + day + '/'
    if os.path.exists(savedir_tmp) == False:
        os.makedirs(savedir_tmp)

    save_middle = savedir + 'mid' + '/'
    if os.path.exists(save_middle) == False:
        os.makedirs(save_middle)
    flist = os.listdir(trace_data_dir)
    num=0
    print(flist)
    for fname in flist:
      #print(fname)
      #fname='1002554.txt'
      ww = np.loadtxt(trace_data_dir + fname, delimiter=',')
      print(num,flist[num])
      num = 1 + num
      grid_informal=grid_point_informal(ww,Gridgraph)

    #除去与网格只有一个交点或者零个交点的trip
      index=''
      for grid_demo in grid_informal :

        if ((len(grid_demo)==1)|(len(grid_demo)==0)):
           continue

        ####中间输出，用以验证
        '''
        middle_put=[]
        for i in grid_demo:
             if len(i[1]) == 1:
                 x=i[1][0]*Gridgraph.size_cell+Gridgraph.origin[0]
             else:
                 x=(i[1][0]+i[1][1])*Gridgraph.size_cell*1.0/2+Gridgraph.origin[0]
             if len(i[2]) == 1:
                 y=Gridgraph.origin[1]-i[2][0]*Gridgraph.size_cell
             else:
                 y=Gridgraph.origin[1]-(i[2][0]+i[2][1])*Gridgraph.size_cell*1.0/2
             middle_put.append([x,y])

        np.savetxt(save_middle+ index+fname,middle_put , fmt='%.10f', delimiter=',')
        ####################
        '''
        grid_formal=ouput(grid_demo,len(Gridgraph.data_x)-1,int(fname[:-4]))
        #print(grid_formal)

        np.savetxt(savedir_tmp+index+fname,grid_formal,fmt='%.10f',delimiter=',')
        index+='1_'
      #break


    print  'end of day ' + day

    end_time = time.clock()
    f1 = open(logfile, 'a')
    f1.write('\nThe step is 5, day is ' + day + ', The code ran for ' + str(end_time - start_time) + ' seconds' +
             '\nIt starts at ' + time.ctime(start_time) +
             '\nIt ends at ' + time.ctime(end_time))
    f1.close()
if __name__ == "__main__":
    data_root = 'D:/'
    start_day = 20150701
    dirname = data_root + 'data_taxi_part/'
    savedir = data_root + 'bjtaxi_grid_output/'
    logfile = data_root + 'logfile.txt'
    if os.path.exists(savedir) == False:
        os.makedirs(savedir)
    #xgap=20000,ygap=19000 四环
    G = Gridgraph((437652,4428006), 100, 200, 190)

    pool = Pool(4)
    #for i in range(start_day, start_day + 31):
    pool.apply_async(grid_point_formal, (dirname, savedir, logfile, str(start_day),G))
    pool.close()
    pool.join()
    print 'end of main()'










