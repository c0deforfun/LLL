extern void bar(int);
int foo(int x, int y) {
  bar(x);
  return x*y;
}

