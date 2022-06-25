# Full name: Nguyen Thi Hue Minh
# ID: K194141733

library(tidyverse)
library(readxl)
library(ggplot2)
data = read_excel("040522 Data Mid-term test Final.xlsx")
View(data)

# 2. CREATE DATASET ============================================================
set.seed(733)
sample =sample(1:nrow(data), 100, replace = F)
df = data[sample,]
View(df)

## Calculate cash holding
df$cash_holding = df$cash/df$totalasset

## Calculate continuous variable
df$leverage = df$totaldebt/df$totalasset

## Transform NA
sum(is.na(df$leverage)) #1
sum(is.na(df$totalasset)) #0 
sum(is.na(df$cash_holding)) #4

df$leverage[is.na(df$leverage)] = median(df$leverage, na.rm=T)
df$cash_holding[is.na(df$cash_holding)]= median(df$cash_holding,na.rm=T)

## create size variable (discrete variable)
df$ln_asset= log(df$totalasset) 

df$size = 0

df$size[df$ln_asset<= median(df$ln_asset)] = "Small" 
df$size[df$ln_asset>= median(df$ln_asset)] ="Big"

df %>%
  group_by(size) %>% 
  summarise(count=n())

# 3. REPORT ====================================================================

## 3.1. 5 firms with highest cash holding---------------------------------------
df %>% arrange(desc(cash_holding)) %>% 
  select(firmname, cash_holding) %>% 
  slice(1:5)

##3.2. 5 firms with lowest cash holding-----------------------------------------
df %>%  arrange(cash_holding) %>% 
  select(firmname, cash_holding) %>% 
  slice(1:5)

##3.3. the name of industries which the firms belong to-------------------------

df$industry=as.factor(df$industry)
levels(df$industry)

##3.4. provide descriptive statistics-------------------------------------------

###different categories of the discrete variable
df %>% 
  group_by(size) %>% 
  summarize(min = min(cash_holding),
            max = max(cash_holding),
            median = median(cash_holding),
            mean = mean(cash_holding),
            standard_deviation = sd(cash_holding))

####groups of above/below median of the continuous variable
df %>% 
  mutate(median_lev = ifelse(leverage > median(leverage),
                             "above median of leverage",
                             "below median of leverage")) %>% 
  group_by(median_lev) %>% 
  summarize(min = min(cash_holding),
            max = max(cash_holding),
            median = median(cash_holding),
            mean = mean(cash_holding),
            standard_deviation = sd(cash_holding))

# 4. DATA VISUALIZATION =======================================================
## 4.1. provide histogram of cash holding
ggplot(df, aes(x=cash_holding)) + 
  geom_histogram(binwidth=0.02,fill='cadetblue', color='steelblue4')

## 4.2. provide scatter plot of cash holding with the continuous variable
ggplot(df, aes(x= leverage, y= cash_holding, color = cash_holding)) + 
  geom_point()

## 4.3. provide boxplot of  holding with the discrete variable 

df %>% ggplot(aes(x=size, y = cash_holding, color = size)) + 
  geom_boxplot()

## 4.4 provide a plot that allow the combination of continuous, discrete variables and cash holding 
ggplot(df, aes(x = leverage, y = cash_holding, color=cash_holding)) +
  geom_point() +
  facet_wrap(~ size, nrow = 1)


# 5. LOOP =======================================================================
## Count the number of firms in an industry 
df2= df %>% 
  group_by(industry) %>% 
  summarise(n = n())

df2

industry_name = readline("Please enter an industry name: ")
repeat{
  if (industry_name %in% df$industry){
    print(paste(industry_name, "has", df2[which(df2$industry==industry_name), 'n'], "firm"))
    y = readline("Do you want to continue? (y/n): ")
    if (y=="y"){
      new_industry_name = readline("Please enter an new industry name: ")
    } else if (y=="n"){
      print("Thank you! The loop ends.")
      break}
  } else {
    industry_name = readline("The industry name is incorrect. Please enter again 
                 (or if you don't want to continue, please enter 'n' to end: ")
    if (industry_name =="n"){
      print("Thank you! The loop ends.")
      break
    } else {next}
  }
  industry_name = new_industry_name
}

## Count the number of firms in an industry and with cash holding above a certain value
value = (readline("Please enter a value: "))

df3 = df %>% 
  group_by(industry) %>% 
  filter(cash_holding>value) %>% 
  summarise(n = n())
df3

industry_name_2 = readline("Please enter an industry name: ")
repeat{
  if (industry_name_2 %in% df$industry){
    if (industry_name_2 %in% df3$industry){
      count = df3[which(df3$industry==industry_name_2), 'n']
      print(paste(industry_name_2, "with cash holding are",  value,"has", count, "firm"))
    } else {
      print(paste("No firms in the", industry_name_2, "industry has a cash holding above ", value))
    }
    y = readline("Do you want to continue? (y/n): ")
    if (y=="y"){
      new_industry_name = readline("Please enter an new industry name: ")
    } else if (y=="n"){
      print("Thank you! The loop ends.")
      break}
  } else {
    industry_name_2 = readline("The industry name is incorrect. Please enter again 
                 (or if you don't want to continue, please enter 'n' to end: ")
    if (industry_name_2 =="n"){
      break
    } else {next}
  }
  industry_name_2 = new_industry_name
}
