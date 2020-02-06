#
# stellarium.py
#
# inspired by https://github.com/mperrin/misc_astro/blob/master/constellations.py
#
# David Moloney, 04 Oct 2019
#

import numpy as np 
#from tkinter import * #as tk
import tkinter as tk
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure

# https://stackoverflow.com/questions/56222259/valueerror-unknown-projection-3d-once-again
# DO NOT DELETE mpl_toolkits.mplot3d reference !!!!!!!!!!!!!!!!!
from mpl_toolkits.mplot3d import Axes3D # <--- This is important for 3d plotting DO NOT REMOVE!!!!

# refactored constellation_data structure containing 88 constellations into cdata.py
#
from cdata import constellation_data  # dict data structure containing constellation information
#from cdata import constellation_names # dict data structure containing constellation information
constellation_names = [] # initialise variable otherwise plot_constellations() causes an error



# https://zulko.wordpress.com/2012/09/29/animate-your-3d-plots-with-pythons-matplotlib/

import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.mplot3d import axes3d
import os
import sys
 
 
##### TO CREATE A SERIES OF PICTURES
 
def make_views(ax,angles,elevation=None, width=4, height = 3,
                prefix='tmprot_',**kwargs):
    """
    Makes jpeg pictures of the given 3d ax, with different angles.
    Args:
        ax (3D axis): te ax
        angles (list): the list of angles (in degree) under which to
                       take the picture.
        width,height (float): size, in inches, of the output images.
        prefix (str): prefix for the files created. 
     
    Returns: the list of files created (for later removal)
    """
     
    files = []
    ax.figure.set_size_inches(width,height)
     
    for i,angle in enumerate(angles):
     
        ax.view_init(elev = elevation, azim=angle)
        fname = '%s%03d.jpeg'%(prefix,i)
        ax.figure.savefig(fname)
        files.append(fname)
     
    return files
 
 
 
# transform series of pictores into an animation
# Uses mencoder, produces a .mp4/.ogv/... movie from a list of picture files.
#
def make_movie(files,output, fps=10,bitrate=1800,**kwargs):
    output_name, output_ext = os.path.splitext(output)
    command = { '.mp4' : 'mencoder "mf://%s" -mf fps=%d -o %s.mp4 -ovc lavc\
                         -lavcopts vcodec=msmpeg4v2:vbitrate=%d'
                         %(",".join(files),fps,output_name,bitrate)}
                          
    command['.ogv'] = command['.mp4'] + '; ffmpeg -i %s.mp4 -r %d %s'%(output_name,fps,output)
     
    print(command[output_ext])
    output_ext = os.path.splitext(output)[1]
    os.system(command[output_ext])
 
 
# Uses imageMagick to produce an animated .gif from a list of picture files
#
 
def make_gif(files,output,delay=100, repeat=True,**kwargs):
    loop = -1 if repeat else 0
    os.system('convert -delay %d -loop %d %s %s' %(delay,loop," ".join(files),output))
 
 
# Uses imageMagick to produce a .jpeg strip from a list of picture files
#
def make_strip(files,output,**kwargs):
    os.system('montage -tile 1x -geometry +0+0 %s %s'%(" ".join(files),output))
     
 
def rotanimate(ax, angles, output, **kwargs):
    """
    Produces an animation (.mp4,.ogv,.gif,.jpeg,.png) from a 3D plot on
    a 3D ax
     
    Args:
        ax (3D axis): the ax containing the plot of interest
        angles (list): the list of angles (in degree) under which to
                       show the plot.
        output : name of the output file. The extension determines the
                 kind of animation used.
        **kwargs:
            - width : in inches
            - heigth: in inches
            - framerate : frames per second
            - delay : delay between frames in milliseconds
            - repeat : True or False (.gif only)
    """
         
    output_ext = os.path.splitext(output)[1]
 
    files = make_views(ax,angles, **kwargs)
     
    D = { '.mp4' : make_movie,
          '.ogv' : make_movie,
          '.gif': make_gif ,
          '.jpeg': make_strip,
          '.png':make_strip}
           
    D[output_ext](files,output,**kwargs)
     
    for f in files: os.remove(f)


# Convert vector(s) from spherical polar to rectangular form.
# Based on IDL JHUAPL lib's polrec3d.pro
#
def polrec3d(radius, az, ax, degrees=False):
    
    z, rxy = polrec(radius, az, degrees=degrees)
    x, y   = polrec(rxy, ax, degrees=degrees)
    return x, y, z


