import os
import subprocess
import glob
import configparser
import tkinter, tkinter.constants, tkinter.filedialog

import pprint

class ConfigHandler:
    def __init__(self, path: str):
        self.path = path
        #self.configFile = configparser.ConfigParser()
        #self.configFile.read(path)

    def GetFromConfigFile(self, section: str, entry: str):
        entryVal = None
        with open(self.path, "r") as cf:
            configFile = configparser.ConfigParser()
            configFile.read_file(cf)
            entryVal = configFile.get(section, entry)
        #return self.configFile.get(section, entry)
        return entryVal

    def UpdateConfigFile(self, section: str, entry: str, data: str):
        configFile = configparser.ConfigParser()
        configFile.read(self.path)
        configFile.set(section, entry, data)

        with open(self.path, "w") as cf:
            configFile.write(cf)
            #configFile._write_section(cf, section, entry)

        # self.configFile.set(section, entry, data)
        # with open(self.path, "w") as cf:
        #     self.configFile.write(cf)


#TODO: look at implement something better than just a wrapper around a dict, but don't go overboard and reimplement dict
class FileTypesHandler:
    def __init__(self):
        self.fileTypes = {}

    def __getitem__(self, key):
        return self.fileTypes[key]

    def keys(self):
        return self.fileTypes.keys()

    def HasFileType(self, fileType: str):
        for f in self.fileTypes:
            if f == fileType: return True
        return False

#PROMLEM: doesn't know fromType and toType are in the dictionary
    def CheckCanConvert(self, targetFile: str, fromType: str, toType: str):
        return (self.HasFileType(fromType) and self.HasFileType(toType))

    def GetExtensions(self, friendlyName: str):
        if friendlyName not in self.fileTypes.keys():
            return []
        return self.fileTypes[friendlyName]

    def GetNumExtensions(self, friendlyName: str):
        if friendlyName not in self.fileTypes.keys():
            return 0
        return len(self.fileTypes[friendlyName])

    def GetEndingExtension(self, filePath: str, fileType: str):
        for ext in self.GetExtensions(fileType):
            if filePath.endswith(ext):
                return ext
        return None

    def GetDefaultExtension(self, fileType: str):
        if fileType not in self.fileTypes.keys():
            return None
        if self.GetNumExtensions(fileType) < 1:
            return None
        return self.fileTypes[fileType][0]

    #TODO: Verify that the typeExtension is of format ".ext", don't allow for funky stuff
    #figure out what's the best exception to throw
    def VerifyTypeExtension(self, typeExtension: str):
        return typeExtension is not None and typeExtension is not ""

    def AddFileType(self, friendlyName: str, typeExtensions: str):

        #add the category if we didn't have it already
            #but don't add any info because we want to verify it first
        if friendlyName not in self.fileTypes.keys():
            self.fileTypes[friendlyName] = []

        #verify that the info is good before we add it
        for ext in typeExtensions:
            if self.VerifyTypeExtension(ext) and ext not in self.fileTypes[friendlyName]:

                #we were passed a single tring, we need to stop now or else we'll add characters one at a time
                if isinstance(typeExtensions, str):
                    self.fileTypes[friendlyName].append(typeExtensions)
                    break

                self.fileTypes[friendlyName].append(ext)


class FileTypesHandler_Krita(FileTypesHandler):
    def __init__(self):
        FileTypesHandler.__init__(self)

        self.AddFileType("PNG", ".png")
        self.AddFileType("JPG", ".jpg")
        self.AddFileType("TIFF", [".tiff", ".tif"])


