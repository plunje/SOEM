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
        if not master.config_init() or master.slave_count == 0:
            print(f'No slaves found or configuration failed on {netif}.')
            master.close()
            return 1

        print(f'{master.slave_count} slaves found and configured.')

        master.config_map()
        master.config_dc()

        print('Slaves mapped and configured for DC.')

        master.state = pysoem.SAFEOP_STATE
        master.write_state()

        while master.state_check(pysoem.SAFEOP_STATE, 5000) != pysoem.SAFEOP_STATE:
            print('Slaves not in safe operational state.')
            time.sleep(1)

        master.state = pysoem.OP_STATE
        master.write_state()

        if master.state_check(pysoem.OP_STATE, 5000) == pysoem.OP_STATE:
            print('Operational state reached for all slaves.')
            while True:
                master.send_processdata()
                master.receive_processdata(10000)

                if slave_index > master.slave_count:
                    print(f'Slave index out of range. Only {master.slave_count} slaves available.')
                    break

                inputs = master.slaves[slave_index - 1].inputs  # -1 because Python uses 0-based indexing

                if inputs:
                    # Extract the specified bit to check the sensor state
                    input_state = bool(inputs[0] & (1 << (channel_index - 1)))
                    print(f'Input: {"true" if input_state else "false"}')

                time.sleep(1)  # Wait 1 second
        else:
            print('Failed to reach operational state.')

        master.close()
        return 0
    finally:
        master.state = pysoem.INIT_STATE
        # stuur alle slaves naar INIT state
        master.write_state()
        master.close()

if __name__ == '__main__':
    sys.exit(main())