# convert Right Ascension (RA) and Declination (DEC) to x,y,z coordinate
#
def radec2xyz(radius, ra, dec, degrees=True):
    northpole = 90 if degrees else np.pi
    return polrec3d(radius, northpole-dec, ra, degrees=degrees)


# Convert 2-d polar coordinates to rectangular coordinates. Based on IDL JHUAPL lib's polrec.pro
# 
def polrec(r, a, degrees=False):

    cf = 1.e0
    if degrees: cf = 180/np.pi

    x = r*np.cos(a/cf)
    y = r*np.sin(a/cf)
    return x, y


# get constellation names from constellation_data
#
def get_cnames(constellation_data=constellation_data):
    clst=list(constellation_data.keys()) # https://www.pythoncentral.io/convert-dictionary-values-list-python/
    return clst


# display list can be a mixture of 0-87 constellation numbers and names
# "all" for all constellations, or "home" for the home constellation only
# this function returns a uniform list of names
#
def gen_list(display_list,home="Andromeda"):
    dlist = []
    ii=0
    for i in display_list: 
        if isinstance(i, str): 
            if   (i=="all")  : return constellation_names
            elif (i=="home") : return home
            else             : dlist.insert(ii,i)
        else : dlist.insert(ii,constellation_names[int(i)])
        ii+=1
    return dlist


# uses tkinter for displaying matplotlib plot so you can zoom, pan etc.
#
def plot_const_3D(master,colour='blue',radius=1,home="Andromeda",display_list=constellation_names):

    # setup tkinter
    master.title("Stellarium: " + " Plotting: " + str(len(display_list)-1) + "/88 constellations Home: " + home )
    fig = Figure(figsize=(10, 10), dpi=100)

    # Create a container
    canvas = FigureCanvasTkAgg(fig, master)  # A tk.DrawingArea.
    canvas.draw()
    ax = fig.add_subplot(111, projection="3d")
    
    #######################################################################
    # constellation_data to be plotted
    
    #print(constellation_data)
    
    # plot constellations 
    cc=0
    print("\nplotting constellations\n")
    for name, point_list in constellation_data.items():
        if name in display_list :
            print(cc, name) #, constellation_names[cc])
            cc=cc+1 # increment constellation count
            
            points = np.asarray(point_list)
            drawtype = points[:,0]
            ra_degrees = points[:,1] * 1.0 / 1800 * 15
            dec_degrees = points[:,2] * 1.0 / 60
            
            for i in range(0, len(drawtype)-1):
                if drawtype[i] == 0: continue # don't draw lines, just move for type 0
                ras =  ra_degrees[i - 1:(i)+1]
                decs = dec_degrees[i - 1:(i)+1]
                xs, ys, zs = radec2xyz(radius, ras, decs)
                ls=':' if drawtype[i] ==2 else "-"
                cl='red' if (name==home) else 'blue'
                ax.plot(xs, ys, zs, linestyle=ls, color=cl) 
    
    # plot lat/long great circles
    pts=45
    # latitude circle
    xs, ys, zs = radec2xyz(radius, np.linspace(0,360,pts), np.zeros(pts))
    ax.plot(xs,ys,zs, linestyle='-', color='black')
    # longitude circle
    xs, ys, zs = radec2xyz(radius, np.zeros(pts), np.linspace(-90,90,pts))
    ax.plot(xs,ys,zs, linestyle=':', color='black') # 1st semicircle
    ax.plot(-xs,ys,zs, linestyle=':', color='black') # 2nd semicircle   
   
    #######################################################################
    
    toolbar = NavigationToolbar2Tk(canvas, master)
    toolbar.update()
    canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)
#
# plot_const_3D()
    