#Generic Conversion Tool to call command line interfaces
class ConversionTool:
    def __init__(self,
                 configInfo: ConfigHandler,
                 validFileTypes: FileTypesHandler,
                 friendlyName: str,
                 path: str,
                 exeName: str,
                 cliCommand: str):

        self.configInfo = configInfo

        self.validFileTypes = validFileTypes

        self.friendlyName = friendlyName
        self.path = path
        self.exeName = exeName
        self.cliCommand = cliCommand

    #def GetFileEnding(self, targetFileFullPath)

    def ConvertFile(self, targetFileFullPath: str, fromType: str, toType: str):

    #ERROR CHECKING
        #can't convert
        if self.validFileTypes.CheckCanConvert(targetFileFullPath, fromType, toType) is not True:
            return
        #it's on record, but we don't know any actual extensions
        if self.validFileTypes.GetNumExtensions(fromType) < 1 or self.validFileTypes.GetNumExtensions(toType) < 1:
            return

        fromExt = None
        toExt = None
        targetFileNoExt = None

        #attempt to extract the full file path and the extension
        possibleExtensions = self.validFileTypes.GetExtensions(fromType)

        for ext in possibleExtensions:
            if targetFileFullPath.endswith(ext) is True:
                fromExt = ext
                targetFileNoExt = targetFileFullPath[:-len(fromExt)]
                break

        if fromExt is None or targetFileNoExt is None:
            return

        toExt = self.validFileTypes.GetDefaultExtension(toType)


        #get us into our tool's directory
        os.chdir(self.path)

        #build the command to run the tool
        finalCommand = self.cliCommand.format(exeName=self.exeName,
                                              fileNameNoExten=targetFileNoExt,
                                              fromType=fromExt,
                                              toType=toExt)

        print("Executing: %s"%finalCommand)

        #call the function we just created on the command line
        subprocess.call(finalCommand.split())

#Special Conversion Tool preconfigured for Krita
class ConversionTool_Krita(ConversionTool):
    #default the data we want to fill to None, but allow for overwriting if we want to do something custom later
    def __init__(self,
                 configInfo: ConfigHandler,
                 validFileTypes: FileTypesHandler = None,
                 friendlyName: str = None,
                 path: str = None,
                 exeName: str = None,
                 cliCommand: str = None):

        #Initialize all data from the class, allow for custom data if you want it
        ConversionTool.__init__(self,
                                configInfo,
                                FileTypesHandler_Krita() if validFileTypes is None else validFileTypes(),
                                "Krita" if friendlyName is None else friendlyName,
                                configInfo.GetFromConfigFile("Krita", "kritainstalllocation") if path is None else path,
                                configInfo.GetFromConfigFile("Krita", "kritaexename") if exeName is None else exeName,
                                "{exeName} {fileNameNoExten}{fromType} --export --export-filename {fileNameNoExten}{toType}" if cliCommand is None else cliCommand)


class MassImageConverterApp(tkinter.Tk):

    def __init__(self, parent):
        tkinter.Tk.__init__(self, parent)

        self.parent = parent

        #store reference to config file
        self.config = ConfigHandler("config.ini")

        self.geometry(self.config.GetFromConfigFile("UserInfo", "prevwindowsize"))

        self.InitializeApp()


    def InitializeApp(self):
        self.grid()
        KritaConverterWindow(self).grid(column = 0, row = 0, sticky = tkinter.constants.NSEW)

        self.grid_columnconfigure(0, weight = 1)
        self.grid_rowconfigure(0, weight = 1)


    def GetFromConfigFile(self, section: str, entry: str):
        return self.config.GetFromConfigFile(section, entry)

    #HELPER FUNCTION FOR UPDATING CONFIG FILE
    def UpdateConfigFile(self, section: str, entry: str, data: str):
        self.config.UpdateConfigFile(section, entry, data)

        # self.config.set(section, entry, data)
        # with open("config.ini", "w") as configFile:
        #     self.config.write(configFile)

    def OnCloseWindow(self):
        self.config.UpdateConfigFile("UserInfo", "prevwindowsize", self.winfo_geometry())

        self.destroy()



class KritaConverterWindow(tkinter.Frame):

