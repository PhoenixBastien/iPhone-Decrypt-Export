arch=arm64 # define architecture of computer
docker pull public.ecr.aws/lambda/python:latest-$arch # pull docker image
docker stop $(docker ps -q) # stop all running containers
docker rm $(docker ps -a -q) # remove all containers
docker build --platform linux/$arch -t docker-image:test . # build container
docker run --platform linux/$arch -d -p 9000:8080 docker-image:test # run new container in background
curl "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{}' # check if success or fail
rm -rf ~/Library/SMS/ # remove decrypted backup in user's Library dir
docker cp $(docker ps -q):/var/task/Library/SMS/ ~/Library/SMS/ # copy decrypted backup to user's Library dir
rm -rf export*/ # remove export dir
imessage-exporter -f html -c full -p ~/Library/SMS/sms.db -o export/ # export messages to html