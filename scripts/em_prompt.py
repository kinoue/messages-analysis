def prompt_char(prompt, options):
    var = ""
    input_prompt = "%s [%s]: " % (prompt, ",".join(list(options) + ['q']))
    while not var in options:
        var_str  = raw_input(input_prompt)
        if var_str.lower() == 'q':
            exit()
        var = var_str.lower()
    return var

## TODO Add type check!!

def prompt_int(prompt, min, max):
    var = -1
    input_prompt = "%s [%d-%d,q]: " % (prompt, min, max)
    while not min <= var <= max:
        var_str  = raw_input(input_prompt)
        if str(var_str).lower() == 'q':
            exit()
        try:          
            var = int(var_str)
        except:
            pass
    return var