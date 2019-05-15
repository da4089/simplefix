import simplefix

f = open('definition.txt')
t = f.read()
f.close()

p = simplefix.FixParser()
p.append_buffer(t)

# FIXME: mark end of FIX message (see simplefix issue#13)
p.append_buffer(b'\x0110=000\x01')

m = p.get_message()

print(m)
