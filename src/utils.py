def user_type(login):
    if login.startswith("TI"):
        return 'ti'
    elif login.startswith("eB"):
        return 'eb'
    else:
        return 'other'


def is_student(login):
    return user_type(login) != 'other'
