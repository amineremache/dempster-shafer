import numpy as np
import pandas as pd
from itertools import combinations 

def construct_omega():
	size = int(input("What is the size of your omega set? : "))
	OMEGA = []
	for i in range(size):
		OMEGA.append(input("Give the {0} item of omega : ".format(i+1)).upper())
	print(OMEGA)
	return OMEGA

def construct_inspectors():
	nb_inspectors = int(input("How many inspectors do you have? : "))
	INDEXES = []
	for i in range(nb_inspectors):
		INDEXES.append(str(i+1))
	print(INDEXES)
	return INDEXES

def construct_matrix(omega, indexes):
	space_x = ['EMPTY']
	for i in range(1,len(omega)+1):
		space_x += combinations(omega,i)

	# convertir les tuples en string pour pouvoir y accéder plus tard en DataFrame  
	for i in range(0,len(space_x)):
		space_x[i] = ''.join(space_x[i])

	# définir les trucs à calculer selon le nombre d'inspecteurs 
	indx_comb = []
	for i in range(1,len(indexes)+1):
		indx_comb += combinations(indexes,i) 

	# convertir les tuples en string pour l'acces en DataFrame

	for i in range(0,len(indx_comb)):
		indx_comb[i] = ''.join(indx_comb[i])

	vals_to_calc = ['m','Bel','Pl']
	space_y = []

	for elem_i in indx_comb:
		for elem_v in vals_to_calc:	
			space_y.append(''.join([elem_v,elem_i]))

	# construire le DataFrame vide
	mat = pd.DataFrame(index=space_y, columns=space_x)

	return mat

def get_sum(mat,row):
	sum = 0
	for col in mat.loc[row]:
		if col is not np.NaN :
			sum += float(col)
	return float(sum)

def fill_row(mat,item):
	sum = get_sum(mat,'m'+item)
	while True:
		continu_inspector = input("Do you wish to give masses for inspector N°{0}? : ([y]es/no) ".format(item))
		if (continu_inspector == "yes") or (continu_inspector == "y"):
			event = str(input("For what event do you want to give the mass ? : ('P','J','PJ', ... and care the order) ")).upper()
			row = 'm'+item
			tmp_val = float(input("What is the value of the mass ? : (between 0 and {0:.2f}) ".format(1-sum)))
			sum = get_sum(mat,row)
			if (round(abs(1.00-sum-tmp_val),2) > 0.00):
				mat.loc[row][event] = tmp_val
				sum = get_sum(mat,row)
			elif (round(abs(1.00-get_sum(mat,row)-tmp_val),2) == 0.00):
				mat.loc[row][event] = tmp_val
				sum = get_sum(mat,row)
				print("The mass for inspector N°{0} is equal to 1, go to next inspector".format(item))
				break
			else :
				print("With this value you exceed the sum of 1, please pick a value between 0 and {0:.2f}".format(1.00-sum))
		else:
			break
	return sum

def fill_matrix(omega,inspectors,matrix):
	while True:
		continu_grl = str(input("Do you wish to continue filling the masses ? : ([y]es/no) ")).lower()
		if (continu_grl == "yes") or (continu_grl == "y"):
			for item in inspectors:
				sum_item = fill_row(matrix,item)
				if sum_item < 1.00 :
					print("The sum is less than 1, please refill the masses")
					fill_row(matrix,item)
		else:
			break	

def calcul_belif(indexes,mat):
	columns = mat.columns[1:]
	bel = 'Bel'
	for index in indexes:
		bel_row = bel+index
		for event in columns:
			belief = 0
			for item in columns:
				if (item in event) and (mat.loc['m'+index][item] is not np.NaN):
					belief += mat.loc['m'+index][item]
			mat.loc[bel_row][event] = belief

def calcul_plaus(indexes,mat):
	columns = mat.columns[1:]
	plaus = 'Pl'
	for index in indexes:
		plaus_row = plaus+index
		for event in columns:
			plausability = 0
			for item in columns:
				if (len(set(event).intersection(item)) > 0) and (mat.loc['m'+index][item] is not np.NaN):
					plausability += mat.loc['m'+index][item]
			mat.loc[plaus_row][event] = plausability

def calcul_DS(indexes,mat):
	columns = mat.columns[1:]
	plaus_indexes = []
	indx_comb = []
	for i in range(1,len(indexes)+1):
		indx_comb += combinations(indexes,i) 

	for i in range(0,len(indx_comb)):
		indx_comb[i] = ''.join(indx_comb[i])
	
	for comb in indx_comb: # I don't know how to do/if it exists a Dempster-Shafer for more than 2 corpses
		if len(comb) == 2:
			corps_x = comb[0]
			corps_y = comb[1]

			for A in columns:
				sum_numerator = 0
				sum_denominator = 0
				for B in columns:
					for C in columns:
						if (set(B).intersection(C)) == set(A) and (mat.loc['m'+corps_x][B] is not np.NaN) and (mat.loc['m'+corps_y][C] is not np.NaN):
							sum_numerator += mat.loc['m'+corps_x][B] * mat.loc['m'+corps_y][C]
						elif len(set(B).intersection(C)) == 0 and (mat.loc['m'+corps_x][B] is not np.NaN) and (mat.loc['m'+corps_y][C] is not np.NaN):
							sum_denominator += mat.loc['m'+corps_x][B] * mat.loc['m'+corps_y][C]
				mat.loc['m'+corps_x+corps_y][str(A)] = sum_numerator / (1-sum_denominator)
				plaus_indexes.append(comb)

	return plaus_indexes

if __name__ == "__main__":
	
	#OMEGA = ['P','J','M']
	#INDEXES = ['1','2']
	OMEGA = construct_omega()
	INDEXES = construct_inspectors()
	mat = construct_matrix(OMEGA,INDEXES)
	fill_matrix(OMEGA,INDEXES,mat)
	calcul_belif(INDEXES,mat)
	calcul_plaus(INDEXES,mat)
	plaus_indexes = calcul_DS(INDEXES,mat)
	calcul_belif(plaus_indexes,mat)
	calcul_plaus(plaus_indexes,mat)
	print(mat)