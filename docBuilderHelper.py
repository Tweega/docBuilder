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
    buildScriptFile = "ljhj"    # strip needs to be true.  Assumed to be in codePath if path not specified.  If found, copies all files and subdirectories from codePath to output and runs this script in bash shell
    












    ##### Run docBuilder with provided settings
    templatePath = templateFile
    if "/" in templateFile:
        templateFilePath = os.path.join(codePath, templateFile)
            

    options = ["--codepath", codePath, "--outputpath", outputPath, "--template", templateFile]
    
    if len(gitURL) > 0:
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
    
    # this should be done in the docBuilder
    if exists(outputPath) and exists(codePath) and strip and buildScriptFile:    
        # copy over all code to output
        src_files = os.listdir(codePath)
        for file_name in src_files:
            full_file_name = os.path.join(codePath, file_name)
            if os.path.isfile(full_file_name):
                shutil.copy(full_file_name, outputPath)

    res = docBuilder.runBuilder(options)

    if res is None:
        if exists(templatePath):
            print("Success")
            if strip and len(buildScriptFile) > 0:
                if "/" in buildScriptFile:
                    buildScriptPath = buildScriptFile                                   
                else:
                    buildScriptPath = os.path.join(codePath, buildScriptFile)
                
                if exists(buildScriptPath):
                    # copy this file over to output and run it'
                    result = subprocess.run(["echo", "Hello, World!"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                    print(result.stdout)

            # if strip option specified then perhaps execute build on output path
        else:
            print(f"FAILED. Output file not found in {templatePath}")
    else :
        print(res)
