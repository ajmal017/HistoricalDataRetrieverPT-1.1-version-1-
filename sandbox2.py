import pandas as pd
import matplotlib.pyplot as plt
excelDF = pd.read_excel("C:\\Users\\rohit kurup\\Documents\\19thOctTILL21stOCtType-1.xlsx")
numbers = excelDF['Real%change'].values
counter = 0
graphList = []
for i in numbers:
    counter = counter + i
    graphList.append(counter)

plt.plot(graphList)
plt.show()