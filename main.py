import string
from TextFromWebPage import text
from bs4 import BeautifulSoup
# TODO, AMENDMENT, FIND A WAY TO GET ALL PREMARKET STOCKS ONLY, SO ONCE YOU SEE A 930 TIMESTAMP YOU STOP
text = text

# do this, then check finviz to make sure that it's greater than 20/15 dollars
stock_set = set()
lowercase_alphabets = string.ascii_lowercase
uppercase_alphabets = string.ascii_uppercase

for i in range(0, len(text)):
    if text[i] == "$": #print until you see a blank space
        stock_string = ""
        for m in range(0, 20):
            if text[i+m+1] in lowercase_alphabets or text[i+m+1] in uppercase_alphabets:
                if text[i+m+1] != "":
                    stock_string = stock_string + text[i + m + 1].upper() # disregard the "$" sign
                else:
                    stock_set.add(stock_string)
                    break
            else:
                stock_set.add(stock_string)
                break
#for stock in stock_set:
#    print(stock)

