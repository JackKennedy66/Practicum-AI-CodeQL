#include <stdio.h>
#include <stdlib.h>

int main() {
    char filename[256];
    FILE *file;
    char ch;

    printf("Enter filename: ");
    scanf("%255s", filename);

    file = fopen(filename, "r");

    if (file == NULL) {
        printf("Error: Could not open file.\n");
        return 1;
    }

    printf("\n--- File Contents ---\n");

    while ((ch = fgetc(file)) != EOF) {
        putchar(ch);
    }

    fclose(file);

    return 0;
}