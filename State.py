class State():

    ROMSTART = 0x200

    def __init__(self, pc=ROMSTART):
        self.index = 0
        self.registers = bytearray(16)
        self.pc = pc
        self.delay_timer = 0
        self.sound_timer = 0
        self.stack = []
        self.key_state = [False]*16
        self.ram = bytearray(4096)

    def __str__(self):
        string = ""
        string += f'Index: {self.index:X}\n'
        string += f'Registers: {self.registers.hex(" ")}'
        return string

    def set_vx(self, vx, value):
        if vx > 15:
            raise ValueError(f"Attempting to set non-existent register: {vx:X}")
        if type(value) == bytes or type(value) == bytearray:
            value = int.from_bytes(value)
        self.registers[vx] = value % 256
    
    def get_vx(self, vx):
        if vx > 15:
            raise ValueError(f"Attempting to get non-existent register: {vx:X}")
        
        return self.registers[vx]
    
    def increment_pc(self, by=2):
        self.pc = (self.pc + by) % 4096
    
    def decrement_pc(self, by=2):
        self.pc = (self.pc - by)

    def get_pc(self):
        return self.pc
    
    def set_pc(self, value):
        if value > 4096:
            raise IndexError("Cannot set PC to value greater than 0xfff")
        self.pc = value

    def set_index(self, value, set_overflow=False):
        if(set_overflow and (value > 4095)):
            self.set_vx(0xf, 1)
        self.index = value % 4096

    def get_index(self):
        return self.index

    # convenience method
    def get_ram_at_pc(self,length=2):
        return self.ram[self.pc:self.pc+length]

    def get_ram(self,length=1,address=None):
        # TODO checks
        # defaults to reading from location that index points to
        if address == None:
            address = self.index
        return self.ram[address:address+length]
    
    def set_ram(self, data, address=None):
        if address == None:
            address = self.index
        if type(data) == int:
            data = data.to_bytes(1)
        elif type(data) == list:
            data = bytes(data)
        if type(data) != bytearray and type(data) != bytes:
            raise ValueError(f"Attempting to set RAM with wrong data type: {type(data)}")
        if address + len(data) > 4096:
            raise OverflowError("Out of memory while writing to RAM.")
        self.ram[address:address+len(data)] = data

    def set_delay_timer(self, value):
        self.delay_timer = value
    
    def get_delay_timer(self):
        return self.delay_timer
    
    def set_sound_timer(self, value):
        self.sound_timer = value
    
    def decrement_delay_timer(self):
        self.delay_timer = max(self.delay_timer - 1, 0)
        return self.delay_timer

    def decrement_sound_timer(self):
        self.sound_timer = max(self.sound_timer - 1, 0)  
        return self.sound_timer

    def stack_push(self, value):
        self.stack.append(value)

    def stack_pop(self):
        if len(self.stack) <= 0:
            raise IndexError("Attempting to pop from empty stack.")
        return self.stack.pop()
    
    def clear_key_state(self):
        self.key_state = [False]*16
    
    def set_key_state(self,key:int,value:bool):
        if key >= 16 or key < 0:
            raise ValueError("Key value out of range.")
        if type(value) != bool:
            raise TypeError("Key state value must be a boolean.")
        self.key_state[key] = value
    
    def get_key_state(self,key=None):
        if key == None:
            return self.key_state
        elif key >= 16 or key < 0:
            raise ValueError("Key value out of range.")
        else:
            return self.key_state[key]