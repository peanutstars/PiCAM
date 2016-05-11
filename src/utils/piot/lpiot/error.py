# define Python user-defined exceptions
class PiotError(Exception) :
    """Base class for other exceptions"""
    pass

class PiotDatabaseError(PiotError) :
    pass ;

class PiotZBParseError(PiotError) :
	pass ;