# uses tkinter for displaying matplotlib plot so you can zoom, pan etc.
#
def plot_const_2D(master,colour='blue',radius=1,home="Cassiopea",only_home=True): #,display_list=constellation_names):

    # setup tkinter
    master.title("Constellation Plot: " + home)
    fig2D = Figure(figsize=(5, 5), dpi=100)

    # Create a container
    canvas = FigureCanvasTkAgg(fig2D, master)  # A tk.DrawingArea.
    canvas.draw()
    #ax = fig2D.add_subplot()
    ax = fig2D.add_subplot(111, projection="3d")
    #
    # https://stackoverflow.com/questions/9295026/matplotlib-plots-removing-axis-legends-and-white-spaces
    #
    ax.set_axis_off()
    
    #######################################################################
    # constellation_data to be plotted
    
    # plot constellations 
    cc=0
    print("\nplotting 2D constellations\n")
    for name, point_list in constellation_data.items():
        if ((name!=home and not(only_home)) or (name==home)) : 
            print(cc, name) #, constellation_names[cc])
            cc=cc+1 # increment constellation count
            
            points = np.asarray(point_list)
            drawtype = points[:,0]
            ra_degrees = points[:,1] * 1.0 / 1800 * 15
            dec_degrees = points[:,2] * 1.0 / 60
            
            for i in range(0, len(drawtype)-1):
                if drawtype[i] == 0: continue # don't draw lines, just move for type 0
                ras =  ra_degrees[i - 1:(i)+1]
                decs = dec_degrees[i - 1:(i)+1]
                xs, ys, zs = radec2xyz(radius, ras, decs)
                ls=':' if drawtype[i] ==2 else "-"
                # 
                # https://stackoverflow.com/questions/19999313/star-sphere-projecting-points-from-sphere-to-2d
                #
                #(x,y) = (-ys/xs, zs/xs)
                #ax.plot(x,y, linestyle=ls, color='green') 
                #
                ax.plot(-ys, -xs, linestyle=ls, color='green') 
                #ax.plot(ys, xs, linestyle=ls, color='green') 
                #ax.plot(xs, ys, zs, linestyle=ls, color='green') 

    #######################################################################
    
    toolbar = NavigationToolbar2Tk(canvas, master)
    toolbar.update()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
#
# plot_const_2D()
    
    
# main plot_constellations call
#
constellation_names = get_cnames() # extract list of constellation names from constellation_data dictionary

home=constellation_names[0] # set home constellation
home="Andromeda" # set home constellation
home="Apus" # set home constellation
home="Draco" # set home constellation
home="Canis_Major" # set home constellation
home="Leo" # set home constellation
home="Orion" # set home constellation
home="Cassiopea" # set home constellation
home="Canis_Minor" # set home constellation
home="Lyra" # set home constellation
home="Centaurus" # set home constellation
home="Scorpius" # set home constellation
home="Lyra" # set home constellation
#home=constellation_names[59] # set home constellation
home=constellation_names[0] # set home constellation
home="Gemini" # set home constellation

#display_list = ["Andromeda",1,2,constellation_names[83]] # display mix of numbers and names
#display_list = ["home"] # display home constellation only
display_list = ["all"] # display all 88 constellations
#display_list = ["Cassiopea"] # display all 88 constellations

display_list = gen_list(display_list)
print("display_list=",display_list)

# plot list of constellations
starplot3D = tk.Tk()
starplot2D = tk.Tk()

plot_const_3D(starplot3D,radius=1,home=home,display_list=display_list) # home constellation displayed in red
plot_const_2D(starplot2D,radius=1,home=home) #,display_list=display_list) # home constellation displayed in red

#
# home constellation selection
#
# https://stackoverflow.com/questions/45441885/how-can-i-create-a-dropdown-menu-from-a-list-in-tkinter
# http://zetcode.com/tkinter/menustoolbars/
# http://effbot.org/tkinterbook/menu.htm
#

# drop-down list
#
variable = tk.StringVar(starplot2D)
variable.set(constellation_names[0]) # default value
w = tk.OptionMenu(starplot2D, variable, *constellation_names)
w.pack()

# selection button
def ok(): print ("home constellation is:" + variable.get())
button = tk.Button(starplot2D, text="OK", command=ok)
button.pack()

#######################################################################################################

starplot2D.mainloop()
starplot3D.mainloop()


###### EXAMPLE
# 
#if __name__ == '__main__':
# 
#    fig = plt.figure()
#    ax = fig.add_subplot(111, projection='3d')
#    X, Y, Z = axes3d.get_test_data(0.05)
#    s = ax.plot_surface(X, Y, Z, cmap=cm.jet)
#    plt.axis('off') # remove axes for visual appeal
#     
#    angles = np.linspace(0,360,21)[:-1] # Take 20 angles between 0 and 360
# 
#    # create an animated gif (20ms between frames)
#    rotanimate(ax, angles,'movie.gif',delay=20) 
# 
#    # create a movie with 10 frames per seconds and 'quality' 2000
#    rotanimate(ax, angles,'movie.mp4',fps=10,bitrate=2000)
# 
#    # create an ogv movie
#    rotanimate(ax, angles, 'movie.ogv',fps=10) 