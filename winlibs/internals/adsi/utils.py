def escape_path(path):
    escapes = (
        ('\+','+'),
        ('\*','*'),
        ('\(','('),
        ('\)',')'),
        ('\/','/'),
        ('\\,',',,'),
        ('\\','\\5c'),
        ('*','\\2a'),
        ('(','\\28'),
        (')','\\29'),
        ('/','\\2f'),
        ('+','\\2b'),
        (chr(0),'\\00')
    )
    for char, escape in escapes:
        path = path.replace(char, escape)
    path = path.replace(",,","\\2c")
    return path
