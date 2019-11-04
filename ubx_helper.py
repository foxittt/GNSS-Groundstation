class ubx_config_helper:
    config = {
        # ubx-config for UART1
        "GLL_UART1": b'\xCA\x00\x91\x20',
        "GSV_UART1": b'\xC5\x00\x91\x20',
        "GGA_UART1": b'\xbb\x00\x91\x20',
        "GSA_UART1": b'\xC0\x00\x91\x20',
        "RMC_UART1": b'\xAC\x00\x91\x20',
        "VTG_UART1": b'\xB1\x00\x91\x20',
        "RAWX_UART1": b'\xA5\x02\x91\x20',
        "SFRBX_UART1": b'\x32\x02\x91\x20'
    }
    @staticmethod
    def compute_checksum(msg):
        '''8-Bit Fletcher Algorithm modelled after ublox documentation. Returns checksum'''
        #print(f"computing checksum of {msg}")
        CK_A = CK_B = 0
        # start at class (byte 2)
        for i in range(2, len(msg)):
            CK_A += msg[i]
            CK_B += CK_A
        # mask to 8bit uint
        CK_A &= 0xFF
        CK_B &= 0xFF
        # convert to bytes
        CK_A = bytes([CK_A])
        CK_B = bytes([CK_B])
        #print("CK_A", CK_A)
        #print("CK_B", CK_B)
        return CK_A+CK_B

    def ubx_msg(self, c, id, payload):
        '''generate a valid ubx message with checksum'''
        sync = b'\xB5\x62'
        print("payload", list(payload))
        length = bytes([len(payload)])
        if (len(length) < 2):
            length += b'\x00'
        msg = sync+c+id+length+payload
        checksum = self.compute_checksum(msg)
        msg += checksum
        return msg

    def ubx_set_val(self, *args):
        '''set ubx config values'''
        if (len(args) % 2 != 0):
            raise ValueError("Number of arguments must be even!")
        c = b'\x06'
        id = b'\x8A'
        payload = b'\x00\x01\x00\x00'
        for arg in args:
            if (type(arg) != bytes):
                arg = bytes([arg])
            payload += arg

        msg = self.ubx_msg(c, id, payload)
        return msg

    def ubx_config_disable(self, *args):
        '''disable ubx messages (multiple strings as argument)'''
        vals = []
        for arg in args:
            vals.append(self.config[arg])
            vals.append(b'\x00')
        return self.ubx_set_val(*vals)

    def ubx_config_disable_all(self):
        '''disable all messages defined in config'''
        return self.ubx_config_disable(*list(self.config.keys()))

    def ubx_config_enable(self, *args):
        '''enable ubx messages (multiple strings as argument)'''
        vals = []
        for arg in args:
            vals.append(self.config[arg])
            vals.append(b'\x01')
        return self.ubx_set_val(*vals)


class ubx_parser:
    sync = b'\xB5\x62'
    data = []
    last_byte = None
    parse_mode = None
    ubx_length = None
    ubx_msg_dict = {
        # lookup table for ubx messages
        b"\x01": {
            "classname": "NAV",

        },
        b"\x02": {
            "classname": "RXM",
            b"\x14": "MEASX",
            b"\x41": "PMREQ",
            b"\x15": "RAWX",
            b"\x59": "RLM",
            b"\x13": "SFRBX"
        },
        b"\x04": {
            "classname": "INF",

        },
        b"\x05":  {
            "classname": "ACK",
            b"\x00": "NAK",
            b"\x01": "ACK"
        },
        b"\x06":  {
            "classname": "CFG",

        },
        b"\x09":  {
            "classname": "UPD",

        },
        b"\x0A":  {
            "classname": "MON",

        },
        b"\x0D":  {
            "classname": "TIM",

        },
        b"\x13":  {
            "classname": "MGA",

        },
        b"\x21":  {
            "classname": "LOG",

        },
        b"\x27":  {
            "classname": "SEC",

        },
    }

    def safeget(self, dict, *keys):
        '''safe getmethod for nested dicts'''
        for key in keys:
            try:
                dict = dict[key]
            except KeyError:
                return None
        return dict

    def add_byte(self, byte):
        if (self.parse_mode == None and byte == b'\x62' and self.last_byte == b'\xB5'):
            self.parse_mode = "UBX"
            self.data = []
            print("received UBX start frame")
            return
        self.last_byte = byte
        if self.parse_mode == "UBX":
            self.data.append(byte)
            # print(f"append {byte}", f"l: {len(self.data)} ",
            # f"data {self.data}")
            if (len(self.data) == 4):
                length = int.from_bytes(
                    self.data[2] + self.data[3], 'little')
                #print(f"length: {length}")
                self.ubx_length = length
            elif (self.ubx_length != None and len(self.data) == (self.ubx_length + 6)):
                data = b''.join(self.data)
                #print(f"sync: {self.sync}", f"data {data}",)
                msg = self.sync+bytes(data)
                checksum = ubx_config_helper.compute_checksum(msg[:-2])
                if checksum != data[-2:]:
                    print(
                        f"wrong checksum {list(checksum)} is not {list(data[-2:])}")
                else:
                    classname = self.safeget(
                        self.ubx_msg_dict, self.data[0], "classname")
                    idname = self.safeget(
                        self.ubx_msg_dict, self.data[0], self.data[1]) or "unknown"
                print(
                    f"received ubx message (class:{classname} id:{idname} payload_length: {self.ubx_length})")
                self.data = []
                self.parse_mode = None
