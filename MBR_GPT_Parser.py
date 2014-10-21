#This program was written by DJ Palombo
#Sources for the information can be found at http://www.jonrajewski.com/data/Presentations/CEIC2013/Rajewski_CEIC_2013_UEFI_MBR_GPT_Oh_My_2013_5_19.pdf
#Pass this program a raw disk image (generally .001 or .img) and it will parse the drive to determine if the drive is MBR or GPT, and how many partitions there are.
#It will then parse out all the information possible from the partitions.

#import binascii #Keeping this line in as part of a testing solution to shorten the code

#The following lines contain flags that are needed to help determine the partition type for MBR Partitions
#Bootable flag and partition types for MBR
bootable = "80"
emptyPartition = "00"
fat12Partition = "01"
ntfsPartition = "07"
fat32Partition = "0B"
fat32LbaPartition = "0C"
extPartition = "83"
freeBsdPartition = "A5"
macOsPartition = "A8"

#The following lines contain flags that are needed to determine the partition type for GPT partitions
#GUID values for GPT
mbrScheme = "024DEE41-33E7-11D3-9D69-0008C781F39F"
efiScheme = "C12A7328-F81F-11D2-BA4B-00A0C93EC93B"
biosPartition = "21686148-6449-6E6F-744E-656564454649"
microsoftReservedPartition = "E3C9E316-0B5C-4DB8-817D-F92DF00215AE"
microsoftBasicDataPartition = "EBD0A0A2-B9E5-4433-87C0-68B6B72699C7"
microsoftLogicalDiskManagerMetadata = "5808C8AA-7E8F-42E0-85D2-E1E90434CFB3"
microsoftLogicalDiskManagerData = "AF9B60A0-1431-4F62-BC68-3311714A69AD"
windowsRecoveryEnvironment = "DE94BBA4-06D1-4D40-A16A-BFD50179D6AC"
linuxFilesystemData = "0FC63DAF-8483-4772-8E79-3D69D8477DE4"
linuxSwap = "0657FD6D-A4AB-43C4-84E5-0933C84B4F4F"
linuxLvm = "E6D6D379-F507-44C2-A23C-238F2A3DF928"
appleHfs = "48465300-0000-11AA-AA11-00306543ECAC"
appleUfs = "55465300-0000-11AA-AA11-00306543ECAC"
eitherOr = "EBD0A0A2-B9E5-4433-87C0-68B6B72699C7"
iQuit = "00000000-0000-0000-0000-000000000000"


def hexFormat(data, location): #This function is used to properly format the hex values being read off the disk
    formattedCorrectly = hex(data[location]) #This created formattedCorrectly as the hex value found at the location given
    strippedData = formattedCorrectly[2:] #This removes the "0x" from in front of the value to allow for easier processing
    if len(strippedData) == 2: #This if statement just ensures that two values are returned, as hex values of double zero and with a leading zero were being problematic
        return (strippedData)
    elif len(strippedData) == 1:
        return ("0"+strippedData)
    else:
        return ("00")

