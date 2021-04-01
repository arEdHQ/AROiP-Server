def merge(update, serverShadow, serverCopy):
    new_serverCopy = threeWayMerge(update, serverCopy, serverShadow)
    serverUpdate = diff(serverShadow, new_serverCopy)
    serverShadow = new_serverCopy

    return serverUpdate, serverShadow, new_serverCopy


def diff(serverShadow, serverCopy):
    isUpdated = False
    update = {}
    for field in serverCopy:
        if serverCopy[field] != serverShadow[field]:
            update[field] = serverCopy
            isUpdated = True

    if isUpdated:
        return update
    return None


def threeWayMerge(update, serverShadow, serverCopy):
    for field in update:
        if serverCopy[field] == serverShadow[field]:
            # TODO if the change is a structural change
                # change will be rejected if there is another
                # positional change on the same ar model
            serverCopy[field] = update[field]
        else:
            # TODO if the change is a state change, server loses
            # TODO add priority
            continue

    return serverCopy
