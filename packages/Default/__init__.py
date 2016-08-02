__all__ = ["list","richtext","emailscrapebasic","emaildump","document"]
name="Default Package"
version=(0,0,0)
authors=["unonu"]

preferenceDict = {
	'emailserver' : {'label':'IMAP Server Address', 'placeholder':'imap.server.com', 'type':'string','tooltip':'Location of the IMAP server.'},
	'emailport' : {'label':'IMAP Server Port', 'placeholder':'993', 'default':'993', 'type':'string','tooltip':'Port to use on the IMAP server.'},
	'emailssl' : {'label':'Connect using SSL', 'default':1,'type':'check','tooltip':'Connect to the IMAP server using SSL.'}
}