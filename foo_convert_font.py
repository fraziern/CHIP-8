# convert font.txt to font.py

with open('font.txt') as f:
    lines = f.readlines()

values = []

for line in lines:
    valuestring = line.split('//')[0]
    values_to_add = [x.strip() for x in valuestring.split(',')]
    int_values_to_add = [int(x,16) for x in values_to_add if x]
    values.extend(int_values_to_add)

output = bytes(values)

with open('font.rom', 'wb') as f:
    f.write(output)