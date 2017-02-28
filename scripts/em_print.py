

def print_mention_list(mention_list, name=None, top_n=20):

    print("")
    print("Top %d %s mentioned in your messages:" % (top_n, name))

    for i, mention in enumerate(mention_list[:top_n]):
        print("%3d: %s (%d)" % (i, mention['pattern'], mention['count']))

    print("")
    total_count  = sum([c['count'] for c in mention_list])
    print("Number of mentions in total: %d" % total_count)

def print_mention(mention):

    print("")
    print("Messages that mentioned %s:" % mention['pattern'])

    for message in mention['messages']:
    	print_message(message)

def print_message(message):
	print(message.text)