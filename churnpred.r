require(data.table)

#3mo validation data
cust = fread("c:/Users/John/Desktop/pythonds/threebackval.csv")

#Original data
cust = fread("c:/Users/John/Desktop/pythonds/custdata.csv")

cust = cust[cust$Type == "R",]

names(cust)[1] = "MemNum"

# cust$Begin = NULL
# cust$End = NULL
# cust$Lat = NULL
# cust$Long = NULL

cust$distance[is.na(cust$distance)] = mean(cust$distance, na.rm = T)
cust$SCOREIndIm[is.na(cust$SCOREIndIm)] = mean(cust$SCOREIndIm, na.rm = T)

cust$Begin = as.Date(cust$Begin, format= "%m/%d/%Y")
cust$End = as.Date(cust$End, format = "%m/%d/%Y")

#dfs = split(cust, cust$Type)

vars = names(cust)

results = c()

for (column in vars) {
  if (column == "Churned" || column == "Type") next
  mdl = glm(paste0("Churned ~ ", column), data = dfs$C, family = "binomial")
  
  results[column] = coef(summary(mdl))[2,4]
}

require(caTools)
splitvec = sample.split(blahblah)
train = cust[splitvec,]
test = cust[!splitvec,]

mdl = glm(Churned ~ ., data = cust[,c("Churned",membervars, nowvars, back3, back6, back12)], family = "binomial")
summary(mdl)

preds = predict(mdl, test, type= "response")
table(preds > .5, test$Churned)

require(rpart)
require(rpart.plot)
partmdl = rpart(Churned ~ Age + CREDITCARDA + DEBITCARDA + DIRECTDEPOSITA + TotalDepositsnow + TotalLoansnow + LoanMaturingWithin3, data = train)
preds = predict(partmdl, test)
table(preds > .5, test$Churned)
prp(partmdl)

partmdl = rpart(Churned ~ ., data = cleancust[splitvec,c("Churned",membervars, nowvars, back3, back6, back12, trendvarsnow, trendvars3back, trendvars6back)], control=list(cp = .005))
preds = predict(partmdl, cleancust[!splitvec,])
table(preds > .5, test$Churned)
prp(partmdl)

reducemdl = function(mydata, response, vars, cutoff = .1){
  model = glm(Churned ~ ., data = mydata[,c(response,vars)], family = "binomial")
  continue = any(coef(summary(model))[,4] > cutoff)
  
  while(continue){
    highest = which.max(coef(summary(model))[-1,4])
    print(paste("Throwing away",vars[highest]))
    vars = vars[-highest]
    model = glm(Churned ~ ., data = mydata[,c(response,vars)], family = "binomial")
    continue = any(coef(summary(model))[,4] > cutoff)
  }
  return (model)
}

newmdl = reducemdl(cust, "Churned",c(membervars, nowvars, back3, back6, back12, trendvarsnow, trendvars3back, trendvars6back))
preds = predict(mdl, test, type= "response")
table(preds > .5, test$Churned)

cust$TotalDeposits3mTrend = (cust$TotalDepositsnow - cust$TotalDepositsminus3) / cust$TotalDepositsminus3
cust$TotalDeposits6mTrend = (cust$TotalDepositsminus3 - cust$TotalDepositsminus6) / cust$TotalDepositsminus6
cust$TotalDeposits12mTrend = (cust$TotalDepositsminus6 - cust$TotalDepositsminus12) / cust$TotalDepositsminus12

cust$TotalLoans3mTrend = (cust$TotalLoansnow - cust$TotalLoansminus3) / cust$TotalLoansminus3
cust$TotalLoans6mTrend = (cust$TotalLoansminus3 - cust$TotalLoansminus6) / cust$TotalLoansminus6
cust$TotalLoans12mTrend = (cust$TotalLoansminus6 - cust$TotalLoansminus12) / cust$TotalLoansminus12

cust$LoanAccts3mTrend = (cust$LoanAcctsnow - cust$LoanAcctsminus3) / cust$LoanAcctsminus3
cust$LoanAccts6mTrend = (cust$LoanAcctsminus3 - cust$LoanAcctsminus6) / cust$LoanAcctsminus6
cust$LoanAccts12mTrend = (cust$LoanAcctsminus6 - cust$LoanAcctsminus12) / cust$LoanAcctsminus12

