# sudo apt install python3-pip
# sudo pip3 install eyed3

import sys
import inspect
import glob
import os
import subprocess
import io
import re
import time
import eyed3
from eyed3.id3.frames import ImageFrame
from logging import getLogger
import smtplib, ssl
from PIL import Image
import base64



#when did I last update this file
last_update = "28 November 2023"

#history
#9 June 2023 - added flags for -count -remove -replace -help
#10 June - added print out of m4b files left to convert 
#10 June - add -show flag to print out m4b files found
#23 September - added short code command line arg. Move help to function
#28 November - added check for ffmpeg location
#29 November - added timer



# colors for printing to console
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def clear_console(): #clear the console screen
    command = "clear"
    #determine the OS
    if os.name in ("nt", "dos"):  #if matches Windows
        command = "cls"
    os.system(command)
    
def print_header ():
    print(f"{bcolors.HEADER}{bcolors.BOLD}")
    print("       _ _  _      ___              ____ ")
    print("  _ __| | || |__  |_  )  _ __  _ __|__ / ")
    print(" | '  \_  _| '_ \  / /  | '  \| '_ \|_ \ ")
    print(" |_|_|_||_||_.__/ /___| |_|_|_| .__/___/ ")
    print("                              |_|        ")
    print(f"{bcolors.OKBLUE} Vesion: " + last_update + f"{bcolors.ENDC}")
    print("")

def getBookInfo(file, number_of_m4b, number_of_m4b_remaining): #run the ffmpeg command on the m4b file and pipe the output to a text file
    if display_function_name:
        print_function_name(inspect.stack()[0][3])

    command = ffmpeg_path + ' -i "' + file + '" -hide_banner > BookInfo.txt 2>&1'
    process = subprocess.Popen(command, stdout = subprocess.PIPE, shell = True)
    
    percent_completed = round(abs(int(number_of_m4b_remaining)/int(number_of_m4b)-1)*100,1)

    #build the message so we can get the string length which allows us to get the ==== underline to the same length
    message = (str(number_of_m4b_remaining) + " of " + str(number_of_m4b) + " files remaining (" + str(percent_completed) + "% completed)")
    underline_txt = ""

    #create the === underline to the same numnber of characters as the message
    for x in message:
        underline_txt = underline_txt + "="

    print("")
    print (padding + message)
    print(padding + underline_txt)
    print (padding + "Parsing audio from : " + file)
    time.sleep(10) # sleep to allow the text file to be written


def getBookInfoContents(): #read the contents of the m4b information file and return the information
    if display_function_name:
        print_function_name(inspect.stack()[0][3])
        
    sleeping(10) # wait for the info file to be created
    bookInfoFile = open(bookInfoFileLocation, "rt") 
    bookInfoContents = bookInfoFile.read()
    bookInfoFile.close()
    return bookInfoContents


def get_cover_art(dir_path, file_name, m4b_file): # pull the cover art from the file
    if display_function_name:
        print_function_name(inspect.stack()[0][3])

    image_name = os.path.join(dir_path + '/cover.jpg') # build the path to save the cover art to

    if (os.path.exists(image_name)):
        print(padding + "There is a cover.jpg file in the folder, we will use this.")

    if not (os.path.exists(image_name)):
        print(padding + "No cover in folder. Will check the .m4b file for one.")
    
        #create cover.jpg from the .m4b file
        FNULL = open(os.devnull, 'w') # open null to redirect contents of the ffmpeg process
        subprocess.call([ffmpeg_path, '-i', m4b_file, image_name], stdout=FNULL, stderr=subprocess.STDOUT) #command to save the cover art
        if (os.path.exists(image_name)):
            print(padding + "There is a cover image in the m4b, we will use this.")
    
    #check if a cover.jpg was created
    if not (os.path.exists(image_name)):
        print(padding + "There was no cover.jpg supplied or obtained from the .m4b file. Please resolve.\n")
        print(padding + "Let's use the generic image.")
        create_missing_cover_art()        

    return (image_name)


def create_missing_cover_art(dir_path)
    if display_function_name:
        print_function_name(inspect.stack()[0][3])

    cover_art_standin_image = "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"
    pilImage.save(dir_path + '/cover.jpg')




def tag_cover_art(output_path):
    if display_function_name:
        print_function_name(inspect.stack()[0][3])
        
    cover_art_image = output_path + "/cover.jpg"
    pattern = os.path.join(output_path, '*.mp3')  # find mp3 files to tag
    file_list = [file for file in glob.glob(pattern, recursive = True)]

    for file in file_list:

        audiofile = eyed3.load(file)
        if (audiofile.tag == None):
            audiofile.initTag()

        audiofile.tag.images.set(ImageFrame.FRONT_COVER, open(cover_art_image,'rb').read(), 'image/jpeg')
        audiofile.tag.save(version=eyed3.id3.ID3_V2_3)


def sleeping(length): #why not?
    if display_function_name:
        print_function_name(inspect.stack()[0][3])
        
    time.sleep(length)


