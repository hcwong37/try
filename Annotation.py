import os
from tkinter import filedialog
from tkinter import *
from PIL import Image

def get_inital_filepath():
    root=Tk()
    initial_filepath =  filedialog.askdirectory(initialdir = "/",title = "Please select a directory")
    root.destroy()
    return initial_filepath

def print_jpg(root_path, upper_path, ext):
    for root, dirs, files in os.walk(root_path):
        for filename in files:
            if filename.endswith(ext):
#                print(filename)
                image = Image.open(root_path+"\\"+filename)
                for root, dirs, files in os.walk(upper_path):
                    for sim_name in files:
                        if sim_name.endswith(".tif"):
                            anno_path = upper_path +'\\' + sim_name 
                whiteline = Image.open(anno_path)
                print(whiteline)
                image_copy = image.copy()
                position = ((image_copy.width - whiteline.width), (image_copy.height - whiteline.height))
                image_copy.paste(whiteline, position, whiteline)
                image_copy.save(root_path+"\\"+filename)
                

def main():
    initial_filepath = get_inital_filepath()
    dirPath = initial_filepath+"\\Results\\"
    a = os.listdir(dirPath)

    for i in a:
        p = i.split('=')[0]
        if p == "X" or  p == "Y":
            anotherstr = dirPath+"\\"+i
            b = os.listdir(anotherstr)
            
            for j in b:
                path = dirPath+"\\"+i+"\\"+j
                print_jpg(path, anotherstr, ".jpg")
    
    print("Annotations are added to images!")           
    
if __name__ == "__main__":

    main()