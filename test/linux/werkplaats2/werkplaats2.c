#include <stdio.h>
#include <unistd.h> // voor sleep()
#include <string.h> // voor memcpy()
#include <stdlib.h> // voor atoi()
#include "ethercat.h"

int main(int argc, char *argv[]) {
    if (argc < 3) {
        fprintf(stderr, "Gebruik: %s <netwerkinterface> <slaveindex>\n", argv[0]);
        return 1;
    }

    char* netif = argv[1];
    int slaveIndex = atoi(argv[2]); // converteer string naar integer

    // Initialiseren van SOEM, starten van de EtherCAT master
    if (!ec_init(netif)) {
        fprintf(stderr, "Fout bij het initialiseren van de EtherCAT master op %s\n", netif);
        return 1;
    }

    printf("EtherCAT initialisatie op %s succesvol.\n", netif);

    // Zoeken en configureren van alle slaves
    if (ec_config_init(FALSE) <= 0) {
        fprintf(stderr, "Geen slaves gevonden of fout bij het configureren van slaves.\n");
        ec_close();
        return 1;
    }

    // Wachten totdat alle slaves in OPERATIONAL staat zijn
    ec_statecheck(0, EC_STATE_OPERATIONAL, EC_TIMEOUTSTATE);

    printf("Slaves geconfigureerd en in operationele staat.\n");
    
    // Leesproces starten
    while (1) {
        ec_send_processdata();
        ec_receive_processdata(EC_TIMEOUTRET);

        // Aanname: de slave data is een eenvoudige integer
        int data;
        memcpy(&data, ec_slave[slaveIndex].inputs, sizeof(int));

        printf("Data van slave %d: %d\n", slaveIndex, data);

        sleep(1);  // Wacht 1 seconde
    }

    // EtherCAT communicatie stoppen
    ec_close();
    return 0;
}
