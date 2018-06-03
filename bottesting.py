import matplotlib.pyplot as plt
import numpy as np
import random as rnd
from BOTfile import *
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

#Empty lists
total_lst=[]
profit_lst=[]
k_lst=[]
rel_profit_lst=[]

#Other definitions
tries = 19*17*11*13
trans_costs=0.05/100

for k in range(tries): 

#---------------------------  Create indicators -------------------------

    RSI_time=RSI_func(price_time)
    SMA_time=SMA_func(price_time,20)
    EMA_time=EMA_func(price_time,20)
    MACD_time=MACD_func(price_time,26,12)

#----------------------------  Set variables  ---------------------------

    margin = -10 + k%19
    k_RSI = (k%17)/4
    trigger_value = 10
    delay = k%11
    k_MACD = k%13

#----------------------------  Starting values big loop  ---------------

    #Starting Balances
    euro = 100
    iota = 0 #100/price_time[1,1]
    
    for i in range(len(price_time)):

#----------------------------  Starting values small loop ---------------  
     
        sell = False
        buy = False
        buy_points = 0
        sell_points = 0
        action = 0
        
    #----------------------------  RSI-based  --------------------------------
    
        #Buy for low RSI, sell for high
        #Variables for RSI: margin and nunmber of points, 'margin' and k_RSI
        
        #Low RSI
        if RSI_time[i,1] < 30 - margin: #and RSI_time[-1,1]>RSI_time[-1-1,1]: #Buy
            buy_points = (30 - margin - RSI_time[i,1])*k_RSI
        
        #High RSI
        if RSI_time[i,1] > 70 + margin: #and RSI_time[i,1] < RSI_time[-1-1,1]: #Sell
            sell_points = (RSI_time[i,1] - 70 - margin) * k_RSI
            
            
    #--------------------------- MACD-based  ---------------------------------
        
        #Positive:
        #If the MACD goes from <0 to >0, this is a positive sign
        if MACD_time[i,3] > 0 and MACD_time[i-delay,3]<0: 
            buy_points = buy_points + k_MACD
        
        #Negative
        if MACD_time[i,3]<0 and MACD_time[i-delay,3]>0:
            sell_points = sell_points + k_MACD
    
    #--------------------------- Create output  -----------------------------
    
        if buy_points > trigger_value:
            buy = True
            
        if sell_points > trigger_value:
            Sell = True
        
    #----------------------------- Adjust the holdings ---------------------------    
            
        if buy == True and euro != 0: #Buying
            iota = (1-trans_costs)*euro/price_time[i,1]
            euro = 0
        if sell == True and iota != 0: #Selling
            euro = (1-trans_costs)*price_time[i,1]*iota
            iota = 0
            
        
    #For several tries: reset the start values and calculate the profit
    profit = euro + iota * price_time[-1,1] - 100

    profit_lst.append(profit)
    
    pot_prof=price_time[-1,1]/price_time[0,1]*100.-100.
    rel_profit = profit-pot_prof
    rel_profit_lst.append(rel_profit)
    k_lst.append(k)
    
    if k%2000==100:
        print 'The process is at ', round(100.*float(k)/tries,1), '%'
    


mx = profit_lst.index(max(profit_lst))

k= mx
margin = -10 + k%19
k_RSI = (k%17)/4
trigger_value = 10
delay = k%11
k_MACD = k%13

print "The optimum values are:"
print 'Margin = ', margin
print 'k_RSI = ',k_RSI
print 'delay = ',delay
print 'k_MACD = ',k_MACD


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
    print 'Potelntial profit was ',round(pot_prof,2)

    
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
    plt.ylabel('Relative profit')
    plt.xlabel('Value of k')
    plt.plot(k_lst,rel_profit_lst)
    
    
    


#==============================================================================
# results
#==============================================================================


'''
From 180 to the end:
    
Random profit = €-36.83

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