#CONSTRUCTOR
    def __init__(self, parent):

        #initialize the TKinter frame we'll be drawing to
        tkinter.Frame.__init__(self, parent)


        self.parent = parent

        self.currentConversionTool = "Krita"

        self.converterTools = {"Krita": ConversionTool_Krita(parent.config)}

        self.fileTypes = FileTypesHandler()
        self.fileTypes.AddFileType("PNG", ".png")
        self.fileTypes.AddFileType("JPG", ".jpg")
        self.fileTypes.AddFileType("TIFF", [".tiff", ".tif"])

        # self.fileTypes = options = {}
        # options["PNG"] = [".png"]
        # options["JPG"] = [".jpg"]
        # options["TIFF"] = [".tiff", ".tif"]

        #set a default
        self.currentFileType_ConvertFrom = self.parent.GetFromConfigFile("UserInfo", "lastfiletoconvertfrom")#"TIFF"
        self.currentFileType_ConvertTo = self.parent.GetFromConfigFile("UserInfo", "lastfiletoconvertto") #"PNG"


        self.targetDir = self.parent.GetFromConfigFile("UserInfo", "lastopendir")
        self.saveDir = self.parent.GetFromConfigFile("UserInfo", "targetsavedir")

        self.filesToConvert = self.GetFilesFromFolder(self.currentFileType_ConvertFrom, self.targetDir)

        #parent.title = "Mass Tiff Converter"

        #FILE OPTIONS
        self.file_opt = options = {} #options dictionary for files
        options["defaultextension"] = ".txt"
        options["filetypes"] = [("all files", ".*"), ("text files", ".txt")]
        options["initialdir"] = "C:\\"
        options["initialfile"] = "myfile.txt"
        options["parent"] = parent
        options["title"] = "This is a title for Files."

        #DIRECTORY OPTIONS
        self.dir_opt = options = {} #options dictionary for directories/files
        options["initialdir"] = self.targetDir
        options["mustexist"] = False
        options["parent"] = parent
        options["title"] = "Open Folder To Mass Convert Images"

        #BUTTON OPTIONS
        self.button_opt = options = {}
        options["fill"] = tkinter.constants.BOTH
        options["padx"] = 5
        options["pady"] = 5



    #OPEN FOLDER
        tkinter.Button(self,
                       text="Open Folder",
                       command=self.AskOpenDirectory).pack(**self.button_opt)


    #HORIZONTAL GROUPING BAR
        #make a horizontal bar to contain the buttons for setting conversion settings
        conversionSettings_HorBar = tkinter.Frame(self)
        conversionSettings_HorBar.pack()


    #SET FILE TYPE WE WANT CONVERTED FROM
        curFileTypeToConvStrVal = tkinter.StringVar(value = self.currentFileType_ConvertFrom)

        tkinter.OptionMenu(conversionSettings_HorBar,
                           curFileTypeToConvStrVal,
                           *list(self.fileTypes.keys()),
                           command = self.UpdateTargetFileType_ConvertFrom).pack(side = tkinter.LEFT)

        self.currentFileType_ConvertFrom = curFileTypeToConvStrVal.get()


    #LABEL TO MAKE CONVERSION LOGIC CLEAR (hopefully)
        tkinter.Label(conversionSettings_HorBar, text = "->").pack(side = tkinter.LEFT)


    #SET FILE TYPE WE WANT TO CONVERT TO
        curFileTypeConvTarget = tkinter.StringVar(value = self.currentFileType_ConvertTo)

        tkinter.OptionMenu(conversionSettings_HorBar,
                           curFileTypeConvTarget,
                           *list(self.fileTypes.keys()),
                           command = self.UpdateTargetFileType_ConverTo).pack(side = tkinter.LEFT)

        self.currentFileType_ConvertTo = curFileTypeConvTarget.get()


    #RELOAD BUTTON
        tkinter.Button(self,
                       text = "Reload Files",
                       command = self.UpdateListbox).pack()

    #GROUPING FOR FILES AND CONVERT BUTTON
        filesAndConvert = tkinter.Frame(self)
        filesAndConvert.pack(side = tkinter.BOTTOM, fill = tkinter.BOTH, expand = True)

    #CONVERT FILES BUTTON
        tkinter.Button(filesAndConvert,
                       text = "Convert Files",
                       command = self.ConvertSelectedFiles).pack(side = tkinter.RIGHT)


    #DISPLAY ALL FILES THAT WILL BE ALTERED
        self.listBox_TargetFiles = tkinter.Listbox(filesAndConvert)
        self.listBox_TargetFiles.pack(side = tkinter.BOTTOM, fill = tkinter.BOTH, expand = True)
        #self.listBox_TargetFiles.grid(column = 0, row = 0, weight = 1)

        #populate the list box in case we had any info we wanted to throw in there
        self.PopulateListBox_TargetFiles(self.filesToConvert)



