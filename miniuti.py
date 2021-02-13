#!/usr/bin/python3

DEFAULT_LOGFILE="local.log"
DEFAULT_VERBOSELEVEL=2
DEFAULT_SHOWTHRESHOLD=False
DEFAULT_WITHTIMEINFO=True
DEFAULT_DATETIMESEPARATOR=""
DEFAULT_BIGFILE_READ_CHUNKSIZE=100000

import shutil
import os
from datetime import datetime


# ================================= IMPLEMENTATION =================================


def file_addneededslash2path(path):
	if path:
		if not path.endswith("/"):
			path+="/"
	return path


def file_pathwnoext(filepath):
	return Path(filepath).stem


def file_ext(filepath):
	return Path(filepath).suffix


def file_delfilesafe(hfile):
	if os.path.isfile(hfile):
		os.remove(hfile)
		return True
	else: return False


def file_readfilesafe(cffilenam,aslist=False):
#Returns the whole content of a file, as a list of lines if aslist is True, as a string otherwise (default is False).
#If file doesn't exist, function returns an empty list or ""
	retstr=""
	retlines=[]
	if os.path.isfile(cffilenam):
		fil = open(cffilenam, "r")
		if aslist:retlines = fil.readlines()
		else: retstr = fil.read()
		fil.close
	if aslist: return retlines
	else: return retstr


def file_writefilesafe(cffilenam,filecontent,overw=False):
#writes filecontent to a file, without overwritting it	if overw is set to False (default behaviour).
#Returns True if file hase been written or overwrite.
	hwritten=False	
	if not os.path.isfile(cffilenam) or overw:
		fil = open(cffilenam, "w")
		hwritten=True
		fil.write(filecontent)
		fil.close
	return hwritten

def file_diriterate(dirpath,callbackfun,filecontentaslist=False): # Iterates in all files inside a directory and for each file opens it and calls a callback function to process it. The callback function must accept 4 arguments: filecounter, filnam, filecontent and filecontentaslist
	cc=0
	for lfilnam in os.listdir(dirpath):
		cc+=1
		filpath=dirpath+"/"+lfilnam
		lfilecontent=file_readfilesafe(filpath,aslist=False)
		callbackfun(filecounter=cc,filnam=lfilnam,filecontent=lfilecontent,filecontentaslist=filecontentaslist)


def file_append2file(hfilenam,hfilecontent,backupfirst=False): # The updated file gets written in an (hopefully) atomic operation. If requested (default off) a backup copy of the non-yet-updated file is made.
	#print("APPEND2FILE NEW!")
	if backupfirst:
		shutil.copyfile(hfilenam,hfilenam+".append2file.bak")
	fil = open(hfilenam, "a+")
	fil.write(hfilecontent)
	fil.close


def file_readbigfilelines(file_name,chunk_size=DEFAULT_BIGFILE_READ_CHUNKSIZE,callback=None,return_whole_chunk=False):
	"""
	read file line by line regardless of its size
	:param file_name: absolute path of file to read
	:param chunk_size: size of data to be read at at time
	:param callback: callback method, prototype ----> def callback(data, eof, file_name)
	:return:
	"""
	def read_in_chunks(file_obj, chunk_size=5000):
		"""
		https://stackoverflow.com/a/519653/5130720
		Lazy function to read a file 
		Default chunk size: 5000.
		"""
		while True:
			data = file_obj.read(chunk_size)
			if not data:
				break
			yield data
	if not callback:
		return False
	fp = open(file_name)
	data_left_over = None
	# loop through characters
	for chunk in read_in_chunks(fp, chunk_size=chunk_size):
		# if uncompleted data exists
		if data_left_over:
			# print('\n left over found')
			current_chunk = data_left_over + chunk
		else:
			current_chunk = chunk
		# split chunk by new line
		lines = current_chunk.splitlines()
		# check if line is complete
		if current_chunk.endswith('\n'):
			data_left_over = None
		else:
			data_left_over = lines.pop()
		if return_whole_chunk:
			callback(data=lines, eof=False, file_name=file_name)
		else:
			for line in lines:
				callback(data=line, eof=False, file_name=file_name)
				pass
	if data_left_over:
		current_chunk = data_left_over
		if current_chunk is not None:
			lines = current_chunk.splitlines()
			if return_whole_chunk:
				callback(data=lines, eof=False, file_name=file_name)
			else :
				for line in lines:
					callback(data=line, eof=False, file_name=file_name)
					pass
	callback(data=None, eof=True, file_name=file_name)


