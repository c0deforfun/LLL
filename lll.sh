#!/bin/bash
dir=`dirname $0`
python=`which python2`
if [[ $? != 0 ]]; then
  python=`which python`
  if [[ $? != 0 ]]; then
	if [ -f /usr/bin/python ];then
	  python="/usr/bin/python"
	else
	  if [ -f /usr/bin/python2 ]; then
		python="/usr/bin/python2"
	  else
		echo "Cannot find python"
		exit 1
	  fi
	fi
  fi
fi
ver=`$python --version 2>&1`
if [[ $ver =~ 'Python 3.' ]];then
  echo "LLL requires Python 2"
  exit 1
else
  exec $python $dir/lll.py $@
fi