cust$DepAccts3mTrend = (cust$DepAcctsnow - cust$DepAcctsminus3) / cust$DepAcctsminus3
cust$DepAccts6mTrend = (cust$DepAcctsminus3 - cust$DepAcctsminus6) / cust$DepAcctsminus6
cust$DepAccts12mTrend = (cust$DepAcctsminus6 - cust$DepAcctsminus12) / cust$DepAcctsminus12

cust$NumDep3mTrend = (cust$NumDepnow - cust$NumDepminus3) / cust$NumDepminus3
cust$NumDep6mTrend = (cust$NumDepminus3 - cust$NumDepminus6) / cust$NumDepminus6
cust$NumDep12mTrend = (cust$NumDepminus6 - cust$NumDepminus12) / cust$NumDepminus12

cust$NumWith3mTrend = (cust$NumWithnow - cust$NumWithminus3) / cust$NumWithminus3
cust$NumWith6mTrend = (cust$NumWithminus3 - cust$NumWithminus6) / cust$NumWithminus6
cust$NumWith12mTrend = (cust$NumWithminus6 - cust$NumWithminus12) / cust$NumWithminus12

cust$ForeignDep3mTrend = (cust$ForeignDepnow - cust$ForeignDepminus3) / cust$ForeignDepminus3
cust$ForeignDep6mTrend = (cust$ForeignDepminus3 - cust$ForeignDepminus6) / cust$ForeignDepminus6
cust$ForeignDep12mTrend = (cust$ForeignDepminus6 - cust$ForeignDepminus12) / cust$ForeignDepminus12

cust$ForeignWith3mTrend = (cust$ForeignWithnow - cust$ForeignWithminus3) / cust$ForeignWithminus3
cust$ForeignWith6mTrend = (cust$ForeignWithminus3 - cust$ForeignWithminus6) / cust$ForeignWithminus6
cust$ForeignWith12mTrend = (cust$ForeignWithminus6 - cust$ForeignWithminus12) / cust$ForeignWithminus12

cust$TellerTrans3mTrend = (cust$TellerTransnow - cust$TellerTransminus3) / cust$TellerTransminus3
cust$TellerTrans6mTrend = (cust$TellerTransminus3 - cust$TellerTransminus6) / cust$TellerTransminus6
cust$TellerTrans12mTrend = (cust$TellerTransminus6 - cust$TellerTransminus12) / cust$TellerTransminus12

cust$POSAct3mTrend = (cust$POSActnow - cust$POSActminus3) / cust$POSActminus3
cust$POSAct6mTrend = (cust$POSActminus3 - cust$POSActminus6) / cust$POSActminus6
cust$POSAct12mTrend = (cust$POSActminus6 - cust$POSActminus12) / cust$POSActminus12

cust$LTDep3mTrend = (cust$LTDepnow - cust$LTDepminus3) / cust$LTDepminus3
cust$LTDep6mTrend = (cust$LTDepminus3 - cust$LTDepminus6) / cust$LTDepminus6
cust$LTDep12mTrend = (cust$LTDepminus6 - cust$LTDepminus12) / cust$LTDepminus12

cust$LTLoan3mTrend = (cust$LTLoannow - cust$LTLoanminus3) / cust$LTLoanminus3
cust$LTLoan6mTrend = (cust$LTLoanminus3 - cust$LTLoanminus6) / cust$LTLoanminus6
cust$LTLoan12mTrend = (cust$LTLoanminus6 - cust$LTLoanminus12) / cust$LTLoanminus12

cust$CreditUtilization3mTrend = (cust$CreditUtilizationnow - cust$CreditUtilizationminus3) / cust$CreditUtilizationminus3
cust$CreditUtilization6mTrend = (cust$CreditUtilizationminus3 - cust$CreditUtilizationminus6) / cust$CreditUtilizationminus6
cust$CreditUtilization12mTrend = (cust$CreditUtilizationminus6 - cust$CreditUtilizationminus12) / cust$CreditUtilizationminus12

