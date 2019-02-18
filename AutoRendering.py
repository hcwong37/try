import re
from tkinter import filedialog
from tkinter import *
import shutil, os

def get_inital_filepath():
    root=Tk()
    initial_filepath =  filedialog.askdirectory(initialdir = "/",title = "Please select a directory")
    root.destroy()
    return initial_filepath

def find_fdsfile(initial_filepath):
    for root, dirs, files in os.walk(initial_filepath):
        for sim_name in files:
            if sim_name.endswith(".fds"):
                filepath = initial_filepath +'\\' + sim_name
        return filepath

def fds_filename(initial_filepath):
    for root, dirs, files in os.walk(initial_filepath):
        for sim_name in files:
            if sim_name.endswith(".fds"):
                filename = sim_name[:-4]
        return filename 

def read_file(filepath):
    file_content =""
    with open(filepath, "r") as myfile:
         file_content = myfile.read()  
    return file_content

def extract_slice(file_content, filename, original_filepath):
    patt = re.compile(r"&SLCF.*TEMPERATURE.*\/")
    groups = patt.findall(file_content)
    slicedata=[]
    count = 0
    
    with open(original_filepath+"\\"+ filename +"_slice_info"+".txt", 'a') as f:
            f.write('View'+"%19s" % 'Plane'+"%15s" % 'Slice Loc'+"%15s" % 'Clip Loc'+'\n'*2)          
    for i in groups:
        i = i.split(',')[1]
        j = i[3]
        k = float(i[5:len(i)-1])
        slicedata.append(j)
        slicedata.append(k)
        if j == "X" or j == "Y":
                    l = ("%.1f" % (k - 0.1))
        else:
                    l = ("%.1f" % (k + 0.1))
        slicedata.append(l)
        count +=1 
        info = ('View'+" "+"{:<11d}".format(count)+"%5s" % j+"%15s" % k+"%15s" % l+'\n'\
                )
       
        with open(original_filepath+"\\"+filename+"_slice_info"+".txt", 'a') as f:
            f.write(info)
            f.close()                   
    return slicedata


def get_slice_names(file_content):     
    patt = re.compile(r"&SLCF.*TEMPERATURE.*\/")
    mobj = patt.findall(file_content)
    slice_name = []
    for i in mobj:
        i = i.split(',')[1]
        j = i[3:len(i)-1]
        slice_name.append(j)
        print(i,j)
    return slice_name

def create_directories(original_filepath, directory_list): 
    dirPath = original_filepath + "\\Results"+"\\"
    for i in directory_list:
        path = dirPath + i
        if not os.path.exists(path):
            os.makedirs((path)+"\\Temp")
            os.makedirs((path)+"\\Vis")
            os.makedirs((path)+"\\CO")
            
def extract_simt(file_content):
    pattern_matcher = re.compile(r"T_END=(?P<SimT>[\S]+).")

    simtlist = pattern_matcher.findall(file_content)
    [float(i) for i in simtlist]

    simT = simtlist[0]
    simT = float(simT)

    return simT

def extract_t_frames(file_content, simT):
    pattern_matcher = re.compile(r"NFRAMES=(?P<nframes>[\w]+).")
    nframeslist = pattern_matcher.findall(file_content)
    pattern_matcher2 = re.compile(r"DT_SLCF=(?P<dt_slcf>[\S]+),")
    dt_slcflist = pattern_matcher2.findall(file_content)

    if nframeslist ==[] and dt_slcflist ==[]:
        nframes = float(1000)
        t_frames = simT/nframes
    elif dt_slcflist ==[]:
        nframes = float(nframeslist[0])
        t_frames = simT/nframes
    else:
        t_frames = float(dt_slcflist[0])

    return t_frames

def renderframe_calc(rendertime, t_frames):
    interval = float(rendertime)/t_frames
    renderframe = int(round(interval))
    return renderframe
    
