stable = 'scala-native-0.3.9'
latest = 'scala-native-0.4.0-SNAPSHOT'


def expand_all(arg):
    confs = []
    for choice in arg:
        expanded = expand_wild_cards(choice)
        if expanded is None:
            confs = [stable, latest]
        else:
            confs += [expanded]
    return confs


def expand_wild_cards(arg):
    if arg is None:
        return arg
    elif arg.startswith("latest"):
        return latest + arg[len("latest"):]
    elif arg.startswith("stable"):
        return stable + arg[len("stable"):]
    else:
        return arg