def mbrParse(data, location, pNumber): #This function is used to parse the MBR.  I use Pt* (Where * represents a number) to denote parts of a value that will later be joined together.

    #This block of code was originally lower in this function, but was moved to be able to determine if a partition was in use
    sixthFlagPt1 = hexFormat(data, (location + 13))
    sixthFlagPt2 = hexFormat(data, (location + 14))
    sixthFlagPt3 = hexFormat(data, (location + 15))
    sixthFlagPt4 = hexFormat(data, (location + 16))
    sixthFlag = "0x" + sixthFlagPt4 + sixthFlagPt3 + sixthFlagPt2 + sixthFlagPt1
    sizeInSectors = int(sixthFlag, 16)
    if sizeInSectors == 0: #If the partition has no size, it does not exist, therefore the drive is done.
        noMorePartitions() #error handling, prints that there are no more partitions.

    print("Regarding Partition", pNumber, ": ")
    print()

    firstFlag = hexFormat(data, location)
    if firstFlag == bootable: #The bootable flag is 80, so this is checking if the drive is bootable using the information from the declarations above.
        print("This Partition is bootable")
    else:
        print("This Parititon is not bootable")

    #The Cylinder-head-sector address for the drive is the little endian version of the three bytes from the starting offset + 2
    #As struct.unpack would not deal with reading small sections of a large file, I devised a way to get the hex values and convert them to little Endian manually
    secondFlagPt1 = hexFormat(data, (location + 2))
    secondFlagPt2 = hexFormat(data, (location + 3))
    secondFlagPt3 = hexFormat(data, (location + 4))
    secondFlag = "0x" + secondFlagPt3 + secondFlagPt2 + secondFlagPt1 #Adding in the 0x and formatting little Endian
    startingChsAddress = int(secondFlag, 16) #finding the integer value of the CHS address
    print("The Starting CHS Address is: ")
    print(startingChsAddress)

    partitionType = hexFormat(data, (location + 5)) #The partition type is one value
    if partitionType == emptyPartition: #determine what the partition type is
        print("This is an empty partition")
    elif partitionType == fat12Partition:
        print("This is a FAT12 Partition")
    elif partitionType == ntfsPartition:
        print("This is a NTFS Partition")
    elif partitionType.upper() == fat32Partition:
        print("This is a FAT32 CHS Partition")
    elif partitionType == extPartition:
        print("This is a Linux Ext3 Partition")
    elif partitionType.upper() == freeBsdPartition:
        print("This is a FreeBSD Partition")
    elif partitionType.upper() == macOsPartition:
        print("This is a HFS+ Partition")
    elif partitionType.upper() == fat32LbaPartition:
        print("This is a FAT32 LBA Partition")
    else: #There are an abundance of partitions that exist, so I chose some common ones to use for this program
        print("This program does not have a matching value for partition type. \n The partition type is ",
              partitionType, ".  \n You can check online resources to find out what that represents")

    #This is the same process as the starting CHS address
    fourthFlagPt1 = hexFormat(data, (location + 6))
    fourthFlagPt2 = hexFormat(data, (location + 7))
    fourthFlagPt3 = hexFormat(data, (location + 8))
    fourthFlag = "0x" + fourthFlagPt3 + fourthFlagPt2 + fourthFlagPt1
    endingChsAddress = int(fourthFlag, 16)
    print("The Ending CHS Address is: ")
    print(endingChsAddress)

    #The Logical Block Address can be important to investigators looking for a partition on a disk.  This section gives that information.
    fifthFlagPt1 = hexFormat(data, (location + 9))
    fifthFlagPt2 = hexFormat(data, (location + 10))
    fifthFlagPt3 = hexFormat(data, (location + 11))
    fifthFlagPt4 = hexFormat(data, (location + 12))
    fifthFlag = "0x" + fifthFlagPt4 + fifthFlagPt3 + fifthFlagPt2 + fifthFlagPt1
    startingLba = int(fifthFlag, 16)
    print("The starting LBA is: ")
    print(startingLba)

    #What is now at the beginning of the function is used to be here, but it was moved to be able to test if a partition was in use.
    #I am still printing it here to maintain the formatting used in MBR
    print("The size of the partition (in sectors) is: ")
    print(sizeInSectors)
    print()
    print()
    #Once I locate somewhere in hex that says the sector size, I will add in another section for sizeInBytes
    
def letterHex(data, location, step): #This is used when parsing GPT.  This is to get the partition name.
    letterHexValue = hexFormat(data, (location + 56 + step)) #The offset for the name is 56
    if letterHexValue == "00": #Once a name ends, it pads the rest of the 72 bytes as 00, which wouldn't work with the name.  So I replace 00 with nothing so it has no effect
        letterHexValue = ""
        return (letterHexValue)
    else:
        letterValue = chr(int(letterHexValue, 16))
        return (letterValue)

