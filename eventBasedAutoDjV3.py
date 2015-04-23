from Tkinter import *
from eventBasedAnimationClass import EventBasedAnimationClass
import soundcloud
import mp3play
import urllib
import ImageTk
import time
import Image

client = soundcloud.Client(client_id='b3023702c1d1c27b03f0c380d145dc23')
#needed for soundcloud api use

class PlayerTrack(object):

	def __init__(self,url):
		self.url = url 
		self.track = client.get('/resolve', url=self.url)
		self.title = self.track.title
		self.isPlaying = False
		self.duration = 0
		self.user = client.get('/users/'+str(self.track.user_id))

	def download(self):
		
		streamUrl = client.get(self.track.stream_url, allow_redirects=False)
		f = open(self.title + '.mp3','wb') #opens and saves mp3 from stream location
		f.write(urllib.urlopen(streamUrl.location).read())
		f.close()
		self.getArtwork()

	def play(self):#takes in width and height of now playing window

		self.clip = mp3play.load(self.title+'.mp3')
		self.duration = self.clip.milliseconds
		self.clip.play()

	def drawNowPlaying(self,canvas,width,height):

		self.progressBarHeight = 40
		canvas.create_text(width/2,height/2-self.progressBarHeight,text=self.title,
			fill = self.textColor)
		canvas.create_image((width/2),(height/2)-10-self.progressBarHeight,
			image=self.artWork,anchor=S)

	def pause(self):
		self.clip.pause()

	def getArtwork(self):
		photo_url = self.track.artwork_url
		f = open(self.title+'.jpg','wb')
		f.write(urllib.urlopen(photo_url).read())
		f.close()	
		self.artWork = ImageTk.PhotoImage(file=self.title+".jpg")
		self.getMainColor()
	
	def __repr__(self):
		return "PlayerTrack(%s)"%(self.url)

	def __str__(self):
		return self.title

	def duration(self):#when called returns duration of player track
		return self.duration

	def drawQueue(self,canvas,index):

		self.margin = 5
		self.boxWidth = 960/4 - 20
		self.boxHeight = 540/9
		queueText = self.title + "\n" + self.user.username
		canvas.create_rectangle(self.margin,self.margin*(index+1)+self.boxHeight*index,
			self.boxWidth+self.margin,(self.margin+self.boxHeight)*(index+1),fill=self.mainColor)
		canvas.create_text(self.margin*2,self.margin*(index+1)+self.boxHeight*index,
			font = "Calbri 8", text=queueText,anchor=NW,width=self.boxWidth-self.margin,
			fill = self.textColor)

	def getRecomendations(self):

		tagList = self.track.tag_list.split(" ")
		index1 = 0
		recoList1 = client.get('/tracks', q=self.user.username, limit = 5,
		 duration={'to':900000})

		for i in xrange(len(recoList1)-1):
			if recoList1[i].streamable == False:
				recoList1.pop(i)

		if len(recoList1) < 2:
			off = 5
			while len(recoList1) < 2:
				if off >= 30:#stop searching for tracks
					break
				tracks = client.get('/tracks', q=self.user.username ,limit=5, 
					offset = off, duration={'to':900000})
				if len(tracks) > 0 :
					for track in tracks:
						userID = track.user_id
						user = client.get('/users/'+str(userID))
						if track.streamable:
							recoList1.append((track.title,user.username,track.permalink_url))
				off += 5

		if len(recoList1) == 0:
			reco1 = None

		else:
			if recoList1[index1].id == self.track.id:
				if len(recoList1) != 1:
					index1 += 1 
			reco1 = recoList1[index1]

		if len(tagList) > 0:

			recoList2 = client.get('/tracks', tags=tagList[0], limit = 5, 
				duration={'to':900000})

			for i in xrange(len(recoList2)-1):
				if recoList2[i].streamable == False:
					recoList2.pop(i)

			if len(recoList2) < 2:
				off = 5
				while len(recoList2) < 2:
					if off >= 30:
						break
					tracks = client.get('/tracks', tags=tagList[0],limit =5, 
						offset = off, duration={'to':900000})
					for track in tracks:
						userID = track.user_id
						user = client.get('/users/'+str(userID))
						if track.streamable:
							recoList2.append((track.title,user.username,track.permalink_url))
					off += 5

			if len(recoList2) == 0:
				reco2 = None
			else:
				index2 = 0
				if recoList2[index2].id == self.track.id:
					if len(recoList2) != 1:
						index2 += 1 
				reco2 = recoList2[index2]

		else:
			if len(recoList1) - 1 > index1 + 1:
				reco2 = recoList1[index1+1]
			else:
				reco2 = None

		return reco1, reco2

	def getMainColor(self):

		im = Image.open(self.title+".jpg")
		a = im.getcolors(10000)#size of soundcloud artwork
		if a == None:
			self.mainColor = "light blue"
		else:
			maxNum = 0 
			maxColor = None
			for pair in a:
				if pair[0] > maxNum:
					maxNum = pair[0]
					maxColor = pair[1]

			if type(maxColor) != tuple:
				#when the max color is black is gets returned at the int 0
				self.mainColor = "white"
				self.textColor = "black"

			else:
				self.mainColor = "#%02x%02x%02x" % (maxColor[0], maxColor[1], maxColor[2])

				if maxColor[0] < 127 or maxColor[1] < 127 or maxColor[2] < 127:
					#if the main color is dark enough
					self.textColor = "white"

				else:
					self.textColor = "black"

