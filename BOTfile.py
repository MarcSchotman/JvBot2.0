import matplotlib.pyplot as plt
import numpy as np
import random as rnd
#==============================================================================
# import the data
#==============================================================================

#fname=open('eosethdata.txt','r')
market = ''
fname=open(market+'data.txt','r')
data=np.loadtxt(fname,delimiter=',')

for i in range(len(data)):
    data[i,0]=i


#data=data[000:8000]
price_time=data

def plot(x_y):
    plt.plot(x_y[:,0],x_y[:,1])
#==============================================================================
# define the indicators
#==============================================================================

###-----------------------RSI--------------------------------------------------

def RSI_func(price_time, n=14):
    
    prices=price_time[:,1]
    prices=np.transpose(prices)
    deltas = np.diff(prices)
    seed = deltas[:n+1]
    up = seed[seed>=0].sum()/n
    down = -seed[seed<0].sum()/n
    rs = up/down
    rsi = np.zeros_like(prices)
    rsi[:n] = 100. - 100./(1.+rs)

    for i in range(n, len(prices)):
        delta = deltas[i-1] # cause the diff is 1 shorter

        if delta>0:
            upval = delta
            downval = 0.
        else:
            upval = 0.
            downval = -delta

        up = (up*(n-1) + upval)/n
        down = (down*(n-1) + downval)/n

        rs = up/down
        rsi[i] = 100. - 100./(1.+rs)
    
    rsi_time=np.array(price_time)
    rsi_time[:,1]=rsi
            
    return rsi_time

###----------------------SMA---------------------------------------------------

def SMA_func(price_time,values):
    prices=price_time[:,1]
    weigths = np.repeat(1.0, values)/values
    smas = np.convolve(prices, weigths, 'valid')
    
    SMA_time=np.array(price_time)[values-1:,:]
    SMA_time[:,1]=smas
    
    return SMA_time
    
###----------------------EMA---------------------------------------------------

def EMA_func(price_time, values):
    
    prices=price_time[:,1]
    weights = np.exp(np.linspace(-1., 0., values))
    weights /= weights.sum()
    a =  np.convolve(prices, weights, mode='full')[:len(prices)]
    a[:values] = a[values]

    EMA_time=np.array(price_time)

    EMA_time[:,1]=a
    
    return EMA_time

###----------------------MACD--------------------------------------------------

def MACD_func(price_time, slow=26, fast=12):
    """
    compute the MACD (Moving Average Convergence/Divergence) using a fast and slow exponential moving avg'
    return value is emaslow, emafast, macd which are len(x) arrays
    """
    emaslow = EMA_func(price_time, slow)[:,1]
    emafast = EMA_func(price_time, fast)[:,1]
    diff = emafast - emaslow
#    print price_time[:,0],diff
    array = np.array([price_time[:,0],emaslow,emafast,diff])
    
#    print array
    return np.transpose(array)

#==============================================================================
# Programm the bot
#==============================================================================

def decision(price_time):
    
    '''
    The input is one array containing the time and prices.
    The output is either buy, sell or nothing.
    Buy:    +1
    Nothing: 0
    Sell:   -1
    '''
#----------------------------  Create indicators ------------------------

    RSI_time=RSI_func(price_time)
    SMA_time=SMA_func(price_time,20)
    EMA_time=EMA_func(price_time,20)
    MACD_time=MACD_func(price_time,26,12)

#----------------------------  Set variables  ---------------------------

    margin = -3
    k_RSI = 2
    trigger_value = 10
    delay = 8
    k_MACD = 9


#----------------------------  Starting values --------------------------  
     
    sell = False
    buy = False
    buy_points = 0
    sell_points = 0
    action = 0
    
#----------------------------  RSI-based  --------------------------------

    #Buy for low RSI, sell for high
    #Variables for RSI: margin and nunmber of points, 'margin' and k_RSI
    
    #Low RSI
    if RSI_time[-1,1] < 30 - margin: #and RSI_time[-1,1]>RSI_time[-1-1,1]: #Buy
        buy_points = (30 - margin - RSI_time[-1,1])*k_RSI
    
    #High RSI
    if RSI_time[-1,1] > 70 + margin: #and RSI_time[i,1] < RSI_time[-1-1,1]: #Sell
        sell_points = (RSI_time[-1,1] - 70 - margin) * k_RSI
        
        
