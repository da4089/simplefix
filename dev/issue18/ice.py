import simplefix

with open('definition.txt') as f:
    t = f.read()

p = simplefix.FixParser()
p.append_buffer(t)

# Mark end of FIX message (see simplefix issue#13)
p.append_buffer(b'\x0110=000\x01')

m = p.get_message()

print(m)
