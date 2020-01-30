import shutil

import numpy as np
from sklearn.metrics import accuracy_score

import torch
from keras import callbacks
from keras.callbacks import CSVLogger
import models



def save_checkpoint(state, is_best, filename='checkpoint.pth.tar'):
    torch.save(state, filename)
    #checkpointer=callbacks.ModelCheckpoint("E:\miniproject\miniproject\nirmals\checkpointssss-{epoch:02d}.hdf5",verbose=1,save_best_only=True,monitor='loss')
    
    #model.save('F:/AMTECH_CEN/SEMESTER 2/Machine_Learning_for_signal_processing/Signal_arrthymia_myocardial/results_arrhythmia_functional/model_arrythmia.hdf5')
    #csvlogger=CSVLogger('E:\miniproject\miniproject\nirmals\csvnormal.csv',separator=",",append=False)
    #models.fit(callbacks=[checkpointer,csvlogger])
    
    
    if is_best:
        shutil.copyfile(filename, 'model_best.pth.tar')

def cal_acc(gt_list, predict_list, num):
    acc_sum = 0
    for n in range(num):
        y = []
        pred_y = []
        for i in range(len(gt_list)):
            gt = gt_list[i]
            predict = predict_list[i]
            if gt == n:
                y.append(gt)
                pred_y.append(predict)
        print ('{}: {:4f}'.format(n if n != (num - 1) else 'Unk', accuracy_score(y, pred_y)))
        if n == (num - 1):
            print ('Known Avg Acc: {:4f}'.format(acc_sum / (num - 1)))
        acc_sum += accuracy_score(y, pred_y)
    print ('Avg Acc: {:4f}'.format(acc_sum / num))
    print ('Overall Acc : {:4f}'.format(accuracy_score(gt_list, predict_list)))

def cosine_rampdown(current, rampdown_length):
    """Cosine rampdown from https://arxiv.org/abs/1608.03983"""
    assert 0 <= current <= rampdown_length
    return float(.5 * (np.cos(np.pi * current / rampdown_length) + 1))