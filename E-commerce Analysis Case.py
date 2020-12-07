#!/usr/bin/env python
# coding: utf-8

# # E-commerce Analysis Case

# * * *
# 
# ## Analysis Process：
# 
# ### 1. Identify Overall Operational Indicators
# ### 2. Find underperforming products from the price range and optimize the product structure
# ### 3. Determine poorly performing products from the discount range and optimize the product structure
# 
# 
# * * *

# ## Introduction ##
# 
# &nbsp;&nbsp;&nbsp;&nbsp;This project's dataset comes from VIPS, a well-known Chinese website dedicated to special offers by selling branded discount products online. A special sale generally refers to selling a specified pair of goods at a discounted price during a specified period, usually in a mall or specialty store. This model has already existed offline for a long (e.g., shopping mall promotions, street sales), but in other countries, there are also discounts on unsold goods in large stores, such as Outlets. The deals are generally inventory clearance, but some businesses specialize in producing goods for sale.
# 
# &nbsp;&nbsp;&nbsp;&nbsp;This special sale industry is a real industrial chain, but because of the rapid distribution channels, geographical location and other reasons, most of them are clustered in first-tier cities. For people in less developed areas, this industry is still very strange to them. Therefore, a group of people have become the brand's porters through social media platform like WeChat and other channels to quickly distribute big brand inventory, to achieve rapid low-cost inventory clearance, and to speed up the turnover of funds back to the purpose.
# 
# &nbsp;&nbsp;&nbsp;&nbsp;In terms of supply, branded tailgates are the most common source of discount retail goods, as they have natural clearance needs, but in fact, as long as the cost is low enough, new product launches, custom underwriting, and private brands can all be a sustainable source of discount retail. In the early days of its establishment, VIPS source of goods is mainly tail products, but with the continuous development of VIPS in the field of e-commerce, the proportion of new products and exclusive supplies has been increasing, as early as in Q2 2016 analysis, VIPS seasonal new products and platform special offer products already accounted for 37%!
# 

# ## Part 1. Evaluate and Optimize
# 
# #### In this part we would evaluate the results of each promotion and optimize the product mix as appropriate in order to make products sell better.

# ### Step 1. Read Each Dataset

# In[17]:


import pandas as pd
import pandas as pd
import numpy as np

import warnings
warnings.filterwarnings('ignore')


# In[69]:


import sqlalchemy


engine = sqlalchemy.create_engine('mysql+pymysql://frogdata05:Frogdata!1321@localhost:3306/froghd')

# Read data
# Commodity Information Sheet
sql_cmd = "select * from sales_info1"

# Execute sql to queries to access data
dt1 = pd.read_sql(sql=sql_cmd, con=engine)

dt1.rename(columns={"商品名": "sale_name",
                    "售卖价":"sale_price",
                    "吊牌价":"tag_price",
                    "折扣率":"discount",
                    "库存量":"inventory",
                    "货值":"inventory_value",
                    "成本价":"cost_price",
                    "利润率":"profit_rate",
                    "skus":"SKU"},
          inplace=True)

dt1.head()


# In[3]:


dt1.to_excel('new.xlsx')


# In[19]:


# Read data
# Commodity Popularity Sheet
sql_cmd = "select * from sales_info2"

# Execute sql to queries to access data
dt2 = pd.read_sql(sql=sql_cmd, con=engine)


dt2.head()


# In[70]:


# Read data
# User Sales Detail Sheet
sql_cmd = "select * from sales_info3"

# Execute sql to queries to access data
dt3 = pd.read_sql(sql=sql_cmd, con=engine)

dt3.rename(columns={"is_tui":"refund_or_not",
                    "tui_cons":"refundNums",
                    "tui_price":"refundPrice"},
          inplace=True)

#Switch "yes" or "no" of "refund_or_not" variable into “1”(yes) and "0" (no)
dt3["refund_or_not"]=dt3["refund_or_not"].map({"是":1,"否":0})
dt3.head()


# ### Step 2. Merge "Commodity Information Sheet" and "Commodity Popularity Sheet"

# In[71]:


# As a result, we get basic product information as well as some popularity information, 
# such as the number of added charts, the number of favorites and the number of uvs (unique visit) 
dt_product = dt1.merge(dt2,how="left",on="sale_name")
dt_product.head()


# ### Step 3. Merge Step 2 Sheet with "User Sales Detail Sheet"

# In[26]:


# Summarize the selling situation of each product and rename columns

product_sales = dt3.groupby("sale_name").agg({"buy_cons":"sum",
                                                 "cost_price":"sum",
                                                 "refundNums":"sum",
                                                 "refundPrice":"sum",
                                                 "buy_price":"mean",
                                                 "user_id":pd.Series.nunique}).reset_index()
product_sales.rename(columns={"buy_cons":"Num_sales",
                              "cost_price":"Amount_sales",
                              "refund_or_not":"Num_refund",
                              "refundPrice":"Amount_refund",
                              "buy_price":"Unit_price",
                              "user_id":"Num_users"},inplace=True)
product_sales.head()


# In[27]:


# Merge Product Information
dt_product_sales = dt_product.merge(product_sales,how="left",on="sale_name")
dt_product_sales.head()


# ### Step 4. Overall Operations Evaluation
# 
# In the overall operations section, the main focus is on sales, sell-through, UV, conversion rate, and other indicators as auxiliary indicators. The sales volume is used to compare with the expected target, and the sell-through ratio is used to see the flow of goods.

# - **GMV**: Gross Merchandise Volume, which means the total volume of transactions (within a certain period). Mostly used in the e-commerce industry, it usually includes the number of unpaid orders that have been placed.
# - **Real Sale Volume**: GMV - Refusal Refund Amount
# - **Sales Volume**: Cumulative sales volume (including refusal refund)
# - **Per Customer Transaction**: GMV / the Number of Customers, positively related to Gross Profit Margin
# - **UV**: number of unique visits to the product's page
# - **Conversion Rate**: The Number of Customers / UV
# - **Discount Rate**: GMV / Total Amount of Tag (tag price * sales volume)
# - **Stock Value**: Tag Price * Inventory Amount
# - **Sales Ratio**: GMV / Stock Value
# - **Collections**: The number of users who have collected a product
# - **Additional Purchases**: The number of users who have added products to charts
# - **SKU**: SKU count in promotional activities (generally refers to the item number)
# - **SPU**: SPU count in promotional activities (generally refers to the style number)
# - **Rejected Volume**: The total number of rejected and returned goods
# - **Rejected Amount**: The total amount of rejections and returns

# In[29]:


#1、GMV: the total volume of transactions, including return amount
gmv = dt_product_sales["Amount_sales"].sum()
gmv


# In[30]:


#2、Real Sale Volume: GMV - Refusal Refund Amount
return_sales = dt_product_sales["Amount_refund"].sum()
return_money = gmv - return_sales
return_money


# In[31]:


#3、Sales Volume: Cumulative sales volume (including refusal refund)
all_sales = dt_product_sales["Num_sales"].sum()
all_sales


# In[32]:


#4、Per Customer Transaction: GMV / the Number of Customers, positively related to Gross Profit Margin
# dt3.user_id.unique().count()

custom_price = gmv / dt_product_sales["Num_users"].sum()
custom_price


# In[33]:


# 5、UV: number of unique visits to the product's page
uv_cons = dt_product_sales["uvs"].sum()
uv_cons


# In[34]:


# 6、Conversion Rate: The Number of Customers / UV
uv_rate = dt_product_sales["Num_users"].sum() / dt_product_sales["uvs"].sum()
uv_rate


# In[35]:


# 7、Discount Rate: GMV / Total Amount of Tag (tag price * sales volume)
tags_sales = np.sum(dt_product_sales["tag_price"] * dt_product_sales["Num_sales"])
discount_rate= gmv / tags_sales 
discount_rate


# In[37]:


# 8、Stock Value: Tag Price * Inventory Amount
goods_value = dt_product_sales["inventory_value"].sum()
goods_value


# In[38]:


# 9、Sales Ratio: GMV / Stock Value
sales_rate = gmv / goods_value
sales_rate


# In[39]:


# 10、Collections: The number of users who have collected a product
coll_cons = dt_product_sales["collections"].sum()
coll_cons


