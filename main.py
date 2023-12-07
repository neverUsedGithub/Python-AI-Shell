from llm import gpt4all
from sty import fg # type: ignore
import subprocess
import time
import sys
import os

start = time.time()
print(fg.li_green + "Loading model... (this may take a while)" + fg.li_blue)
model = gpt4all.Model()
print(fg.li_green + f"Loaded model in {round(time.time() - start, 2)}s.")

sys_prompt = ""
with open("prompt.txt", "r") as f:
    sys_prompt = f.read()

sys_prompt = sys_prompt \
    .replace("{PLATFORM}", sys.platform) \
    .replace("{PWD_COMMAND}", "cd" if sys.platform == "win32" else "pwd") \
    .replace("{LS_COMMAND}", "dir" if sys.platform == "win32" else "ls") \
    .replace("{MAKE_FILE_COMMAND}", "echo. >" if sys.platform == "win32" else "touch")

model.set_system_prompt(sys_prompt)
model.chat_start()

while True:
    try:
        user_input = input(fg.li_yellow + f"({os.getcwd()}) ? ")
    except KeyboardInterrupt:
        break
    
    command = ""

    if user_input in [ "quit", "exit" ]:
        break

    start = time.time()
    is_first_token = True

    print(fg.li_green + f"> ", end="", flush=True)
    for tok in model.chat_generate(prompt=user_input, temp=0, max_tokens=64):
        if is_first_token:
            print(f"\r({round(time.time() - start, 2)}s) > ", end="", flush=True)
            is_first_token = False

        tok = tok \
            .replace("`", "") \
            .replace("\n", "") \
            .replace("\t", "")

        print(tok, end="", flush=True)
        command += tok
    print()

    if command.startswith("rm"):
        yn = input(fg.li_red + "! do you want to execute this command? " + fg.li_yellow)

        if yn.lower() not in [ "y", "yes", "yea", "yep", "yeah" ]:
            continue
    
    if command.startswith("cd"):
        path = command[3:]
        os.chdir(os.path.join(os.getcwd(), path))
    elif command in [ "quit", "exit" ]:
        break
    else:
        try:
            proc = subprocess.Popen(command, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE, encoding="utf-8")
            retcode = proc.wait()

            if retcode == 0 and proc.stdout:
                output = proc.stdout.read()
                print(fg.li_green + output + fg.rs)
                model.chat_add_message("system", "(SUCCESS) Output: ```\n" + output + "\n```")
            elif retcode != 0 and proc.stderr:
                output = proc.stderr.read()
                print(fg.li_red + output + fg.rs)
                model.chat_add_message("system", "(FAILURE) Only run this command again if you modify it. Output: ```\n" + output + "\n```")
        except subprocess.CalledProcessError as e:
            print(fg.li_red + "command failed with unknown error" + fg.rs)