import sys
import time
import pysoem

def main():
    if len(sys.argv) < 3:
        print('Gebruik: {} <netwerkinterface> <slaveindex>'.format(sys.argv[0]))
        return

    netif = sys.argv[1]
    slave_index = int(sys.argv[2])

    master = pysoem.Master()
    master.open(netif)

    try:
        if not master.config_init() or master.slave_count == 0:
            print('Geen slaves gevonden of fout bij het configureren van slaves.')
            return

        master.config_map()

        if not master.config_dc():
            print('Fout bij het configureren van Distributed Clocks.')
            return

        master.state_check(pysoem.SAFEOP_STATE, 50000)

        if master.state == pysoem.SAFEOP_STATE:
            master.state = pysoem.OP_STATE
            master.write_state()

            master.state_check(pysoem.OP_STATE, 50000)
            if master.state == pysoem.OP_STATE:
                print('Slaves geconfigureerd en in operationele staat.')
                while True:
                    master.send_processdata()
                    master.receive_processdata(10000)
                    if len(master.slaves[slave_index].inputs) > 0:
                        data = int.from_bytes(master.slaves[slave_index].inputs, byteorder='little')
                        print(f'Data van slave {slave_index}: {data}')
                    time.sleep(1)
            else:
                print('Slaves niet in operationele staat.')
        else:
            print('Slaves niet in veilige operationele staat.')
    finally:
        master.state = pysoem.INIT_STATE
        # stuur alle slaves naar INIT state
        master.write_state()
        master.close()

if __name__ == '__main__':
    main()
