#!/bin/python

import sys
import getopt
from datetime import datetime, timedelta

class Acct :

  W_ACCT = 12
  W_AMOUNT = 12
  W_DATE = 10
  W_LINE = 2 * W_ACCT + W_AMOUNT + W_DATE
  gssTypes = ( 'D_', 'C_', 'P_' ) # valid account name types

  def __init__( self, sFile ) :
    try :
      self.mFile = open( sFile )
    except :
      print "FATAL, could not open file", sFile
      sys.exit( 1 )

    self.miMov = 0
    self.mDictSaldo = {}


  @staticmethod
  def valAcct( sVal ) :
    liRet = 0 # OK, default
    liLen = len( sVal )
    if liLen > Acct.W_ACCT :
      liRet = 1
      print 'account name %s too long (%d), max is %d' % ( sVal, liLen, Acct.W_ACCT )
    elif sVal[ : 2 ] not in Acct.gssTypes :
      liRet = 1
      print 'account name %s not valid, must start by %s' % ( sVal, Acct.gssTypes )
    return liRet

  @staticmethod
  def valAmnt( sVal ) :
    liRet = 0 # OK, default
    liLen = len( sVal )
    if liLen > Acct.W_AMOUNT :
      liRet = 1
      print 'amount %s too long (%d), max is %d' % ( sVal, liLen, Acct.W_AMOUNT )
    try :
      lfAmount = float( sVal )
    except :
      liRet = 1
      print 'amount %s is not a floating point number' % ( sVal )
    return liRet

  @staticmethod
  def valDate( sVal ) :
    liRet = 0 # OK, default
    liLen = len( sVal )
    if liLen > Acct.W_DATE :
      liRet = 1
      print 'date %s too long (%d), max is %d' % ( sVal, liLen, Acct.W_AMOUNT )
    # TODO : check if ISO-format YYYY-MM-DD
    return liRet

  def parseLine( self, sLine ) :
    liRet = 0 # OK
    liLen = len( sLine )
    # TODO : allow comments at end of line => split by '#'
    if sLine[ 0 ] == '#' : pass # OK, comment
    elif liLen == 1 : pass # OK, empty line
    elif liLen < Acct.W_LINE :
      print "line lenght %d not enough, minimum %d" % ( liLen, Acct.W_LINE )
      liRet = 1
    else : # now a real line
      lss = sLine.split()
      #print lss
      lsAcctDeb = lss[ 0 ]
      lsAcctCre = lss[ 1 ]
      lsAmount  = lss[ 2 ]
      lsDate    = lss[ 3 ]
      liRet += Acct.valAcct( lsAcctDeb )
      liRet += Acct.valAcct( lsAcctCre )
      liRet += Acct.valAmnt( lsAmount )
      liRet += Acct.valDate( lsDate )
      if liRet > 0 :
        print "reject line, contains %d format/content errors"
        liRet = 1 # meaning 1 line with errors
      else :
        self.account( lsAcctDeb, lsAcctCre, lsAmount, lsDate )
    return liRet


  def account( self, sAcctDeb, sAcctCre, sAmount, sDate ) :

    self.miMov += 1
    print "accounting mov %d" % ( self.miMov )
    print "amount %s, on %s(D) - %s(H)" % ( sAmount, sAcctDeb, sAcctCre )
    lfAmount = float( sAmount ) # checked before

    try :
      lfSaldo = self.mDictSaldo[ sAcctDeb ]
    except :
      lfSaldo = 0.0
    lfSaldo2 = lfSaldo + lfAmount
    self.mDictSaldo[ sAcctDeb ] = lfSaldo2
    print "%12s : %0.2f => %0.2f" % ( sAcctDeb, lfSaldo, lfSaldo2 )
    # TODO : display mov method?

    try :
      lfSaldo = self.mDictSaldo[ sAcctCre ]
    except :
      lfSaldo = 0.0
    lfSaldo2 = lfSaldo - lfAmount
    self.mDictSaldo[ sAcctCre ] = lfSaldo2
    print "%12s : %0.2f => %0.2f" % ( sAcctCre, lfSaldo, lfSaldo2 )

    # TODO : do something with sDate
    print "--"
    

  # TODO : sumar total caixes i total people/players
  def displaySaldos( self ) :
    lfGent = .0
    lfGone = .0
    lfCash = .0
    print "========="
    print "BALANCES:"
    lListKeys = self.mDictSaldo.keys()
    #print lListKeys
    lListKeys2 = sorted( lListKeys )
    #print lListKeys2
    for lsAcct in lListKeys2 :
      # no need to try:
      lfSaldo = self.mDictSaldo[ lsAcct ]
      print "%-12s : %0.2f" % ( lsAcct, lfSaldo )
      if lsAcct[ 0 : 2 ] == "C_" : # caixa
        lfCash += lfSaldo
      elif lsAcct[ 0 : 2 ] == "D_" : # despesa
        lfGone += lfSaldo
      elif lsAcct[ 0 : 2 ] == "P_" : # people
        lfGent += lfSaldo
    print "========="
    print "%-12s : %0.2f" % ( "total gent", lfGent )
    print "%-12s : %0.2f" % ( "total desp", lfGone )
    print "%-12s : %0.2f" % ( "total cash", lfCash )

  def inputLoop( self ) :
    liErrors = 0
    for lsLine in self.mFile :
      liErrors += self.parseLine( lsLine )
    print "file processed, lines with errors:", liErrors
    print "total movements =", self.miMov


if __name__ == "__main__" :

  lAcct = Acct( sys.argv[ 1 ] )
  lAcct.inputLoop()
  lAcct.displaySaldos()

