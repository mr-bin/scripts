#!/bin/sh

result=0
ping_query="ping -c 1 $1"
ping_timeout=$2
light_timeout=$3

while [ true ]; do
	ping_request=$(exec $ping_query | grep 'time=')

	sleep $ping_timeout;

	if [ "$ping_request" = '' ]; then
		result="fail";
	else 
		result="success";
	fi

	if [ "$result" = fail ]; then
		(exec gpio disable 3);
	fi

	if [ "$result" = success ]; then
		(exec gpio disable 4);
	fi

	sleep $light_timeout;

	(exec gpio enable 3);
	(exec gpio enable 4);

done

