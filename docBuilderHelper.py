from math import fabs
import subprocess
import os
import docBuilder
import shutil

from os.path import exists

    
if __name__ == "__main__":
    
    # REQUIRED settings
    codePath = os.path.abspath(r"../../norsk/client/media-test")
    outputPath = os.path.abspath(r"./test/output") #will be deleted (then recreated) if it exists and buildScriptFile != ""
    templateFile = "../../norsk/client/docs/index2.html"
    
    # OPTIONal settings
    gitURL = "" # eg:    r"git@github.com:Tweega/CodeExamples.git"
    help = False
    verbose = False
    strip = True  # strips code sample files of [Example] markup and copies to outputPath
    doGitPull = False
    buildScriptFile = "../../norsk/client/run-demo2"    # strip needs to be true.  Assumed to be in codePath if path not specified.  If found, will be copied to parent of output path and  executed
    












    ##### Run docBuilder with provided settings
    templatePath = templateFile
    if "/" in templateFile:
        templateFilePath = os.path.join(codePath, templateFile)
            

    options = ["--codepath", codePath, "--outputpath", outputPath, "--template", templateFile]
    
    if gitURL:
        options.append("--gitrepo")
        options.append(gitURL)

    if help:
        options.append("--help")
        
    if doGitPull:
        options.append("--gitpull")
        
    if verbose:
        options.append("--verbose")

    if strip:
        options.append("--strip")
    
    
    res = docBuilder.runBuilder(options)

    if res is None:
        if exists(templatePath):
            print("Success")
            buildScriptPath = buildScriptFile                                   
            
            if strip and buildScriptFile:
                if ("/" in buildScriptFile):
                    revStr = buildScriptFile[::-1]
                    x = revStr.find("/")
                    s = revStr[0:x]
                    buildScriptFile = s[::-1]

                else:
                    buildScriptPath = os.path.join(codePath, buildScriptFile)
                
                buildScriptPath = os.path.abspath(buildScriptPath)
                if os.path.isfile(buildScriptPath):
                    # copy this file over to output parent directory and run it'
                    revStr = outputPath[::-1]
                    slashPos = revStr.find("/")
                    pathLen = len(outputPath) - slashPos
                    buildTargetPath = outputPath[0:pathLen]
                    
                    if os.path.isdir(buildTargetPath):
                        deployedScript = os.path.join(buildTargetPath, buildScriptFile)

                        shutil.copy(buildScriptPath, deployedScript)  
                        
                        if os.path.isfile(deployedScript):    
                            try:                                       
                                result = subprocess.run(['sh', deployedScript], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                                print(f"Result:s {result.stdout}")
                            except Exception as e:
                                print(f"template was processed successfully  but could not execute script at: {deployedScript}")
                                print(f"Error: {e}")
                                
                    else:
                        print(f"template was processed successfully  but could not find build builder file  {buildTargetPath}")
                        
                else:
                    print(f"template was processed successfully  but could not find build script file in  {buildScriptPath}")
                
            # if strip option specified then perhaps execute build on output path
        else:
            print(f"FAILED. Output file not found in {templatePath}")
    else :
        print(res)
