from pickletools import uint8
import sounddevice as sd
import numpy as np
from bitstream import BitStream
import math
import matplotlib.pyplot as plt
import time
from datetime import timedelta
def f_t(input):
    alfa = 1.99999
    if (input >= 0 and input < 0.5):
        return(alfa*input)
    else:
        return(alfa*(1-input))

#swap first half with second half 

def bitSwap(int_64):
    mask_low = 0xFFFF0000
    mask_high = 0x0000FFFF
    eq_low = int_64 and mask_low
    eq_high = int_64 and mask_high
    eq_high = eq_high << 32
    eq_low = eq_low >> 32 
    result = eq_low or eq_high
    return result

def entropy(max_prob, probes = []):
    entropy_array = []
    propability_array = []
    for x in range(0,256):
        entropy_array.append(0)
        propability_array.append(0)
    
    for x in probes:
        entropy_array[x] += 1 

    calculated_entropy = 0 

    if (max_prob == 255):
        start = 0
        end = 256
    else:
        start = 1 
        end = 255

    for x in range (start,end):
        propability_array[x] = (entropy_array[x]/len(probes))
        calculated_entropy += propability_array[x]*math.log(propability_array[x],2)
    

    return -1*calculated_entropy
    
def generateStream(bitsCount):
    start_time = time.monotonic()
    fs = 44100 #probing freq
    stream = BitStream()
    temp_stream = BitStream()
    probes_count = 44100*3 #probing freq * time
    myrecording = sd.rec(int(probes_count), samplerate=fs, channels=1, dtype='int16') # recording
    sd.wait()  # Wait until recording is finished

    probes = []

    #const in algorythm
    mask1 = 0b1111111100000000
    mask2 = 0b0000000011111111
    lsbMask = 0b11100000
    omega = 0.5
    gamma = 4 
    #denominator is 2^b - 1, with b = 3, denominator always be 7 
    denominator = 7 
    epsilon = 0.05
    #L in article - numbers of random bits
    bits = int(8)

    #manual casting to uint8
    for x in range (44100,probes_count):
        probes.append(np.uint8(myrecording[x]))
    extracted = []

    #extracted contain 3 LSB from each new 8 bit sample

    for x in range (0,probes_count-44100):
        extracted.append((probes[x] & lsbMask) >> 5)

    probes_count = probes_count - 44100 
    
    # afert deleting 1st sec of record, we have 44100 less probes
    #extracted[x] is same as y[c] in article

    processedRandomNumber = []
    processedRandomNumber.append([0.14592, 0.653589, 0.793238, 0.462641, 0.383279, 0.502884, 0.197169, 0.399375])
    for x in range (0,8):
        processedRandomNumber.append([0,0,0,0,0,0,0,0])

    result = 0

    #coordinat for processedRandomNumber is [y][x] same as [t][i] in article

    counter = 0 

    z = [0,0,0,0,0,0,0,0]

    while result <= probes_count:  #
        z = [0,0,0,0,0,0,0,0]
        #first loop

        for x in range (0,8):
            processedRandomNumber[0][x] = (((omega * extracted[counter])/denominator)+ processedRandomNumber[0][x]) * (1/(1+omega))
            if (counter+1 >= probes_count):
                counter = 0 
            else:
                counter +=1
            
        #second loop
        #t is in 0,3 range
        for t in range (0,gamma):
            for i in range (0, bits):
                #evry value is depend from other
                neg_index_i = (i-1)%bits
                pos_index_i = (i+1)%bits
                processedRandomNumber[t+1][i] = (1-epsilon)*f_t(processedRandomNumber[t][i]) + (epsilon/2) * (f_t(processedRandomNumber[t][pos_index_i])+f_t(processedRandomNumber[t][neg_index_i]))
        #third loop
        for i in range (0,8):
            temp_stream.write(processedRandomNumber[gamma-1][i], np.float64) 
            processedRandomNumber[0][i] = processedRandomNumber[gamma-1][i]

        z = temp_stream.read(np.uint64, 8)

        #fourth loop
        for i in range (0,int(bits/2)):
            z[i] = (int(z[i]) ^ bitSwap(z[i+4]))
        
        for x in range (0,4):
            stream.write(z[x], np.uint64)
        
        result+=1
        temp_stream = BitStream()
    
    result -= 1 
    #uint8_array contain random number as array 

    uint8_array = [] 
    uint8_array = stream.read(np.uint8, (result*256)/8) 
    temp_array = []
    temp_stream = BitStream()
    counter = 1 
    print("Bit counts: ", bitsCount)

    for x in uint8_array:
        if counter > bitsCount:
            break
        else:
            if (int(x) == 0 or int(x) == 255):
                continue
            else:
                counter += 1
                temp_array.append(int(x))
    
    end_time = time.monotonic()
    print(timedelta(seconds=end_time - start_time))
    return bytes(temp_array)

   
   
""" 
    #to make histogram use: Probes - contain values from extractor
    # uint8_array has numbers after postprocessing ; len()

    toPrint = []
    toPrint2 = []
    for x in probes:
        toPrint.append(int(x))

    #deleting 0 and 255 from array

    for x in uint8_array:
        if (int(x) == 0 or int(x) == 255):
            continue
        else:
            toPrint2.append(int(x))
    
    source_entropy = entropy(max(toPrint), toPrint)
    processed_entropy = entropy(254, toPrint2)

    print("Total: ", len(toPrint2))
    print("Entropy for source: ", source_entropy)
    print("Entropy for postprocessed: ", processed_entropy)

    
    figImg, axsImg = plt.subplots(2,1,figsize = [12, 12])
    axsImg[0].hist(toPrint, bins=256, range=[0, 255])
    #axsImg[0].set_tile("Entropy for source: " , source_entropy)
    axsImg[1].hist(toPrint2, bins=256, range=[0, 255])
    #axsImg[1].set_tile("Entropy for source: " , processed_entropy)
    figImg.tight_layout(pad=5.0)
    #figImg.show()
    plt.show()
    """
#if __name__ == "__main__":
#    main()


