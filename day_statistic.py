#coding=utf-8
import time
import os
import numpy as np
import pandas as pd
from multiprocessing import Pool
#将同个网格一天中不同时刻的经过车辆路径统计在一个文件中
def grid_day_carnumber(dirname,
                       savedir,
                       logfile,
                       day
                      ):
    start_time = time.clock()
    print 'begin of day ' + day

    trace_data_dir = dirname + day + "/"
    savedir_tmp = savedir + day + '/'
    if os.path.exists(savedir_tmp) == False:
        os.makedirs(savedir_tmp)

    flist = os.listdir(trace_data_dir)
    num = 0
    all_index={}
    for fname in flist:
        # print(fname)
        print(num, fname)
        ww = np.loadtxt(trace_data_dir + fname, delimiter=',')
        num = 1 + num
        #可能出现txt只有一行情况
        if ww.ndim==1:
            ww=np.array([ww])
        ###
        for line in ww:

            name=str(int(line[2]))
            if all_index.has_key(name) == False:
                all_index[name] = np.expand_dims(line, axis=0)
            else:
                all_index[name]=np.row_stack((all_index[name],np.expand_dims(line, axis=0)))
    #txt文件名为网格编号
    for key,value in all_index.items():
        np.savetxt(savedir_tmp + key+'.txt', value, fmt='%.10f', delimiter=',')
    print  'end of day ' + day

    end_time = time.clock()
    f1 = open(logfile, 'a')
    f1.write('\nThe step is 6, day is ' + day + ', The code ran for ' + str(end_time - start_time) + ' seconds' +
             '\nIt starts at ' + time.ctime(start_time) +
             '\nIt ends at ' + time.ctime(end_time))
    f1.close()

if __name__ == "__main__":
        data_root = 'D:/'
        start_day = 20150701
        dirname = data_root + 'bjtaxi_grid_output/'
        savedir = data_root + '7grid_statistic/'
        logfile = data_root + 'logfile.txt'
        if os.path.exists(savedir) == False:
            os.makedirs(savedir)
        pool = Pool(4)
        # for i in range(start_day, start_day + 31):
        pool.apply_async(grid_day_carnumber, (dirname, savedir, logfile, str(start_day)))
        pool.close()
        pool.join()
        print 'end of main()'