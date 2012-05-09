## @package pyrtai
# Various useful functions

## Parses an integer state value which, converted into binary value, represents 4 states.
# The 4 states are (array indexes):
# 0 - Target running
# 1 - Target connected
# 2 - Target exists
# 3 - Error occurred
#
# @param int_state The integer value of the state
# @return An hash containing explained states
def getStateFromResponse(int_state):
    ret = {}
    # Transforms '0b0101' into '0101' or '0b10' into '0010'
    state = bin(int(int_state)).lstrip('0b')[-4:].rjust(4, '0')

    ret['target_running'] = (state[0] == '1')
    ret['target_connected'] = (state[1] == '1')
    ret['target_exists'] = (state[2] == '1')
    ret['error'] = (state[3] == '1')
    
    return ret

## Implements readline() with sockets.
# This method returns data with yield, so it can be called within a cycle
# @param socket The data socket
# @return The read string
def linesplit(socket):
    data_buffer = socket.read(4096)
    done = False
    while not done:
        if "\n" in data_buffer:
            (line, data_buffer) = data_buffer.split("\n", 1)
            yield line+"\n"
        else:
            more = socket.read(4096)
            if not more:
                done = True
            else:
                data_buffer = data_buffer + more
    if data_buffer:
        yield data_buffer