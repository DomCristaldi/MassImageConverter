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
        self.filesToConvert = []

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

                # #OPEN FILE
        # tkinter.Button(self,
        #                text="Open File",
        #                command=self.AskOpenFile).pack(**self.button_opt)

    #OPEN FOLDER
        tkinter.Button(self,
                       text="Open Folder",
                       command=self.AskOpenDirectory).pack(**self.button_opt)


    #HORIZONTAL GROUPING BAR
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


        #RELOAD BUTTON
        tkinter.Button(self,
                       text = "Reload Files",
                       command = self.UpdateListbox).pack()


    #DISPLAY ALL FILES THAT WILL BE ALTERED
        self.listBox_TargetFiles = tkinter.Listbox(self)
        self.listBox_TargetFiles.pack(side = tkinter.BOTTOM)
        
        #populate the list box in case we had any info we wanted to throw in there
        self.PopulateListBox_TargetFiles(self.filesToConvert)

        #self.DrawUI()

#POPULATE LIST BOX WITH FILES WE WITH TO CONVERT
    def PopulateListBox_TargetFiles(self, fileNames):
        #clear list box
        self.listBox_TargetFiles.delete(0, tkinter.END)

        for fN in fileNames:
            #print(fN)
            self.listBox_TargetFiles.insert(tkinter.END, fN)


    def GetFilesFromFolder(self, fileTypeConvertFrom, folderPath):

        #for each supplied file extension, construct a string of the path to the target directory, the wildcard, and the file extension
            #ie, folderPath/*.fileExten
        filePaths = ["%s/*%s"%(folderPath ,p) for p in self.fileTypes[fileTypeConvertFrom]]

        foundFiles = []
        for fPath in filePaths:
            foundFiles.extend(glob.glob(fPath))

        return foundFiles

#HELPER FUNCTION TO AUTOMATE UPDATING LIST BOX WITH NEW FILES
    def UpdateListbox(self):
        self.PopulateListBox_TargetFiles(self.GetFilesFromFolder(self.currentFileTypeToConvert,
                                                                 self.targetDir))

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