# In[40]:


# 11、Additional Purchases: The number of users who have added products to charts
add_shop_cons = dt_product_sales["carts"].sum()
add_shop_cons


# In[41]:


# 12、SKU: SKU count in promotional activities (generally refers to the item number)
sku_cons = dt_product_sales["SKU"].sum()
sku_cons


# In[42]:


# 13、SPU: SPU count in promotional activities (generally refers to the style number)
spu_cons = len(dt_product_sales["sale_name"].unique())
spu_cons


# In[43]:


# 14、Rejected Volume: The total number of rejected and returned goods
reject_cons = dt_product_sales["refundNums"].sum()
reject_cons


# In[45]:


# 15、Rejected Amount: The total amount of rejections and returns
reject_money = dt_product_sales["Amount_refund"].sum()
reject_money


# In[46]:


# Summary


sales_state_dangqi = pd.DataFrame(
    {"GMV":[gmv,],"Real Sale Volume":[return_money,],"Sales Volume":[all_sales,],"Per Customer Transaction":[custom_price,],
     "UV":[uv_cons,],"Conversion Rate":[uv_rate,],"Discount Rate":[discount_rate,],"Stock Value":[goods_value,],
     "Sales Ratio":[sales_rate,],"Collections":[coll_cons,],"Additional Purchases":[add_shop_cons,],"SKU":[sku_cons,],
     "SPU":[spu_cons,],"Rejected Volume":[reject_cons,],"Rejected Amount":[reject_money,],}, 
    ) #index=["2020 Double11 Shopping Festival",]

# Here are statistics of 2019 Double11 shopping Festival as follows, which have been calculated already. 
sales_state_tongqi = pd.DataFrame(
    {"GMV":[2261093,],"Real Sale Volume":[1464936.517,],"Sales Volume":[7654,],"Per Customer Transaction":[609.34567,],
     "UV":[904694,],"Conversion Rate":[0.0053366,],"Discount Rate":[0.46,],"Stock Value":[12610930,],
     "Sales Ratio":[0.1161,],"Collections":[4263,],"Additional Purchases":[15838,],"SKU":[82,],
     "SPU":[67,],"Rejected Volume":[2000,],"Rejected Amount":[651188.57,],}, 
    ) #index=["2019 Double11 Shopping Festival",]

#sales_state = pd.concat([sales_state_dangqi, sales_state_tangqi])
sales_state_dangqi_s = pd.DataFrame(sales_state_dangqi.stack()).reset_index().iloc[:,[1,2]]
sales_state_dangqi_s.columns = ["Indicators","2020 double11"]
sales_state_tongqi_s = pd.DataFrame(sales_state_tongqi.stack()).reset_index().iloc[:,[1,2]]
sales_state_tongqi_s.columns = ["Indicators","2019 double11"]
sales_state = pd.merge(sales_state_dangqi_s, sales_state_tongqi_s,on="Indicators")
sales_state["Year-on-Year Ratio"] = (sales_state["2020 double11"] - sales_state["2019 double11"]) / sales_state["2019 double11"]
sales_state


# ## Part 2. Identify and Optimize From the Price Range
# 
# #### What we need to do is to in-depth explore the data of different intervals to optimize the later promotion structure. First of all, we need to find the sales source data in this range of in this promotion. The source data requires the display of specific model number, sales, sales and other information. The second step is to calculate the conversion rate and discount rate of each item.

# ### Indicators:
# - Sales Amount
# - Sales Volume
# - Per Customer Transaction
# - Numbers of Customers
# - UV
# - Conversion Rate
# - Inventory Volume
# - Inventory Value
# - Sales Ratio

# In[51]:


# Divide price range
# Set the segmentation range
listBins = [0,200, 400, 100000]

# Set labels for each range
listLabels = ['1_200','200_400','400 or more']

# Use pd.cut for data discretization slicing, with consistent group labels and group numbers
"""
pandas.cut(x,bins,right=True,labels=None,retbins=False,precision=3,include_lowest=False)

"""
dt_product_sales['price range'] = pd.cut(dt_product_sales['sale_price'], bins=listBins, labels=listLabels, include_lowest=True)
dt_product_sales.head()


