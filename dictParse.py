# dictParse.py

#b'\xb4\x02\x00\x02\x04\x00\x00\x01\x0c\xc7'

def dictParse(byteStream):
    #byteStream = byteStream.decode()
    print(byteStream[9])

    # if first bit is not equal to 180 and 10th bit is not 199
    
    

# for evoking from command line:
dictParse(b'\xb4\x02\x00\x02\x04\x00\x00\x01\x0c\xc7')