trendvarsnow = c("TotalDeposits3mTrend","TotalLoans3mTrend","LoanAccts3mTrend","DepAccts3mTrend","NumDep3mTrend","NumWith3mTrend","ForeignDep3mTrend","ForeignWith3mTrend","TellerTrans3mTrend","POSAct3mTrend","LTDep3mTrend","LTLoan3mTrend","CreditUtilization3mTrend")
trendvars3back = c("TotalDeposits6mTrend","TotalLoans6mTrend","LoanAccts6mTrend","DepAccts6mTrend","NumDep6mTrend","NumWith6mTrend","ForeignDep6mTrend","ForeignWith6mTrend","TellerTrans6mTrend","POSAct6mTrend","LTDep6mTrend","LTLoan6mTrend","CreditUtilization6mTrend")
trendvars6back = c("TotalDeposits12mTrend","TotalLoans12mTrend","LoanAccts12mTrend","DepAccts12mTrend","NumDep12mTrend","NumWith12mTrend","ForeignDep12mTrend","ForeignWith12mTrend","TellerTrans12mTrend","POSAct12mTrend","LTDep12mTrend","LTLoan12mTrend","CreditUtilization12mTrend")

cust$Age[is.na(cust$Age)] = mean(cust$Age, na.rm = TRUE)

cleanit = function(x){
  if(is.numeric(x))  x[is.infinite(x) | is.na(x)] = 0
  return (x)
}

cleancust = data.frame(lapply(cust, cleanit))

newmdl = reducemdl(cleancust[splitvec,], "Churned", c(membervars, nowvars, back3, back6, back12, trendvarsnow, trendvars3back, trendvars6back))
summary(newmdl)
preds = predict(newmdl, cleancust[!splitvec,], type="response")
table(preds > .25, test$Churned)

smallmdl = reducemdl(cleancust[splitvec,], "Churned", c(membervars, nowvars))
summary(smallmdl)
preds = predict(smallmdl, cleancust[!splitvec,], type="response")
table(preds > .3, test$Churned)

scalecust = cleancust

trendvars = names(scalecust)[endsWith(names(scalecust), "Trend")]

for(item in trendvars){
  scalecust[scalecust[,item] > 0,item] = 1
  scalecust[scalecust[,item] < 0,item] = -1
}

cust3back = scalecust

scalemdl = reducemdl(scalecust[splitvec,], "Churned", c(membervars, nowvars, back3, back6, back12, trendvarsnow, trendvars3back, trendvars6back))
summary(scalemdl)
preds = predict(scalemdl, scalecust[!splitvec,], type="response")
table(preds > .3, test$Churned)

library(ggplot2)
ggplot(hi, aes(xvals, yvals)) + geom_line() + geom_abline(slope=1, intercept=0) + ylim(0,1) + xlim(0,1) + theme_minimal()

cust3back = scalecust[!is.na(cust$NumDepminus3),]
splitvec = sample.split(cust3back$Churned)
mdl3back = reducemdl(cust3backsub, "Churned", c(membervars, back3, back6, back12, trendvars3back, trendvars6back), .5)
summary(mdl3back)
preds = predict(mdl3back, cust3back[!splitvec,], type="response")
table(preds > .3, cust3back$Churned[!splitvec])

cust6back = scalecust[!is.na(cust$NumDepminus6),]
splitvec = sample.split(cust6back$Churned)
mdl6back = reducemdl(cust6back[splitvec,], "Churned", c(membervars, back6, back12, trendvars6back))
summary(mdl6back)
preds = predict(mdl6back, cust6back[!splitvec,], type="response")
table(preds > .3, cust6back$Churned[!splitvec])

cust12back = scalecust[!is.na(cust$NumDepminus12),]
splitvec = sample.split(cust12back$Churned)
mdl12back = reducemdl(cust12back[splitvec,], "Churned", c(membervars, back12))
summary(mdl12back)
preds = predict(mdl12back, cust12back[!splitvec,], type="response")
table(preds > .15, cust12back$Churned[!splitvec])

val3back = scalecust
activemems = fread("c:/Users/John/Desktop/pythonds/activemembers.csv")
activemems = data.frame(activemems)
names(activemems)[1] = "MemNum"
activemems = activemems[,c("MemNum","Age","CHARGEOFFACCOUNTA","CREDITCARDA","DEBITCARDA","DIRECTDEPOSITA")]
combined = base::merge(activemems[,c("MemNum","Age","CHARGEOFFACCOUNTA","CREDITCARDA","DEBITCARDA","DIRECTDEPOSITA")], val3back)

