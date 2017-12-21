

def resampling_idxes(d):
	pce_values = []
    for p in d:
		pce_values.append(p[1])

	lower = []
	upper = []
	weights = []
	with open(rawdata_folder + '/%sweights_%.2f.txt' % (prefix, bin_width), 'r') as f:
        	for line in f:
            		lb, ub, w = line.strip().split(' ')
        	    	lower.append(float(lb))
	        	upper.append(float(ub))
            		weights.append(float(w))

	sample_idxes = {}
	output_cnt = {}
	for i in range(len(lower)):
		sample_idxes.setdefault(i, [])
		output_cnt.setdefault(i, 0)

	num_test = int(len(pce_values) * test_percent)
	print num_test
	with open(rawdata_folder + '/%stest_idxes-bw-%.2f.txt' % (prefix, bin_width), 'w') as f:
		for i in range(num_test):
			f.write(str(i) + '\n')

	for i in range(num_test, len(pce_values)):
		idx = find_weight_idx(lower, upper, weights, pce_values[i])
		sample_idxes[idx].append(i)


	total_samples = 0
	for i in sample_idxes:
		if len(sample_idxes[i]) > total_samples:
			total_samples = len(sample_idxes[i])

	total_samples = int(total_samples * len(weights))
	train_idxes = []
	for i in range(total_samples):
		if i % 10000 == 0:
			print i
		idx = random.randint(0, len(weights) - 1)
		if output_cnt[idx] < len(sample_idxes[idx]):
			train_idxes.append(str(sample_idxes[idx][output_cnt[idx]]) + '\n')
		else:
			sample = random.randint(0, len(sample_idxes[idx]) - 1)
			train_idxes.append(str(sample_idxes[idx][sample]) + '\n')
		output_cnt[idx] += 1
	
	random.shuffle(train_idxes)    