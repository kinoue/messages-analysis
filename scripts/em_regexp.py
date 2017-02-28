import re

def regexp(expr, item):
    if item:
        try:
            reg = re.compile(expr)
        except:
            print("error while compling the regexp: ", expr)
            return False

        try: 
            match = reg.search(item) 
            return match is not None
        except Exception as inst:
            print("error while searching", inst)
            print("type of the item: %s" % str(type(item)))
            print(type(inst))    # the exception instance
            print(inst.args)     # arguments stored in .args
            print(inst)       
            return False
    return False