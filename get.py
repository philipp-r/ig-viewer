# Import
import json
from subprocess import call
import os
import time
import sys

# Settings:
follow_list = "users.json"
# cookies for normal account
cookie_file = "cookies.txt"
user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/601.6.17 (KHTML, like Gecko) Version/9.1.1 Safari/601.6.17"
# Cookies for Snoop account
cookie_file2 = "cookies2.txt"
user_agent2 = "Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0"
# Cookies for Snoop account
cookie_file3 = "cookies3.txt"
user_agent3 = "Mozilla/5.0 (Windows NT 6.3; rv:35.0) Gecko/20100101 Firefox/35.0"
# user agent get pics
user_agentGetPics = "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko"



# FUNCTION download html, extract json and parse
def get_instagram_data( cookie_file, ig_username, user_agent, url_params = "" ):
	"download html, extract json and parse"
	# Instagram API
	# I cannot get an own key because of the Instagram terms but found one on the internet
	# Call shell script to get instagram HTML site (http://stackoverflow.com/a/89243) (http://stackoverflow.com/a/17243334)
	call(["wget", "--load-cookies="+cookie_file, "--output-document=html/"+ig_username+".html", "https://www.instagram.com/"+ig_username+"/"+url_params, "-nv", "--referer=https://instagram.com/", "--user-agent="+user_agent ])
	# extract JSON from HTML (http://stackoverflow.com/a/8247835)
	ig_html_file = open("html/"+ig_username+".html").read(200000)
	s1 = ig_html_file.split('<script type="text/javascript">window._sharedData = ')[1]
	ig_json = s1.split(';</script>')[0]
	# Parse JSON
	ig_data = json.loads(ig_json)
	# remove the html file (https://docs.python.org/3/library/os.html#os.remove)
	os.remove("html/"+ig_username+".html")
	return ig_data;



# FUNCTION download pics from Instagram
def get_instagram_pics( ig_data, cookie_file, user_agent ):
	"download pics from Instagram"
	download_all = 0 # will be true later
	# If directory not exists (http://stackoverflow.com/a/8933290)
	if not os.path.isdir("images/"+ig_username):
		# create dir (http://stackoverflow.com/a/273227)
		os.makedirs("images/"+ig_username)
		# setting to download also old pictures
		download_all = 1
	
	# Download pics while download_all is true do-while-loop (http://www.php2python.com/wiki/control-structures.do.while/)
	while True:
		# foreach image item
		for value in ig_data['entry_data']['ProfilePage'][0]['user']['media']['nodes']:
			img_data = value
			# if is not video
			if not img_data['is_video']:
				# convert date int to string (http://stackoverflow.com/a/961638)
				img_data['date']=str(img_data['date'])
				# build filename
				img_filename = img_data['date']+"-"+img_data['id']+".jpg"
				img_filepath = "images/"+ig_username+"/"+img_filename
				# if image not already exists (http://stackoverflow.com/a/8933290)
				if not os.path.exists(img_filepath):
					# download image, cookies/login is not required for this (http://linux.die.net/man/1/wget)
					call(["wget", "--output-document="+img_filepath, img_data['display_src'], "-nv", "--no-cookies", "--referer=https://instagram.com/"+ig_username+"/", "--user-agent="+user_agentGetPics, "--no-check-certificate"])
					# ImageOptim (https://imageoptim.com/command-line.html)
					# call(["/Applications/ImageOptim.app/Contents/MacOS/ImageOptim", img_filepath])
					# Add symbolic link to recent images (http://www.tutorialspoint.com/python/os_symlink.htm)
					# not working with subdirectory for "recent"
					os.symlink(img_filepath, "recent-"+img_data['date']+"-"+ig_username+"-"+img_data['id'])

		# end if download_all is false
		if not download_all:
			break
		# if download_all is true
		else:
			# check if we have a next page & download from there
			if ig_data['entry_data']['ProfilePage'][0]['user']['media']['page_info']['end_cursor']:
				####
				#### BUG
				#### This will lead to a loop after all images were downloaded
				####
				next_page_url = "?max_id="+ig_data['entry_data']['ProfilePage'][0]['user']['media']['page_info']['end_cursor']
				# get Instagram JSON with function
				ig_data = get_instagram_data( cookie_file, ig_username, user_agent, next_page_url )
				#break
			else:
				break
	return;







if len(sys.argv) > 1:
	parsed_user_list = {}
	sys.argv.remove('get.py');
	parsed_user_list['follow'] = sys.argv
else:
	# Read follow list (http://www.php2python.com/wiki/function.file-get-contents/)
	json_user_list = open(follow_list).read(2000)
	# parse JSON (http://docs.python-guide.org/en/latest/scenarios/json/)
	parsed_user_list = json.loads(json_user_list)


# TO DO remove recent images


