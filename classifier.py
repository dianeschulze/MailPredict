from dateutil import parser
import numpy
import sys
import csv
from sklearn import utils
from sklearn import cross_validation
from sklearn.linear_model import *
from sklearn.svm import LinearSVC
from sklearn import tree
import random
from sklearn.metrics import *
from sklearn.externals import joblib
import pickle


# This script builds classifiers to predict whether I'll respond or not. It also builds a linear regression model that predicts how long it will take me to respond. 
def main(inputFile):
	cFeatures = []
	cLabels = []
	rFeatures = []
	rLabels = []
	with open(inputFile, 'rb') as f:
		reader = csv.reader(f)
		header = next(reader)

		f.seek(0) #reset the reader
		next(reader)

		# Shuffle the rows so you don't just use the most recent data to test 
		datarows = []	
		for filerow in reader:
			datarows.append(filerow)
		random.shuffle(datarows)

		for row in datarows:
			if row[3] == '0': # I didnt reply
				#iclassifier features: is_weekday, is_weekeve, is_weeknight, is_weekendday, is_weekendeve, num_recipients, brown_sender
				cFeatures.append([int(row[6]), int(row[7]),int(row[8]), int(row[9]),int(row[10]), int(row[11])])
				cLabels.append(0)
			else: 
				# classifier features
				cFeatures.append([int(row[6]), int(row[7]),int(row[8]), int(row[9]),int(row[10]), int(row[11])])
				cLabels.append(1)


				rLabels.append([float(row[5])]) # time to reply in seconds 
				# regression features: average response time to this sender, whether the sender has a brown.edu address, the number of recipients
				rFeatures.append([float(row[13]), int(row[12])])

		cLabels = numpy.array(cLabels)
		rLabels = numpy.array(rLabels)

		# reserve 30% of the data as test data
		num_c_train_rows = 7*int(len(cLabels)/10)
		num_r_train_rows = 7*int(len(rLabels)/10)


		cFeaturesTrain = cFeatures[:num_c_train_rows]
		cLabelsTrain = cLabels[:num_c_train_rows]
		cFeaturesTest = cFeatures[num_c_train_rows:]
		cLabelsTest = cLabels[num_c_train_rows:]


		rFeaturesTrain = rFeatures[:num_r_train_rows]
		rLabelsTrain = rLabels[:num_r_train_rows]
		rFeaturesTest = rFeatures[num_r_train_rows:]
		rLabelsTest = rLabels[num_r_train_rows:]


		# ****** Classifiers **************
		# decision tree
		#dt = tree.DecisionTreeClassifier()
		#dt.fit(cFeaturesTrain, cLabelsTrain)

		# logistic regression
		#logit = LogisticRegression()
		#logit.fit(cFeaturesTrain, cLabelsTrain)

		# svm
		#svm = LinearSVC()
		#svm.fit(cFeaturesTrain, cLabelsTrain)

		# print "\n******** Classifier Results ********"
		# print 'Decision tree training accuracy:', dt.score(cFeaturesTrain, cLabelsTrain)
		# print 'Decision tree test accuracy:', dt.score(cFeaturesTest,cLabelsTest)


		# print 'Logit training accuracy:', logit.score(cFeaturesTrain, cLabelsTrain)
		# print 'Decision tree test accuracy:', logit.score(cFeaturesTest,cLabelsTest)

		# print 'SVM training accuracy:', svm.score(cFeaturesTrain, cLabelsTrain)
		# print 'Decision tree test accuracy:', svm.score(cFeaturesTest,cLabelsTest)

	    
		# print "\n********Regression Results********"


		#reg = LinearRegression() 
		reg = LinearRegression(normalize = True)
		reg.fit(rFeaturesTrain, rLabelsTrain)


		# ********Ridge***********
		#ridge = Ridge(alpha = .9)
		#ridge.fit(rFeaturesTrain, rLabelsTrain)
		# print "Ridge training r^2:", ridge.score(rFeaturesTrain, rLabelsTrain)
		# print "Ridge testing r^2:", ridge.score(rFeaturesTest, rLabelsTest)

		# ********Lasso***********
		#lasso = Lasso(alpha = .5)
		#lasso.fit(rFeaturesTrain, rLabelsTrain)
		# print "Lasso training r^2:", lasso.score(rFeaturesTrain, rLabelsTrain)
		# print "Lasso testing r^2:", lasso.score(rFeaturesTest, rLabelsTest)

		# ********Elastic Net***********
		#enet= ElasticNet()
		#enet.fit(rFeaturesTrain, rLabelsTrain)
		# print "ElasticNet training r^2:", enet.score(rFeaturesTrain, rLabelsTrain)
		# print "ElasticNet testing r^2:", enet.score(rFeaturesTest, rLabelsTest)
		# print '\n'

		print "********* MLR Metrics********\n"

		pred_labels = reg.predict(rFeaturesTest)
		print "testing accuracy:", reg.score(rFeaturesTest, rLabelsTest)
		print "variance: ",explained_variance_score(rLabelsTest, pred_labels)
		print "mse: ", mean_squared_error(rLabelsTest, pred_labels)  
		print "r2:", r2_score(rLabelsTest, pred_labels)  
		

		# output the classifier to a pickle file
		#joblib.dump(reg, 'model/regression_model.pkl')

if __name__ == '__main__':
	if len(sys.argv) < 2:
		print "usage: python classifier.py path_to_input"
	inputFile = sys.argv[1]
	main(inputFile)
