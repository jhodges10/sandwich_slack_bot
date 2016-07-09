import sys, subprocess,time,os
from fuzzywuzzy import fuzz,process

dropbox_path = '/Users/sanvidpro/Dropbox/'
server_directory = '/Volumes/Sandwich/projects/'
shots_folder = '/editorial/_to editorial/shots/'

CRF_VALUE = '19' # controls the quality of the encode
PROFILE = 'high422' # h.264 profile
PRESET = 'fast' # encoding speed:compression ratio
TUNE = 'film' # tune setting
FFMPEG_PATH = '/usr/local/bin/ffmpeg' # path to ffmpeg bin
THREADS = '8' # of threads to use
SCALER_1080 = "scale=-1:1080, scale=trunc(iw/2)*2:1080" # 1080 Scale settings

def encode_1080(video,fn,shot_dir,db_dir):
    output = dropbox_path + str(db_dir) + "/shots/" + fn + "-1080.mov"
    print output
    if not os.path.exists(output):
	    try:
	        subprocess.call([FFMPEG_PATH, '-i', video, '-c:v', 'libx264', '-tune', TUNE, '-pix_fmt', 'yuv420p', '-preset', PRESET, '-profile:v', PROFILE, '-vf', SCALER_1080, '-crf', CRF_VALUE, '-c:a', 'libfdk_aac', '-b:a', '192k', '-threads', THREADS, output])
	        return dropbox_output
	    except:
	        print "That directory didn't exist or something else happened"
    else:
        print "This file already exists but the loop will continue onto the next one."

def return_projects():
    projects = os.listdir(server_directory)
    print (projects)
    return projects
    
def fuzzy_dropbox(project):
    directory_listing = os.listdir(dropbox_path)
    dir_temp = process.extract(project,directory_listing,limit=1)
    dropbox_output_directory = dir_temp[0]
    dropbox_output_directory = dropbox_output_directory[0]
    return dropbox_output_directory

def fuzzy_server(project):
	directory_listing = os.listdir(server_directory)
	dir_temp = process.extract(project,directory_listing,limit=1)
	cur_project_directory= dir_temp[0]
	cur_project_directory = cur_project_directory[0]
	return cur_project_directory

def setup():
	return_projects()
	cur_project = str(raw_input('Type the name of the project to encode all shots for:'))
	print 'This is what you typed: ' +str(cur_project)
	db_dir = fuzzy_dropbox(cur_project)
	server_dir = fuzzy_server(cur_project)
	print 'The Dropbox directory to traverse is ' +db_dir
	print 'The server directory to traverse is ' +server_dir
	if raw_input('Would you like to continue? y/n') == 'y':
            encode_loop(server_dir,db_dir)
        else:
            print "Guess we're done here."
        
def encode_loop(server_dir,db_dir):
	for each_folder in os.listdir(server_directory+server_dir+shots_folder):
		print each_folder
        for each_video in os.listdir(each_folder):
			print each_video
			each_video = fn
			db_dir = db_dir + each_folder

#			encode_1080(each_video,fn,shot_dir,db_dir)
# we will then call the encode function on each one

setup()
