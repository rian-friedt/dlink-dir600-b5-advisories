#include "llmnresp.h"

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

int o_verbose = 0;
int msockfd4 = -1;
int msockfd6 = -1;
int signal_pipe[2] = {-1, -1};
char *o_ifinet6 = "/dev/null";
char *o_interface = "offline";
char *o_name = "offline";
char *o_dot = ".";
int max_udp_pdu_size = MAX_V4UDP_PDU_SIZE;

void verbose(const char *format, ...) {
    (void)format;
}

uint32_t sioc_getifaddr(const char *ifname) {
    (void)ifname;
    return 0;
}

int llmnresp_send(
    int fd,
    struct sockaddr *addr,
    socklen_t *addrlen,
    struct llmnr_header_t *header,
    int offset,
    int record_length
) {
    (void)fd;
    (void)addr;
    (void)addrlen;
    (void)header;
    (void)offset;
    (void)record_length;
    return -1;
}

/* Expose the vendor-static parser helper without changing its function body. */
#define static
#include "rec_op.c"
#undef static

int main(int argc, char **argv) {
    FILE *input;
    long length;
    unsigned char *buffer;

    if (argc != 2) {
        fprintf(stderr, "usage: %s INPUT\n", argv[0]);
        return 2;
    }
    input = fopen(argv[1], "rb");
    if (input == NULL || fseek(input, 0, SEEK_END) != 0) {
        perror("open input");
        return 2;
    }
    length = ftell(input);
    if (length < 13 || length > MAX_V4UDP_PDU_SIZE || fseek(input, 0, SEEK_SET) != 0) {
        fprintf(stderr, "input length is outside the bounded LLMNR fixture range\n");
        fclose(input);
        return 2;
    }
    buffer = malloc((size_t)length);
    if (buffer == NULL || fread(buffer, 1, (size_t)length, input) != (size_t)length) {
        fprintf(stderr, "failed to read input\n");
        free(buffer);
        fclose(input);
        return 2;
    }
    fclose(input);

    (void)get_name_size(buffer + 12);
    free(buffer);
    return 0;
}
