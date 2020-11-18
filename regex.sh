grep -Po "'P[0-9]*': {'label': (\"[[:alpha:] \/']*\"|'[[:alpha:] \/]*'), 'values': {'(img|value|link|Q[0-9]*)': [^}]*}?}?" out/tv_producers.json | sort
