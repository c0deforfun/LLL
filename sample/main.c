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
*
*
*
*
*
*
*
*
*
*
*
*
*
*
*
*
*
*
*
*
*
*
*
*
*
*
*/
int main(int argc, char** argv) {
    int i;
    for(i=0;i<argc;++i)
        printf("arg[%i]=%s\n", i, argv[i]);

	sleep(argc);
	i = foo(argc,2);
	printf("hello :%d\n", i);
	return 0;
}

