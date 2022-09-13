import getopt
import sys
import os
import re
import shutil
import tempfile
import subprocess

from git import Repo
from os.path import exists

PROGRAM = "docBuilder.py"
VERSION = '0.1'
        
def runBuilder(args):

    cachedFiles = {}
    errorState = None

    reTemplateExcerpt = r'.*?\[excerpt](.+)\[\/excerpt]'
    reStartExcerpt  =  r'.*?\[excerpt\s*(.+)\]'
    reEndExcerpt = r'.*?\[\/excerpt\s*(.+)\]'
    reExcerpt = f"{reStartExcerpt}|{reEndExcerpt}"
        
    accumulatedOutput = []
    completedExcerptsMap = {}
    openExcerptsMap = {}
    filesToSearchMap = {}
    repoPath = "" 
    outputPath = ""
    repoGitUrl = ""
    templateFile = ""
    buildScriptFile = ""
    verbose = False
    strip = False
    gitPull = False
    useTempDir = False
    repoGitBranch = "main"

    def getFileLines(fileName, cache=False): # cache would be for when getting data from git
        errorMsg = None
        try:
            cachedLines = cachedFiles.get(fileName)
            if cachedLines:
                return cachedLines, errorMsg
            else:
                fileLines = []
                if repoPath != "":
                    filePath = os.path.join(repoPath, fileName)
                    with open(filePath, 'r', encoding='UTF-8') as file:
                        while (bool(lineIn := file.readline())):
                            line = lineIn.rstrip()
                            fileLines.append(line)
                else:
                    errorMsg = f"unable to load file: {fileName}"
                
                if (errorMsg is None) and cache:
                    cachedFiles[fileName] = fileLines

                return fileLines, errorMsg
        except Exception as e:
                msg = str(e)
                errorMsg = f"Error occured in getFileLines: {msg}"
        return [], errorMsg
            

    def saveTextFile(fileText, outPath):
        vPrint(f"Saving to : {outPath}")
        errorMsg = None
        try:
            with open(outPath, 'w') as f:
                f.write(fileText)
        except Exception as e:
                msg = str(e)
                errorMsg = f"Error occured when saving output file. {msg}"
        errorMsg
            

    def vPrint(str):
        if verbose:
            print(f"{str}\n")
            

    vPrint (f'ARGV: {args}')

    try: 
        options, remainder = getopt.getopt(args, 'c:g:pt:o:sb:vhq', ['codepath=', 
                                                            'gitrepo=',
                                                            'gitpull',
                                                            'template=',
                                                            'outputpath=',
                                                            'strip',
                                                            'buildscript=',
                                                            'version',
                                                            'help',
                                                            'verbose',
                                                            ])
        for opt, arg in options:
            if opt in ('-c', '--codepath'):
                repoPath = arg            
            elif opt in ('-g', '--gitrepo'):
                repoGitUrl = arg
            elif opt in ('-p', '--gitpull'):
                gitPull = True
            elif opt in ('-b', '--buildscript'):
                buildScriptFile = arg
            elif opt in ('-t', '--template'):
                templateFile = arg            
            elif opt in ('-o', '--outputpath'):
                outputPath = arg
            elif opt in ('-s', '--strip'):
                strip = True
            elif opt in ('-v', '--version'):
                errorState = f"Version: {PROGRAM}: {VERSION}"
            elif opt in ('-h', '--help'):
                usageLines = ["usage", "programName.py",
                "Probably easiest to edit docBuilderHelper.py and run that instead"
                "options: ", 
                "-c, --codepath : the local path to code repository. (one, and only one, required from --gitrepo or --codepath).  Alternatively set env variable NORSK_SAMPLE_CODE_PATH",
                "-g, --gitrepo: the url to git repo to extract code examples from. (one, and only one, required from --gitrepo or --codepath).  --templateFile in this case must be complete file path.  Alternatively set env variable NORSK_SAMPLE_CODE_GIT_URL",
                "-p, --gitpull: only used with --codepath, when that directory is a git repo",
                "-t, --template: the file into which excerpts should be inserted.  This can be complete path, otherwise assumed to be in --codepath (required)",
                "-o, --outputpath: directory to save output files into(required). Alternatively set env variable NORSK_SAMPLE_OUTPUT_PATH",
                "-s, --strip: Strips files listed in template file of [excerpt] markup and copies to --outputpath directory.",
                "-b, --buildscript: bash script to run after stripping code files.  Script file copied into parent of outputpath. Either a complete path or codepath is assumed.",
                "-v, --version: prints version of this program (the program does not execute when this option is provided)",
                "-h, --help: displays this usage text (the program does not execute when this option is provided)"
                ]
                errorState = "\n".join(usageLines)            
            elif opt in ('-q', '--verbose'):
                verbose = True
    
    except Exception as e:
        errorState = f"Not happy with the options passed in:\n {e}\n"


    if repoPath:
        repoPath = os.path.abspath(repoPath)
    if outputPath:
        outputPath = os.path.abspath(outputPath)
    if templateFile and "/" in templateFile:
        templateFile = os.path.abspath(templateFile)
    
    vPrint ("Options:")
    vPrint (f"repoPath: {repoPath}")
    vPrint (f"repoGitUrl: {repoGitUrl}")
    vPrint (f"repoGitBranch: {repoGitBranch}")
    vPrint (f"templateFile: {templateFile}")
    vPrint (f"outputPath: {outputPath}")
    vPrint (f"strip: {strip}")
    vPrint (f"buildscript: {buildScriptFile}")
    vPrint (f"verbose: {verbose}")

    if errorState is None:    
        if repoPath and not(os.path.isdir(repoPath)):
            errorState = f"Unable to access code path: {repoPath}"

        if not outputPath:
            errorState = "--outputpath must be specified"
        else:
            if outputPath == repoPath:
                errorState = f"Repo path and output path should not be the same {outputPath} otherwise files may be overwritten"
            elif not(os.path.isdir(outputPath)):
                errorState = f"Unable to access output path: {outputPath}"

        if repoPath:       
            if repoGitUrl:
                errorState = "Only ONE of --gitrepo or --codepath should be provided"

        else:
            if repoGitUrl:
                # Create temporary dir
                repoPath = tempfile.mkdtemp()
                vPrint (f"Created temp dir: {repoPath}")
                useTempDir = True
            
            else:    
                errorState = "One of --gitrepo or --codepath must be provided"

    if errorState is None:    
        if not templateFile:
            errorState = f"--template must be supplied"
        elif "/" in templateFile:
            templateFilePath = templateFile
            revStr = templateFile[::-1]
            x = revStr.find("/")
            s = revStr[0:x]
            templateFile = s[::-1]            
        else:
            templateFilePath = os.path.join(repoPath, templateFile)
        
        
    if errorState is None and not exists(templateFilePath):
        errorState = f"template file does not exist: {templateFilePath}"
            
    if errorState is None : 
        if gitPull:
            try:
                repo = Repo(repoPath) 
                repo.remotes.origin.pull() 
                # checkout specific branch?     
                vPrint (f"Pulling from git: {repo.remotes.origin.name}")
                
            except Exception as e:
                msg = str(e)
                errorState = f"Error occured when pulling from git repo {repoPath}. Error: {msg}"

        elif repoGitUrl:
            try:
                if useTempDir:   # we actually need to check if git initialised yet tk
                    vPrint (f"Cloning from git: {repoGitUrl}")
                    repo = Repo.clone_from(repoGitUrl, repoPath, branch=repoGitBranch, depth=1)
                    
            except Exception as e:
                msg = str(e)
                errorState = f"Error occured when cloning from git repo {repoGitUrl}.  Error: {msg}"


    if errorState is None :
        # open the template file and get a list of files that excerpts need to be retrieved from 
                
        fileLines, errorState = getFileLines(templateFilePath, True)
        numLines = len(fileLines)
        lineIndex = 0
        while ((lineIndex < numLines) and (errorState is None)):
            line = fileLines[lineIndex]
            lineIndex += 1

            match = re.search(reTemplateExcerpt, line)
            if match:
                excerptContents = match.groups()[0]
                vPrint(f"found, {excerptContents}")
                # add this file to the map, if it does not already exist
                splitDetails = excerptContents.split(",")
                if len(splitDetails) == 2:
                    codeFile = splitDetails[0].strip()
                    excerptID = splitDetails[1].strip()
                    excerptKey = ":".join([codeFile, excerptID])
                        
                    vPrint(f"excerpt key is : {excerptKey}")

                    existingExcerpts = filesToSearchMap.get(codeFile)
                    excerpts = [excerptKey]
                    if existingExcerpts: 
                        vPrint(f"Existing excerpts: {existingExcerpts}")
                        existingExcerpts.append(excerptKey)
                    else: 
                        filesToSearchMap[codeFile] = excerpts

                else:
                    errorState = f"Could not split contents of excerpt tag {excerptContents}"

        vPrint("Iterating map")

        if errorState is None:
        
            for i in filesToSearchMap:
                extracts = filesToSearchMap.get(i)
                vPrint(f"file: {i}, excerpts: {extracts}")

            #  we have a list of files to extract excerpts from
            for codeFile in filesToSearchMap:
                codeFilePath = os.path.join(repoPath, codeFile)
                
                fileLines, errorState = getFileLines(codeFilePath, strip) # if stripping coode files then keep in cache
                numLines = len(fileLines)
                lineIndex = 0
                while ((lineIndex < numLines) and (errorState is None)):
                    line = fileLines[lineIndex]
                    lineIndex += 1
                
                    match = re.search(reStartExcerpt, line)
                    if match:
                        excerptContents = match.groups()[0]
                        excerptID = excerptContents.strip()
                        excerptKey = ":".join([codeFile, excerptID])
                        
                        vPrint(f"Start excerpt for {excerptContents}")
                        # add excerpt id to openExcerptsMap
                        openExcerpt = openExcerptsMap.get(excerptKey)
                        if openExcerpt: 
                            msg = (f"openExcerpt: {excerptKey} already exists.  You may have meant to close the excerpt, but forgor the leading slash")
                            errorState = msg
                        else: 
                            # check that this excerptID is not in the closed map
                            closedExcerpt = completedExcerptsMap.get(excerptKey)
                            if closedExcerpt: 
                                msg = (f"closedExcerpt: {excerptKey} already exists in completed map")
                                errorState = msg
                            else: 
                                vPrint(f"adding excerptKey: {excerptKey}")
                                openExcerptsMap[excerptKey] = []

                    else:
                        match = re.search(reEndExcerpt, line)
                        if match:
                            excerptContents = match.groups()[0]
                            excerptID = excerptContents.strip()                                
                            excerptKey = ":".join([codeFile, excerptID])
                        
                            vPrint(f"End excerpt for {excerptKey}")
                            openExcerptLines = openExcerptsMap.get(excerptKey)
                            if openExcerptLines: 
                                completedExcerptsMap[excerptKey] = openExcerptLines
                                del openExcerptsMap[excerptKey]
                            else:
                                msg = (f"openExcerpt: {excerptKey} could not be found - probably never opened in the first place)")
                                errorState = msg 

                        else:
                            # add this line to any open excerpts
                            for exKey in openExcerptsMap:
                                openExcerptsMap[exKey].append (line)

        if errorState is None: 

            # all code files have been read and excerpts extracted - check that there are no open excerpts left
            if len(openExcerptsMap) > 0: 
                stillOpenList = []
                for k in openExcerptsMap.keys():
                    stillOpenList.append (k)
                
                keyStr = ", ".join(stillOpenList)
                    
                errorState = f"The following excerpts were not correctly closed: {keyStr}"
        
        if errorState is None: 
            '# now iterate through the user guide creating another copy with extracts inserted'
            fileLines, errorState = getFileLines(templateFilePath)
            numLines = len(fileLines)
            lineIndex = 0
            while ((lineIndex < numLines) and (errorState is None)):
                line = fileLines[lineIndex]
                lineIndex += 1
            
                match = re.search(reTemplateExcerpt, line)
                if match:
                    excerptContents = match.groups()[0]
                    vPrint(f"found, {excerptContents}")
                    # add this file to the map, if it does not already exist
                    splitDetails = excerptContents.split(",")
                    if len(splitDetails) == 2:
                        codeFile = splitDetails[0].strip()
                        excerptID = splitDetails[1].strip()
                        excerptKey = ":".join([codeFile, excerptID])
                        
                        vPrint(f"excerpt key is : {excerptKey}")
                        # copy over the contents of this excerpt into the accumulator
                        excerptLines = completedExcerptsMap.get(excerptKey)
                        if excerptLines:
                            for l in excerptLines:
                                accumulatedOutput.append(l)
                        else:
                            errorState = f"could not find excerpt contents for {excerptKey}"
                        
                    else:
                        errorState = f"Could not split contents of excerpt tag {excerptContents} this would be unusual as we have already iterated over this file"
                else:
                    # append this line to the accumulator
                    accumulatedOutput.append(line)

        if errorState is None:
            guideStr = "\n".join(accumulatedOutput)
            codeFilePath = os.path.join(outputPath, templateFile)
            errorState = saveTextFile(guideStr, codeFilePath)

            if errorState is None:
                if strip: 
                    excerptFilter = lambda l: not(bool(re.search(reExcerpt, l)))
                    for codeFile in filesToSearchMap:
                        vPrint(f"stripping {codeFile}")
                        if errorState is None:
                            codeFilePath = os.path.join(repoPath, codeFile)
                    
                            codeLines, errorState = getFileLines(codeFilePath)
                            strippedLines = list(filter(excerptFilter, codeLines))
                            strippedText = "\n".join(strippedLines)
                            outPath = os.path.join(outputPath, codeFile)
                            vPrint(f"Saving stripped file to {outPath}")
                            errorState = saveTextFile(strippedText, outPath)

                    # if script building needed
                    if errorState is None:
                        if exists(templateFilePath):
                            buildScriptPath = buildScriptFile                                   
                            
                            if strip and buildScriptFile:
                                if ("/" in buildScriptFile):
                                    revStr = buildScriptFile[::-1]
                                    x = revStr.find("/")
                                    s = revStr[0:x]
                                    buildScriptFile = s[::-1]

                                else:
                                    buildScriptPath = os.path.join(repoPath, buildScriptFile)
                                
                                buildScriptPath = os.path.abspath(buildScriptPath)
                                if os.path.isfile(buildScriptPath):
                                    # copy this file over to output parent directory and run it'
                                    revStr = outputPath[::-1]
                                    slashPos = revStr.find("/")
                                    pathLen = len(outputPath) - slashPos
                                    buildTargetPath = outputPath[0:pathLen]
                                    
                                    if os.path.isdir(buildTargetPath):
                                        deployedScript = os.path.join(buildTargetPath, buildScriptFile)
                                        if not buildScriptPath == deployedScript:
                                            shutil.copy(buildScriptPath, deployedScript)  
                                        
                                        if os.path.isfile(deployedScript):    
                                            vPrint(f"buildTargetPath: {buildTargetPath}")
                                            try:                                       
                                                result = subprocess.run(['sh', deployedScript], cwd=buildTargetPath, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                                                vPrint(f"Result: {result.stdout}")
                                                vPrint(f"Result: {result.stderr}")
                                            except Exception as e:
                                                errorState = (f"template was processed successfully  but could not execute script at: {deployedScript}\n Error:  {e}")
                                                
                                    else:
                                        errorState = (f"template was processed successfully  but could not find build builder file  {buildTargetPath}")
                                        
                                else:
                                    errorState = (f"template was processed successfully  but could not find build script file in  {buildScriptPath}")
                                
                            # if strip option specified then perhaps execute build on output path
                        else:
                            errorState = (f"FAILED. Output file not found in {templateFilePath}")
                


    if useTempDir:
        # Remove temporary dir used for repository clone
        shutil.rmtree(repoPath)

    if errorState is None:
        print ("Ok")

    else:
        print(errorState)
    
    return errorState
        

if __name__ == "__main__":
    runBuilder(sys.argv[1:])