class recomendedTrack(object):

	def __init__(self,track):
		
		self.track = track
		self.title = self.track.title
		user = client.get('/users/'+str(self.track.user_id))
		self.user = user.username

	def draw(self,canvas,width,height,position):
	#position will be either 1 or 2 since there are two recommendations given
		self.boxWidth = 960/4 
		self.boxHeight = 540/9
		self.topMargin = 20
		self.boxSpace = 40
		if position == 1:
			canvas.create_rectangle(width*.125,height/2+100,width*.125+self.boxWidth,
				height/2+100+self.boxHeight,fill = "white", outline = "white")
			canvas.create_text(width*.125+5,height/2+100,text=self.title,anchor=NW,
				width=self.boxWidth-5)
		elif position == 2:
			canvas.create_rectangle(width*.125+self.boxWidth+self.boxSpace,height/2+100,
				width*.125+(self.boxWidth*2)+self.boxSpace,height/2+100+self.boxHeight,
				fill = "white", outline = "white")
			canvas.create_text(width*.125+self.boxWidth+self.boxSpace+5,height/2+100,
				text=self.title,anchor=NW,width=self.boxWidth-5)

class AutoDj(EventBasedAnimationClass):

	def __init__(self):
		self.width = 960
		self.height= 540
		super(AutoDj,self).__init__(self.width,self.height)

	def initAnimation(self):

		self.urlBox = Entry(self.root,bg="grey")
		self.helpText = StringVar()
		self.helpText.set("enter search terms or URL")
		self.urlBox.config(text=self.helpText)
		self.scroll = Scrollbar(self.root)
		self.canvas.config(bg = "light blue")
		self.canvas2 = Canvas(self.root,width=.25*self.width, height= self.height-20, 
			yscrollcommand=self.scroll.set, bg = "white")
		self.scroll.config(command=self.canvas2.yview)              
		self.canvas2.config(scrollregion=(0,0,25*self.width, 3*self.height))
		self.margin = 5
		self.boxHeight = 540/9
		self.boxWidth = 960/4 -20
		self.boxSpace = 40
		self.isPlaying = False
		self.nowPlaying = None
		self.trackList = []
		self.counter = 0
		self.mouseX = None
		self.mouseY = None
		self.playButton = Button(self.root,text="Play/Pause")
		self.nextButton = Button(self.root,text="Next")
		self.root.bind("<B1-Motion>",lambda event: self.onMotion(event))
		self.root.bind("<ButtonRelease-1>",lambda event: self.onRelease(event))
		self.urlBox.bind("<Button 1>",self.clearBox)
		self.playButton = ImageTk.PhotoImage(file="play.png")
		self.pauseButton = ImageTk.PhotoImage(file="pause.png")
		self.skipButton = ImageTk.PhotoImage(file = "skip.png")
		self.recomend1 = None
		self.recomend2 = None
		self.playTime = None

	def clearBox(self,event):
		if self.urlBox.get() == self.helpText.get():
			text1 = StringVar()
			text1.set("")
			self.urlBox.config(text=text1)

	def redrawAll(self):

		self.canvas.delete(ALL)
		self.canvas2.delete(ALL)
		self.buttonWidth = 60
		if self.isPlaying:
			self.canvas.create_image(self.width*.75/2-self.buttonWidth,self.height/2+10,
				image = self.pauseButton,anchor = NW)
		else:
			self.canvas.create_image(self.width*.75/2-self.buttonWidth,self.height/2+10,
			image = self.playButton,anchor=NW)
		self.canvas.create_window(self.width,0,anchor=NE,height= 20,width=.25*self.width+25,
			window=self.urlBox)
		self.canvas.create_window(self.width-20,20,anchor=NE,window=self.canvas2)
		self.canvas.create_window(self.width,20,anchor=NE,window=self.scroll,
			height = self.height-20,width=20)
		for i in xrange(len(self.trackList)):
			self.trackList[i].drawQueue(self.canvas2,i)
		if self.nowPlaying != None:
			self.nowPlaying.drawNowPlaying(self.canvas,self.width*.75,self.height)
			self.canvas.config(bg=self.nowPlaying.mainColor)
			self.canvas.create_text(self.width*.125,self.height/2+self.buttonWidth+20,
				text="Recommendations:", fill = self.nowPlaying.textColor)
			self.drawProgress()
		self.canvas.create_image(self.width*.75/2,self.height/2+25,
			image = self.skipButton,anchor=NW)
		if self.recomend1 != None:
			self.recomend1.draw(self.canvas,self.width,self.height,1)
		if self.recomend2 != None:
			self.recomend2.draw(self.canvas,self.width,self.height,2)

	def drawProgress(self):

		self.progressBarHeight = 20
		self.progressBarWidth = self.width/4
		cx = (.75*self.width)/2
		cy = self.height/2
		try:
			progressWidth = (self.counter/self.nowPlaying.clip.seconds())*self.progressBarWidth
		except:
			progressWidth = 0
		if self.nowPlaying.textColor == "black":
			self.canvas.create_rectangle(cx-self.progressBarWidth/2,
				cy-self.progressBarHeight,cx+self.progressBarWidth/2,cy,fill="white",
				outline = "white")
		else:
			self.canvas.create_rectangle(cx-self.progressBarWidth/2,
				cy-self.progressBarHeight,cx+self.progressBarWidth/2,cy,
				fill=self.nowPlaying.mainColor,	outline =self.nowPlaying.mainColor)
		self.canvas.create_rectangle(cx-self.progressBarWidth/2,cy-self.progressBarHeight,
			cx-self.progressBarWidth/2+progressWidth,cy,fill=self.nowPlaying.textColor,
			outline = self.nowPlaying.textColor)
		

	def togglePlay(self):

		if self.isPlaying:
			self.nowPlaying.clip.pause()
			self.isPlaying = False
		elif self.nowPlaying != None:
			self.isPlaying = True
			self.nowPlaying.clip.unpause()

	def onMotion(self,event):

		if self.mouseX == None and self.mouseY==None:
			self.mouseX = event.x
			self.mouseY = event.y

		if self.mouseX in xrange(0,(self.width/4)-20) and len(self.trackList) > 0:
			self.redrawAll()
			boxIndex = self.mouseY/(self.margin+self.boxHeight)
			if boxIndex <= len(self.trackList) - 1:
				self.redrawAll 
				self.canvas2.create_rectangle(event.x-self.boxWidth/2,event.y-self.boxHeight/2,
					event.x+self.boxWidth/2,event.y+self.boxHeight/2)
				self.canvas2.create_text((event.x-self.boxWidth/2)+10,event.y-self.boxHeight/2,
					text=self.trackList[boxIndex].title,anchor=NW,width=self.boxWidth-self.margin)

		elif self.mouseX in xrange(int(self.width*.125),int(self.width*.125+self.boxWidth)) and (
			self.mouseY in xrange(int(self.height/2+100),int(self.height/2+100+self.boxHeight))) and (
				self.recomend1 != None):
			self.redrawAll()
			fill = self.nowPlaying.textColor 
			self.canvas.create_rectangle(event.x-self.boxWidth/2,event.y-self.boxHeight/2,
				event.x+self.boxWidth/2,event.y+self.boxHeight/2,outline = fill)
			self.canvas.create_text((event.x-self.boxWidth/2)+10,event.y-self.boxHeight/2,
				text=self.recomend1.title,anchor=NW,width=self.boxWidth-10, fill = fill)

		elif self.mouseX in xrange(int(self.width*.125+self.boxWidth+self.boxSpace),
			int(self.width*.125+(self.boxWidth*2)+self.boxSpace)) and (
				self.mouseY in xrange(int(self.height/2+100),int(self.height/2+100+self.boxHeight))) and (
				self.recomend2 != None):
			self.redrawAll()
			fill = self.nowPlaying.textColor 
			self.canvas.create_rectangle(event.x-self.boxWidth/2,event.y-self.boxHeight/2,
				event.x+self.boxWidth/2,event.y+self.boxHeight/2, outline = fill)
			self.canvas.create_text((event.x-self.boxWidth/2)+10,event.y-self.boxHeight/2,
				text=self.recomend2.title,anchor=NW,width=self.boxWidth-10, fill = fill)

	def onRelease(self,event):

		if self.mouseX in xrange(0,int(.25*self.width)-20):
			if event.x in xrange(0,int(.25*self.width)-20):
				oldIndex = self.mouseY/(self.margin+self.boxHeight)
				newIndex = event.y/(self.margin+self.boxHeight)
				if oldIndex <= len(self.trackList) - 1:
					if newIndex > len(self.trackList) - 1:
						self.trackList.append(self.trackList.pop(oldIndex))
					else:
						self.trackList.insert(newIndex,self.trackList.pop(oldIndex))
			elif event.x < 0:
				oldIndex = self.mouseY/(self.margin+self.boxHeight)
				if oldIndex <= len(self.trackList) - 1:
					self.trackList.pop(oldIndex)

		elif self.mouseX in xrange(int(self.width*.125),int(self.width*.125+self.boxWidth)) and (
			self.mouseY in xrange(int(self.height/2+100),int(self.height/2+100+self.boxHeight))) and (
				self.recomend1 != None):
			if event.x in xrange(int(.75*self.width),self.width):
				newTrack = PlayerTrack(self.recomend1.track.permalink_url)
				newTrack.download()
				self.trackList.append(newTrack)

		elif self.mouseX in xrange(int(self.width*.125+self.boxWidth+self.boxSpace),
			int(self.width*.125+(self.boxWidth*2)+self.boxSpace)) and (
				self.mouseY in xrange(int(self.height/2+100),int(self.height/2+100+self.boxHeight))) and (
				self.recomend2 != None):
			if event.x in xrange(int(.75*self.width),self.width):
				newTrack = PlayerTrack(self.recomend2.track.permalink_url)
				newTrack.download()
				self.trackList.append(newTrack)
		
		self.mouseX = None
		self.mouseY = None


	def onKeyPressed(self,event):

		if event.keysym == "Return":
			if self.urlBox.get() != "":
				if self.urlBox.get().startswith("http"):
					try:
						a = PlayerTrack(self.urlBox.get())
						a.download()
						self.trackList.append(a)
						self.urlBox.delete(0,END)
					except:
						print "NOT A VALID URL"
						self.urlBox.delete(0,END)	
				else:
					self.search(self.urlBox.get())
					self.urlBox.delete(0,END)

	def search(self,string):
		
		tracks = client.get('/tracks', q=string ,limit=10, duration={'to':900000})
		results = []
		if len(tracks) > 0:
			for track in tracks:
				userID = track.user_id
				user = client.get('/users/'+str(userID))
				if track.streamable:
					results.append((track.title,user.username,track.permalink_url))

		if len(results) < 10:
			off = 10
			while len(results) < 10:
				if off >= 60:
					break
				tracks = client.get('/tracks', q=string ,limit=10, offset = off, 
					duration={'to':900000})
				if len(tracks) > 0:
					userID = track.user_id
					user = client.get('/users/'+str(userID))
					if track.streamable:
						results.append((track.title,user.username,track.permalink_url))
				off += 10

		if len(results) == 0:

			searchWindow = Toplevel()
			searchWindow.text = "Search Results"
			searchList = Listbox(searchWindow,width=100)
			searchList.pack()
			searchList.insert(END,"No results found")

		else:

			searchWindow = Toplevel()
			searchWindow.text = "Search Results"
			searchList = Listbox(searchWindow,width=100)
			for track in results:
				searchList.insert(END,track[0]+' --- '+track[1])
			searchList.pack()
			searchWindow.bind("<Double-Button-1>",lambda event:doubleClick())
		
		def doubleClick():
			index = searchList.curselection()[0]
			a = PlayerTrack(results[index][2])
			a.download()
			self.trackList.append(a)
			searchWindow.destroy()
			self.redrawAll

	def onMousePressed(self,event):

		if event.x in xrange(int(self.width*.75/2-self.buttonWidth),int(self.width*.75/2)) and (
			event.y in xrange(int(self.height/2+10),int(self.height/2+10+self.buttonWidth))):
			self.togglePlay()
		elif event.x in xrange(int(self.width*.75/2),int(self.width*.75/2+45)) and (
			event.y in xrange(int(self.height/2+25),int(self.height/2+25+45))):
			self.playNextSong()

	def onTimerFired(self):
		
		if self.isPlaying:
			self.counter += time.time() - self.playTime
			self.playTime = time.time()
			if self.counter >= self.nowPlaying.clip.seconds():
				self.playNextSong()
		elif self.nowPlaying == None:
			self.playNextSong()
		else:
			self.playTime = time.time()
		
	def playNextSong(self):

		self.isPlaying = False
		if self.trackList != []:
			self.nowPlaying = self.trackList[0]
			self.trackList.pop(0)
			self.findRecomendations()
			self.nowPlaying.play()
			self.counter = 0
			self.playTime = time.time()
			self.isPlaying = True
			
	def findRecomendations(self):

		track1,track2 = self.nowPlaying.getRecomendations()
		if track1 != None:
			self.recomend1 = recomendedTrack(track1)
		else:
			self.recomend1 = None
		if track2 != None:
			self.recomend2 = recomendedTrack(track2)
		else:
			self.recomend2 = None

AutoDj().run()
