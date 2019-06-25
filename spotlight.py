# fetches all wallpaper size files from windows spotlight folder and copies them into a wallpaper folder as jpg

import os
from PIL import Image
from shutil import copyfile

source = r"C:\Users\andre\AppData\Local\Packages\Microsoft.Windows.ContentDeliveryManager_cw5n1h2txyewy\LocalState\Assets"
destination = r"D:\Wallpapers"
sourceFiles, sourceFileNames = os.scandir(source), [os.path.splitext(file)[0] for file in os.listdir(source)]
destinationFiles, destinationFileNames = os.scandir(destination), [os.path.splitext(file)[0] for file in os.listdir(destination)]

for file in sourceFiles:
	if os.path.getsize(file)>100000:
		im = Image.open(file.path)
		width, height = im.size
		if width>height and width>1000 and height>1000 and file.name+".jpg" not in destinationFileNames:
			copyfile(file, destination+"\\"+file.name+".jpg")
			destinationFileNames.append(file.name)


for fileName in destinationFileNames:
	if len(destinationFileNames)<=8:
		break
	if fileName not in sourceFileNames:
		os.remove(destination + "\\" + fileName +".jpg")
		destinationFileNames.remove(fileName)