def setting_ouput(j,l,k,m,renderframe):

    dic_plan = {'X' : ['1',' 1 {0} 0 0 ',' 0 0 0 0 ',' 0 0 0 0 '],
           'Y' : ['2',' 0 0 0 0 ',' 1 {0} 0 0 ',' 0 0 0 0 '],
           'Z' : ['3',' 0 0 0 0 ',' 0 0 0 0 ',' 0 0 1 {0}']
               }
    
    temp = ""
    temp =         ("XSCENECLIP"+'\n'
                    +(dic_plan[j][1]).format(l)+ '\n'
                    +"YSCENECLIP"+'\n'
                    +(dic_plan[j][2]).format(l)+'\n'
                   +"ZSCENECLIP"+'\n'
                   +(dic_plan[j][3]).format(l)+'\n'
                   +"SCENECLIP"+'\n'
                   +" "+"1"+'\n'
                   +"LOADSLICE"+'\n'
                   +" "+"TEMPERATURE"+'\n'
                   +" {4} {1}"+'\n'
                   +"CBARNORMAL"+'\n'
                   +"RENDERDIR"+'\n'+" "+".\\Results\\{2}\\Temp"+'\n'
                   +"RENDERALL"+'\n'+" {3}"+'\n'+" "+"T="+'\n'+"UNLOADALL"+'\n'*2
                   +"LOADSLICE"+'\n'+" "+"SOOT VISIBILITY"+'\n'
                   +" {4} {1}"+'\n'
                   +"CBARNORMAL"+'\n'+"CBARFLIP"+'\n'
                   +"RENDERDIR"+'\n'+" "+".\\Results\\{2}\\Vis"+'\n'
                   +"RENDERALL"+'\n'+" {3}"+'\n'+" "+"T="+'\n'+"UNLOADALL"+'\n'*2
                   +"LOADSLICE"+'\n'+" "+"CARBON MONOXIDE VOLUME FRACTION"+'\n'
                   +" {4} {1}"+'\n'
                   +"CBARNORMAL"+'\n'
                   +"RENDERDIR"+'\n'+" "+".\\Results\\{2}\\CO"+'\n'
                   +"RENDERALL"+'\n'+" {3}"+'\n'+" "+"T="+'\n'+"UNLOADALL"+'\n'*2).format(l,k,m,renderframe,dic_plan[j][0])
    return temp
            
def create_ssh_file(file_content, filename, original_filepath,renderframe):
    patt = re.compile(r"&SLCF.*TEMPERATURE.*\/")
    groups = patt.findall(file_content)
    slicedata=[]
    setting =[]
    count = 0

    with open(original_filepath + "\\"+filename+".ssf", 'a') as f:
            f.write("LOADINIFILE"+'\n'\
                    + filename +".INI"+'\n'*2 \
                    +"XSCENECLIP"+'\n'
                    +" 0 0 0 0"+'\n'
                    +"YSCENECLIP"+'\n'
                    +" 0 0 0 0"+'\n'
                    +"ZSCENECLIP"+'\n'
                    +" 0 0 0 0 " +'\n'*2
                    )
            
    for i in groups:
        i = i.split(',')[1]
        j = i[3]
        m = i[3:len(i)-1]
        k = float(i[5:len(i)-1])
        slicedata.append(j)
        slicedata.append(k)
       
        if j == "X" or j == "Y":
                    l = ("%.1f" % (k - 0.1))
        else:
                    l = ("%.1f" % (k + 0.1))
        slicedata.append(l)
        count +=1
        
        setting = setting_ouput(j,l,k,m,renderframe)
            
        with open(original_filepath+ "\\"+filename+".ssf", 'a') as f:
            f.write("SETVIEWPOINT"+'\n'\
                    +" "+"view"+" "+str(count)+'\n'
                    +setting)
            