class minimalobj():
	def __init__(this,name=""):
		this.verbose=10
		this.msg=""
		this.logfile=DEFAULT_LOGFILE
		this.longname=name
		this.name=name
		this.objtype="genericobj"



def time_getcurrtime_str(nospacechar="",uptoseconds=False):
	retval=str(datetime.now())
	if uptoseconds:
		retval=retval[:-7]
	if nospacechar:
		retval=retval.replace(" ",nospacechar)
	return retval


def msg_cprint(stri,logfile=DEFAULT_LOGFILE,cond=True,dontprint=False,recycleline=False,print2log=True):
	'''
	Conditionally prints stri when cond is True.
	The same gets written to log file if logfile. Returns the printed string+"\n"
	'''
	if cond:
		if not dontprint:
			if recycleline:
				print(stri,end="\r")
			else:
				print(stri)
			if logfile and print2log:
				file_append2file(logfile,stri+"\n")
		return stri+"\n"

cprint=msg_cprint


def msg_cprintbold(stri,cond=True,linechar="_",linecharpos="updn",linecharlen=-1,linechartitle="",logfile=DEFAULT_LOGFILE,print2log=True,dontprint=False,recycleline=False):
	'''
	When cond is True, conditionally prints stri preceded and followed in the former and following line by a bar of linechars the same length of the string, with optionally a title linechartitle inserted inside the top bar.
	The same gets written to log file if logfile. Returns the printed string without the top and bottom bars+"\n"
	'''
	if cond:
		linechars=linechar
		linecharpatternlen=len(linechar)
		linecharsno=0
		stri2=""
		stris=stri.split("\n")
		for strng in stris:
			strnglen=len(strng)
			if linecharsno<strnglen: linecharsno=strnglen
			stri2+=strng+"\n"
		stri2=stri2[:-1]
		linecharsmax=linecharlen
		if linecharlen<0:
			linecharsmax=int(linecharsno/linecharpatternlen)+3
		linecharsmax=int((linecharsmax/2)/linecharpatternlen)-1
		for x in range (0,linecharsmax): linechars+=linechar
		linecharsup=linechars+linechartitle+linechars
		linecharsdn=linechars+linechars
		if linechar: linecharsdn+=linechar*len(linechartitle)
		str2print=""
		if "up" in linecharpos:
			str2print=linecharsup+"\n"
			if linechar=="_" or linechar==".":
				str2print+="\n"
			else:
				str2print="\n"+str2print
		else:
			str2print="\n"+str2print
		str2print+=stri2
		if "dn" in linecharpos:
			str2print=str2print+"\n"+linecharsdn
		return msg_cprint(str2print,logfile=logfile,print2log=print2log,dontprint=dontprint,recycleline=recycleline)

cprintbold=msg_cprintbold


