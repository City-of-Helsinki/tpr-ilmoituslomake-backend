export HOSTIP=$(docker run --rm alpine ip route | awk 'NR==1 {print $3}')
docker-compose up $1
