#include <assert.h>

void bar(int x) {
	assert(x!=3 && "x cannot be 3");
}