def parseBook(dir_path, file_name, file,replace_files):
    if display_function_name:
        print_function_name(inspect.stack()[0][3])
        

    #print ("Reading m4b file.")
    bookInfoContents = 	getBookInfoContents()
    rex = re.compile(r"(Chapter #\d+:\d+): start ([\d\.]+), end ([\d\.]+)")

    cover_art_image = get_cover_art (dir_path, file_name, file)

    
    numberOfChapters = 1 #count the number of Chapters in the book. Starting from 1 as there has to be at least 1 chapter
    for chapter in rex.findall(bookInfoContents):
        numberOfChapters +=1
    print(padding + 'There are ' + str(numberOfChapters-1) + ' chapters in this book')
    print(padding + '')
    

    #====================================================================================================================
    #if there is only 1 chapter in the m4b
    if numberOfChapters-1 == 0:

        start_time = time.time()

        print(padding + 'There are ' + str(numberOfChapters-1) + ' defined chapters in this m4b, so we will output to a single mp3')
        output_path = os.path.join(dir_path + "/", file_name + '.mp3') #build the file name for each chapter to be saved as mp3

        #print (f"os path: {os.path.exists(output_path)}")
        #print (f"replace_files: {replace_files}")
        #exit()

        # if there are already mp3s which will get overwritten and you did not pass the "-replace" then exit
        if os.path.exists(output_path) and not replace_files:
            print (padding + ".mp3 files exist in destination folder and you don't want to over write.")
            exit()

        # Convert
        print(padding + "Converting \033[1m" + file + "\033[0m")	#print information on current chapter
        FNULL = open(os.devnull, 'w') # open null to redirect contents of the ffmpeg process
        #wite out the mp3
        # -y to overwrite without prompt
        
        subprocess.call([ffmpeg_path, '-y', '-i', file, '-i', cover_art_image, '-acodec', 'libmp3lame', output_path], stdout=FNULL, stderr=subprocess.STDOUT)
        
        end_time = time.time()
        elapsed_time = round(end_time - start_time,2)
        print(padding + 'Execution time:', elapsed_time, 'seconds')


    #====================================================================================================================

    #====================================================================================================================
    #if there are more than 1 chapter in the audiobook
    if numberOfChapters-1 > 0:
        # get the required information on the book and chapter then loop and write each chapter to disk at the same location as the m4b file
        counter = 1

        start_time = time.time()

        for chapter, start, end in rex.findall(bookInfoContents): #use the regex to find each chapter information from the bookContents information
                      
            #bookChapterNumber = chapter.split(':',1) #dont need to use the chapter number from the information as the counter does this for us
            chapterStartTime = start #chapter start time from the m4b information
            chapterEndTime = end #chapter end time from the m4b information

            #pad the file number to allow easy sorting on playback device
            
            #less than 10 chapters
            if numberOfChapters <10:
                fileNumberPrefix = ('0' + str(counter))

            #more than 10 chapters and less than 100
            if numberOfChapters <100 and counter <10:
                fileNumberPrefix = ('0' + str(counter))
            
            if numberOfChapters <100 and counter <100 and counter > 9:
                fileNumberPrefix = ('' + str(counter))

            #more than 100 chapters
            if numberOfChapters >100 and counter <10:
                fileNumberPrefix = ('00' + str(counter))
            
            if numberOfChapters >100 and counter <100 and counter > 9:
                fileNumberPrefix = ('0' + str(counter))

            if numberOfChapters >100 and counter <100 and counter > 99:
                fileNumberPrefix = ('' + str(counter))

   		
            output_path = os.path.join(dir_path + "/", fileNumberPrefix + ' - ' + file_name + '.mp3') #build the file name for each chapter to be saved as mp3

            # if there are already mp3s which will get overwritten and you did not pass the "-replace" then exit
            if os.path.exists(output_path) and not replace_files:
                print (padding + ".mp3 files exist in destination folder and you don't want to over write.")
                exit()

        	# Convert
            chaptersRemaining = numberOfChapters - counter #count how many chapters are left to convert
            percent_completed = round(abs(int(chaptersRemaining+1)/int(numberOfChapters)-1)*100,1)

            print(padding + 'Converting chapter ' + fileNumberPrefix + ' from [' + file_name + '] -//- (' + str(chaptersRemaining) + ' remaining / ' + str(percent_completed) + '%)')	#print information on current chapter
            FNULL = open(os.devnull, 'w') # open null to redirect contents of the ffmpeg process
			#wite out the mp3
            #quiet log display             
            # -y to overwrite without prompt
            subprocess.call([ffmpeg_path, '-y', '-ss', chapterStartTime, '-to', chapterEndTime, '-i', file, '-i', cover_art_image, '-acodec', 'libmp3lame', output_path], stdout=FNULL, stderr=subprocess.STDOUT)
  
            counter +=1

        end_time = time.time()
        elapsed_time = round(end_time - start_time,2)
        print(padding + 'Execution time:', elapsed_time, 'seconds')


        #====================================================================================================================



def removeFile(bookFileLocation): #remove the file passed in bookFileLocation
    if display_function_name:
        print_function_name(inspect.stack()[0][3])
        
    print(padding + 'Removing: ' + bookFileLocation)
    os.remove(bookFileLocation)
    time.sleep(15) # sleep to allow the file to be removed


