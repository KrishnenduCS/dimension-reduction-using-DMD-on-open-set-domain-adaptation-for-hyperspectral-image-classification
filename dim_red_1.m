%function [ O2,b_selc1 ] = dmd(w,plane)
w= randi(5,6,6,5);
plane  = size(w,3);
w = reshape(w,size(w,1)*size(w,2),size(w,3));
F=[w w(:,end)]%last column replicated
[z,v1]=size(F)
 X1=F(:,1:end-1);
 [imy,loi]=size(X1)
  X2=F(:,2:end);
 [OIY,LOP]=size(X2)
 [U, sig, V] = svd(X1, 'econ');
% 
 Stild = U' * X2 * V * pinv(sig);
 [eig_vec eig_val]= eig(Stild);
[Q1 R1 P1]=qr(eig_vec);
[pre,yut]=size(P1)
O2=F(:,1:end-1)*P1;
O2= O2(:,1:(end/2));
[yui,ploi]=size(O2)
%dimension reduction(taking 50%bands)
band_selc1= find(P1==1);
b_selc1=rem(band_selc1,plane);
%b_selc1=b_selc1(1:110);
%division


