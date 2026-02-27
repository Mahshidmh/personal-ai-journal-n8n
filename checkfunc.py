def ifGoodOrBad(text):
    textIntoList=text.lower().split()
    negative_words = ["bad","shit","not good"]
    positive_words = ["good","love","nice"]
    negative=0
    positive=0
    for i in textIntoList:
        if i in negative_words:
            negative += 1 
        elif i in positive_words:
            positive += 1
    print(f"Negativity: {negative}")
    print(f"Positivity: {positive}")
    return        
text ="I love coding because it so good!"
ifGoodOrBad(text)

    
