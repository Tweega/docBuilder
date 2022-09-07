import os
import docBuilder
import shutil
import re
from os.path import exists

# TO ONLY RUN A SINGLE TEST, set RUN_ALL to False (around line 50) and set the ...Or False.. clause for the test in questiong to True
# The contents of the test output folder are deleted just prior to running any test.  To inspect a particular test's output, only run that test.
## the last test to run is the most complete test so on a full test there will be something to inspect after RUN_ALL

def mkdir(path):
    if not exists(path):
        os.makedirs(path)


def getFileLines(fileName):
    errorMsg = None
    try:
        fileLines = []
        if repoPath != "":
            filePath = os.path.join(repoPath, fileName)
            with open(filePath, 'r', encoding='UTF-8') as file:
                while (bool(lineIn := file.readline())):
                    line = lineIn.rstrip()
                    fileLines.append(line)
        else:
            errorMsg = f"unable to load file: {fileName}"
        return fileLines, errorMsg
    except Exception as e:
            msg = str(e)
            errorMsg = f"Error occured in getFileLines: {msg}"
    return [], errorMsg
        


def deleteFolder(folder):
    errMsg = None
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            errMsg =  'Failed to delete %s. Reason: %s' % (file_path, e)
    return errMsg    

if __name__ == "__main__":
    ## these are not unit tests as the interpolator relies mainly on side effects

    RUN_ALL = True
    ONLY_SHOW_FAILURES = False
    repoPath = os.path.abspath(r"./test/sampleCode/withGit/CodeExamples")
    nonGitRepoPath = os.path.abspath(r"./test/sampleCode/noGit/CodeExamples")
    testOutPath = os.path.abspath(r"./test/output")

    mkdir(testOutPath)

    testOutPathNotExist = os.path.join(repoPath, "output", "DoesNotExist")
    gitURLPublic = r"git@github.com:Tweega/CodeExamples.git"
    gitURLPrivate = r"git@github.com:Tweega/CodeInterpolationtest.git"
    gitURLDoesNotExist = r"git@github.com:Tweega/DoesNotExist.git"
    
    templateFile = "media_proto.html"
    relTemplateFile = "./test/sampleCode/noGit/CodeExamples/" + templateFile
    relOutPath = "./test/output"
    relCodePath = "./test/sampleCode/noGit/CodeExamples"

    tFile = os.path.join(repoPath,  templateFile)

    errorState = deleteFolder(testOutPath)

    successes = []
    failures = []

    if errorState is None:
        print ("tests for docBuilder.py")
        
        reason = "Version: docBuilder.py: 0.1"
        if RUN_ALL or False:
            res = docBuilder.runBuilder(["--version"])
            if res == reason:
                successes.append(f"{reason} PASSED")
            else :
                failures.append(f"{reason} FAILED.  Got: {res}")


        reason = "--Help returns usage"
        if RUN_ALL or False:
            res = docBuilder.runBuilder(["--help"])
            err = "usage"
            strLen = len(err)
            if res is not None and res[0:strLen] == err:
                successes.append(f"{reason} PASSED")
            else :
                failures.append(f"{reason} FAILED.  Got: {res[0:strLen]}")

        
        reason = "One of --gitrepo or --repopath must be provided"
        if RUN_ALL or False:
            res = docBuilder.runBuilder(["--template", tFile])
            if res == reason:
                successes.append(f"{reason} PASSED")
            else :
                failures.append(f"{reason} FAILED.  Got: {res}")


        reason = "--outputpath must be specified"
        if RUN_ALL or False:
            res = docBuilder.runBuilder(["--codepath", repoPath, "--template", tFile])
            if res == reason:
                successes.append(f"{reason} PASSED")
            else :
                failures.append(f"{reason} FAILED.  Got: {res}")
        
        reason = "--template must be supplied"
        if RUN_ALL or False:
            res = docBuilder.runBuilder(["--codepath", repoPath, "--outputpath", testOutPath])
            if res == reason:
                successes.append(f"{reason} PASSED")
            else :
                failures.append(f"{reason} FAILED.  Got: {res}")


        reason = "--output path must be valid"
        if RUN_ALL or False:
            res = docBuilder.runBuilder(["--codepath", repoPath, "--outputpath", testOutPathNotExist, "--template", templateFile])
            err = "Unable to access output path:"
            strLen = len(err)
            if res is not None and res[0:strLen] == err:
                successes.append(f"{reason} PASSED")
            else:
                failures.append(f"{reason} FAILED.  Got: {res}")


        reason = "--repo path must be valid"
        if RUN_ALL or False:
            res = docBuilder.runBuilder(["--codepath", testOutPathNotExist, "--outputpath", testOutPath, "--template", tFile])
            err = "Unable to access code path:"
            strLen = len(err)
            if res is not None and res[0:strLen] == err:
                successes.append(f"{reason} PASSED")
            else :
                failures.append(f"{reason} FAILED.  Got: {res}")
                
                

        reason = "template file must be valid"
        if RUN_ALL or False:
            res = docBuilder.runBuilder(["--codepath", repoPath, "--outputpath", testOutPath, "--template", "doesNotExist"])
            err = "template file does not exist:"
            strLen = len(err)
            if res is not None and res[0:strLen] == err:
                successes.append(f"{reason} PASSED")
            else:
                failures.append(f"{reason} FAILED.  Got: {res}")

        
        reason = "Only ONE of --gitrepo or --repopath should be provided"
        if RUN_ALL or False:
            res = docBuilder.runBuilder(["--codepath", repoPath, "--gitrepo", gitURLPublic, "--outputpath", testOutPath, "--template", templateFile])
            if res is not None and res == reason:
                successes.append(f"{reason} PASSED")
            else :
                failures.append(f"{reason} FAILED.  Got: {res}")

        reason = "template gets processed when repoPath is NOT a git repo)"
        if RUN_ALL or False:
            deleteFolder(testOutPath)
            res = docBuilder.runBuilder(["--codepath", nonGitRepoPath, "--outputpath", testOutPath, "--template", templateFile])
            if res is None:
                filePath = os.path.join(testOutPath, templateFile)
                if exists(filePath):
                    successes.append(f"{reason} PASSED")
                else:
                    failures.append(f"{reason} FAILED. Template file not found in {filePath}")
            else :
                failures.append(f"{reason} FAILED.  Got: {res}")


        reason = "template file is processed to target (and local repo is NOT refreshed from git)"
        if RUN_ALL or False:
            errorState = deleteFolder(testOutPath)
            res = docBuilder.runBuilder(["--codepath", repoPath, "--outputpath", testOutPath, "--template", templateFile, "--verbose"])
            if res is None:
                filePath = os.path.join(testOutPath, templateFile)
                if exists(filePath):
                    successes.append(f"{reason} PASSED")
                else:
                    failures.append(f"{reason} FAILED. Template file not found in {filePath}")
            else :
                failures.append(f"{reason} FAILED.  Got: {res}")

        reason = "We can use a full template path in conjunction with --codepath)"
        if RUN_ALL or False:
            errorState = deleteFolder(testOutPath)
            res = docBuilder.runBuilder(["--codepath", repoPath, "--outputpath", testOutPath, "--template", tFile, "--verbose"])
            if res is None:
                filePath = os.path.join(testOutPath, templateFile)
                if exists(filePath):
                    successes.append(f"{reason} PASSED")
                else:
                    failures.append(f"{reason} FAILED. Template file not found in {filePath}")
            else :
                failures.append(f"{reason} FAILED.  Got: {res}")

        reason = "template file processed to target (and local repo is refreshed from git)"
        if RUN_ALL or False:
            errorState = deleteFolder(testOutPath)
            res = docBuilder.runBuilder(["--codepath", repoPath, "--gitpull", "--outputpath", testOutPath, "--template", tFile, "--verbose"])
            if res is None:
                filePath = os.path.join(testOutPath, templateFile)
                if exists(filePath):
                    successes.append(f"{reason} PASSED")
                else:
                    failures.append(f"{reason} FAILED. Template file not found in {filePath}")
            else :
                failures.append(f"{reason} FAILED.  Got: {res}")

        reason = "Public Git repo cloned to temp file and used for code sources"
        if RUN_ALL or False:
            errorState = deleteFolder(testOutPath)
            res = docBuilder.runBuilder(["--gitrepo", gitURLPublic, "--outputpath", testOutPath, "--template", tFile, "--verbose"])
            if res is None:
                filePath = os.path.join(testOutPath, templateFile)
                if exists(filePath):
                    successes.append(f"{reason} PASSED")
                else:
                    failures.append(f"{reason} FAILED. Template file not found in {filePath}")
            else :
                failures.append(f"{reason} FAILED.  Got: {res}")


        reason = "Private Git repo cloned to temp file and used for code sources"
        if RUN_ALL or False:
            errorState = deleteFolder(testOutPath)
            res = docBuilder.runBuilder(["--gitrepo", gitURLPublic, "--outputpath", testOutPath, "--template", tFile, "--verbose"])
            if res is None:
                filePath = os.path.join(testOutPath, templateFile)
                if exists(filePath):
                    successes.append(f"{reason} PASSED")
                else:
                    failures.append(f"{reason} FAILED. Template file not found in {filePath}")
            else :
                failures.append(f"{reason} FAILED.  Got: {res}")



        reason = "bad git url"
        if RUN_ALL or False:
            errorState = deleteFolder(testOutPath)
            res = docBuilder.runBuilder(["--gitrepo", gitURLDoesNotExist, "--outputpath", testOutPath, "--template", tFile, "--verbose"])
            
            err = "Error occured when cloning from git repo git@github.com:Tweega/DoesNotExist.git."
            strLen = len(err)
            if res is not None and res[0:strLen] == err:
                successes.append(f"{reason} PASSED")
            else :
                failures.append(f"{reason} FAILED.  Got: {res}")
            

        reason = "relative paths accepted for outputpath and codepath)"
        if RUN_ALL or False:
            
            deleteFolder(testOutPath)
            res = docBuilder.runBuilder(["--codepath", relCodePath, "--outputpath", relOutPath, "--template", templateFile, "--verbose"])
            if res is None:
                filePath = os.path.join(relOutPath, templateFile)
                if exists(filePath):
                    successes.append(f"{reason} PASSED")
                else:
                    failures.append(f"{reason} FAILED. Template file not found in {filePath}")
            else :
                failures.append(f"{reason} FAILED.  Got: {res}")

    
        reason = "relative path accepted for template file)"
        if RUN_ALL or False:
            deleteFolder(testOutPath)        
            res = docBuilder.runBuilder(["--codepath", nonGitRepoPath, "--outputpath", testOutPath, "--template", relTemplateFile])
            if res is None:
                filePath = os.path.join(testOutPath, templateFile)
                if exists(filePath):
                    successes.append(f"{reason} PASSED")
                else:
                    failures.append(f"{reason} FAILED. Template file not found in {filePath}")
            else :
                failures.append(f"{reason} FAILED.  Got: {res}")

        
    ############### short options form
        reason = "Template processed when repoPath is NOT a git repo)"
        if RUN_ALL or False:
            errorState = deleteFolder(testOutPath)
            res = docBuilder.runBuilder(["-c", nonGitRepoPath, "-o", testOutPath, "-t", templateFile])
            if res is None:
                filePath = os.path.join(testOutPath, templateFile)
                if exists(filePath):
                    successes.append(f"{reason} PASSED")
                else:
                    failures.append(f"{reason} FAILED. Template file not found in {filePath}")
            else :
                failures.append(f"{reason} FAILED.  Got: {res}")

        reason = "Template gets processed  (and local repo is NOT refreshed from git)"
        if RUN_ALL or False:
            errorState = deleteFolder(testOutPath)
            res = docBuilder.runBuilder(["-c", repoPath, "--o", testOutPath, "-t", templateFile, "-q"])
            if res is None:
                filePath = os.path.join(testOutPath, templateFile)
                if exists(filePath):
                    successes.append(f"{reason} PASSED")
                else:
                    failures.append(f"{reason} FAILED. Template file not found in {filePath}")
            else :
                failures.append(f"{reason} FAILED.  Got: {res}")


        reason = "We can use a full template path in conjunction with --codepath)"
        if RUN_ALL or False:
            errorState = deleteFolder(testOutPath)
            res = docBuilder.runBuilder(["-c", repoPath, "-o", testOutPath, "-t", tFile, "-q"])
            if res is None:
                filePath = os.path.join(testOutPath, templateFile)
                if exists(filePath):
                    successes.append(f"{reason} PASSED")
                else:
                    failures.append(f"{reason} FAILED. Template file not found in {filePath}")
            else :
                failures.append(f"{reason} FAILED.  Got: {res}")
                
                

        reason = "template file processed to target (and local repo is refreshed from git)"
        if RUN_ALL or False:
            errorState = deleteFolder(testOutPath)
            res = docBuilder.runBuilder(["-c", repoPath, "-p", "-o", testOutPath, "-t", tFile, "-q"])
            if res is None:
                filePath = os.path.join(testOutPath, templateFile)
                if exists(filePath):
                    successes.append(f"{reason} PASSED")
                else:
                    failures.append(f"{reason} FAILED. Template file not found in {filePath}")
            else :
                failures.append(f"{reason} FAILED.  Got: {res}")


        reason = "Git repo cloned to temp file and used for code sources"
        if RUN_ALL or False:
            erorState = deleteFolder(testOutPath)
            res = docBuilder.runBuilder(["-g", gitURLPublic, "-o", testOutPath, "-t", tFile, "-q"])
            if res is None:
                filePath = os.path.join(testOutPath, templateFile)
                if exists(filePath):
                    successes.append(f"{reason} PASSED")
                else:
                    failures.append(f"{reason} FAILED. Template file not found in {filePath}")
            else :
                failures.append(f"{reason} FAILED.  Got: {res}")


        reason = "stripped code files get copied into target folder"
        if RUN_ALL or False:
            errorState = deleteFolder(testOutPath)
            res = docBuilder.runBuilder(["-c", repoPath, "-s", "-o", testOutPath, "-t", templateFile, "--verbose"])
            if res is None:
                filePath = os.path.join(testOutPath, templateFile)
                # check that the file contains no [exceprt] tags
                lines, errMsg = getFileLines(filePath)
                if errMsg is None:
                    reExcerpt = r'excerpt'
                    reCodeFile = r'THIS IS FROM CODE FILE'

                    excerptFilter = lambda l: bool(re.search(reExcerpt, l))
                    excerptLines = list(filter(excerptFilter, lines))

                    if len(lines) < 10:
                        failures.append(f"{reason} FAILED. template file contains too few lines: {filePath}")
                    elif len(excerptLines) > 0:
                        failures.append(f"{reason} FAILED. template file contains excerpt markup: {filePath}")
                    else:
                        # check that processed file contains inserted code
                        
                        codeFilter = lambda l: bool(re.search(reCodeFile, l))
                        codeLines = list(filter(codeFilter, lines))
                        if len(codeLines) != 3:
                            failures.append(f"{reason} FAILED. processed template file missing lines {filePath}")

                        # now check that stripped files have been copied over
                        filePath = os.path.join(testOutPath, "proto_code.html")
                        lines, errMsg = getFileLines(filePath)
                        if errMsg is None:
                            excerptFilter = lambda l: bool(re.search(reExcerpt, l))
                            excerptLines = list(filter(excerptFilter, lines))

                            if len(lines) < 10:
                                failures.append(f"{reason} FAILED. stripped code file contains too few lines: {filePath}")
                            elif len(excerptLines) > 0:
                                failures.append(f"{reason} FAILED. stripped code file contains excerpt markup: {filePath}")
                            else:
                                filePath = os.path.join(testOutPath, "proto_code2.html")
                                lines, errMsg = getFileLines(filePath)
                                if errMsg is None:
                                    excerptFilter = lambda l: bool(re.search(reExcerpt, l))
                                    excerptLines = list(filter(excerptFilter, lines))

                                    if len(lines) < 10:
                                        failures.append(f"{reason} FAILED. stripped code file contains too few lines: {filePath}")
                                    elif len(excerptLines) > 0:
                                        failures.append(f"{reason} FAILED. stripped code file contains excerpt markup: {filePath}")
                                    else:
                                        successes.append(f"{reason} PASSED")
                        else :
                            failures.append(f"{reason} FAILED. Could not load lines from  {filePath}")
                else :
                    failures.append(f"{reason} FAILED. Could not load lines from  {filePath}")
            else :
                failures.append(f"{reason} FAILED.  Got: {res}")    


        reason = "dodgy options"
        if RUN_ALL or False:
            res = docBuilder.runBuilder(["--cosepath", repoPath, "--gitpull", "--outputpath", testOutPath, "--template", tFile, "--verbose"])
            err = "Not happy with the options passed in"
            strLen = len(err)
            if res is not None and res[0:strLen] == err and "cosepath" in res:
                successes.append(f"{reason} PASSED")
            else :
                failures.append(f"{reason} FAILED.  Got: {res}")
            

        reason = "dodgy options2"
        if RUN_ALL or False:
            res = docBuilder.runBuilder(["--codepath", repoPath, "--gitpull", "--outputpath", testOutPath, "--template", tFile, "--verbosely"])
            err = "Not happy with the options passed in"
            strLen = len(err)
            if res is not None and res[0:strLen] == err and "verbosely" in res:
                successes.append(f"{reason} PASSED")
            else :
                failures.append(f"{reason} FAILED.  Got: {res}")
            


        reason = "stripped code files get copied into target folder"
        if RUN_ALL or False:
            errorState = deleteFolder(testOutPath)
            res = docBuilder.runBuilder(["--codepath", repoPath, "--strip", "--outputpath", testOutPath, "--template", templateFile, "--verbose"])
            if res is None:
                filePath = os.path.join(testOutPath, templateFile)
                # check that the file contains no [exceprt] tags
                lines, errMsg = getFileLines(filePath)
                if errMsg is None:
                    reExcerpt = r'excerpt'
                    reCodeFile = r'THIS IS FROM CODE FILE'

                    excerptFilter = lambda l: bool(re.search(reExcerpt, l))
                    excerptLines = list(filter(excerptFilter, lines))

                    if len(lines) < 10:
                        failures.append(f"{reason} FAILED. template file contains too few lines: {filePath}")
                    elif len(excerptLines) > 0:
                        failures.append(f"{reason} FAILED. template file contains excerpt markup: {filePath}")
                    else:
                        # check that processed file contains inserted code
                        
                        codeFilter = lambda l: bool(re.search(reCodeFile, l))
                        codeLines = list(filter(codeFilter, lines))
                        if len(codeLines) != 3:
                            failures.append(f"{reason} FAILED. processed template file missing lines {filePath}")

                        # now check that stripped files have been copied over
                        filePath = os.path.join(testOutPath, "proto_code.html")
                        lines, errMsg = getFileLines(filePath)
                        if errMsg is None:
                            excerptFilter = lambda l: bool(re.search(reExcerpt, l))
                            excerptLines = list(filter(excerptFilter, lines))

                            if len(lines) < 10:
                                failures.append(f"{reason} FAILED. stripped code file contains too few lines: {filePath}")
                            elif len(excerptLines) > 0:
                                failures.append(f"{reason} FAILED. stripped code file contains excerpt markup: {filePath}")
                            else:
                                filePath = os.path.join(testOutPath, "proto_code2.html")
                                lines, errMsg = getFileLines(filePath)
                                if errMsg is None:
                                    excerptFilter = lambda l: bool(re.search(reExcerpt, l))
                                    excerptLines = list(filter(excerptFilter, lines))

                                    if len(lines) < 10:
                                        failures.append(f"{reason} FAILED. stripped code file contains too few lines: {filePath}")
                                    elif len(excerptLines) > 0:
                                        failures.append(f"{reason} FAILED. stripped code file contains excerpt markup: {filePath}")
                                    else:
                                        successes.append(f"{reason} PASSED")
                        else :
                            failures.append(f"{reason} FAILED. Could not load lines from  {filePath}")
                else :
                    failures.append(f"{reason} FAILED. Could not load lines from  {filePath}")
            else :
                failures.append(f"{reason} FAILED.  Got: {res}")    


        #RESULTS
        testCount = len(successes) + len(failures)
        if not(ONLY_SHOW_FAILURES):
            print (f"\nTest successes: {len(successes)} out of {testCount} that were run\n")
            for r in successes:
                print (r)
        
        if len(failures) > 0:
            for r in failures:
                print (r)
        
        print (f"\nTest failures: {len(failures)} out of {testCount} that were run\n")
    if not errorState is None:
        print(f"Error: {errorState}")

