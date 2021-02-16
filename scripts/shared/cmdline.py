stable = 'scala-native-0.4.0'
latest = 'scala-native-0.4.1-SNAPSHOT'
default_scala_version = "2.12"

def expand_all(arg):
    confs = []
    for choice in arg:
        expanded = expand_wild_cards(choice)
        if expanded is None:
            confs = list(map(add_version_suffix, [stable, latest]))
        else:
            confs += [expanded]
    return confs

def add_version_suffix(arg):
    return arg + "-" + default_scala_version

def expand_wild_cards(arg):
    if arg is None:
        return arg
    elif arg.startswith("latest"):
        return add_version_suffix(latest) + arg[len("latest"):]
    elif arg.startswith("stable"):
        return add_version_suffix(stable) + arg[len("stable"):]
    else:
        return arg