
# For Ubuntu (Kathrin)
#sudo docker rm gameOfLife
#xhost +
#sudo docker run --name=gameOfLife -v/tmp/.X11-unix:/tmp/.X11-unix -e DISPLAY=unix$DISPLAY -it seal

# For Mac (Patrick)
sudo docker rm gameOfLife
ip=$(ifconfig en0 | grep inet | awk '$1=="inet" {print $2}')
xhost + $ip
sudo docker run --name=gameOfLife -v/tmp/.X11-unix:/tmp/.X11-unix -e DISPLAY=$ip:0 -it seal
sudo docker cp gameOfLife:/SEAL/log_client  log_client