def gptParse(data, location, x): #The actual GPT parser.  I append P* (where * stands for a number) for parts of an entry
    #The 16 bytes for Partition type GUID.  I format it manually, as no automated methods I could conceive would work.
    #This is in some mix of little and big Endian, so the manual formatting used throughout comes in handy.
    firstFlagP1 = hexFormat(data, location)
    firstFlagP2 = hexFormat(data, (location + 1))
    firstFlagP3 = hexFormat(data, (location + 2))
    firstFlagP4 = hexFormat(data, (location + 3))
    firstFlagP5 = hexFormat(data, (location + 4))
    firstFlagP6 = hexFormat(data, (location + 5))
    firstFlagP7 = hexFormat(data, (location + 6))
    firstFlagP8 = hexFormat(data, (location + 7))
    firstFlagP9 = hexFormat(data, (location + 8))
    firstFlagP10 = hexFormat(data, (location + 9))
    firstFlagP11 = hexFormat(data, (location + 10))
    firstFlagP12 = hexFormat(data, (location + 11))
    firstFlagP13 = hexFormat(data, (location + 12))
    firstFlagP14 = hexFormat(data, (location + 13))
    firstFlagP15 = hexFormat(data, (location + 14))
    firstFlagP16 = hexFormat(data, (location + 15))
    firstFlagNonSensitive = firstFlagP4 + firstFlagP3 + firstFlagP2 + firstFlagP1 + "-" +firstFlagP6 + firstFlagP5 + "-" + firstFlagP8 +firstFlagP7 + "-" + firstFlagP9 + firstFlagP10 + "-" + firstFlagP11 + firstFlagP12 + firstFlagP13 + firstFlagP14 + firstFlagP15 + firstFlagP16
    firstFlag = firstFlagNonSensitive.upper() #I ensure the hex values are uppercase, as when I gave flags earlier I used uppercase

    if firstFlag != iQuit: #I created a properly formatted value consisting only of 0 to denote empty partitions and named it iQuit.  That will send it to my error notification.
        print("Regarding partition ", x, ":") #The line printing what the partition number is.
        print()

    if firstFlag == mbrScheme: #This if statement is for the Partition Type GUIDs
        print("This is a MBR Partition Type GUID")
    elif firstFlag == efiScheme:
        print("This is a EFI Partition Type GUID")
    elif firstFlag == biosPartition:
        print("This is a BIOS Partition Type GUID")
    elif firstFlag == microsoftReservedPartition:
        print("This is a Microsoft Reserved Partition Type GUID")
    elif firstFlag == microsoftBasicDataPartition:
        print("This is a Microsoft Basic Data Partition Type GUID")
    elif firstFlag == microsoftLogicalDiskManagerMetadata:
        print("This is a Microsoft Logical Disk Management Metadata Partition Type GUID")
    elif firstFlag == microsoftLogicalDiskManagerData:
        print("This is a Microsoft Logical Disk Management Data Partition Type GUID")
    elif firstFlag == windowsRecoveryEnvironment:
        print("This is a Windows Recovery Environment Partition Type GUID")
    elif firstFlag == linuxFilesystemData:
        print("This is a Linux Filesystem Data Partition Type GUID")
    elif firstFlag == linuxSwap:
        print("This is a Linux Swap Partition Type GUID")
    elif firstFlag == linuxLvm:
        print("This is a Linux Logical Volume Management Partition Type GUID")
    elif firstFlag == appleHfs:
        print("This is an Apple HFS+ Partition Type GUID")
    elif firstFlag == appleUfs:
        print("This is an Apple UFS Partition Type GUID")
    elif firstFlag == eitherOr:
        print("This can be either a Linux partition or a Windows partition type GUID")
    elif firstFlag == iQuit: #If it is iQuit, as mentioned above, it sends the program to the error handling function.
        noMorePartitions()
    else: #As with MBR, there is a substantial number of partition type GUIDS, so I included common ones with a link to a list of all of them.
        print("This is not in the list of partitions known by this program.  \n Please reference http://en.wikipedia.org/wiki/GUID_Partition_Table for more options.")

    #The second flag is the Partition GUID, which is just the hex values.  This uses the same construct as I have been using throughout.
    secondFlagP1 = hexFormat(data, (location + 16))
    secondFlagP2 = hexFormat(data, (location + 17))
    secondFlagP3 = hexFormat(data, (location + 18))
    secondFlagP4 = hexFormat(data, (location + 19))
    secondFlagP5 = hexFormat(data, (location + 20))
    secondFlagP6 = hexFormat(data, (location + 21))
    secondFlagP7 = hexFormat(data, (location + 22))
    secondFlagP8 = hexFormat(data, (location + 23))
    secondFlagP9 = hexFormat(data, (location + 24))
    secondFlagP10 = hexFormat(data, (location + 25))
    secondFlagP11 = hexFormat(data, (location + 26))
    secondFlagP12 = hexFormat(data, (location + 27))
    secondFlagP13 = hexFormat(data, (location + 28))
    secondFlagP14 = hexFormat(data, (location + 29))
    secondFlagP15 = hexFormat(data, (location + 30))
    secondFlagP16 = hexFormat(data, (location + 31))
    secondFlag = secondFlagP16 + secondFlagP15 + secondFlagP14 + secondFlagP13 + secondFlagP12 + secondFlagP11 + secondFlagP10 + secondFlagP9 + secondFlagP8 + secondFlagP7 + secondFlagP6 + secondFlagP5 + secondFlagP4 + secondFlagP3 + secondFlagP2 + secondFlagP1
    print()
    print("The Unique Partition GUID is: "+ secondFlag.upper())
    print()

    #Starting and Ending LBA values for the partition, much the same as in MBR.
    thirdFlagP1 = hexFormat(data, (location + 32))
    thirdFlagP2 = hexFormat(data, (location + 33))
    thirdFlagP3 = hexFormat(data, (location + 34))
    thirdFlagP4 = hexFormat(data, (location + 35))
    thirdFlagP5 = hexFormat(data, (location + 36))
    thirdFlagP6 = hexFormat(data, (location + 37))
    thirdFlagP7 = hexFormat(data, (location + 38))
    thirdFlagP8 = hexFormat(data, (location + 39))
    thirdFlag = "0x" + thirdFlagP8 + thirdFlagP7 + thirdFlagP6 + thirdFlagP5 + thirdFlagP4 + thirdFlagP3 + thirdFlagP2 + thirdFlagP1
    startingLbaGpt = int(thirdFlag, 16)
    print("The starting LBA for this partition is: ", startingLbaGpt)
    print()

    fourthFlagP1 = hexFormat(data, (location + 40))
    fourthFlagP2 = hexFormat(data, (location + 41))
    fourthFlagP3 = hexFormat(data, (location + 42))
    fourthFlagP4 = hexFormat(data, (location + 43))
    fourthFlagP5 = hexFormat(data, (location + 44))
    fourthFlagP6 = hexFormat(data, (location + 45))
    fourthFlagP7 = hexFormat(data, (location + 46))
    fourthFlagP8 = hexFormat(data, (location + 47))
    fourthFlag = "0x" + fourthFlagP8 + fourthFlagP7 + fourthFlagP6 + fourthFlagP5 + fourthFlagP4 + fourthFlagP3 + fourthFlagP2 + fourthFlagP1
    endingLbaGpt = int(fourthFlag, 16)
    print("The ending LBA for this partition is: ", endingLbaGpt)
    print()

    #Attributes will be supported in a future version
    #The attributes could be hidden or read only, etc, but there was no efficient way that I could come up with thus far to parse it

    nameValue = 0
    #The following commented lines are something I was testing (and will continue to test) to make the code shorter and more efficient.
    #partitionName = []

    #while nameValue < 72:
    #    letterHexValue = hexFormat(data, (location + 56 + nameValue))
    #    #letterValue = binascii.unhexlify(letterHexValue)
    #    letterValue = chr(int(letterHexValue, 16))
    #    theValue = letterValue.replace("'", "")
    #    print(letterValue)
    #    nameValue = (nameValue + 2)

    #Using the letterHex function from above, I am passing every other character.  This allows me to ignore every other value, which is a placeholder in ASCII when looking at the hex.
    theNameP1 = letterHex(data, location, 0)
    theNameP2 = letterHex(data, location, 2)
    theNameP3 = letterHex(data, location, 4)
    theNameP4 = letterHex(data, location, 6)
    theNameP5 = letterHex(data, location, 8)
    theNameP6 = letterHex(data, location, 10)
    theNameP7 = letterHex(data, location, 12)
    theNameP8 = letterHex(data, location, 14)
    theNameP9 = letterHex(data, location, 16)
    theNameP10 = letterHex(data, location, 18)
    theNameP11 = letterHex(data, location, 20)
    theNameP12 = letterHex(data, location, 22)
    theNameP13 = letterHex(data, location, 24)
    theNameP14 = letterHex(data, location, 26)
    theNameP15 = letterHex(data, location, 28)
    theNameP16 = letterHex(data, location, 30)
    theNameP17 = letterHex(data, location, 32)
    theNameP18 = letterHex(data, location, 34)
    theNameP19 = letterHex(data, location, 36)
    theNameP20 = letterHex(data, location, 38)
    theNameP21 = letterHex(data, location, 40)
    theNameP22 = letterHex(data, location, 42)
    theNameP23 = letterHex(data, location, 44)
    theNameP24 = letterHex(data, location, 46)
    theNameP25 = letterHex(data, location, 48)
    theNameP26 = letterHex(data, location, 50)
    theNameP27 = letterHex(data, location, 52)
    theNameP28 = letterHex(data, location, 54)
    theNameP29 = letterHex(data, location, 56)
    theNameP30 = letterHex(data, location, 58)
    theNameP31 = letterHex(data, location, 60)
    theNameP32 = letterHex(data, location, 62)
    theNameP33 = letterHex(data, location, 64)
    theNameP34 = letterHex(data, location, 66)
    theNameP35 = letterHex(data, location, 68)
    theNameP36 = letterHex(data, location, 70) #The following line is why I was trying the loop and the list, but as it would not work, I use this method for the time being.
    theName = theNameP1 + theNameP2 + theNameP3 + theNameP4 + theNameP5 + theNameP6 + theNameP7 + theNameP8 + theNameP9 + theNameP10 + theNameP11 + theNameP12 + theNameP13 + theNameP14 + theNameP15 + theNameP16 + theNameP17 + theNameP18 + theNameP19 + theNameP20 + theNameP21 + theNameP22 + theNameP23 + theNameP24 + theNameP25 + theNameP26 + theNameP27 + theNameP28 + theNameP29 + theNameP30 + theNameP31 + theNameP32 + theNameP33 + theNameP34 + theNameP35 + theNameP36
    print("The name of this partition is: ", theName)

   # print(partitionName)