table(combined$Active3, combined$Active6)
combined = combined[combined$Active3, ]

combined[is.na(combined$Age), "Age"] = mean(combined$Age, na.rm= TRUE)

preds3month = predict(mdl3back, combined, type="response")
table(preds3month > .5, combined$Active3ChurnNow)


combined = base::merge(activemems[,c("MemNum","Age","CHARGEOFFACCOUNTA","CREDITCARDA","DEBITCARDA","DIRECTDEPOSITA")], scalecust)
preds6month = predict(mdl6back, combined, type="response")
table(preds3month > .5, combined$Active6ChurnNow)


library(ROCR)
cust3backround2 = cust3back[sample(nrow(cust3back)),]
folds = cut(seq(1, nrow(cust3backround2)), breaks = 10, labels = FALSE)
models = list()
rocs = c()
for(i in 1:10){
  print(i)
  testIndexes = which(folds == i, arr.ind = TRUE)
  testData = cust3backround2[testIndexes,]
  trainData = cust3backround2[-testIndexes,]
  models[[i]] = reducemdl(trainData,"Churned",c(membervars, back3, back6, back12, trendvars3back, trendvars6back), .0001)
  preds = predict(models[[i]], testData)
  rocs[i] = performance(prediction(preds, testData$Churned), "auc")@y.values[[1]]
}

for(i in 1:10){
  testIndexes = which(folds == i, arr.ind = TRUE)
  testData = cust3backround2[testIndexes,]
  preds = predict(models[[i]], testData, type = "response")
  print(table(preds > .3, testData$Churned))
}

for(i in 1:10){
  print(summary(models[[i]]))
}

precs = list()
recs = list()
mdl3back = glm(Churned ~ ., data = cust3back[,c('Churned','Age','CHARGEOFFACCOUNTA','CREDITCARDA','DEBITCARDA','DIRECTDEPOSITA','TotalDepositsminus3','TotalLoansminus3','LoanAcctsminus3','DepAcctsminus3','NumDepminus3','NumWithminus3','ForeignDepminus3','TellerTransminus3','POSActminus3','LTDepminus3','LTLoanminus3','CreditUtilizationminus3','NumDepminus6','NumWithminus6','POSActminus6','CreditUtilizationminus6','TotalDepositsminus12','LoanAcctsminus12','DepAcctsminus12','NumDepminus12','POSActminus12','LTDepminus12','LTLoanminus12','TotalDeposits6mTrend','TotalLoans6mTrend','LoanAccts6mTrend','DepAccts6mTrend','NumWith6mTrend','ForeignDep6mTrend','TellerTrans6mTrend','POSAct6mTrend','CreditUtilization6mTrend','TotalDeposits12mTrend','TotalLoans12mTrend','LoanAccts12mTrend','DepAccts12mTrend','NumDep12mTrend','NumWith12mTrend','ForeignDep12mTrend','ForeignWith12mTrend','LTLoan12mTrend','CreditUtilization12mTrend')], family = binomial)
preds3month = predict(mdl3back, combined, type="response")
for(i in 1:9){
mytable = table(preds3month > i / 10, combined$Active3ChurnNow)
precs[[i]] = mytable[2,2] / sum(mytable[2,])
recs[[i]] = mytable[2,2] / sum(mytable[,2])
}
plot(precs, recs)

