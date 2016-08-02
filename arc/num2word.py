def num2word(num):
	words = ["zero","one","two","three","four","five","six","seven","eight","nine","ten","eleven","twelve","twen","thir","four","fif","six","seven","eigh","nine"]
	ab_num = abs(int(num))
	val = ''
	#more
	if ab_num > 1000000000000000:
		return "a lot"

	#trillions
	if ab_num // 1000000000000 < 1000 and ab_num // 1000000000000 > 0:
		if len(val) > 0:
			val += ' '
		val += num2word(ab_num // 1000000000000) + " trillion"
	ab_num = ab_num % 1000000000000

	#billions
	if ab_num // 1000000000 < 1000 and ab_num // 1000000000 > 0:
		if len(val) > 0:
			val += ' '
		val += num2word(ab_num // 1000000000) + " billion"
	ab_num = ab_num % 1000000000

	#millions
	if ab_num // 1000000 < 1000 and ab_num // 1000000 > 0:
		if len(val) > 0:
			val += ' '
		val += num2word(ab_num // 1000000) + " million"
	ab_num = ab_num % 1000000

	#thousands
	if ab_num // 1000 < 1000 and ab_num // 1000 > 0:
		if len(val) > 0:
			val += ' '
		val += num2word(ab_num // 1000) + " thousand"
	ab_num = ab_num % 1000

	#hundreds
	if ab_num // 100 < 10 and ab_num // 100 > 0:
		if len(val) > 0:
			val += ' '
		val += num2word(ab_num // 100) + " hundred"
	ab_num = ab_num % 100
	
	if len(val) > 0:
		val += " and "
	#tens
	if ab_num < 13:
		val += words[ab_num]
	elif ab_num < 20:
		#i = ab_num % 10 + (3 if ab_num > 12 else 0)
		val += words[ab_num + 1] + "teen"
	elif ab_num < 100:
		val += words[ab_num//10 + 11] + "ty"
		val += ("-" + words[ab_num%10]) if ab_num%10 > 0 else ''

	return ("negative" if num < 0 else '') + val