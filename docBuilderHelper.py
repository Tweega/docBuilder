from math import fabs
import subprocess
import os
import docBuilder
import shutil

from os.path import exists

    
if __name__ == "__main__":
    
    # REQUIRED settings
    codePath = os.path.abspath(r"../../norsk/client/media-test")
    outputPath = os.path.abspath(r"../some_repo/client/media-test") #will be deleted (then recreated) if it exists and buildScriptFile != ""
    templateFile = "../../norsk/client/docs/index2.html"

    
    # OPTIONal settings
    gitURL = "" # eg:    r"git@github.com:Tweega/CodeExamples.git"
    help = False
    verbose = True
    strip = True  # strips code sample files of [Example] markup and copies to outputPath
    doGitPull = False
    buildScriptFile = "../../norsk/client/run-demo"   # strip needs to be true.  Assumed to be in codePath if path not specified.  If found, will be copied to parent of output path and  executed
    










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
    
    if buildScriptFile:
        options.append("--buildscript")
        options.append(buildScriptFile)

    











    ################ run the builder
    res = docBuilder.runBuilder(options)

    if res is None:
            print("Success")
    else :
        print(res)
