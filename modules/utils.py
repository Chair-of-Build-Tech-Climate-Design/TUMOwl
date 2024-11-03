
print("--> Importing Utility Functions from 'Utils'.")

def PrintLogSeperator(text: str = 'Separator'):
    width = 125
    print(width * '-')
    #print('{: ^{width}}'.format(text, width=width))
    print(text)
    print(width * '-')
    return