#--------------------------- MACD-based  ---------------------------------
    
    #Positive:
    #If the MACD goes from <0 to >0, this is a positive sign
    if MACD_time[-1,3] > 0 and MACD_time[-1-delay,3]<0: 
        buy_points = buy_points + k_MACD
    
    #Negative
    if MACD_time[-1,3]<0 and MACD_time[-1-delay,3]>0:
        sell_points = sell_points + k_MACD

#--------------------------- Create output  -----------------------------

    if buy_points > trigger_value:
        action = 1
        
    if sell_points > trigger_value:
        action = -1
        
    return action


#==============================================================================
# Run and test the decision bot
#==============================================================================

dec_lst = []

#Starting Balances
euro = 100
iota = 0 #100/price_time[1,1]

#Empty lists
euro_lst=[]
iota_lst=[]
total_lst=[]
profit_lst=[]
k_lst=[]
rel_profit_lst=[]

trans_costs=0.05/100

tries = 1

for k in range(tries):

    for i in range(len(price_time)):
        
        prices = price_time[:i,:] #Only use data until now
     
        buy = False
        sell = False
        
        if i<50:
            sell =False
            buy = False
            
        elif decision(prices) == 1:
            buy = True
            sell = False
            
        elif decision(prices) == -1:
            sell = True
            buy = False
        
        
    #----------------------------- Adjust the holdings ---------------------------    
            
        if buy == True and euro != 0: #Buying
            iota = (1-trans_costs)*euro/price_time[i,1]
            euro = 0
        if sell == True and iota != 0: #Selling
            euro = (1-trans_costs)*price_time[i,1]*iota
            iota = 0
              
        
        #Append the lists
        euro_lst.append(euro)
        iota_lst.append(iota)
        total_lst.append(euro+iota*price_time[i,1])
            
        
    #For several tries: reset the start values and calculate the profit
    profit = euro + iota * price_time[-1,1] - 100

    profit_lst.append(profit)
    
    pot_prof=price_time[-1,1]/price_time[0,1]*100.-100.
    rel_profit = profit-pot_prof
    rel_profit_lst.append(rel_profit)
    
    k_lst.append(k)
    

mx = profit_lst.index(max(profit_lst))




#print max(profit_lst)


#==============================================================================
# --------------------Plot stuff----------------------------------------------
#==============================================================================

if tries == 1:
    
    #Regual commands
    plt.clf()
    plt.grid()
    
    #Price graph
    plt.subplot(221)
    plt.ylim(0,max(data[:,1])*1.05)
    plot(data)
    plt.ylabel(market)
    plot(SMA_time)
    plot(EMA_time)
    

        
    #Holdings graph
    plt.subplot(222)
    plt.ylabel('Euro')
    plt.plot(price_time[:,0],euro_lst)
    plt.plot(price_time[:,0],total_lst)
    

    
    ##MACD graph
    plt.subplot(223)
    plt.ylabel('MACD')
    plt.plot(MACD_time[:,0],MACD_time[:,1])
    plt.plot(MACD_time[:,0],MACD_time[:,2])
    plt.plot(MACD_time[:,0],5*MACD_time[:,3])
    plt.plot(MACD_time[:,0],np.zeros(( len(MACD_time) ,1 ))  )
       
    print 'A plot was made'
    
    pot_prof=price_time[-1,1]/price_time[0,1]*100.-100.
    print 'Profit is ', round(profit,2)
    print 'Potelntial profit was',round(pot_prof,2)

    
    #RSI graph
    plt.subplot(224)
    plt.ylabel('RSI')
    plt.plot(RSI_time[:,0],RSI_time[:,1])
    plt.plot(RSI_time[:,0],np.ones(( len(RSI_time),1 ))*30 )
    plt.plot(RSI_time[:,0],np.ones(( len(RSI_time),1 ))*70 )
else:
    #K graph
#   plt.subplot(224)
    plt.clf()
    plt.plot(k_lst,rel_profit_lst)
    


#==============================================================================
# results
#==============================================================================

'''


From 180 to the end:
    
Random profit = -36.83

Optimum stragety:
Margin = -5
k_RSI = 1.75
Delay = 12
k_MACD = 13

MACD:
For three coins, a = 60 seems to be the optimum

IOTA short term:
Optimum a combination of MACD and RSI
'''