def msg(obj,text,withobjtype=True,objtypeendlinechar=":",withtimeinfo=DEFAULT_WITHTIMEINFO,forceverboselevel=-1,threshold=1,forceverbose=False,prefx="",initialtab="    ",linechar="",linecharpos="updn",linecharlen=-1,linechartitle="",spaced=True,recycleline=False,showthreshold=DEFAULT_SHOWTHRESHOLD,logfile=DEFAULT_LOGFILE,print2log=True,dontprint=False,noobjname="",objnamefilter=[]): # If linechar != "" prints with cprintbold, with the desider linechar
	if forceverboselevel>-1:
		lverboselevel=forceverboselevel
	if not obj:
		obj=minimalobj()
		obj.longname=noobjname
		if forceverboselevel>-1:
			lverboselevel=forceverboselevel
		else:
			try:
				lverboselevel=DEFAULT_VERBOSELEVEL
			except:
				lverboselevel=100
	else:
		if "verbose" in obj.__dict__:
			lverboselevel=obj.verbose
		elif  "verboselevel" in obj.__dict__:
			lverboselevel=obj.verboselevel
		else:
			lverboselevel=forceverboselevel
	if lverboselevel<threshold:
		if not forceverbose:
			return
	goprint=True
	if objnamefilter:
		goprint=False
		for itm in objnamefilter:
			if itm in obj.longname:
				goprint=True
	if goprint:
		obj.msg=text
		llogfile=logfile
		if hasattr(obj,"logfile"):
			llogfile=obj.logfile
		str2print=""
		internalprefx=""
		if withtimeinfo:
			internalprefx=internalprefx+"LT"+time_getcurrtime_str(nospacechar=DEFAULT_DATETIMESEPARATOR,uptoseconds=False)
		initialcr=""
		if (not withobjtype) and (text.startswith("\n")):
			initialcr="\n"
		str2prints=text.split("\n")
		for strng in str2prints:
			if strng!="":
				if internalprefx:
					str2print+=prefx+initialtab+"["+internalprefx+"] "+strng+"\n"
				else:
					str2print+=prefx+initialtab+strng+"\n"
		str2print=str2print[:-1]
		if withobjtype:
			midfix=""
			if obj.longname:
				llongname=obj.longname
				llongname=str_getobjlongname(obj)
				midfix=llongname+":\n"
				midfix=llongname+f"{objtypeendlinechar}\n"
			str2print=prefx+midfix+str2print
		if showthreshold: str2print="[T"+str(threshold)+"V"+str(lverboselevel)+"] "+str2print
		str2print=initialcr+str2print
		if not linechar:
			if withobjtype:
				if spaced:
					str2print="\n"+str2print
			return msg_cprint(str2print,logfile=llogfile,print2log=print2log,dontprint=dontprint,recycleline=recycleline)
		else:
			return msg_cprintbold(str2print,linechar=linechar,linecharpos=linecharpos,linecharlen=linecharlen,linechartitle=linechartitle,logfile=llogfile,print2log=print2log,dontprint=dontprint,recycleline=recycleline)


def msg0(text="",obj=None,withobjtype=True,objtypeendlinechar=":",withtimeinfo=DEFAULT_WITHTIMEINFO,forceverboselevel=-1,threshold=1,forceverbose=False,prefx="",initialtab="    ",linechar="",linecharpos="updn",linecharlen=-1,linechartitle="",spaced=True,recycleline=False,showthreshold=DEFAULT_SHOWTHRESHOLD,logfile=DEFAULT_LOGFILE,print2log=True,dontprint=False,noobjname="",objnamefilter=[]): # If linechar != "" prints with cprintbold, with the desider linechar
	# print("AAA")
	return msg(obj,text,withobjtype=withobjtype,objtypeendlinechar=objtypeendlinechar,withtimeinfo=withtimeinfo,forceverboselevel=forceverboselevel,threshold=threshold,forceverbose=forceverbose,prefx=prefx,initialtab=initialtab,linechar=linechar,linecharpos=linecharpos,linecharlen=linecharlen,linechartitle=linechartitle,spaced=spaced,recycleline=recycleline,showthreshold=showthreshold,logfile=logfile,print2log=print2log,dontprint=dontprint,noobjname=noobjname,objnamefilter=objnamefilter)


# ================================= TESTS =================================


if __name__=="__main__":
	pass
	msg0("Ciao!",linechar="-",linechartitle="Test")



