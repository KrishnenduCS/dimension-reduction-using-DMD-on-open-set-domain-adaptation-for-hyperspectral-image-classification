from __future__ import print_function
import argparse
import numpy as np

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optimizer

from get_dataset import *
import models
import utils

from sklearn.metrics import confusion_matrix, roc_curve,auc
from sklearn.metrics import classification_report
import matplotlib.pyplot as plt
import numpy as np
import itertools

import pandas as pd
from sklearn import datasets
from sklearn.metrics import roc_curve,auc
from scipy import interp
from itertools import cycle
import time


NUM_CLASSES = 7

# Training settings
parser = argparse.ArgumentParser(description='Openset-DA SVHN -> MNIST Example')
parser.add_argument('--task', choices=['s2sa'], default='s2sa',
                    help='type of task')
parser.add_argument('--batch-size', type=int, default=128, metavar='N',
                    help='input batch size for training (default: 128)')
parser.add_argument('--epochs', type=int, default=500, metavar='N',
                    help='number of epochs to train (default: 200)')
parser.add_argument('--lr', type=float, default=0.0000001, metavar='LR',
                    help='learning rate (default: 0.001)')
parser.add_argument('--lr-rampdown-epochs', default=501, type=int, metavar='EPOCHS',
                        help='length of learning rate cosine rampdown (>= length of training)')
parser.add_argument('--momentum', default=0.9, type=float, metavar='M',
                    help='momentum')
parser.add_argument('--grl-rampup-epochs', default=20, type=int, metavar='EPOCHS',
                        help='length of grl rampup')
parser.add_argument('--weight-decay', '--wd', default=1e-3, type=float,
                    metavar='W', help='weight decay (default: 1e-3)')
parser.add_argument('--th', type=float, default=0.5, metavar='TH',
                    help='threshold (default: 0.5)')
parser.add_argument('--log-interval', type=int, default=100, metavar='N',
                    help='how many batches to wait before logging training status')
parser.add_argument('--resume', default='', type=str, metavar='PATH',
                    help='path to latest checkpoint (default: none)')
args = parser.parse_args()

# C:/Users/Nirmal/Desktop/PYNB/project/GAN/checkpoint.pth.tar

torch.backends.cudnn.benchmark = True

source_dataset, target_dataset = get_dataset(args.task)

source_loader = torch.utils.data.DataLoader(source_dataset, 
    batch_size=args.batch_size, shuffle=True, num_workers=0)

target_loader = torch.utils.data.DataLoader(target_dataset,
    batch_size=args.batch_size, shuffle=True, num_workers=0)

model = models.Net(task=args.task).cuda()
repr(model)
# if args.task=='s2sa':
    # optimizer = torch.optim.SGD(model.parameters(), args.lr,
                                    # momentum=args.momentum,
                                    # weight_decay=args.weight_decay,
                                    # nesterov=True)
if args.task=='s2sa':
    optimizer = torch.optim.Adam(model.parameters(), args.lr,
                                    weight_decay=args.weight_decay)
                                
if args.resume:
    print("=> loading checkpoint '{}'".format(args.resume))
    checkpoint = torch.load(args.resume)
    args.start_epoch = checkpoint['epoch']
    best_prec1 = checkpoint['best_prec1']
    model.load_state_dict(checkpoint['state_dict'])
    optimizer.load_state_dict(checkpoint['optimizer'])
    print("=> loaded checkpoint '{}' (epoch {})"
            .format(args.resume, checkpoint['epoch']))

criterion_bce = nn.BCELoss()
criterion_cel = nn.CrossEntropyLoss()

