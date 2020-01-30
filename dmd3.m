clc;
clear all;
close all;
tic
load('Salinas.mat');
load('Salinas_gt.mat');
S=input('enter the reduction factor');
Salinas=salinas;
%figure
% imagesc(Salinas(:,:,25));
% colormap('gray');
G= salinas_gt;
[row col plane]=size(salinas);
D = salinas;
G1 = G(:);
G1=G1';
D3 = [];
[m n b] = size(D);

for i = 1:b
D1 =D(:,:,i);
D3 = [D3,D1(:)];
end  


[SALINA,b_selc1]=dim_red2(D3,b,S);
D3 = SALINA';
 normd=D3;
 normd5_m=[];
 vn_n=[];
 
  for i=1:b/S
      v1=normd(i,:);%each row taken here seperately
     vx=v1*2/(max(v1)-min(v1));
     %vn=vx-(min(vx)+1);% to get in [-1 1] range
     vn_n=[vx;vn_n];
  end
  
D3= vn_n;

k = [];
D4 = [];
P = [];

for i = 2:3
    p = find(G1 == i);
    
    P = [P p];
    [m1 n1] = size(p);
    k = [k [m1*n1]];
    D4 = [D4 D3(:,p(1:end))];
%     p = [q p];
end
 for i = 10:11
    p = find(G1 == i);
    
    P = [P p];
    [m1 n1] = size(p);
    k = [k [m1*n1]];
    D4 = [D4 D3(:,p(1:end))];
%     p = [q p];
 end
for i = 13:14
    p = find(G1 == i);
    
    P = [P p];
    [m1 n1] = size(p);
    k = [k [m1*n1]];
    D4 = [D4 D3(:,p(1:end))];
end
 K = sum(sum(k));
 Cu = cumsum(k);
class1 = D4(:,1:(Cu(1)));
 classes = [];
class2 = D4(:,(Cu(1)+1):Cu(2));
class3 = D4(:,(Cu(2)+1):Cu(3));
class4 = D4(:,(Cu(3)+1):Cu(4));
class5 = D4(:,(Cu(4)+1):Cu(5));
class6 = D4(:,(Cu(5)+1):Cu(6));
% % class7 = D4(:,(Cu(6)+1):Cu(7));
% % class8 = D4(:,(Cu(7)+1):Cu(8));
% % class9 = D4(:,(Cu(8)+1):Cu(9));
%  class2 = D4(:,(Cu(9)+1):Cu(10));
% class3 = D4(:,(Cu(10)+1):Cu(11));
% class4 = D4(:,(Cu(11)+1):Cu(12));
% class5 = D4(:,(Cu(12)+1):Cu(13));
% %class6 = D4(:,(Cu(13)+1):Cu(14));
% 
 classes = [class1 class2 class3 class4 class5 class6 ];
% 
% %creating the testing and training matrix
%r1=randperm(2009,1607);
r1=randperm(3726,2981);
r2=randperm(1976,1581);
r3=randperm(3278,2622);
r6=randperm(1070,749);
r4=randperm(1068,854);
 r5=randperm(916,641);
%r6=randperm(1927,1542);

% r1=randperm(2009,1406);
% r2=randperm(3278,2295);
% r3=randperm(1068,748);
% r4=randperm(1927,1349);
% r5=randperm(916,641);
% r6=randperm(1070,749);
%r6=randperm(799,639);
% 
train=[];
test=[];
% 
% 
for r=1:6
    if r == 1
        train1 = class1(:,r1);
        test1 = class1;
        test1(:,r1(1:end))=[];
    end
    
    if r == 2
        train2 = class2(:,r2);
        test2 = class2;
        test2(:,r2(1:end))=[];
    end
    
    if r == 3
        train3 = class3(:,r3);
        test3 = class3;
        test3(:,r3(1:end))=[];
    end
    
    if r == 4
        train4 = class4(:,r4);
        test4 = class4;
        test4(:,r4(1:end))=[];
    end
    
    if r == 5
        train5 = class5(:,r5);
        test5 = class5;
        test5(:,r5(1:end))=[];
    end
    if r == 6
        train6 = class6(:,r6);
        test6 = class6;
        test6(:,r6(1:end))=[];
    end
    
end
k1= [];
% 
P = [];
D5=[];
for i =1
    p1 = find(G1 ==i);
    
    P = [P p];
    [m1 n1] = size(p1);
    k1 = [ k1 m1*n1];
    D5 = [D5 D3(:,p1(1:end))];
%     p = [q p];
end
for i =12
    p1 = find(G1 ==i);
    
    P = [P p];
    [m1 n1] = size(p1);
    k1 = [ k1 m1*n1];
    D5 = [D5 D3(:,p1(1:end))];
%     p = [q p];
end
 test7=D5;
% 
 train=[train1 train2 train3 train4 train5 train6];
train=train';
test=[test1 test2 test3 test4 test5 test6 test7];
test=test';
% 
% %creating the train_label and test_label
% % train_label=[ones(313,1) zeros(313,5); zeros(1074,1) ones(1074,1) zeros(1074,4); zeros(493,2) ones(493,1) zeros(493,3); zeros(1220,3) ones(1220,1) zeros(1220,2); zeros(539,4) ones(539,1) zeros(539,1); zeros(639,5) ones(639,1)];
% % 
% % test_label= [ones(78,1) zeros(78,5); zeros(269,1) ones(269,1) zeros(269,4); zeros(123,2) ones(123,1) zeros(123,3); zeros(305,3) ones(305,1) zeros(305,2); zeros(135,4) ones(135,1) zeros(135,1); zeros(160,5) ones(160,1)];
train_label=[(zeros(2981,1) );ones(1581,1); (ones(2622,1).*2);(ones(854,1).*3) ;( ones(641,1).*4); ( ones(749,1).*5)];
% 
test_label= [(zeros(745,1) );ones(395,1); (ones(656,1).*2);(ones(214,1).*3) ;( ones(275,1).*4) ;(ones(321,1).*5) ;(ones(3936,1).*6)];
% % % save('trainanother90.mat','train');
% % save('trainanother_label90.mat','train_label');
% % save('testanother90.mat','test');
% % save('testanother_label90.mat','test_label');
% % % 
% % 
tr=[train train_label];
ts=[test test_label];

% toc
% p(512,217)=0;
% f=1;
% 
% for i=1:512
%    for j=1:217
%        if G(i,j)==0
%            p(i,j)=0;
%        else
%        p(i,j)=classes(f);
%        f=f+1;
%        end
%     end
% end
% figure;
% imagesc(test);
% colormap(blue,gray,red);axis off;
%trainshuf2_20='train.mat'
% testshuf2_20='test.mat'
% save(trainshuf2_20);
% save(testshuf2_20);
% flnmt=strcat('salinasc',num2str(tr),'orgfileTm.mat');
csvwrite('shuf3trainsalinas50.csv',tr)
 csvwrite('shuf3testsalinas50.csv',ts)