def slice_limit(temp_min,temp_max,vis_max,vis_min,CO_min,CO_max,filename,original_filepath):  
    with open(original_filepath + "\\"+filename+".ini", 'a') as f:
         f.write('\n'*2+
                 'V_SLICE' + '\n' \
                 +' 1 '+ str(temp_min) +' 1 '+ str(temp_max) +' temp : 0.000000 1.000000 1' +'\n'\
                 +'V_SLICE' + '\n' \
                 +' 1 ' + str(vis_min) +' 1 '+ str(vis_max) +' VIS_Soot : 0.000000 1.000000 1'+'\n'\
                 +'V_SLICE' + '\n' \
                 +' 1 '+ str(CO_min) +' 1 '+ str(CO_max) +' X_CO : 0.000000 1.000000 1'+'\n'*2\
                 +'RENDERFILETYPE'+ '\n'+' 1 1'+ '\n'\
                 +'RENDERFILELABEL'+ '\n'+' 1 1')

def copy_smv(smv_location, original_filepath):
    shutil.copy(smv_location, original_filepath)
         
def file_rename(original_filepath):
    dirPath = original_filepath+"\\Results\\"
    a = os.listdir(dirPath)
    for i in a:
     anotherstr = dirPath+"\\"+i
     b = os.listdir(anotherstr)
     for j in b:
         path = dirPath+"\\"+i+"\\"+j
         for root, dirs, files in os.walk(path):
             for filename in files:
                 if filename.endswith(".jpg"):
                     old_name = path + "\\"+filename
                     newpath = path + "\\"
                     rename = filename.replace('_', '')
                     newnamenum = str(round(float((rename.split('T=')[1])[:-7]),-1))[:-2]
                     new_pic_name= newpath+"T="+newnamenum+"s.jpg"
                     if new_pic_name != old_name:
                         os.rename(old_name, new_pic_name)
    return a

def operation_procedure(filename):
    print("\n"*2
          +"==============================================================================================================="+"\n"\
          +"Procedure to adjust your designated camera view for each slice"+"\n"\
          +"1. Open "+filename+".smv"+"\n"\
          +"2. Assign your designated camera views one by one according to the pop-ed out slice_info list"+"\n"\
          +"   (Tips: Press (Shift+1) for camera alignment, (Alt+M) to pop camera view window, (Alt+C) to pop clip window)"+"\n"\
          +"3. Close the "+filename+"_slice_info.txt"+"\n"\
          +"4. Press any key to continue the rendering process"+"\n"\
          +"==============================================================================================================="
          +"\n"*2)
          
def main():
    initial_filepath = get_inital_filepath()
    original_filepath = initial_filepath
    filepath = find_fdsfile(initial_filepath)
    filename = fds_filename(initial_filepath)
    smv_location = str(os.getcwd()+"\\smokeview.exe")
    
    copy_smv(smv_location, original_filepath)
            
    render_time = input('Please input time interval for rendering (s): ')  
    temp_min = input ('Please enter lower bound for Temperature slices (deg C): ') 
    temp_max = input ('Please upper bound for Temperature slices (deg C): ') 
    vis_min = input ('Please lower bound for Visibility slices (m): ') 
    vis_max = input ('Please upper bound for Visibility slices (m): ')
    CO_min = input ('Please lower bound for CO Concentrations (ppm): ') 
    CO_max = input ('Please upper bound for CO Concentration slices (ppm): ')
    
  
    file_content = read_file(filepath)
    extract_slice(file_content, filename, original_filepath)
    operation_procedure(filename)
    os.chdir(initial_filepath)
    os.system(".\\"+filename+"_slice_info"+".txt")
    os.system('pause')
    
    slice_limit(temp_min,temp_max,vis_max,vis_min,CO_min,CO_max,filename,original_filepath)  
    simT = extract_simt(file_content)      
    t_frames = extract_t_frames (file_content, simT)
    renderframe = renderframe_calc(render_time, t_frames)
    folder_names = get_slice_names(file_content)
    create_directories(original_filepath, folder_names)                        
    create_ssh_file(file_content, filename, original_filepath, renderframe)

    os.system('.\\smokeview ' + filename + ' -script ' + filename + '.ssf')    
    file_rename(original_filepath)
    os.remove((original_filepath + "\\"+filename+".ssf"))
    print("Rendering process completed!")
                           
if __name__ == "__main__":

    main()