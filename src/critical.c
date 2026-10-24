#include <stdio.h>
#include <omp.h>
int main(){
 long counter=0;
 #pragma omp parallel for
 for(long i=0;i<10000000;i++){
 #pragma omp critical
 {counter++;}
 }
 printf("Counter=%ld\n",counter);
}