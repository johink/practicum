library(data.table)
survdata = fread("c:/Users/John/Desktop/pythonds/survival.csv")
cust = fread("c:/Users/John/Desktop/pythonds/custdata.csv")
mems = cust$`Member Number`[cust$Begin != "9/1/2014"]
survsub = survdata[survdata$MemNum %in% mems,]
survsub$Time2 = survsub$Time + 1

library(survival)
library(survminer)

fit = coxph(Surv(Time, Time2, Churn) ~ strata(MemType) + LoanAccts + Age + DirectDeposit, data = survsub)

ggsurvplot(survfit(fit, newdata=data.frame(MemType = "R", LoanAccts = 0, Age = 25, DirectDeposit = FALSE)), xlab = "Months", ylim = c(.5,1),ylab="Survival", censor= FALSE, legend.title= "Member Type", legend.labs=c("Commercial","Indirect","Residential"))

ggsurvplot(survfit(fit, newdata=data.frame(MemType = "R", LoanAccts = 1, Age = 40, DirectDeposit = TRUE)), xlab = "Months", ylab="Survival", censor= FALSE, ylim = c(.98, 1), legend.title= "Member Type", legend.labs=c("Commercial","Indirect","Residential")
      
           
aggsurv = aggregate(Churn ~ Month, data = survdata, FUN = function(x) c("Churned" = sum(x), "Active" = length(x)))

p = ggplot(aggsurv, aes(x = Month)) + geom_bar(aes(y = Churn.Active), stat = "identity")
p = p + ggtitle("Membership Levels & Churn Numbers by Month")
p = p + ylab("Number of Members")
p