# foreach user (http://www.php2python.com/wiki/control-structures.foreach/)
for value in parsed_user_list['follow']:
	# set username variable
	ig_username = value
	# get Instagram JSON with function
	ig_data = get_instagram_data( cookie_file, ig_username, user_agent, "" ) # use first cookie file

	# if user has hd profile pic
	if 'profile_pic_url_hd' in ig_data['entry_data']['ProfilePage'][0]['user'].keys():
		# Extract image name from URL
		profile_pic_filename = ig_data['entry_data']['ProfilePage'][0]['user']['profile_pic_url_hd'].split('/')[5]
		# If directory not exists (http://stackoverflow.com/a/8933290)
		if not os.path.isdir("profilepic/"+ig_username):
			# remove size from URL
			profile_pic_url = ig_data['entry_data']['ProfilePage'][0]['user']['profile_pic_url_hd'].replace("s320x320/", "")
			# create dir (http://stackoverflow.com/a/273227)
			os.makedirs("profilepic/"+ig_username)
			# Download picture
			call(["wget", "--output-document="+"profilepic/"+ig_username+"/"+profile_pic_filename, profile_pic_url, "-nv", "--no-cookies", "--referer=https://instagram.com/"+ig_username+"/", "--user-agent="+user_agent, "--no-check-certificate"])
			os.symlink("profilepic/"+ig_username+"/"+profile_pic_filename, "recent-"+str(time.time())+"-"+ig_username+"-profilepic")
		else:
			# check if profile pic not already exists
			if not os.path.exists("profilepic/"+ig_username+"/"+profile_pic_filename):
				# remove size from URL
				profile_pic_url = ig_data['entry_data']['ProfilePage'][0]['user']['profile_pic_url_hd'].replace("s320x320\/", "")
				# Download picture
				call(["wget", "--output-document="+"profilepic/"+ig_username+"/"+profile_pic_filename, profile_pic_url, "-nv", "--no-cookies", "--referer=https://instagram.com/"+ig_username+"/", "--user-agent="+user_agent, "--no-check-certificate"])
				os.symlink("profilepic/"+ig_username+"/"+profile_pic_filename, "recent-"+str(time.time())+"-"+ig_username+"-profilepic")
	# if user has profile pic
	elif 'profile_pic_url' in ig_data['entry_data']['ProfilePage'][0]['user'].keys():
		# Extract image name from URL
		profile_pic_filename = ig_data['entry_data']['ProfilePage'][0]['user']['profile_pic_url'].split('/')[4]
		# If directory not exists (http://stackoverflow.com/a/8933290)
		if not os.path.isdir("profilepic/"+ig_username):
			# remove size from URL
			profile_pic_url = ig_data['entry_data']['ProfilePage'][0]['user']['profile_pic_url'].replace("s150x150/", "")
			# create dir (http://stackoverflow.com/a/273227)
			os.makedirs("profilepic/"+ig_username)
			# Download picture
			call(["wget", "--output-document="+"profilepic/"+ig_username+"/"+profile_pic_filename, profile_pic_url, "-nv", "--no-cookies", "--referer=https://instagram.com/"+ig_username+"/", "--user-agent="+user_agent, "--no-check-certificate"])
			os.symlink("profilepic/"+ig_username+"/"+profile_pic_filename, "recent-"+str(time.time())+"-"+ig_username+"-profilepic")
		else:
			# check if profile pic not already exists
			if not os.path.exists("profilepic/"+ig_username+"/"+profile_pic_filename):
				# remove size from URL
				profile_pic_url = ig_data['entry_data']['ProfilePage'][0]['user']['profile_pic_url'].replace("s150x150\/", "")
				# Download picture
				call(["wget", "--output-document="+"profilepic/"+ig_username+"/"+profile_pic_filename, profile_pic_url, "-nv", "--no-cookies", "--referer=https://instagram.com/"+ig_username+"/", "--user-agent="+user_agent, "--no-check-certificate"])
				os.symlink("profilepic/"+ig_username+"/"+profile_pic_filename, "recent-"+str(time.time())+"-"+ig_username+"-profilepic")


	# If user has images (http://stackoverflow.com/q/1602934)
	if ig_data['entry_data']['ProfilePage'][0]['user']['media']['nodes']:
		print "User is public or has access with cookie_file"
		# get pics with function
		get_instagram_pics( ig_data, cookie_file, user_agent  )

	# user has no images or private
	else:
		# get Instagram JSON with cookie_file2
		ig_data = get_instagram_data( cookie_file2, ig_username, user_agent2, "" ) # use alternative cookie file
		# If user now has images
		if ig_data['entry_data']['ProfilePage'][0]['user']['media']['nodes']:
			print "Has access with cookie_file2"
			# get pics with function
			get_instagram_pics( ig_data, cookie_file2, user_agent2  )
	
		# user has no images or private
		else:
			# get Instagram JSON with cookie_file3
			ig_data = get_instagram_data( cookie_file3, ig_username, user_agent3, "" ) # use alternative 3 cookie file
			# If user now has images
			if ig_data['entry_data']['ProfilePage'][0]['user']['media']['nodes']:
				print "Has access with cookie_file3"
				# get pics with function
				get_instagram_pics( ig_data, cookie_file3, user_agent3  )
		
			# user has no images or private
			else:
				print "-------------- \nUser "+ig_username+" is PRIVATE or has no images \n-------------- "
		