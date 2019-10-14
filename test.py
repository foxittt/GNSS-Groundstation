import numpy as np

def compute_checksum(msg, n):
    
    ck_a = np.zeros((1,1),dtype='uint8')
    ck_b = np.zeros((1,1),dtype='uint8')
    
    # Convert buffer of bytes to a numpy array
    val = np.frombuffer(msg,dtype='uint8')
    
    # Compute checksum
    for ii in range(2,n):
        ck_a[0] = ck_a[0] + val[ii]
        ck_b[0] = ck_b[0] + ck_a[0]
        
    return msg+ck_a.tobytes()+ck_b.tobytes()

msg_disable_gll = b'\xB5\x62\x06\x8A\x09\x00\x00\x01\x00\x00\xCC\x00\x91\x20\x00'
msg_disable_gll = compute_checksum(msg_disable_gll,len(msg_disable_gll)) 
print(msg_disable_gll)

