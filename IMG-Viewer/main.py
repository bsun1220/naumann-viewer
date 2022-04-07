import tifffile
import numpy as np
import random
from tkinter import *
from tkinter.ttk import *
import matplotlib.pyplot as plt
import napari
import os
from PIL import ImageTk, Image
from skimage.segmentation import watershed
from scipy import ndimage

class DataAnnotate:
    def __init__(self, patch_num = 250, 
                 tif_path = r'\Users\naumannlab\Desktop\IMG-Viewer\zstack_0.tif', 
                 label_path = r'\Users\naumannlab\Desktop\IMG-Viewer\manual_data.tif',
                 arr = None):
        
        #dimensions of patch image
        self.patch_num = patch_num
        
        #data type that looks at labels
        self.labels = np.array(tifffile.imread(label_path) > 0, dtype = int)
        
        #provides updated editings to the labels
        self.edited_labels = self.labels
        self.points_labels = self.labels
        
        #data type storing cell image data
        self.tif = tifffile.imread(tif_path)
        
        #defines whether all patches are finished or not 
        self.complete = False
        
        #will later add functionality for flexibile img sizes
        assert self.tif.shape[1] % patch_num == 0 and self.tif.shape[2] % patch_num == 0
        
        #creates dataframe for patches
        self.length_tiff = (int)(self.tif.shape[1]/self.patch_num)
        self.width_tiff = (int)(self.tif.shape[2]/self.patch_num)
        self.arr_length = self.length_tiff*self.width_tiff*self.tif.shape[0]
        
        #index showing how many more patches to go 
        self.arr = arr
        
        if self.arr is None:
        
        #index showing how many more patches to go 
            self.arr = np.arange(0, self.arr_length, dtype =int)
        
    def get_patch(self, index, length, width):
        assert(index < self.tif.shape[0] and index >= 0)     
        
        #length calculation
        dim1_low = length * self.patch_num
        dim1_high = (length + 1)* self.patch_num
        
        #width calculation 
        dim2_low = width * self.patch_num
        dim2_high = (width + 1)* self.patch_num
        
        tif = self.tif[index][dim1_low:dim1_high,dim2_low:dim2_high]
        label = self.labels[index][dim1_low:dim1_high,dim2_low:dim2_high]
        return tif, label, (index, length, width)
    
    def save_patch(self, index, length, width, patch, points = False):
        assert(index < self.tif.shape[0] and index >= 0)     
        
        #length calculation
        dim1_low = length * self.patch_num
        dim1_high = (length + 1)* self.patch_num
        
        #width calculation 
        dim2_low = width * self.patch_num
        dim2_high = (width + 1)* self.patch_num
        
        if points:
            self.points_labels[index][dim1_low:dim1_high,dim2_low:dim2_high] = patch
        else:
            self.edited_labels[index][dim1_low:dim1_high,dim2_low:dim2_high] = patch
    
    def get_edited_labels(self):
        return self.edited_labels
    
    def get_points_labels(self):
        return self.points_labels
    
    def get_random_patch(self):
 
        indx = random.randint(0, len(self.arr) - 1)
        
        val = self.arr[indx]
        
        #delete from index
        self.arr = np.delete(self.arr, indx)
        
        if(len(self.arr) == 0):
            print("All Patches are Complete!")
            self.complete = True
        
        #get unique index value 
        index = int(val/(self.length_tiff * self.width_tiff))
        
        #edit val
        val = val % (self.length_tiff * self.width_tiff)
        
        #get length
        length = int(val/(self.length_tiff))
        
        #get width
        width = val % self.length_tiff
        
        return self.get_patch(index, length, width)

class ImageViewer():
    def __init__(self, patch_num = 250, 
                 tif_path = r'\Users\naumannlab\Desktop\IMG-Viewer\zstack_0.tif', 
                 label_path = r'\Users\naumannlab\Desktop\IMG-Viewer\manual_data.tif',
                 arr = None, 
                 output1 = "edited_labels.tiff",
                 output2 = "points_labels.tiff"):
        
        self.data = DataAnnotate(patch_num, tif_path, label_path, arr)
        self.napari = napari.Viewer()
        self.output1 = output1
        self.output2 = output2
   
        self.root = Tk()
        self.root.title("GUI Image Viewer")
        self.root.geometry("300x300")
        self.root.resizable(False, False)
        self.image1 = ImageTk.PhotoImage(Image.open("download.jpg"))
        self.image = Label(image = self.image1)
        self.image.grid(row = 1, column = 1)
        self.next_button = Button(text = "Next", command = self.next_click)
        self.next_button.grid(row = 0, column = 1, columnspan = 3)
        
        self.next_button = Button(text = "Upload", command = self.upload)
        self.next_button.grid(row = 2, column = 1, columnspan = 3)
        self.root.mainloop()
    
     def next_click(self):
        if(len(self.napari.layers) != 0):
            self.data.save_patch(*self.dims, self.napari.layers["Labels"].data)
            self.create_points()
        
        while(len(self.napari.layers) != 0):
            self.napari.layers.pop(0)
        
        if(self.data.complete):
            self.next_button = Button(text = "Next(Complete)", command = self.next_click, state = DISABLED)
            self.next_button.grid(row = 0, column = 1, columnspan = 3)
            return
        
        self.tif, self.label, self.dims = self.data.get_random_patch()
        new_layer = self.napari.add_image(self.tif, name = "Cell Data")
        labels = self.napari.add_labels(self.label, name = "Labels")
        points = self.napari.add_points(np.empty(0), size = 2, name = "Points")
        self.napari.layers["Cell Data"].gamma = 0.4
        self.napari.layers["Labels"].opacity = 0.4
    
    def create_points(self):
        cell_points = self.napari.layers["Points"].data
        gt_data = self.napari.layers["Labels"].data
        
        distance = ndimage.distance_transform_edt(gt_data)
        pts_img = np.zeros(gt_data.shape)
        n = 1
        
        for p in cell_points:
            pts_img[int(p[0]), int(p[1])] = n
            n += 1
        
        labels_ws = watershed(-distance, pts_img, mask=gt_data)
        self.data.save_patch(*self.dims, labels_ws, True)
        
    def upload(self):
        tifffile.imsave(self.output1, self.data.get_edited_labels())
        tifffile.imsave(self.output2, self.data.get_points_labels())
        self.root.destroy()
        self.napari.close()
    
    def get_arr(self):
        return self.data.arr
    
    def get_gt(self):
        return self.data.tif
