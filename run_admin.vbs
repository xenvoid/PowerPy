Set UAC = CreateObject("Shell.Application")
UAC.ShellExecute "cmd.exe", "/k C:\Users\xenvo\Pythonprojects\powerpy", "", "runas", 1