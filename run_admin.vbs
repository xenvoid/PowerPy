Set UAC = CreateObject("Shell.Application")
Set fso = CreateObject("Scripting.FileSystemObject")
scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
cmdArgs = "/k cd /d """ & scriptDir & """"
UAC.ShellExecute "cmd.exe", cmdArgs, "", "runas", 1