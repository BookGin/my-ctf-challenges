#include <stdio.h>
#include <stdlib.h>

int main() 
{ 
  FILE *f = fopen("/flag", "r");
  char buf[256] = {0};
  fgets(buf, 256, f);
  puts(buf);
  fclose(f);
  return 0;
}
