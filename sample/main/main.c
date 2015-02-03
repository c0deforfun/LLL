#include <stdio.h>
extern int foo(int x, int y);

/*
* blablabla
*
*
*
*
*
*
*ddff
888*/

int main(int argc, char** argv) {
    int i;
    int list[] = {1,2,3,4,5};
    const char* str = "Hello";
    struct Car {
       unsigned int year;
       unsigned int mileage;
       struct Engine {
          int MPG;
          float displacement;
} engine;
} car;
    car.year = 2014;
    car.mileage = 888;
    car.engine.MPG = 30;
    car.engine.displacement = 3.3;

    printf("car: year:%d, disp.:%2.1f\n", car.year, car.engine.displacement);

    for(i=0;i<argc;++i)
        printf("arg[%i]=%s\n", i, argv[i]);

	sleep(argc);
	i = foo(argc,2);
	printf("hello :%d\n", i);
	return 0;
}

