#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main() {
    char command[256];

    printf("Enter a system command to execute: ");
    fgets(command, sizeof(command), stdin);

    command[strcspn(command, "\n")] = '\0';

    system(command);

    return 0;
}