docker run --rm --name flask_app -it -p 5000:80 -v $(pwd):/root/src --link jaeger:jaeger opentracing-example
