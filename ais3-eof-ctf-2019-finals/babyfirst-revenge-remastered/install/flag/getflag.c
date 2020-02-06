// x86_64-w64-mingw32-gcc getflag.c -Wall -Wextra -o getflag
#include <stdio.h>
#include <string.h>
int main(int argc, char *argv[]) 
{ 
  if (argc == 9 
     && 0 == strcmp(argv[1], "I")
     && 0 == strcmp(argv[2], "rea11y")
     && 0 == strcmp(argv[3], "wan7")
     && 0 == strcmp(argv[4], "t0")
     && 0 == strcmp(argv[5], "get")
     && 0 == strcmp(argv[6], "7h3")
     && 0 == strcmp(argv[7], "f1ag")
     && 0 == strcmp(argv[8], "plz!")
  ) {
    puts("EOF{Wind0ws_<3_LinuX,right?}");
    return 0;
  }
  printf("Usage: %s ... ...\n", argv[0]);
  puts("Please see the challenge description to see how to get the flag");
  return 0;
}