# In[54]:


dt_product_sales_info = dt_product_sales.groupby("price range").agg({
                                        "inventory_value":"sum",
                                        "Amount_sales":"sum",
                                        "Num_sales":"sum",
                                        "uvs":"sum",
                                        "Num_users":"sum",
                                        "collections":"sum",
                                        "carts":"sum"
                                        }).reset_index()
dt_product_sales_info.head()


# In[56]:


# Calculate indicators
dt_product_sales_info["Proportion_values"]=dt_product_sales_info["inventory_value"]/dt_product_sales_info["inventory_value"].sum()
dt_product_sales_info["Proportion_sales"]=dt_product_sales_info["Amount_sales"]/dt_product_sales_info["Amount_sales"].sum()
dt_product_sales_info["Per Customer Transaction"]=dt_product_sales_info["Amount_sales"]/dt_product_sales_info["Num_users"]
dt_product_sales_info["Conversion Rate"]=dt_product_sales_info["Num_users"]/dt_product_sales_info["uvs"]

dt_product_sales_info.head()


# In[57]:


# Take out data beyond price range 400
product_400 = dt_product_sales[dt_product_sales["price range"]=='400 or more']
product_400.head()


# In[58]:


# Calculate indicators for this price range
# Conversion Rate: The Number of Customers / UV
product_400['Conversion Rate'] = product_400["Num_users"]/product_400["uvs"]
# Stock Value: Tag Price * Inventory Amount
product_400["stock value"] = product_400["tag_price"]*product_400["inventory"]
product_400.head()


# In[60]:


# Sales Ratio: GMV / Stock Value
product_400["Sales Ratio"] = product_400["Amount_sales"]/product_400["stock value"]
product_400.head()


# In[62]:


product_400[["sale_name","Amount_sales","Num_sales","Num_users","uvs",'Conversion Rate',"inventory","stock value","Sales Ratio"]]


# ### Optimal Suggestion:
# 
# #### - Commodities with a conversion rate greater than 0.7%: temporarily reserved for the next promotion
# 
# #### - Commodities with a conversion rate less than 0.7%, but with a sale ratio of 36% or more: Served for next promotion
# 
# #### - Commodities with a conversion rate less than 0.7% and a sale ration less than 36%: Clearance sales
# 

# In[63]:


# Select qualified commodities
# 1、Commodities with a conversion rate greater than 0.7%: temporarily reserved for the next promotion
stay_stocks571 = product_400[product_400["Conversion Rate"]>0.007]
stay_stocks571


# In[64]:


# Select qualified commodities
# 2、Commodities with a conversion rate less than 0.7%, but with a sale ratio of 36% or more: Served for next promotion
stay_stocks573 = product_400[(product_400["Sales Ratio"]>=0.36)&(product_400["Conversion Rate"]<0.007)]
stay_stocks573


# In[65]:


# Select qualified commodities
# 3、Commodities with a conversion rate less than 0.7% and a sale ration less than 36%: Clearance sales
stay_stocks574 = product_400[(product_400["Sales Ratio"]<0.36)&(product_400["Conversion Rate"]<0.007)]
stay_stocks574


# ## Part 3. Identify and Optimize From the Discount Range
# 
# 
# #### Likewise, we choose the 0.35-0.4 discount range for further exploration. dt_product_discount_info table, we can get a sale ratio of 16.90%, conversion rate of 0.53%, and discount rate of 37% for the 0.35-0.4 discount range, which should be compared when optimizing the product structure.

# In[66]:


dt_product_sales.head()


# In[81]:


# Divide price range
# Set the segmentation range
listBins = [0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 1]

# Set labels for each range
listLabels = ['0.15_0.2','0.2_0.25','0.25_0.3','0.3_0.35','0.35_0.4','0.4_0.45','0.45_0.5','0.5_0.55','0.55_0.6','0.6_0.65','0.65_0.7','0.7_1']

## Use pd.cut for data discretization slicing, with consistent group labels and group numbers
"""
pandas.cut(x,bins,right=True,labels=None,retbins=False,precision=3,include_lowest=False)

"""
dt_product_sales['discount range'] = pd.cut(dt_product['discount'], bins=listBins, labels=listLabels, include_lowest=True)
dt_product_sales.head()


