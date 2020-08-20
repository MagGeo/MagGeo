def Kradius (lat):
    if 0 <= lat < 90 :
        #for Northern Latitudes 
        nlat = (-10 * lat) + 1800
        #print("The R on the North")
    if -90 < lat < 0:
        #for Southern Latitudes
        nlat = (10 * lat) + 1800
        #print ("The R on the South")
    return nlat