
def log(info: str, file_name:str):
    """
    Log when a request was made to OSV and what the request was
    """
    with open("./docs/log.log", "a") as a:
        a.write(info + "\n")
    
    print(file_name + "\n" + info + "\n\n")