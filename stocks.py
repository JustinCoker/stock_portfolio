import pandas as pd
from googlefinance import getQuotes

#initialize everything to 0, will receive confirmation
def restart():
    if input('THIS WILL ERASE EVERYTHING. Confirm? Y/N>').upper()=='Y':
        global columns
        global portfolio
        global cashval
        columns= ['Ticker', 'LastPrice', 'Shares', 'CostPer', 'Fees', 'TotalCost', 'Value', 'Gain/Loss', 'CashDividend']
        portfolio=pd.DataFrame(columns= columns)
        cashval=0


#%%
#adjust cash balance variable (e.g. deposit, withdrawal, cash dividend)
def cash(Amount):
    global cashval
    cashval=cashval+Amount #adds entered amount to cash balance (i.e. uses negative
                           #amount for withdrawal or purchase).

def getprice(symbol):
    return getQuotes(symbol)[0] #uses google finance API to return a dict of stock info

#initial purchase of shares
def buy(ticker, shares, cost): #ticker must be a string, shares and cost an int or float.
    global portfolio #the blank portfolio df
    data= getprice(ticker)#accesses stock info and saves it as a local var, data
    fees= 6.95 #all commissions currently set to $6.95.
    global info
    #info is used to populate the portfolio dataframe with entered or accessed info.
    info= [data['StockSymbol'], float(data['LastTradePrice']), shares, cost, fees] #((cost*shares)+fees), (float(data['LastTradePrice'])*shares), ]
    
    
    if len(portfolio.index.tolist())==0:
        editing_loc= 0 #edits the 1st line if df is empty
    else:
        editing_loc= max(portfolio.index.tolist())+1 #edits next blank row
             
    portfolio.loc[editing_loc,0:(len(info))]= info #adds info to the df
    calculate() #calls the calculate fn to populate calculated columns
    cash(-1*portfolio.loc[editing_loc,'TotalCost'])  #subtracts from cash 
    portfolio.loc[editing_loc,'CashDividend']=0 #sets cash dividend to initial 0.
    
   
#allows manual updates last price and recalculates calculated colujmns
def update():
    for i in range(len(portfolio.index.tolist())):
        portfolio.loc[i,'LastPrice']= float(getprice(portfolio['Ticker'].loc[i])['LastTradePrice'])
    calculate()

#performs calculations to populate calculated columns    
def calculate():
    portfolio['Value']= portfolio['LastPrice']*portfolio['Shares']
    portfolio['TotalCost']= (portfolio['Shares']*portfolio['CostPer'])+portfolio['Fees']
    portfolio['Gain/Loss']= portfolio['Value']-portfolio['TotalCost']

#allows manual editing certain vars. All else should be edited 
#through update() or calculate().
def edit(ticker, category):
    #sets the index to be edited based on Ticker symbol
    index= portfolio[portfolio['Ticker']==ticker].index.tolist()[0] 
    category= category.lower()
    
    if category== 'shares': #accesses the shares column
        #gets the new value from user input
        new= float(input('enter new shares for '+ ticker+ '>'))
        #gets the old value from df
        old= portfolio.loc[index, 'Shares']
        #confimration
        if input('Change '+ticker+' '+ category+' from '+str(old)+' to '+str(new)+'? Y/N>').upper()=='Y':
            portfolio.loc[index, 'Shares']= new
            print('Change Confirmed')
            
            
    elif category== 'costper': #accesses the costper column
        new= float(input('enter new cost per share for '+ ticker+ '>'))
        old= portfolio.loc[index, 'CostPer']
        if input('Change '+ticker+' '+ category+' from '+str(old)+' to '+str(new)+'? Y/N>').upper()=='Y':
            portfolio.loc[index, 'CostPer']= new
            print('Change Confirmed')
            
            
    elif category== 'fees': #accesses the Fees column
        new= float(input('enter new fees share for '+ ticker+ '>'))
        old= portfolio.loc[index, 'Fees']
        if input('Change '+ticker+' '+ category+' from '+str(old)+' to '+str(new)+'? Y/N>').upper()=='Y':
            portfolio.loc[index, 'Fees']= new
            print('Change Confirmed')
            
            
    elif category== 'cashdiv' or 'cashdividend': #accesses the Fees column
        new= float(input('enter new CashDividend for '+ ticker+ '>'))
        old= portfolio.loc[index, 'CashDividend']
        if input('Change '+ticker+' '+ category+' from '+str(old)+' to '+str(new)+'? Y/N>').upper()=='Y':
            portfolio.loc[index, 'CashDividend']= new
            print('Change Confirmed')
            print('!!!!!!!!!!!!!!!!!!!!!!!!!!!')
            print('EDIT CASH BALANCE MANUALLY!')
            
    calculate()
    
#enter cash dividend using ticker and amount.   
def CashDiv(ticker, amount):
    cash(amount) #adds to cash
    #sets index to be edited
    index= portfolio[portfolio['Ticker']==ticker].index.tolist()[0]
    #updates cash dividend column in df accordingly
    current_val= portfolio.loc[index, 'CashDividend']
    portfolio.loc[index, 'CashDividend']= current_val+amount


    
def test():
    cash(1000)
    buy('CSCO',10,50)
    buy('GOOG', 10, 20)