import pandas as pd
from googlefinance import getQuotes

#initialize everything to 0, will receive confirmation
def restart():
    if input('THIS WILL ERASE EVERYTHING. Confirm? Y/N>').upper()=='Y':
        global columns
        global portfolio
        global cashval
        columns= ['Ticker', 'LastPrice', 'Shares','DripShares', 'TotalShares', 'CostPer', 'Fees', 'TotalCost', 'Value', 'Cap_Gain/Loss_UNRL', 'CashDividend', 'DripValue', 'Net_Gain/Loss_UNRL', 'Realized_Gain/Loss', 'Total_Gain/Loss']
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
def initial_buy(ticker, shares, cost): #ticker must be a string, shares and cost an int or float.
    global portfolio #the portfolio df
    data= getprice(ticker)#accesses stock info and saves it as a local var, data
    fees= 6.95 #all commissions currently set to $6.95.
    global info
    #info is used to populate the portfolio dataframe with entered or accessed info.
    info= [data['StockSymbol'], float(data['LastTradePrice']), shares,0,0, cost, fees] #((cost*shares)+fees), (float(data['LastTradePrice'])*shares), ]
    
    
    if len(portfolio.index.tolist())==0:
        editing_loc= 0 #edits the 1st line if df is empty
    else:
        editing_loc= max(portfolio.index.tolist())+1 #edits next blank row
             
    portfolio.loc[editing_loc,0:(len(info))]= info #adds info to the df
    
    
    portfolio.loc[editing_loc,'CashDividend']=0 #sets cash dividend to initial 0.
    portfolio.loc[editing_loc,'DripShares']=0 #sets DRIP to initial 0.
    portfolio.loc[editing_loc,'Realized_Gain/Loss']=0 #sets to initial 0.
    portfolio.loc[editing_loc,'Total_Gain/Loss']=0 #sets DRIP to initial 0.
    calculate() #calls the calculate fn to populate calculated columns
    cash(-1*portfolio.loc[editing_loc,'TotalCost'])  #subtracts from cash 

def buy(ticker, shares, cost):
    if ticker not in portfolio['Ticker'].values: #checks if ticker is already in portfolio, if not, initial buy function is called.
        initial_buy(ticker, shares, cost)
    else:
        index= portfolio[portfolio['Ticker']==ticker].index.tolist()[0] #sets index for editing
        portfolio.loc[index, 'CostPer']= (portfolio.loc[index,'Shares']*portfolio.loc[index, 'CostPer']+shares*cost)/(portfolio.loc[index,'Shares']+shares)
        portfolio.loc[index,'Shares']= portfolio.loc[index,'Shares']+shares
        portfolio.loc[index, 'Fees']= portfolio.loc[index, 'Fees']+6.95 #accumulates 6.95 commission.
        calculate()
        cash(-1*(shares*cost)-6.95)  #subtracts from cash 
        
    
    update()
        

 
#allows manual updates last price and recalculates calculated colujmns
def update():
    for i in range(len(portfolio.index.tolist())):
        portfolio.loc[i,'LastPrice']= float(getprice(portfolio['Ticker'].loc[i])['LastTradePrice'])
    calculate()

#performs calculations to populate calculated columns    
def calculate():
    portfolio['TotalShares']= portfolio['Shares']+portfolio['DripShares']
    portfolio['Value']= portfolio['LastPrice']*portfolio['TotalShares']
    portfolio['TotalCost']= (portfolio['Shares']*portfolio['CostPer'])+portfolio['Fees']
    portfolio['Cap_Gain/Loss_UNRL']= portfolio['Shares']*portfolio['LastPrice']-portfolio['TotalCost']
    portfolio['DripValue']= portfolio['DripShares']*portfolio['LastPrice']
    portfolio['Net_Gain/Loss_UNRL']= portfolio['Cap_Gain/Loss_UNRL']+ portfolio['DripValue']
    portfolio['Total_Gain/Loss']= portfolio['Net_Gain/Loss_UNRL']+portfolio['Realized_Gain/Loss']+ portfolio['CashDividend']

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
        #if input('Change '+ticker+' '+ category+' from '+str(old)+' to '+str(new)+'? Y/N>').upper()=='Y':
        portfolio.loc[index, 'Fees']= new
            #print('Change Confirmed')
            
            
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
    
    #sets index to be edited
    index= portfolio[portfolio['Ticker']==ticker].index.tolist()[0]
    #updates cash dividend column in df accordingly
    current_val= portfolio.loc[index, 'CashDividend']
    #if input('Add a '+str(amount)+' cash dividend for '+ticker+'? Y/N>').lower()=='y':
    cash(amount) #adds to cash
    portfolio.loc[index, 'CashDividend']= current_val+amount
    
    calculate()
    
