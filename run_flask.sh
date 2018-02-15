docker run --rm --name $1 -it -P -v $(pwd):/root/src --network host opentracing-example