mdl3back = glm(Churned ~ ., data = cust3back[,c('Churned','Age','CHARGEOFFACCOUNTA','CREDITCARDA','DEBITCARDA','DIRECTDEPOSITA','TotalDepositsminus3','TotalLoansminus3','LoanAcctsminus3','DepAcctsminus3','NumDepminus3','NumWithminus3','ForeignDepminus3','TellerTransminus3','POSActminus3','LTDepminus3','LTLoanminus3','CreditUtilizationminus3','NumDepminus6','NumWithminus6','POSActminus6','CreditUtilizationminus6','TotalDeposits6mTrend','TotalLoans6mTrend','LoanAccts6mTrend','DepAccts6mTrend','NumWith6mTrend','ForeignDep6mTrend','TellerTrans6mTrend','POSAct6mTrend','CreditUtilization6mTrend','TotalDeposits12mTrend','TotalLoans12mTrend','LoanAccts12mTrend','DepAccts12mTrend','NumDep12mTrend','NumWith12mTrend','ForeignDep12mTrend','ForeignWith12mTrend','LTLoan12mTrend','CreditUtilization12mTrend')], family = binomial)
preds3month = predict(mdl3back, combined, type="response")
for(i in 1:9){
  mytable = table(preds3month > i / 10, combined$Active3ChurnNow)
  precs[[i]] = mytable[2,2] / sum(mytable[2,])
  recs[[i]] = mytable[2,2] / sum(mytable[,2])
}
plot(precs, recs)

mdl3back = glm(Churned ~ ., data = cust3back[,c('Churned','Age','CHARGEOFFACCOUNTA','CREDITCARDA','DEBITCARDA','DIRECTDEPOSITA','TotalDepositsminus3','TotalLoansminus3','LoanAcctsminus3','DepAcctsminus3','NumDepminus3','NumWithminus3','ForeignDepminus3','TellerTransminus3','POSActminus3','LTDepminus3','LTLoanminus3','CreditUtilizationminus3','NumDepminus6','NumWithminus6','POSActminus6','CreditUtilizationminus6','TotalDeposits6mTrend','TotalLoans6mTrend','LoanAccts6mTrend','DepAccts6mTrend','NumWith6mTrend','ForeignDep6mTrend','TellerTrans6mTrend','POSAct6mTrend','CreditUtilization6mTrend')], family = binomial)
preds3month = predict(mdl3back, combined, type="response")
for(i in 1:9){
  mytable = table(preds3month > i / 10, combined$Active3ChurnNow)
  precs[[i]] = mytable[2,2] / sum(mytable[2,])
  recs[[i]] = mytable[2,2] / sum(mytable[,2])
}
plot(precs, recs)

cust3backsub = cust3back[10000:nrow(cust3back),]
mdl3back = glm(Churned ~ ., data = cust3backsub[,c('Churned','Age','CHARGEOFFACCOUNTA','CREDITCARDA','DEBITCARDA','DIRECTDEPOSITA','TotalDepositsminus3','TotalLoansminus3','LoanAcctsminus3','DepAcctsminus3','NumDepminus3','NumWithminus3','ForeignDepminus3','TellerTransminus3','POSActminus3','LTDepminus3','LTLoanminus3','CreditUtilizationminus3','NumWithminus6','POSActminus6','CreditUtilizationminus6','TotalDeposits6mTrend','TotalLoans6mTrend','LoanAccts6mTrend','DepAccts6mTrend','NumWith6mTrend','ForeignDep6mTrend','TellerTrans6mTrend','POSAct6mTrend','CreditUtilization6mTrend')], family = binomial)

pos = cust3back[cust3back$Churned,]
neg = cust3back[!cust3back$Churned,]
cust3backsub = rbind(pos, neg[sample(1:nrow(neg), 50000),])
logpreds = predict(mdl3back, combined)

library(rpart)
partmdl = rpart(Churned ~ ., data = cust3backsub[,c('Churned','Age','CHARGEOFFACCOUNTA','CREDITCARDA','DEBITCARDA','DIRECTDEPOSITA','TotalDepositsminus3','TotalLoansminus3','LoanAcctsminus3','DepAcctsminus3','NumDepminus3','NumWithminus3','ForeignDepminus3','TellerTransminus3','POSActminus3','LTDepminus3','LTLoanminus3','CreditUtilizationminus3','NumDepminus6','NumWithminus6','POSActminus6','CreditUtilizationminus6','TotalDeposits6mTrend','TotalLoans6mTrend','LoanAccts6mTrend','DepAccts6mTrend','NumWith6mTrend','ForeignDep6mTrend','TellerTrans6mTrend','POSAct6mTrend','CreditUtilization6mTrend')])
partpreds = predict(partmdl, combined)
table(partpreds > .5, combined$Active3ChurnNow)
table(logpreds > .5, combined$Active3ChurnNow)
table(partpreds > .5 & logpreds > .5, combined$Active3ChurnNow)
