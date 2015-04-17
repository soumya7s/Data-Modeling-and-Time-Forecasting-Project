#!/usr/bin/env python
from re import sub;
from decimal import Decimal;
import numpy as np
from scipy.optimize import curve_fit
import scipy.optimize as optimize

#Connecting to the MySQLdb
import mysql
import mysql.connector 

#declaring lists and variables
installDate = list();
source = list();
CPI = list();
installs = list();
installDateR = list();
sourceR = list();
cumu_arpu = list();
revenue = list();
totalRevenue = 0;
total = 0;

#Connecting to local host, Standard connection
cnx = mysql.connector.connect(user='root', password='', host='127.0.0.1', database='Dots1')

#Getting user input
inputDate = raw_input ("Please enter the date (YYYY-MM-DD) when players installed the game:") 
inputSource = raw_input ("Please enter the source (facebook / twitter):")

#Format for date in Revenue table
inputDate1 = inputDate[6]+"/"+inputDate[9]+"/"+inputDate[2:4] 

try:
	cursor = cnx.cursor()

	#Retrieving the Spending for the particular sources of input
	cursor.execute("SELECT * FROM Spending WHERE install_date = %s AND source = %s", (inputDate, inputSource))
	result = cursor.fetchone()
	installDate = result[0]
	source = result[1]
	CPI = float(Decimal(sub(r'[^\d.]','',result[4])))
	installs = result[2]
	
	#Retrieving the Revenue for the specified input sources
	cursor.execute("SELECT * FROM Revenue WHERE install_date = %s AND source = %s", (inputDate1, inputSource))
	while True:
		X = cursor.fetchone()
		if X == None: 
			break
		installDateR.append(X[0])
		sourceR.append(X[2])
		revenue.append(X[3])
		totalRevenue = totalRevenue + revenue[len(revenue)-1]
		temp = totalRevenue/float(installs)
		cumu_arpu.append(temp)		
		
	X = len(cumu_arpu) - 1
	total = round(cumu_arpu[X],2)
	
	# Define your function to be y = a * ln(x) + b
	def func(x, a, b):
		return a * np.log(x) + b
	
	def funcinverse(y,a,b):
		return np.exp((y-b)/a)

	xdata = np.linspace(1, len(cumu_arpu), len(cumu_arpu));
	
	# popt has the values for a and b
	popt, pcov = optimize.curve_fit(func, xdata, cumu_arpu);

	# So now invert the function y = a * ln(x) + b to x = exp((y-b)/a)
	# in my case, i've defined it as funcinverse(y,a,b)
	DTBE =int(funcinverse(CPI, popt[0], popt[1]));

	#Print Output
	print '{}	{}		{}	{}	{}	{}'.format("install_date", "source", "installs", "cumu_ARPU", "CPI", "DTBE")
	print '{}	{} 	{}	 	${}		{}	{}'.format(inputDate, inputSource, installs, total, CPI, DTBE)

finally:
	cnx.close()
