#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <windows.h>

#define MAX_INPUT 10

int run_command(const char *program_path) {
    STARTUPINFO si;
    PROCESS_INFORMATION pi;

    ZeroMemory(&si, sizeof(si));
    si.cb = sizeof(si);
    ZeroMemory(&pi, sizeof(pi));

    char command_line[MAX_PATH];
    snprintf(command_line, sizeof(command_line), "\"%s\"", program_path);

    if (!CreateProcess(
            program_path,
            command_line,
            NULL,
            NULL,
            FALSE,
            0,
            NULL,
            NULL,
            &si,
            &pi)) {
        fprintf(stderr, "Error: Could not execute command.\n");
        return 1;
    }

    WaitForSingleObject(pi.hProcess, INFINITE);

    CloseHandle(pi.hProcess);
    CloseHandle(pi.hThread);

    return 0;
}

int main() {
    char input[MAX_INPUT];

    printf("Secure Command Executor\n");
    printf("Choose an allowed command:\n");
    printf("1. Show current user\n");
    printf("2. Show hostname\n");
    printf("3. Show IP configuration\n");
    printf("Enter choice: ");

    if (fgets(input, sizeof(input), stdin) == NULL) {
        fprintf(stderr, "Error reading input.\n");
        return 1;
    }

    input[strcspn(input, "\n")] = '\0';

    if (strlen(input) != 1 || input[0] < '1' || input[0] > '3') {
        fprintf(stderr, "Invalid input. Only choices 1-3 are allowed.\n");
        return 1;
    }

    switch (input[0]) {
        case '1':
            return run_command("C:\\Windows\\System32\\whoami.exe");

        case '2':
            return run_command("C:\\Windows\\System32\\hostname.exe");

        case '3':
            return run_command("C:\\Windows\\System32\\ipconfig.exe");

        default:
            fprintf(stderr, "Invalid option.\n");
            return 1;
    }
}