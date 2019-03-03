import json
import numpy as np 
import os
import cv2
import torch

TUSIMPLE_PATH='./train_set'

def clean_values(sample,target='binary'):
    H,W=sample.shape
    if target=='binary':
        values=[0,255]
        for h in range(H):
            for w in range(W):
                if sample[h,w] not in values:
                    sample[h,w]=0
    else:
        values=[255,205,155,105,55]
        for h in range(H):
            for w in range(W):
                if sample[h,w] not in values:
                    sample[h,w]=0
    return sample

class Rescale():
    def __init__(self,output_size,method='INTER_AREA'):
        self.size=output_size
    
    def __call__(self,sample,target='binary'):
        return cv2.resize(sample,self.size,interpolation=cv2.INTER_CUBIC)
 
##标注并结构化图森数据集
class CreateTusimpleData():

    def __init__(self,tusimple,line_width,transform=Rescale((256,512))):

        self.tusimple=tusimple 
        self.line_width=line_width
        self.transform=transform
        
    def __call__(self):
        if not os.path.exists('./data/train_binary'):
            os.mkdir('./data/train_binary')
        if not os.path.exists('./data/cluster'):
            os.mkdir('./data/cluster')
        if not os.path.exists('./data/LaneImages'):
            os.mkdir('./data/LaneImages')
        jsons=[json for json in os.listdir(self.tusimple) if json.split('.')[-1]=='json']
        for j in jsons:
            data=[]
            with open(os.path.join(self.tusimple,j)) as f:
                for line in f.readlines():
                    data.append(json.loads(line))
            for entry in data:
                height=entry['h_samples']
                width=entry['lanes']
                for index,w in enumerate(width):
                    counter=list(set(w))
                    if counter[0]==-2 and len(counter)==1:
                        del width[index]
                clip=entry['raw_file']
                img=cv2.imread(os.path.join(self.tusimple,clip))
                cv2.imwrite(os.path.join('./data/LaneImages','_'.join(clip.split('/')[1:])),img)
                img=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
                img_binary=np.zeros_like(img)
                img_cluster=np.zeros_like(img)
                for lane in range(len(width)):
                    queue=[]
                    for h,w in zip(height,width[lane]):
                        if w<0:
                            continue
                        else:
                            queue.insert(0,(w,h))
                            if len(queue)==2:
                                cv2.line(img_binary,queue[0],queue[1],255,self.line_width)
                                cv2.line(img_cluster,queue[0],queue[1],255-50*lane,self.line_width)
                            if len(queue)>1:
                                queue.pop()
                new_name='_'.join(clip.split('/')[1:])
                new_name='.'.join([new_name.split('.')[0],'png'])

                img_binary=self.transform(img_binary)
                img_binary=clean_values(img_binary)
                img_cluster=self.transform(img_cluster)
                img_cluster=clean_values(img_cluster)
  
                cv2.imwrite(os.path.join('./data/train_binary',new_name),img_binary)
                cv2.imwrite(os.path.join('./data/cluster',new_name),img_cluster)
      
if __name__=='__main__':

    creator=CreateTusimpleData(TUSIMPLE_PATH,10)
    creator()


    






    