#POPULATE LIST BOX WITH FILES WE WITH TO CONVERT
    def PopulateListBox_TargetFiles(self, fileNames: str):
        #clear list box
        self.listBox_TargetFiles.delete(0, tkinter.END)

        for fN in fileNames:
            self.listBox_TargetFiles.insert(tkinter.END, fN)

#CONVER FILES
    def ConvertSelectedFiles(self):
        print("Converting")

        for f in self.filesToConvert:
            print("Converting Items %s/%s"%(self.filesToConvert.index(f),
                                            len(self.filesToConvert)))

            self.converterTools[self.currentConversionTool].ConvertFile(f,
                                                                        'TIFF',#self.currentFileType_ConvertFrom,
                                                                        'PNG')#self.currentFileType_ConvertTo)
        print("Done")

    def GetFilesFromFolder(self, fileType: str, folderPath: str):

        #for each supplied file extension, construct a string of the path to the target directory, the wildcard, and the file extension
            #ie, folderPath/*.fileExten
        filePaths = ["%s/*%s"%(folderPath, p) for p in self.fileTypes[fileType]]

        foundFiles = []
        for fPath in filePaths:
            foundFiles.extend(glob.glob(fPath))

        return foundFiles

#HELPER FUNCTION TO AUTOMATE UPDATING LIST BOX WITH NEW FILES
    def UpdateListbox(self):
        #update the list of all files we think we can convert
        self.UpdateTargetFileType_ConvertFrom(self.currentFileType_ConvertFrom)

        print(self.filesToConvert)

        #self.PopulateListBox_TargetFiles(self.GetFilesFromFolder(self.currentFileType_ConvertFrom,
        #                                                         self.targetDir))


    def UpdateTargetFileType_ConvertFrom(self, fType):
        self.currentFileType_ConvertFrom = fType
        self.filesToConvert = self.GetFilesFromFolder(fType, self.targetDir)

        self.PopulateListBox_TargetFiles(self.filesToConvert)

        #update config file so we remember our setting next time we open the program
        self.parent.UpdateConfigFile("UserInfo", "lastfiletoconvertfrom", self.currentFileType_ConvertFrom)

        #self.UpdateListbox()

    def UpdateTargetFileType_ConverTo(self, fType):
        self.currentFileType_ConvertTo = fType

        #update config file so we remember our setting next time we open the program
        self.parent.UpdateConfigFile("UserInfo", "lastfiletoconvertto", self.currentFileType_ConvertTo)

    # def UpdateListbox(self, fType = None):
    #     if fType is None:
    #         fType = self.currentFileType_ConvertFrom

    #     self.PopulateListBox_TargetFiles(self.GetFilesFromFolder(fType,
    #                                                              self.targetDir))

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
            #find out how to get parent's config variable
            self.parent.UpdateConfigFile("UserInfo", "lastopendir", dirName)

        return dirName


if __name__ == "__main__":
    # ROOT = tkinter.Tk()
    # KritaConverterWindow(ROOT).grid(sticky = tkinter.NSEW)
    # ROOT.mainloop()


    app = MassImageConverterApp(None)
    app.title("Mass Image Converter")
    app.protocol("WM_DELETE_WINDOW", app.OnCloseWindow)
    app.mainloop()