best_prec1 = 0
best_pred_y = []
best_gt_y = []
global_step = 0
total_steps = args.grl_rampup_epochs * len(source_loader)
acc11=[]
epoch11=[]
def train(epoch):
    model.train()
    global global_step
    for batch_idx, (batch_s, batch_t) in enumerate(zip(source_loader, target_loader)):
        adjust_learning_rate(optimizer, epoch, batch_idx, len(source_loader)) if args.task=='s2m' else None
        p = global_step / total_steps
        constant = 2. / (1. + np.exp(-10 * p)) - 1

        data_s, target_s = batch_s
        data_t, target_t = batch_t

        data_s, target_s = data_s.cuda(), target_s.cuda(non_blocking=True)
        data_t, target_t = data_t.cuda(), target_t.cuda(non_blocking=True)

        batch_size_s = len(target_s)
        batch_size_t = len(target_t)

        optimizer.zero_grad()

        data_s = data_s.unsqueeze(1)
        data_t = data_t.unsqueeze(1)

        output_s = model(data_s)
        output_t = model(data_t, constant = constant, adaption = True)

        target_s = target_s.long()
        loss_cel = criterion_cel(output_s, target_s)

        output_t_prob_unk = F.softmax(output_t, dim=1)[:,-1]
        loss_adv = criterion_bce(output_t_prob_unk, torch.tensor([args.th]*batch_size_t).cuda())

        loss =  loss_cel + loss_adv
        
        loss.backward()
        optimizer.step()

        global_step += 1

        if batch_idx % args.log_interval == 0:
            print('Train Epoch: {} [{}/{} ({:.0f}%)]\tLoss: {:.6f}\tConstant: {:.4f}'.format(
                epoch, batch_idx * args.batch_size, len(source_loader.dataset),
                100. * batch_idx / len(source_loader), loss.item(), constant))

def test(epoch):
    global acc11
    global epoch11
    global best_prec1
    model.eval()
    loss = 0
    pred_y = []
    true_y = []

    correct = 0
    ema_correct = 0
    with torch.no_grad():
        for batch_idx, (data, target) in enumerate(target_loader):
            data, target = data.cuda(), target.cuda(non_blocking=True)
            data = data.unsqueeze(1)
            output = model(data)

            target = target.long()
            loss += criterion_cel(output, target).item() # sum up batch loss

            pred = output.max(1, keepdim=True)[1] # get the index of the max log-probability

            for i in range(len(pred)):
                pred_y.append(pred[i].item())
                true_y.append(target[i].item())

            correct += pred.eq(target.view_as(pred)).sum().item()

    loss /= len(target_loader.dataset)

    utils.cal_acc(true_y, pred_y, NUM_CLASSES)

    print('\nTest set: Average loss: {:.4f}, Accuracy: {}/{} ({:.0f}%)\n'.format(
        loss, correct, len(target_loader.dataset),
        100. * correct / len(target_loader.dataset)))

    prec1 = 100. * correct / len(target_loader.dataset)
    if epoch % 1 == 0:
        acc11.append(prec1)
        epoch11.append(epoch)
        #print(acc11)
        #print(epoch11)
        acc=np.round_(acc11)
        np.savetxt('csvfile.csv', acc)
        is_best = prec1 > best_prec1
        best_prec1 = max(prec1, best_prec1)
        utils.save_checkpoint({
            'epoch': epoch,
            'state_dict': model.state_dict(),
            'best_prec1': best_prec1,
            'optimizer' : optimizer.state_dict(),
        }, is_best)
        if is_best:
            global best_gt_y
            global best_pred_y
            best_gt_y = true_y
            best_pred_y = pred_y

def adjust_learning_rate(optimizer, epoch, step_in_epoch, total_steps_in_epoch):
    lr = args.lr
    epoch = epoch + step_in_epoch / total_steps_in_epoch

    lr *= utils.cosine_rampdown(epoch, args.lr_rampdown_epochs)

    for param_group in optimizer.param_groups:
        param_group['lr'] = lr

start = time.time()
try:
    for epoch in range(1, args.epochs + 1):
        train(epoch)
        test(epoch)
    print ("------Best Result-------")
    utils.cal_acc(best_gt_y, best_pred_y, NUM_CLASSES)
except KeyboardInterrupt:
    print ("------Best Result-------")
    utils.cal_acc(best_gt_y, best_pred_y, NUM_CLASSES)
    
stop = time.time()
print('time taken = ' + str(stop - start) + 'secs')


# ########################################################################################################################


