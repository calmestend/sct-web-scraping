def parseText(element):
    element = element.replace('\u00a0', ' ')  
    element = element.replace('\r', '')  
    element = element.replace('\n', '')
    element = element.replace('\t', '') 
    element = ' '.join(element.split())  
    element = element.encode('utf-8').decode('utf-8')
    return element
