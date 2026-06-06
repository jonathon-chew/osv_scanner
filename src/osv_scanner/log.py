
def log(info: str):
    with open("./docs/log.log", "a") as a:
        a.write(info + "\n")