#enter DRIP transaction. Will add specified fraction of shares
#without impacting Costs or cash. i.e. the div is fully capitalized.
def drip(ticker, partial_shares):
    #sets the index to be edited
    index= portfolio[portfolio['Ticker']==ticker].index.tolist()[0]
    old= portfolio.loc[index, 'DripShares']
    new = old+partial_shares
    portfolio.loc[index, 'DripShares']= new #sets new DripShares so that total value adjusts
        #adjusts DripValue (cumulative)
    calculate()
        
def sell(ticker, shares, sell_price, fees):
    index= portfolio[portfolio['Ticker']==ticker].index.tolist()[0]
    if shares==portfolio.loc[index, 'Shares']:#if selling all
        tempfees= portfolio.loc[index,'Fees']
        portfolio.loc[index,'Fees']=0
    else:
        tempfees=0
        
    
    old= portfolio.loc[index, 'Realized_Gain/Loss']
    portfolio.loc[index, 'Shares']= portfolio.loc[index, 'Shares']-shares
    portfolio.loc[index, 'Realized_Gain/Loss']= old+(sell_price-portfolio.loc[index, 'CostPer'])*shares-fees-tempfees
    cash((shares*sell_price)-fees)
    calculate()

#%%
#cash
cash(3100)

buy('DUK', 13, 77.98)
buy('SPY', 6, 210.00)
buy('DIA', 4, 176.98)

cash(1000)

buy('AAXN', 42, 22.74)

CashDiv('DIA', 1.42)

cash(100)

CashDiv('SPY', 6.47)

buy('CSCO', 7, 30.69)

CashDiv('DIA', .54)

cash(10.66)

cash(19.00)

CashDiv('DIA', 2.62)

CashDiv('DUK', 11.12)

CashDiv('DIA', 1.42)

CashDiv('CSCO', 1.82)

CashDiv('SPY', 6.49)

CashDiv('DIA', 0.72)

cash(200)

cash(37.38)

buy('CSCO', 7, 29.65)

CashDiv('DIA', 2.13)

CashDiv('DUK', 11.12)

cash(100)

buy('SNSR', 12, 15.7)

CashDiv('DIA', 1.73)

CashDiv('CSCO', 3.64)

CashDiv('SPY', 7.97)

###########2/3/2017 IRA

cash(1690) #845 into each IRA. a 1080x2 deposit was simply tranfer from CMA

#below is all CMA/JMC IRA data. CHC IRA to follow

sell('SPY', 6, 229.1, 6.98)
sell('DIA', 4, 199.89, 6.96)

CashDiv('DIA', 0.77)

buy('DVY', 10, 89.75)

buy('TWTR', 5, 15.96)

buy('AAXN', 19, 23.25)

buy('VOO', 2, 219.08)

drip('DUK', .1359)

sell('SNSR', 12, 18.06, 6.96)

CashDiv('VOO', 2.00)

cash(.01)

drip('DVY', .0769)

cash(50.00)

drip('CSCO', .1193)

buy('CSCO', 9, 31.28)

drip('DUK', .1287)

CashDiv('VOO', 2.02)

drip('DVY', .0006)

drip('DVY', .0787)

###############
#CHC IRA

buy('VUG', 8, 117.2)

buy('BND', 3, 80.63)

buy('VGT', 2, 134.2)


CashDiv('VUG', 3.03)

CashDiv('VGT', 0.73)

cash(0.01)

cash(300.00)

CashDiv('BND', 0.52)

buy('DIA', 3, 207)

drip('BND', .0062)

drip('DIA', .0026)

drip('BND', .0063)

drip('DIA', .0086)

drip('VUG', .0214)

drip('VGT', .0058)

drip('BND', .0063)





