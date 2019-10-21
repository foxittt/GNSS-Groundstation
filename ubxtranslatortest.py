from ubx_helper import ubx_parser, ubx_config_helper

parser = ubx_parser()
helper = ubx_config_helper()


print(helper.ubx_config_enable("RAWX_UART1"))
msg = b'\xB5\x62\x06\x8A\x09\x00\x00\x01\x00\x00\xA5\x02\x91\x20\x01\xf3\x66'
ck = ubx_config_helper.compute_checksum(msg[:-2])
print(f"ck: {list(ck)}")
for b in msg:
    b = bytes([b])
    print(f"add {b}")
    parser.add_byte(b)
