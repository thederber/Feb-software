
def save_data(fname):
	#save data in json format:
	#{ 'matrix0' : {(row,col) : [time_when_data_taken, threshold, hits] , (row2,col2) : [time,threshold,hits], ...}, 'matrix1' : {...}, 'matrix2' : {...} }
	with open(fname,'w',encoding='utf-8') as f:
		json.dump(hists,f,default=timep2dic)

def encode_data(data):
	pass	
