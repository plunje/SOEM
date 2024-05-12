import sys
import time
import pysoem

def main():
    if len(sys.argv) < 4:
        print(f'Usage: {sys.argv[0]} <network_interface> <slave_index> <channel_id>')
        return 1

    netif = sys.argv[1]
    slave_index = int(sys.argv[2])
    channel_index = int(sys.argv[3])

    if slave_index < 1:
        print(f'Invalid slave index: {slave_index}')
        return 1

    if channel_index < 1 or channel_index > 8:
        print(f'Invalid channel index: {channel_index}')
        return 1

    master = pysoem.Master()
    master.open(netif)

    try:
        if not master.config_init() or len(master.slaves) == 0:
            print(f'No slaves found or configuration failed on {netif}.')
            master.close()
            return 1

        print(f'{len(master.slaves)} slaves found and configured.')

        master.config_map()
        master.config_dc()

        print('Slaves mapped and configured for DC.')


        master.state = pysoem.OP_STATE
        master.write_state()
        
        while master.state_check(pysoem.OP_STATE, 50000) != pysoem.OP_STATE:
            print('Slaves not in operational state.')
            time.sleep(1)
            
        print('Slaves in operational state.')

        if master.state_check(pysoem.OP_STATE, 50000) == pysoem.OP_STATE:
            print('Operational state reached for all slaves.')
            while True:
                master.send_processdata()
                master.receive_processdata(10000)

                if slave_index > len(master.slaves):
                    print(f'Slave index out of range. Only {len(master.slaves)} slaves available.')
                    break

                slave = master.slaves[slave_index - 1]
                if slave.input:
                    # Extract the specified bit to check the sensor state
                    input_state = bool(slave.input[0] & (1 << (channel_index - 1)))
                    print(f'Input: {"true" if input_state else "false"}')

                time.sleep(1)  # Wait 1 second
        else:
            print(f'Failed to reach operational state. {master.state_check(pysoem.OP_STATE, 50000)}')

        master.close()
        return 0
    finally:
        master.state = pysoem.INIT_STATE
        # stuur alle slaves naar INIT state
        master.write_state()
        master.close()

if __name__ == '__main__':
    sys.exit(main())
