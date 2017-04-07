import os
import glob
import tkinter, tkinter.constants, tkinter.filedialog


class KritaConverterWindow(tkinter.Frame):

#CONSTRUCTOR
    def __init__(self, root):

        self.fileTypes = options = {}
        options["PNG"] = [".png"]
        options["JPG"] = [".jpg"]
        options["TIFF"] = [".tiff", ".tif"]

        #set a default
        self.currentFileTypeToConvert = "TIFF"
        self.currentFileTypeConvertTarget = "PNG"


        self.targetDir = ""


        #root.title = "Mass Tiff Converter"

        #FILE OPTIONS
        self.file_opt = options = {} #options dictionary for files
        options["defaultextension"] = ".txt"
        options["filetypes"] = [("all files", ".*"), ("text files", ".txt")]
        options["initialdir"] = "C:\\"
        options["initialfile"] = "myfile.txt"
        options["parent"] = root
        options["title"] = "This is a title for Files."

        #DIRECTORY OPTIONS
        self.dir_opt = options = {} #options dictionary for directories/files
        options["initialdir"] = "C:\\"
        options["mustexist"] = False
        options["parent"] = root
        options["title"] = "This is a Title for Directories."

        #BUTTON OPTIONS
        self.button_opt = options = {}
        options["fill"] = tkinter.constants.BOTH
        options["padx"] = 5
        options["pady"] = 5

        print("boop")

        #initialize the TKinter frame we'll be drawing to
        tkinter.Frame.__init__(self, root)

        #kick off drawing ui function
        self.DrawUI()


    # def GetFilesFromFolder(self, folderPath):
    #     print (glob.glob(self.targetDir + "/" + ))


#GENERAL STRUCTURE OF UI
    def DrawUI(self):

        # #OPEN FILE
        # tkinter.Button(self,
        #                text="Open File",
        #                command=self.AskOpenFile).pack(**self.button_opt)

        #OPEN FOLDER
        tkinter.Button(self,
                       text="Open Folder",
                       command=self.AskOpenDirectory).pack(**self.button_opt)


        #make a horizontal bar to contain the buttons for setting conversion settings
        conversionSettings_HorBar = tkinter.Frame(self)
        conversionSettings_HorBar.pack()


        #SET FILE TYPE WE WANT CONVERTED FROM
        curFileTypeToConvStrVal = tkinter.StringVar(value = self.currentFileTypeToConvert)

        tkinter.OptionMenu(conversionSettings_HorBar,
                           curFileTypeToConvStrVal,
                           *list(self.fileTypes.keys())).pack(side = tkinter.LEFT)

        self.currentFileTypeToConvert = curFileTypeToConvStrVal.get()

        
        #LABEL TO MAKE CONVERSION LOGIC CLEAR (hopefully)
        tkinter.Label(conversionSettings_HorBar, text = "->").pack(side = tkinter.LEFT)

        #SET FILE TYPE WE WANT TO CONVERT TO
        curFileTypeConvTarget = tkinter.StringVar(value = self.currentFileTypeConvertTarget)

        tkinter.OptionMenu(conversionSettings_HorBar,
                           curFileTypeConvTarget,
                           *list(self.fileTypes.keys())).pack(side = tkinter.LEFT)

        self.currentFileTypeConvertTarget = curFileTypeConvTarget.get()



        #DISPLAY ALL FILES THAT WILL BE ALTERED
        listBox_TargetFiles = tkinter.Listbox(self)
        listBox_TargetFiles.pack(side = tkinter.BOTTOM)


#BINDING FUNCTIONS FOR UI ELEMENTS
    def AskOpenFile(self):
        fileName = tkinter.filedialog.askopenfile(mode="r", **self.file_opt)

        if fileName:
            print(fileName)
        
        return fileName

    def AskOpenDirectory(self):
        dirName = tkinter.filedialog.askdirectory(**self.dir_opt)

        if dirName:
            self.targetDir = dirName
            print(dirName)

        return dirName



if __name__ == "__main__":
    ROOT = tkinter.Tk()

    #create title for window
    #windowLabel = tkinter.Label(ROOT, fg="green")
    #windowLabel.pack()

    KritaConverterWindow(ROOT).pack()

    #ROOT.title("Mass Tiff Converter")

    

    ROOT.mainloop()
