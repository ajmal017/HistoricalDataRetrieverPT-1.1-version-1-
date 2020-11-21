import pandas as pd
import matplotlib.pyplot as plt
excelDF = pd.read_excel("C:\\Users\\rohit kurup\\Documents\\PlayType-1Point1(2ndNovTo20thNov2020)(StocksFrom21stTo25thSept)Test1.xlsx")
numbers = excelDF['Real%change'].values
counter = 0
graphList = []
for i in numbers:
    counter = counter + i
    graphList.append(counter)

plt.plot(graphList)
plt.show()