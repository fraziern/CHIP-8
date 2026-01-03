def get_instr_definition(n1, n2, n3, n4, nn, nnn) -> str:
    match n1:
        case 0x0:
            match nn:
                case 0xe0:      # 00e0 clear screen
                    return "clear screen"
                case 0xee:      # 00ee return from subroutine
                    return "return from subroutine"
        case 0x1:               # 1nn:Xn jump
            return f"jump to {nnn:3X}"
        case 0x2:               # 2nn:Xn call subroutine
            return f"call subroutine at {nnn:3X}"
        case 0x3:               # 3xnn:X skip one instr if vx == nn:X
            return f'skip if v{n2:X} == {nn:X}'
        case 0x4:               # 4xnn:X skip one instr if vx != nn:X
            return f'skip if v{n2:X} != {nn:X}'
        case 0x5:               # 5xy0 skips if the values in VX and VY are equal
            return f'skip if v{n2:X} == v{n3:X}'
        case 0x6:               # 6xnn:X set register vx
            return f'set v{n2:X} to {nn:X}'
        case 0x7:               # 7xnn:X add value to register vx
            return f'add {nn:X} to v{n2:X}'
        case 0x8:
            match n4:
                case 0x0:       # 8xy0 set x = y
                    return f'set v{n2:X} = v{n3:X}'
                case 0x1:       # 8xy1 binary OR
                    return f'binary v{n2:X} OR v{n3:X}'
                case 0x2:       # 8xy2 binary AND
                    return f'binary v{n2:X} AND v{n3:X}'
                case 0x3:       # 8xy3 binary XOR
                    return f'binary v{n2:X} XOR v{n3:X}'
                case 0x4:       # 8xy4 add with carry
                    return f'binary v{n2:X} + v{n3:X}'
                case 0x5:       # 8XY5 sets VX to the result of VX - VY
                    return f'binary v{n2:X} - v{n3:X}'
                case 0x6:       # 8xy6 right shift
                    return f'binary v{n2:X} >> v{n3:X}'
                case 0x7:       # 8XY7 sets VX to the result of VY - VX
                    return f'binary v{n3:X} - v{n2:X}'
                case 0xe:       # 8xye left shift
                    return f'binary v{n2:X} << v{n3:X}'           
        case 0x9:               # 9xy0 skips if the values in VX and VY are not equal
            return f'skip if {n2:X} != {n3:X}'
        case 0xa:               # ann:Xn set index register I
            return f'set index I to {nnn:3X}'
        case 0xb:               # bnn:Xn jump with offset
            return f'jump to index I +{nnn:3X}'
        case 0xc:               # cxnn:X random
            return f'set v{n2:X} to random number AND {nn:X}'
        case 0xd:               # dxyn draw
            return f'draw sprite at I, at x = v{n2:X} y = v{n3:X} height {n4:X}'
        case 0xe:
            match nn:
                case 0x9e:      # ex9e skip if vx key pressed
                    return f'skip if key at v{n2:X} pressed'
                case 0xa1:      # exa1 skip if vx key not pressed
                    return f'skip if key at v{n2:X} not pressed'
        case 0xf:
            match nn:
                case 0x07:      # fx07 get delay timer
                    return f'set v{n2:X} to delay timer'
                case 0x0a:      # fx0a get key
                    return f'wait for key then set v{n2:X} to key'
                case 0x15:      # fx15 set delay timer to vx
                    return f'set delay timer to v{n2:X}'
                case 0x18:      # fx18 set sound timer to vx
                    return f'set sound timer to v{n2:X}'
                case 0x1e:      # fx1e add to index
                    return f'add v{n2:X} to index I'
                case 0x29:      # fx29 set I to font location for char x
                    return f'set index I to font location for v{n2:X}'
                case 0x33:      # fx33 BCD conversion
                    return f'BCD conversion of value in v{n2:X}'
                case 0x55:      # fx55 store registers to memory
                    return f'store {n2:X} registers to memory'
                case 0x65:      # fx65 load registers from memory
                    return f'load {n2:X} registers from memory'
