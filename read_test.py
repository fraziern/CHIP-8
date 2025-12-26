# import array


filename = 'IBM Logo.ch8'

def pretty_print(data:bytearray):
    import textwrap
    data_string = data.hex(' ')
    wrapped_list = textwrap.wrap(data_string, 80)
    for line in wrapped_list:
        print(line)

with open(filename,'rb') as file:
    full_rom = file.read()

memory = bytearray(4096)

memory[0x200:0x200 + len(full_rom)] = full_rom

pretty_print(memory)