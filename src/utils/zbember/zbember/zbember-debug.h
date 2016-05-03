#ifndef __ZBEMBER_DEBUG_H__
#define __ZBEMBER_DEBUG_H__


#define DBG(x,args...)	do{ emberAfAppPrintln("%s@" x,__FUNCTION__,##args); }while(0)

char* toStringEmberEUI64(EmberEUI64 eui)
{
	static char buf[17] = { 0 , } ;
	int i ;
	int p ;

	for (i=7, p=0; i >= 0; i--, p++){
		sprintf(&buf[p*2], "%02X", eui[i]) ;
	}

	return buf ;
}

#endif /* __ZBEMBER_DEBUG_H__ */
