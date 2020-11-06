rm /etc/nginx/conf.d/default.conf
cp /default.conf /etc/nginx/conf.d/default.conf
echo "upstream frontend { server $HOSTIP:3000; }" | cat - /etc/nginx/conf.d/default.conf > temp && mv temp /etc/nginx/conf.d/default.conf