#This is kept for future testing purposes, I was trying to use a flag that would tell me how many partitions were in use, but the values are not where they are supposed to be.
#def partitionEntries(data):
#    partitionEntriesP1 = hexFormat(data, 592)
#    partitionEntriesP2 = hexFormat(data, 593)
#    partitionEntriesP3 = hexFormat(data, 594)
#    partitionEntriesP4 = hexFormat(data, 595)
#    partEntry = "0x" + partitionEntriesP4 + partitionEntriesP3 + partitionEntriesP2 + partitionEntriesP1
#    numberPartitionEntries = int(partEntry, 16)
#    return numberPartitionEntries

def main():
    print("You must enter a valid raw/dd image of a drive.")
    given = input("Enter a path to an image file: ")
    with open(given, "rb") as infile: #Open the file as binary

        data = infile.read(10240) #Reading a section of the file so that excessive memory is not used

        #Validating that the drive is formatted MBR or GPT.
        isValidP1 = hexFormat(data, 510)
        isValidP2 = hexFormat(data, 511)
        isValidDisk = isValidP1 + isValidP2
        if isValidDisk != "55aa":
            badDisk(isValidDisk)

        isMbr = hexFormat(data, 450)
        if isMbr.upper() == "EE": #The flag EE at offset 450 states that it is GPT drive using protected MBR.  This sends the program to the GPT parsing function.

            #Again, more testing for calculating the number of partitions, which allows for the exact amount of the file to be opened
            #numberOfPartitions = partitionEntries(data)
            #infile.close()
            #with open(given, "rb") as infile:
            #    startLocation = numberOfPartitions * 128 + 1024
            #    data = infile.read(startLocation)

            x = 0 #There can only be 128 partitions, so I use a while loop to calculate the partition number and offset
            while x < 128:
                print()
                print()
                gptParse(data, (x * 128 + 1024), x)
                x = x + 1
        else: #If it isn't EE, it is an MBR disk.  The offsets are known, and there are only 4 partitions, so the calls to the mbrParse function written out manually.
            print("Your drive is MBR")
            mbrParse(data, 446, 1)
            print()
            mbrParse(data, 462, 2)
            print()
            mbrParse(data, 478, 3)
            print()
            mbrParse(data, 494, 4)


        #endOfMbr = hexFormat(data, 510) + hexFormat(data, 511)
        #print(endOfMbr)

def badDisk(isValidDisk): #Error catching.  If bytes 510 and 511 are not 55aa, then the drive isn't MBR or GPT
    if isValidDisk != "55aa":
        print("The image you entered is either not a valid raw disk image or does not contain a MBR or GPT.")
        quit()

def noMorePartitions(): #This is merely printing that there are no more partitions and closing the program.  
    print("There are no more active partitions on this disk")
    quit()

main()
