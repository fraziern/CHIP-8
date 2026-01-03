import random
from debug_utils import get_instr_definition

class CPU():
    ROMSTART = 0x200
    FONTSTART = 0x50

    def __init__(self, state, keyboard, display, config):
        self.config = {'nineties_shift':False, 'nineties_bnnn':False, 'debug':False}
        self.config |= config # in-place update
        self.state = state
        self.keyboard = keyboard
        self.display = display
        self.config = config


    # instr will be a 2 byte opcode
    def _decode_instruction(self, instr:bytearray):
        if len(instr) != 2:
            print(f'instr:{instr}')
            raise ValueError("Instruction is the wrong size for decoding.")
        
        # nibbles
        n1 = (instr[0] >> 4) & 0xf
        n2 = instr[0] & 0xf
        n3 = (instr[1] >> 4) & 0xf
        n4 = instr[1] & 0xf
        nn = instr[1]
        nnn = (n2 << 8) | (n3 << 4) | n4

        return n1, n2, n3, n4, nn, nnn


    def _add(self, state, a, b, result_to=None):
        if result_to is None:
            result_to = a
        value = state.get_vx(a) + state.get_vx(b)
        value, vf = (value % 256, 1) if value > 255 else (value, 0)
        state.set_vx(result_to,value)
        state.set_vx(0xf,vf) # carry


    def _subtract(self, state, a, b, result_to=None): 
        # function for 8xy5 and 8xy7, subtracts a - b and updates state
        if result_to is None:
            result_to = a
        value = state.get_vx(a) - state.get_vx(b)
        value, vf = ((value + 256) % 256, 0) if value < 0 else (value, 1)
        state.set_vx(result_to,value)
        state.set_vx(0xf, vf)


    def _right_shift(self, state, a, b, result_to=None):
        # 8xy6
        if result_to is None:
            result_to = a
        if self.config['nineties_shift']:
            state.set_vx(a, state.get_vx(b))
        vf = state.get_vx(a) & 0x1 # grab the rightmost bit
        state.set_vx(a, state.get_vx(a) >> 1)
        state.set_vx(0xf, vf)


    def _left_shift(self, state, a, b, result_to=None):
        # 8xye
        if result_to is None:
            result_to = a
        if self.config['nineties_shift']:
            state.set_vx(a, state.get_vx(b))
        vf = (state.get_vx(a) >> 7) & 0x1 # grab the leftmost bit
        state.set_vx(a, state.get_vx(a) << 1)
        state.set_vx(0xf, vf)


    def _draw_instr(self, state, display, vx, vy, n):
        x = state.get_vx(vx)
        y = state.get_vx(vy)
        sprite = state.get_ram(n)
        vf = display.update_screen(x, y, sprite)
        state.set_vx(0xf, vf)

    def run_cycle(self):
        # 3. Fetch instruction
        instr = self.state.get_ram_at_pc()
        self.state.increment_pc()
        
        # 4. Decode/Execute instruction
        n1, n2, n3, n4, nn, nnn = self._decode_instruction(instr)
        if self.config['debug']:
            definition = get_instr_definition(n1, n2, n3, n4, nn, nnn)
            print(f'Instruction {self.state.get_pc()-self.ROMSTART:X}: {instr.hex()} {definition}')

        match n1:
            case 0x0:
                match nn:
                    case 0xe0:      # 00e0 clear screen
                        self.display.clear_screen()
                        screen_updated = True
                    case 0xee:      # 00ee return from subroutine
                        self.state.set_pc(self.state.stack_pop())
                    case _:
                        raise SyntaxError(f"Instruction not recognized: {instr.hex()}")
            case 0x1:               # 1nnn jump
                self.state.set_pc(nnn)
            case 0x2:               # 2nnn call subroutine
                self.state.stack_push(self.state.get_pc())
                self.state.set_pc(nnn)
            case 0x3:               # 3xnn skip one instr if vx == nn
                if self.state.get_vx(n2) == nn:
                    self.state.increment_pc()
            case 0x4:               # 4xnn skip one instr if vx != nn
                if self.state.get_vx(n2) != nn:
                    self.state.increment_pc()
            case 0x5:               # 5xy0 skips if the values in VX and VY are equal
                if self.state.get_vx(n2) == self.state.get_vx(n3):
                    self.state.increment_pc()
            case 0x6:               # 6xnn set register vx
                self.state.set_vx(n2, nn)
            case 0x7:               # 7xnn add value to register vx
                new_value = self.state.get_vx(n2) + nn
                self.state.set_vx(n2, new_value)
            case 0x8:
                match n4:
                    case 0x0:       # 8xy0 set x = y
                        self.state.set_vx(n2,self.state.get_vx(n3))
                    case 0x1:       # 8xy1 binary OR
                        value = self.state.get_vx(n2) | self.state.get_vx(n3)
                        self.state.set_vx(n2,value)
                    case 0x2:       # 8xy2 binary AND
                        value = self.state.get_vx(n2) & self.state.get_vx(n3)
                        self.state.set_vx(n2,value)
                    case 0x3:       # 8xy3 binary XOR
                        value = self.state.get_vx(n2) ^ self.state.get_vx(n3)
                        self.state.set_vx(n2,value)
                    case 0x4:       # 8xy4 add with carry
                        self._add(self.state, n2, n3, result_to=n2)
                    case 0x5:       # 8XY5 sets VX to the result of VX - VY
                        self._subtract(self.state,n2,n3)
                    case 0x6:       # 8xy6 right shift
                        self._right_shift(self.state, n2, n3)
                    case 0x7:       # 8XY7 sets VX to the result of VY - VX
                        self._subtract(self.state, n3, n2, result_to=n2)
                    case 0xe:       # 8xye left shift
                        self._left_shift(self.state, n2, n3)
                    case _:
                        raise SyntaxError(f"Instruction not recognized: {instr.hex()}")              
            case 0x9:               # 9xy0 skips if the values in VX and VY are not equal
                if self.state.get_vx(n2) != self.state.get_vx(n3):
                    self.state.increment_pc()
            case 0xa:               # annn set index register I
                self.state.set_index(nnn)
            case 0xb:               # bnnn jump with offset
                if self.config['nineties_bnnn']:
                    self.state.set_pc(nnn+self.state.get_vx(n2))
                else:
                    self.state.set_pc(nnn)
            case 0xc:               # cxnn random
                r = random.randint(0,0xff)
                self.state.set_vx(n2,(nn & r))
            case 0xd:               # dxyn draw
                self._draw_instr(self.state, self.display, n2, n3, n4)
                screen_updated = True
            case 0xe:
                match nn:
                    case 0x9e:      # ex9e skip if vx key pressed
                        if self.keyboard.is_pressed(self.state.get_vx(n2)):
                            self.state.increment_pc()
                    case 0xa1:      # exa1 skip if vx key not pressed
                        if not self.keyboard.is_pressed(self.state.get_vx(n2)):
                            self.state.increment_pc()
                    case _:
                        raise SyntaxError(f"Instruction not recognized: {instr.hex()}")
            case 0xf:
                match nn:
                    case 0x07:      # fx07 get delay timer
                        self.state.set_vx(n2, self.state.get_delay_timer())
                    case 0x0a:      # fx0a get key
                        keypress = self.keyboard.is_pressed()
                        if not keypress:
                            self.state.decrement_pc()
                        else:
                            self.state.set_vx(n2, keypress)
                    case 0x15:      # fx15 set delay timer to vx
                        self.state.set_delay_timer(self.state.get_vx(n2))
                    case 0x18:      # fx18 set sound timer to vx
                        self.state.set_sound_timer(self.state.get_vx(n2)) 
                    case 0x1e:      # fx1e add to index
                        value = self.state.get_index() + self.state.get_vx(n2)
                        self.state.set_index(value, set_overflow=True)
                    case 0x29:      # fx29 set I to font location for char x
                        self.state.set_index((self.state.get_vx(n2) * 5) + self.FONTSTART)
                    case 0x33:      # fx33 BCD conversion
                        bcd = self.state.get_vx(n2)
                        bcd_list = [(bcd//100),(bcd%100)//10,bcd%10]
                        self.state.set_ram(bcd_list)
                    case 0x55:      # fx55 store registers to memory
                        for i in range(n2+1):
                            self.state.set_ram(self.state.get_vx(i), self.state.get_index()+i)
                    case 0x65:      # fx65 load registers from memory
                        for i in range(n2+1):
                            self.state.set_vx(i, self.state.get_ram(address=self.state.get_index()+i))
                    case _:
                        raise SyntaxError(f"Instruction not recognized: {instr.hex()}")
        if(self.config['debug']):
            print(self.state)