# In[76]:


dt_product_discount_info = dt_product_sales.groupby("discount range").agg({
                                        "inventory_value":"sum",
                                        "Amount_sales":"sum",
                                        "Num_sales":"sum",
                                        "uvs":"sum",
                                        "Num_users":"sum",
                                        "collections":"sum",
                                        "carts":"sum"
                                        }).reset_index()
dt_product_discount_info


# In[77]:


# Calculate indicators
dt_product_discount_info["Proportion_values"]=dt_product_discount_info["inventory_value"]/dt_product_discount_info["inventory_value"].sum()
dt_product_discount_info["Proportion_sales"]=dt_product_discount_info["Amount_sales"]/dt_product_discount_info["Amount_sales"].sum()
dt_product_discount_info["Per Customer Transaction"]=dt_product_discount_info["Amount_sales"]/dt_product_discount_info["Num_users"]
dt_product_discount_info["Conversion Rate"]=dt_product_discount_info["Num_users"]/dt_product_discount_info["uvs"]

dt_product_discount_info


# In[78]:


# Take out data within rage 0.35-0.4
product_354 = dt_product_sales[dt_product_sales["discount range"]=='0.35_0.4']
product_354.head()


# In[79]:


# Calculate indicators for this price range
# Conversion Rate: The Number of Customers / UV

product_354['Conversion Rate'] = product_354["Num_users"]/product_354["uvs"]

# Stock Value: Tag Price * Inventory Amount
product_354["stock value"] = product_354["tag_price"]*product_354["inventory"]
product_354.head()


# In[80]:


# Sales Ratio: GMV / Stock Value
product_354["Sales Ratio"] = product_354["Amount_sales"]/product_354["stock value"]
product_354.head()


# In[84]:


product_354[["sale_name","Amount_sales","Num_sales","Unit_price","Num_users","uvs","inventory","stock value","discout","Sales Ratio",'Conversion Rate']]


# ### Optimal Suggestions:
# 
# #### The part with the discount rate **greater than 37%** should be reserved for products with a sale ratio greater than 36.5% and a conversion rate greater than 0.7%, and the rest will be processed for clearance;
# 
# #### The part with the discount rate **less than 37%** should be reserved for the part with the sale ratio greater than 36.5% and the conversion rate greater than 0.7%, and the rest will be cleared.
# 
# 
# 
# 
# 
# 

# In[85]:


# Select qualified commodities
# 1、Reservation：The part with a discount rate greater than 37% is reserved for products with a sale-to-sale ratio greater than 36.5% and a conversion rate greater than 0.7%
stay_stocks1 = product_354[(product_354["discout"]>0.37)&(product_354["Sales Ratio"]>0.365)&(product_354["Conversion Rate"]>0.007)]
stay_stocks1


# In[86]:


# 2、Clearance processing products that do not meet the conditions: the part with a discount rate greater than 37% is looking for products with a sale-to-sale ratio less than 36.5% or a conversion rate less than 0.7%
stay_stocks2 = product_354[(product_354["discout"]>=0.37)&((product_354["Sales Ratio"]<=0.365)|(product_354["Conversion Rate"]<=0.007))] #
stay_stocks2


# In[88]:


# Select Qualified Commodities：
# 3、Reservation：In the part where the discount rate is less than 37%, the part with the sales-to-sale ratio greater than 36.5% and the conversion rate greater than 0.7% is retained
stay_stocks3 = product_354[(product_354["discout"]<=0.37)&(product_354["Conversion Rate"]>0.007)&(product_354["Sales Ratio"]>0.365)] 
stay_stocks3


# In[90]:


# 4、Clearance processing products that do not meet this condition: look for the part where the discount rate is less than 37% and the sales-to-sell ratio is less than 36.5% or the conversion rate is less than 0.7%
stay_stocks4 = product_354[((product_354["discout"]<0.37) & ((product_354["Sales Ratio"]<0.365)|(product_354["Conversion Rate"]<0.007)))]
stay_stocks4

