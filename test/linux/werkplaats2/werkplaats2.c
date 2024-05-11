#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include "ethercat.h"

// Declare IOmap as a global variable
uint8_t IOmap[4096];  // Adjust the size according to your needs

int main(int argc, char *argv[]) {
    if (argc < 4) {
        fprintf(stderr, "Usage: %s <network_interface> <slave_index> <channel_id>\n", argv[0]);
        return 1;
    }

    int slave_index = atoi(argv[2]);
    if (slave_index < 1) {
        fprintf(stderr, "Invalid slave index: %d\n", slave_index);
        return 1;
    }

    int channel_index = atoi(argv[3]);
    if (channel_index < 1 || channel_index > 8) {
        fprintf(stderr, "Invalid channel index: %d\n", channel_index);
        return 1;
    }

    if (!ec_init(argv[1])) {
        fprintf(stderr, "Error initializing the EtherCAT master on %s\n", argv[1]);
        return 1;
    }

    printf("EtherCAT initialization on %s succeeded.\n", argv[1]);

    if (ec_config_init(FALSE) <= 0) {
        fprintf(stderr, "No slaves found or configuration failed.\n");
        ec_close();
        return 1;
    }

    printf("%d slaves found and configured.\n", ec_slavecount);

    ec_config_map(&IOmap);
    ec_configdc();

    printf("Slaves mapped and configured for DC.\n");

    ec_statecheck(0, EC_STATE_SAFE_OP, EC_TIMEOUTSTATE * 4);

    ec_slave[0].state = EC_STATE_OPERATIONAL;
    ec_writestate(0);

    while (ec_statecheck(0, EC_STATE_OPERATIONAL, EC_TIMEOUTSTATE) != EC_STATE_OPERATIONAL) {
        fprintf(stderr, "Slaves not in operational state.\n");
        sleep(1);
    }

    printf("Operational state reached for all slaves.\n");

    while (1) {
        ec_send_processdata();
        ec_receive_processdata(EC_TIMEOUTRET);

        if (slave_index > ec_slavecount) {
            fprintf(stderr, "Slave index out of range. Only %d slaves available.\n", ec_slavecount);
            break;
        }

        // Assuming EL1008 starts at position 0 in the input bytes
        uint8_t inputs = *(ec_slave[slave_index].inputs);
        
        printf("Input: %s\n", (inputs & (1 << (channel_index - 1))) ? "true" : "false");

        sleep(1);  // Wait 1 second
    }

    ec_close();
    return 0;
}
