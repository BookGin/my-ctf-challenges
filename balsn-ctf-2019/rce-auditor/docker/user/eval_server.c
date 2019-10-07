#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

/*
 * Run this command to start the server.
 * The ncat is from zmap package.
 * 
 * ncat -klv 127.0.0.1 6666 -c 'timeout 30 ./eval_server'
 */

int main(int argc, char *argv[]) 
{
  setvbuf(stdout, NULL, _IONBF, 0);
  setvbuf(stderr, NULL, _IONBF, 0);
  while (1) {
    char buffer[1024]; // It's vulnerable to buffer overflow. Let's pwn it. Just trigger exit(), right?
    int count = 0;
    read(0, buffer+count, 1);
    while (buffer[count] != '\r' && buffer[count] != '\n') 
      read(0, &buffer[++count], 1);
    buffer[count] = '\0';
    system(buffer);
  }
  return 0;
}
