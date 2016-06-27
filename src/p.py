#: processes accounting movements from text file, and prints the balance
#:
#: usage: python p.py [<options>] <file>
#: options:
#: -d : date min/max/month/year
#:   examples: 2016, 2016-04, 2016-04:2016-05, 2016-04-02:2016-04-08
#:
#: can be called from any folder, and can use wrapper script p.sh
#:
#: file contains accounting movements with format ...
from __future__ import print_function

import sys
import getopt
from datetime import datetime, timedelta

# TODO : only define in 1 place valid account types (use dict in displaySaldos)
# TODO : add option to set initial and final dates to process
# TODO : read balance with starting value for accounts
# TODO : process more than 1 movs file


class Acct :

  @staticmethod
  def usage() :
    liLine = 0
    print( "" )
    print( sys.argv[ 0 ] )
    lF = open( sys.argv[ 0 ], 'r' )
    lbFirstComm = True
    lsL = lF.readline()
    while lsL and lbFirstComm == True :
      liLine += 1
      if lsL.startswith( "#:" ) :
        print( lsL[ 3 : -1 ] )
        lsL = lF.readline()
      else :
        break
    lF.close()

  W_ACCT = 12
  W_AMOUNT = 12
  W_DATE = 10
  W_LINE = 2 * W_ACCT + W_AMOUNT + W_DATE
  gssTypes = ( 'S_', 'D_', 'C_', 'P_', 'F_', 'X_' ) # valid account name types

  gsFmtYear = "%Y"
  gsFmtMonth = "%Y-%m"
  gsFmtDate = "%Y-%m-%d"
  gsFmtDateUI = "yyyy-mm-dd"

  def __init__( self, sFile = None ) :
    if sFile == None :
      self.mFile = sys.stdin
      print( "reading from stdin" )
    else :
     try :
      self.mFile = open( sFile )
     except :
      print( "FATAL, could not open file " + sFile )
      sys.exit( 1 )

    self.miMov = 0
    self.mDictSaldo = {}
    self.mDateIni = None
    self.mDateFin = None


  @staticmethod
  def eprint( sErrorMsg ) :
    print( sErrorMsg, file=sys.stderr )


  @staticmethod
  def valAcct( sVal ) :
    liRet = 0 # OK, default
    liLen = len( sVal )
    if liLen > Acct.W_ACCT :
      liRet = 1
      Acct.eprint( 'account name %s too long (%d), max is %d' % ( sVal, liLen, Acct.W_ACCT ) )
    elif sVal[ : 2 ] not in Acct.gssTypes :
      liRet = 1
      Acct.eprint( 'account name %s not valid, must start by %s' % ( sVal, Acct.gssTypes ) )
    return liRet

  @staticmethod
  def valAmnt( sVal ) :
    liRet = 0 # OK, default
    liLen = len( sVal )
    if liLen > Acct.W_AMOUNT :
      liRet = 1
      Acct.eprint( 'amount %s too long (%d), max is %d' % ( sVal, liLen, Acct.W_AMOUNT ) )
    try :
      lfAmount = float( sVal )
    except :
      liRet = 1
      Acct.eprint( 'amount %s is not a floating point number' % ( sVal ) )
    return liRet

  @staticmethod
  def valDate( sVal ) :
    liRet = 0 # OK, default
    liLen = len( sVal )
    if liLen > Acct.W_DATE :
      liRet += 1
      Acct.eprint( 'date %s too long (%d), max is %d' % ( sVal, liLen, Acct.W_AMOUNT ) )
    # TODO : check if ISO-format YYYY-MM-DD
    try :
      lDate = datetime.strptime( sVal, Acct.gsFmtDate )
      #print( lDate.strftime( Acct.gsFmtDate ) )
    except :
      Acct.eprint( "%s not a valid date in %s format" % ( sVal, Acct.gsFmtDateUI ) )
      liRet += 1
      sys.exit( 2 )
    return liRet

  def parseLine( self, sLine0 ) :
    liRet = 0 # OK
    # discard comment
    sLine = sLine0.split( '#' )[ 0 ]
    liLen = len( sLine )
    if liLen <= 1 : pass # OK, empty or comment line
    elif liLen < Acct.W_LINE :
      print( "line lenght %d not enough, minimum %d" % ( liLen, Acct.W_LINE ) )
      liRet = 1
    else : # now a real line
      lss = sLine.split()
      lsAcctDeb = lss[ 0 ]
      lsAcctCre = lss[ 1 ]
      lsAmount  = lss[ 2 ]
      lsDate    = lss[ 3 ]
      liRet += Acct.valAcct( lsAcctDeb )
      liRet += Acct.valAcct( lsAcctCre )
      liRet += Acct.valAmnt( lsAmount )
      liRet += Acct.valDate( lsDate )
      if liRet > 0 :
        Acct.eprint( "FATAL. rejected line, contains %d format/content errors" )
        liRet = 1 # meaning 1 line with errors
        sys.exit( 1 )
      else :
        self.account( lsAcctDeb, lsAcctCre, lsAmount, lsDate )
    return liRet


  def account( self, sAcctDeb, sAcctCre, sAmount, sDate ) :

    self.miMov += 1
    print( "accounting mov %d" % ( self.miMov ) )
    print( "amount %s, on %s(D) - %s(H)" % ( sAmount, sAcctDeb, sAcctCre ) )
    lfAmount = float( sAmount ) # checked before

    try :
      lfSaldo = self.mDictSaldo[ sAcctDeb ]
    except :
      lfSaldo = 0.0
    lfSaldo2 = lfSaldo + lfAmount
    self.mDictSaldo[ sAcctDeb ] = lfSaldo2
    print( "%12s : %9.2f => %9.2f" % ( sAcctDeb, lfSaldo, lfSaldo2 ) )
    # TODO : display mov method?

    try :
      lfSaldo = self.mDictSaldo[ sAcctCre ]
    except :
      lfSaldo = 0.0
    lfSaldo2 = lfSaldo - lfAmount
    self.mDictSaldo[ sAcctCre ] = lfSaldo2
    print( "%12s : %9.2f => %9.2f" % ( sAcctCre, lfSaldo, lfSaldo2 ) )

    # sDate is OK, was checked before
    lDate = datetime.strptime( sDate, Acct.gsFmtDate )
    if self.mDateIni == None : self.mDateIni = lDate
    else :
      if lDate < self.mDateIni : self.mDateIni = lDate
    if self.mDateFin == None : self.mDateFin = lDate
    else :
      if lDate > self.mDateFin : self.mDateFin = lDate

    print( "--" )
    

  # TODO rename to balance()
  def displaySaldos( self ) :
    lfGent = .0
    lfGone = .0
    lfCash = .0
    lfPend = .0
    lfStok = .0
    lfExtl = .0
    lsDateIni = self.mDateIni.strftime( Acct.gsFmtDate )
    lsDateFin = self.mDateFin.strftime( Acct.gsFmtDate )
    print( "=========" )
    print( "BALANCES:" )
    print( "found movements from %s to %s" % ( lsDateIni, lsDateFin ) )
    lListKeys = self.mDictSaldo.keys()
    #print lListKeys
    lListKeys2 = sorted( lListKeys )
    #print lListKeys2
    for lsAcct in lListKeys2 :
      # no need to try:
      lfSaldo = self.mDictSaldo[ lsAcct ]
      print( "%-12s : %9.2f" % ( lsAcct, lfSaldo ) )
      lsAcctType = lsAcct[ 0 : 2 ]
      # TODO : use a dictionary for this
      if lsAcctType == "C_" : # caixa
        lfCash += lfSaldo
      elif lsAcctType == "D_" : # despesa
        lfGone += lfSaldo
      elif lsAcctType == "P_" : # people
        lfGent += lfSaldo
      elif lsAcctType == "F_" : # factures
        lfPend += lfSaldo
      elif lsAcctType == "S_" : # capital
        lfStok += lfSaldo
      elif lsAcctType == "X_" : # eXternal
        lfExtl += lfSaldo
      else :
        eprint( "unknown acct type '%s'" % lsAcctType )
        sys.exit( 1 )
    print( "=========" )
    print( "%-12s : %9.2f" % ( "total stock",  lfStok ) )
    print( "%-12s : %9.2f" % ( "total people", lfGent ) )
    print( "%-12s : %9.2f" % ( "total xtrnal", lfExtl ) )
    print( "%-12s : %9.2f" % ( "total desp",   lfGone ) )
    print( "%-12s : %9.2f" % ( "total credit", lfPend ) )
    print( "%-12s : %9.2f" % ( "total cash",   lfCash ) )

  def inputLoop( self ) :
    liErrors = 0
    print( "----------" )
    for lsLine in self.mFile :
      liErrors += self.parseLine( lsLine )
    print( "file processed, lines with errors: %d" % liErrors )
    print( "total movements = %d" % self.miMov )


  @staticmethod
  def parseFlexDate( sDate ) :

    lDate = None
    # check in this order!
    for lsFmt in ( Acct.gsFmtDate, Acct.gsFmtMonth, Acct.gsFmtYear ) :
      try :
        lDate = datetime.strptime( sDate, lsFmt )
        print( "%s : is a %s date! => %s" % ( sDate, lsFmt, str( lDate ) ) )
        break
      except :
        print( "%s : not a %s date" % ( sDate, lsFmt ) )
        continue

    return lDate


  @staticmethod
  def parseDates( sDates ) :

    lDates = None # return value, default
    lss = sDates.split( ':' )
    liS = len( lss )
    if liS == 1 : # 1 date (year/month)
      lDate = Acct.parseFlexDate( lss[ 0 ] )
      # TODO : add 1 day/month/year to 2nd date depending on len
      lDates = ( lDate, lDate )
    elif liS == 2 : # 2 dates (year/month)
      pass
    else : # > 2 dates => invalid
      pass

    return lDates



  @staticmethod
  def checkOptions( pListParams ) :

    print( "checkOptions, args:", pListParams )
    try:
      lOptList, lList = getopt.getopt( pListParams, 'd:' )

    except getopt.GetoptError:
      Acct.eprint( "FATAL : error analyzing command line options" )
      Acct.eprint( "" )
      Acct.usage()
      sys.exit( 1 )

    # TODO : use shift / setenv --

    #print( lOptList )
    #print( lList )
    for lOpt in lOptList :
      #print( 'lOpt :' + str( lOpt )
      if lOpt[0] == '-d':
        lsVal = lOpt[1]
        lDateRange = Acct.parseDates( lsVal )
        if lDateRange == None :
          Acct.eprint( 'FATAL: Invalid date/date range' )
          Acct.usage()
          sys.exit( 1 )
        print( "date range: %s - %s" % ( lDateRange[ 0 ], lDateRange[ 1 ] ) )
      if lOpt[0] == '-M':
        lsVal = lOpt[1]
        try :
          liVal = int( lsVal )
          self.miMaxDY = liVal
        except :
          Acct.eprint( 'FATAL: NON-numerical value for Max DY (Y diff)' )
          Acct.usage()
          sys.exit( 1 )
          # TODO : only-1 exit point

    Acct.gsFiles = lList
    Acct.gTupDateRange = lDateRange


if __name__ == "__main__" :

  if len( sys.argv ) > 1 :
    Acct.checkOptions( sys.argv[ 1 : ] )
  if len( Acct.gsFiles ) == 0 :
    # use stdin
    lAcct = Acct()
  else :
    # TODO : process more than 1 movs file (for)
    lAcct = Acct( Acct.gsFiles[ 0 ] )
  lAcct.inputLoop()
  lAcct.displaySaldos()