def print_function_name(funcation_name):
    print("Function: " + funcation_name)


def display_help():
    print ("Usage : python3 m4b2mp3.py -count -remove -replace -help")
    print (" -c [-count] = count the number of m4b files and exit")
    print (" -r [-remove] = remove the m4b file after convert")
    print (" -o [-overwrite] = overwrite the mp3 files if they already exist")
    print (" -s [-show] = list the m4b files found")
    print (" -h [-help] = display this message\n")
    sleeping(5)


def check_for_ffmpeg():
    if display_function_name:
        print_function_name(inspect.stack()[0][3])

    if not os.path.exists(ffmpeg_path):
        print ("Error : ffmpeg_path not found : " + ffmpeg_path + " does not exist.")
        print ("")
        exit()


#==========================
#set global variables

#user update this path to ffmeg
ffmpeg_path = "/usr/bin/ffmpeg" # location of ffmpeg binary
#==========================================================

bookInfoFileLocation = "BookInfo.txt" # location file to store the information about each audiobook
display_function_name = False
base_dir = os.getcwd() # what directory contains the audiobooks - the current directory
padding = "  "


def main():
    clear_console()
    print_header()

    check_for_ffmpeg()


    #if no command line arguments passed display the help message
    
    if len(sys.argv) < 2:
        display_help()

    # (in main)
    # Suppress WARNINGS generated by eyed3
    getLogger().setLevel('ERROR')

    if display_function_name:
        print_function_name(inspect.stack()[0][3])
    
    #Print("cmd entry:", sys.argv)
    #set the pass variable default incase they are not passed
    replace_files = False
    remove_m4b = False
    count_only = False
    show_m4b = False

    for i in range(1, len(sys.argv)):
        
        #print('argument:', i, 'value:', sys.argv[i])
        if sys.argv[i] == "-help" or sys.argv[i] == "-h" or sys.argv[i] == "":
            display_help()            
            exit()
        
        if sys.argv[i] == "-count" or sys.argv[i] == "-c":
            count_only = True

        if sys.argv[i] == "-overwrite" or sys.argv[i] == "-o":
            replace_files = True
        
        if sys.argv[i] == "-remove" or sys.argv[i] == "-r":
            remove_m4b = True

        if sys.argv[i] == "-show" or sys.argv[i] == "-s":
            show_m4b = True

        
    if not count_only:        
        if replace_files and remove_m4b:
            print(padding + "I will " + f"{bcolors.FAIL}replace " + f"{bcolors.ENDC}any existing .mp3's and will " + f"{bcolors.FAIL}remove" + f"{bcolors.ENDC} the .m4b")
        
        if replace_files and not remove_m4b:
            print(padding + "I will " + f"{bcolors.FAIL}replace " + f"{bcolors.ENDC}any existing .mp3's and will " + f"{bcolors.OKGREEN}keep" + f"{bcolors.ENDC} the .m4b")

        if not replace_files and remove_m4b:        
            print(padding + "I will " + f"{bcolors.OKGREEN}not replace " + f"{bcolors.ENDC}any existing .mp3's and will " + f"{bcolors.FAIL}remove" + f"{bcolors.ENDC} the .m4b")


        if not replace_files and not remove_m4b:        
            print(padding + "I will " + f"{bcolors.OKGREEN}not replace " + f"{bcolors.ENDC}any existing .mp3's and will " + f"{bcolors.OKGREEN}keep" + f"{bcolors.ENDC} the .m4b")


    pattern = os.path.join(base_dir, '**', '*.m4b')  # start at the base_dir (defined in global variables section) and find all m4b files for conversion
    file_list = [file for file in glob.glob(pattern, recursive = True)]

    number_of_m4b = 0
    for file in file_list:
        number_of_m4b = number_of_m4b + 1

    if number_of_m4b == 0:
        print (padding + "No m4b files found. Please check the contents of the directory.\n")
    else:
        print (padding + "I found " + str(number_of_m4b) + " m4b file(s) to convert\n")
        
    if show_m4b:
        for file in file_list:
            print (padding + file)

    if count_only: #if the -count flag was passed only count the number of m4b and exit
        exit()

    number_of_m4b_remaining = number_of_m4b

    for file in file_list: #for each file to be converted

        getBookInfo(file,number_of_m4b, number_of_m4b_remaining) #get the m4b information
        dir_path, file_name = os.path.split(file) # split the m4b file location into path and filename
        file_name = os.path.splitext(file_name)[0] # Drop the file extension so we can use mp3
        
        parseBook(dir_path, file_name, file,replace_files) # convert the book to mp3
        removeFile(bookInfoFileLocation) # remove the text information file

        if remove_m4b:
            removeFile(file) # remove the m4b file

        sleeping(10) # sleep for 10 seconds
        number_of_m4b_remaining = number_of_m4b_remaining - 1
        #does this work?
        #tag_cover_art(file_name) #tag the mp3s with the cover art already extracted from the m4b

    
    print ("")
    print(padding + "Conversion complete...")
    print ("")

if __name__ == "__main__":
    main()