def plot_confusion_matrix(cm,
                          target_names,
                          title='Confusion matrix',
                          cmap=None,
                          normalize= False):
    """
    given a sklearn confusion matrix (cm), make a nice plot

    Arguments
    ---------
    cm:           confusion matrix from sklearn.metrics.confusion_matrix

    target_names: given classification classes such as [0, 1, 2]
                  the class names, for example: ['high', 'medium', 'low']

    title:        the text to display at the top of the matrix

    cmap:         the gradient of the values displayed from matplotlib.pyplot.cm
                  see http://matplotlib.org/examples/color/colormaps_reference.html
                  plt.get_cmap('jet') or plt.cm.Blues

    normalize:    If False, plot the raw numbers
                  If True, plot the proportions

    Usage
    -----
    plot_confusion_matrix(cm           = cm,                  # confusion matrix created by
                                                              # sklearn.metrics.confusion_matrix
                          normalize    = True,                # show proportions
                          target_names = y_labels_vals,       # list of names of the classes
                          title        = best_estimator_name) # title of graph

    Citiation
    ---------
    http://scikit-learn.org/stable/auto_examples/model_selection/plot_confusion_matrix.html

    """


    accuracy = np.trace(cm) / float(np.sum(cm))
    misclass = 1 - accuracy

    if cmap is None:
        cmap = plt.get_cmap('Blues')

    plt.figure(figsize=(9, 7))
    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()

    if target_names is not None:
        tick_marks = np.arange(len(target_names))
        plt.xticks(tick_marks, target_names, rotation=45)
        plt.yticks(tick_marks, target_names)

    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]


    thresh = cm.max() / 1.5 if normalize else cm.max() / 2
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        if normalize:
            plt.text(j, i, "{:0.4f}".format(cm[i, j]),
                     horizontalalignment="center",
                     color="white" if cm[i, j] > thresh else "black")
        else:
            plt.text(j, i, "{:,}".format(cm[i, j]),
                     horizontalalignment="center",
                     color="white" if cm[i, j] > thresh else "black")


    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label\naccuracy={:0.4f}; misclass={:0.4f}'.format(accuracy, misclass))
    plt.show()
    plt.savefig('Confusion Matrix', dpi=200, format='png', bbox_inches='tight')
    plt.close()

# Compute confusion matrix
cm = confusion_matrix(best_gt_y, best_pred_y)

print(cm)

# Show confusion matrix in a separate window
plt.matshow(cm)

plot_confusion_matrix(cm,
                          target_names= ['a', 'b', 'c', 'd', 'e', 'u'],
                          title='Confusion matrix',
                          cmap=None, normalize= False)

#print(classification_report(best_gt_y, best_pred_y, labels=['0', '1', '2', '3', '4', '5'], target_names=['a', 'b', 'c', 'd', 'e', 'u']))
#a=classification_report(best_gt_y, best_pred_y, labels=['0', '1', '2', '3', '4', '5'], target_names=['a', 'b', 'c', 'd', 'e', 'u'])
plt.show()
#plt.savefig('Classification Report.png', dpi=200, format='png', bbox_inches='tight')
plt.close()

#############################################################################################################################

# Compute ROC curve and ROC area for each class
### MACRO
fpr = dict()
tpr = dict()
roc_auc = dict()

for i in range(NUM_CLASSES):
    fpr[i], tpr[i], _ = roc_curve(np.array(pd.get_dummies(best_gt_y))[:, i], np.array(pd.get_dummies(best_pred_y))[:, i])
    roc_auc[i] = auc(fpr[i], tpr[i])


all_fpr = np.unique(np.concatenate([fpr[i] for i in range(NUM_CLASSES)]))

mean_tpr = np.zeros_like(all_fpr)
for i in range(NUM_CLASSES):
    mean_tpr += interp(all_fpr, fpr[i], tpr[i])

mean_tpr /= NUM_CLASSES

fpr["macro"] = all_fpr
tpr["macro"] = mean_tpr
roc_auc["macro"] = auc(fpr["macro"], tpr["macro"])

lw=2
plt.figure(figsize=(8,5))
plt.plot(fpr["macro"], tpr["macro"],
         label='macro-average ROC curve (area = {0:0.2f})'
               ''.format(roc_auc["macro"]),
         color='green', linestyle=':', linewidth=4)

colors = cycle(['red', 'olive', 'orange', 'black', 'yellow', 'green'])
for i, color in zip(range(NUM_CLASSES), colors):
    plt.plot(fpr[i], tpr[i], color=color, lw=lw,
             label='ROC curve of class {0} (area = {1:0.2f})'
             ''.format(i, roc_auc[i]))

plt.plot([0, 1], [0, 1], 'k--',color='red', lw=lw)
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.annotate('Random Guess',(.5,.48),color='red')
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Hyperspectral Image Dataset')
plt.legend(loc="lower right")
plt.show()
plt.savefig('ROC')
plt.close()
