class State():

    ROMSTART = 0x200

    def __init__(self, pc=ROMSTART):
        self.index = 0
        self.registers = bytearray(16)
        self.pc = pc
        self.delay_timer = 0
        self.sound_timer = 0
        self.stack = []
        self.ram = bytearray(4096)

    def __str__(self):
        string = ""
        string += f'PC: {self.pc:X}\n'
        string += f'Registers: {self.registers.hex()}'
        return string

    def set_vx(self, vx, value):
        if vx > 15:
            raise ValueError(f"Attempting to set non-existent register: {vx:X}")
        
        self.registers[vx] = value % 256
    
    def get_vx(self, vx):
        if vx > 15:
            raise ValueError(f"Attempting to get non-existent register: {vx:X}")
        
        return self.registers[vx]
    
    def increment_pc(self, by=2):
        self.pc += by
        # TODO: overflow check
    
    def set_pc(self, value):
        self.pc = value
        # TODO checks

    def set_index(self, value):
        # TODO overflow check
        self.index = value
    
    # def get_index   just use state.index

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
        if type(data) != bytearray and type(data) != bytes:
            raise ValueError("Attempting to set RAM with wrong data type.")
        if address + len(data) > 4096:
            raise OverflowError("Out of memory while writing to RAM.")
        self.ram[address:address+len(data)] = data

    def set_delay_timer(self, value):
        self.delay_timer = value
    
    def set_sound_timer(self, value):
        self.sound_timer = value
    
    def decrement_delay_timer(self):
        self.delay_timer = max(self.delay_timer - 1, 0)

    def decrement_sound_timer(self):
        self.sound_timer = max(self.sound_timer - 1, 0)  
    