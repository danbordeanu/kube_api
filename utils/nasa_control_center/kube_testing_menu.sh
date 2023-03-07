#!/bin/bash

#do some checks

# dialog is a must, without it no magic
if ! [ -x "$(command -v dialog)" ]; then
  echo 'Error: dialog is not installed.....run aptitude install dialog' >&2
  exit 1
fi

# curl is a must, without it no magic to access the API
if ! [ -x "$(command -v curl)" ]; then
  echo 'Error: curl is not installed.....run aptitude install curl' >&2
  exit 1
fi


# TODO this is killing some on my daemons!! move to PID based 
# killall used to kill services, seems is not part of base debian
if ! [ -x "$(command -v killall)" ]; then
  echo 'Error: killall is not installed.....run aptitude install psmisc' >&2
  exit 1
fi

# multitail to aggregate logs
if ! [ -x "$(command -v multitail)" ]; then
  echo 'Error: multitail is not installed.....aptitude install multitail' >&2
  exit 1
fi


# lsof to get pid of port
if ! [ -x "$(command -v lsof)" ]; then
  echo 'Error: lsof is not installed.....aptitude install lsof' >&2
  exit 1
fi

# docker-compose to spin up all containers
if ! [ -x "$(command -v docker-compose)" ]; then
  echo 'Error: docker is not installed.....Please read the docs to install docker-ce and docker-compose' >&2
  exit 1
fi

#set variables
# Input error in dialog box.
E_INPUT=85
INPUT=/tmp/menu.sh.$$
OUTPUT=/tmp/output.sh.$$
OUTPUTNAMESPACE=/tmp/outputnamespace.sh.$$
OUTPUTDEPLOY=/tmp/outputdeploy.sh.$$
OUTPUTSERVICE=/tmp/outputservice.sh.$$
OUTPUTSERVICEDELETE=/tmp/outputservicedelete.sh.$$
OUTPUTSERVICEUPDATE=/tmp/outputserviceupdate.sh.$$
OUTPUTSERVICEREAD=/tmp/outputserviceread.sh.$$
OUTPUTDEPLOYDELETE=/tmp/outputdeploydelete.sh.$$
OUTPUTDEPLOYUPDATE=/tmp/outputdeployupdate.sh.$$
OUTPUTLISTPODS=/tmp/outputlistpods.sh.$$
PODLIST=/tmp/podlist.sh.$$
SERVICEREAD=/tmp/serviceread.sh.$$
OUTPUTINGRESS=/tmp/outputingress.$$
OUTPUTINGRESSDELETE=/tmp/outputingressdelete.$$
OUTPUTSECRET=/tmp/outputsecret.$$
OUTPUTSECRETDELETE=/tmp/outputsecretdelete.$$
OUTPUTVOLUMES=/tmp/outputvolumes.$$
OUTPUTVOLUMESDELETE=/tmp/outputvolumesdelete.$$
OUTPUTSCALE=/tmp/outputscale.$$
OUTPUTSCALEDELETE=/tmp/outputscaledel.$$
OUTPUTBIGDEMO=/tmp/outputbigdemo.$$
OUTPUTCREATEROLE=/tmp/outputcreaterole.$$
OUTPUTDELETEROLE=/tmp/outputdeleterole.$$


# services nane
KUBE_API_APP=kube_proxy.py

# how many get requests for job id
REQUESTS=100

# interval to send requests
INTERVAL=1


# trap and delete temp files
trap "rm $OUTPUT; rm $INPUT; exit" SIGHUP SIGINT SIGTERM


# check kube cluster api endpoint from env vars
# to set kube cluster ip, (eg: export KUBE_HOST=ip:port)
function set_kube_cluster_ip(){
echo "Set kube host from env vars"
if [[ -z "${KUBE_HOST}" ]]; then
    # by default kube_api is listening on 5000 port
    KUBE_HOST="http://localhost:5000"
else
    # use the host from env vars (eg: export KUBE_HOST=127.0.0.1)
    KUBE_HOST=`echo $KUBE_HOST`
fi
}

set_kube_cluster_ip


function set_kube_token(){
echo "Set kube token from env vars"
if [[ -z "${KUBE_TOKEN}" ]]; then
    # set some random user
    echo 'no login token...you need to login and set KUBE_TOKEN, eg: curl -i  -H "Content-Type: application/json"  -X POST -d '{"password": "base64encoded"}' http://kube_api/api/kube/login/user@mail.com'
    exit
else
    KUBE_TOKEN=`echo $KUBE_TOKEN`

fi
}

set_kube_token
# start kube api
function start_api(){
if lsof -n -ti:5000 &>/dev/null; then
    dialog --title 'KUBE-API' --msgbox 'Seems running, consider killing it...' 5 20
else
    cd ..
    python $KUBE_API_APP &> output_kube_api.log &
    cd ../test
fi
cd ../test
}


# about 
function about_about(){
dialog --title 'ABOUT' --msgbox 'Dan is the best and he created this magical tool' 10 20
}


# killall services aka push service and http mock
function stop_all(){
dialog --title 'KILLINGALL' --msgbox 'Start killing everyone on board' 5 50
if lsof -n -ti:5000  &>/dev/null; then
    kill -9 `lsof -n -ti:5000`
else 
    echo 'kube api not running'
    dialog --title 'NOKILL' --msgbox 'kube api not running' 5 50
fi
}




# start mock/push/socket in the same time

function start_all()
{
dialog --title 'STARTALL' --msgbox 'Start mock/push/socket' 5 50
start_api
}

# spinning up all docker containers:memcached, nginx and api

function docker_start()
{
dialog --title 'DOCKER' --msgbox 'WARNING,starting all docker containers' 5 60
docker-compose -f ../docker/X64/docker-compose.yml up -d
}

# switching off all docker containers

function docker_stop()
{
dialog --title 'DOCKER' --msgbox 'WARNING, shutting down all docker containers' 5 60
docker-compose -f ../docker/X64/docker-compose.yml down
}



# exit program and clean up variables in temp dir
function exit_all(){
[ -f $OUTPUT ] && rm $OUTPUT
[ -f $OUTPUTNAMESPACE ] && rm $OUTPUTNAMESPACE
[ -f $OUTPUTDEPLOY ] && rm $OUTPUTDEPLOY
[ -f $OUTPUTSERVICE ] && rm $OUTPUTSERVICE
[ -f $OUTPUTSERVICEDELETE ] && rm $OUTPUTSERVICEDELETE
[ -f $OUTPUTSERVICEUPDATE ] && rm $OUTPUTSERVICEUPDATE
[ -f $OUTPUTDEPLOYDELETE ] && rm $OUTPUTDEPLOYDELETE
[ -f $OUTPUTDEPLOYUPDATE ] && rm $OUTPUTDEPLOYUPDATE
[ -f $OUTPUTLISTPODS ] && rm $OUTPUTLISTPODS
[ -f $OUTPUTSERVICEREAD ] && rm $OUTPUTSERVICEREAD
[ -f $SERVICEREAD ] && rm $SERVICEREAD
[ -f $PODLIST ] && rm $PODLIST
[ -f $INPUT ] && rm $INPUT
[ -f $OUTPUTINGRESS ] && rm $OUTPUTINGRESS
[ -f $OUTPUTINGRESSDELETE ] && rm $OUTPUTINGRESSDELETE
[ -f $OUTPUTSECRET ] && rm $OUTPUTSECRET
[ -f $OUTPUTSECRETDELETE ] && rm $OUTPUTSECRETDELETE
[ -f $OUTPUTVOLUMES ] && rm $OUTPUTVOLUMES
[ -f $OUTPUTVOLUMESDELETE ] && rm $OUTPUTVOLUMESDELETE
[ -f $OUTPUTSCALE ] && rm $OUTPUTSCALE
[ -f $OUTPUTSCALEDELETE ] && rm $OUTPUTSCALEDELETE
[ -f $OUTPUTBIGDEMO ] && rm $OUTPUTBIGDEMO
[ -f $OUTPUTCREATEROLE ] && rm $OUTPUTCREATEROLE
[ -f $OUTPUTDELETEROLE ] && rm $OUTPUTDELETEROLE
exit
}


function logs_aggregator()
{
#detect env
desktop_version=$DESKTOP_SESSION
case $desktop_version in
xfce)
dialog --title 'XFCE' --msgbox 'Calling xfce4-terminal to aggregate logs' 5 60
xfce4-terminal --command='multitail -ci red ../output__kube_api.log'  &
;;
gnome)
dialog --title 'GNOME' --msgbox 'ALEX? Is that you?' 5 20
xfce4-terminal --command='multitail -ci red ../output__kube_api.log'  &
;;
*)
dialog --title 'NONAME' --msgbox 'No idea what you are running' 5 20
xterm -e 'multitail -ci red  ../output_kube_api.log' &
;;
esac
}

function docker_logs()
{
desktop_version=$DESKTOP_SESSION
case $desktop_version in
xfce)
dialog --title 'XFCE' --msgbox 'Calling xfce4-terminal to aggregate docker logs' 5 60
xfce4-terminal --command='docker-compose -f ../docker/X64/docker-compose.yml logs --tail=0 --follow'  &
;;
gnome)
dialog --title 'GNOME' --msgbox 'ALEX? Is that you?' 5 20
gnome-terminal -e 'docker-compose -f ../docker/X64/docker-compose.yml logs --tail=0 --follow'  &
;;
*)
dialog --title 'NONAME' --msgbox 'No idea what you are running' 5 20
xterm -e 'docker-compose -f ../DOCKER/X64/docker-compose.yml logs --tail=0 --follow' &
;;
esac
}


# about 
function about_about_mumu(){
dialog --title 'ABOUT' --msgbox 'Dan is the best and he created this' 10 20
}

# create namespace
function create_namespace()
{
dialog --backtitle "Create Namespace" --title "Input - Form" \
--form "\nCreate namespace" 25 90 16 \
"namespace_name:" 1 1 "" 1 25 40 30  \
"namespace_owner:" 2 1 "best_team_ever" 2 25 40 30  > $OUTPUTNAMESPACE \
2>&1 >/dev/tty
if test $? -eq 0
then
namespace=`sed -n 1p $OUTPUTNAMESPACE`
owner=`sed -n 2p $OUTPUTNAMESPACE`
echo "Creating namespace: $namespace"
curl -i -H "token:$KUBE_TOKEN" -H "Content-Type: application/json" -X POST -d '{"action":"create", "options": {"owner":"'"$owner"'"}}' $KUBE_HOST/api/kube/namespace/$namespace
else
echo "cancel...going back"
fi
}

# delete namespace
function delete_namespace()
{
dialog --title "DELETE - Namespace" --inputbox "Enter namespace to be deleted" 8 60 2>$OUTPUTNAMESPACE
if test $? -eq 0
then
namespace=$(<$OUTPUTNAMESPACE)
echo "Deleting namespace: $namespace"
curl -i -H "token:$KUBE_TOKEN" -H "Content-Type: application/json" -X DELETE -d '{"action":"delete"}' $KUBE_HOST/api/kube/namespace/$namespace
else
echo "cancel...going back"
fi
}

#create deployment
function create_deployment()
{
dialog --backtitle "Create deployment" --title "Input - Form" \
--form "\nCreate deployment" 25 90 16 \
"deployment_name:" 1 1 "nginx-deploy" 1 25 40 30  \
"container_name:" 2 1 "nginx" 2 25 40 30  \
"container_image:" 3 1 "nginx:1.7.9" 3 25 40 90  \
"container_port:" 4 1 "80" 4 25 40 30  \
"metadata_labels:" 5 1 "nginx" 5 25 40 30 \
"replicas:" 6 1 "1" 6 25 40 30 \
"namespace:" 7 1 "ns-staging" 7 25 40 30  \
"mount_path:" 8 1 "/mnt/azure/" 8 25 40 30 \
"volume_claim:" 9 1 "nginx-volumes" 9 25 40 30 \
"command" 10 1 "" 10 25 40 30 \
"args" 11 1 "" 11 25 40 30 \
"env_secret:" 12 1 '{"username":{"mysecret":"username"},"password":{"mysecret":"password"}}' 12 25 40 80 \
"env:" 13 1 '{"key":"val","keyy":"vall"}' 13 25 40 30 > $OUTPUTDEPLOY \
"resources:" 14 1 '{"limits":{"cpu":"2","memory":"1024Mi"},"requests":{"cpu":"100m","memory":"64Mi"}}' 14 25 40 90 \
2>&1 >/dev/tty
if test $? -eq 0
then
# Start retrieving each line from temp file 1 by one with sed and declare variables as inputs
deployment_name=`sed -n 1p $OUTPUTDEPLOY`
container_name=`sed -n 2p $OUTPUTDEPLOY`
container_image=`sed -n 3p $OUTPUTDEPLOY`
container_port=`sed -n 4p $OUTPUTDEPLOY`
metadata_labels=`sed -n 5p $OUTPUTDEPLOY`
replicas=`sed -n 6p $OUTPUTDEPLOY`
namespace=`sed -n 7p $OUTPUTDEPLOY`
mount_path=`sed -n 8p $OUTPUTDEPLOY`
volume_claim=`sed -n 9p $OUTPUTDEPLOY`
command=`sed -n 10p $OUTPUTDEPLOY`
args=`sed -n 11p $OUTPUTDEPLOY`
env_secret=`sed -n 12p $OUTPUTDEPLOY`
env=`sed -n 13p $OUTPUTDEPLOY`
resources=`sed -n 14p $OUTPUTDEPLOY`
# execute curl
curl -i -H "token:$KUBE_TOKEN" -H "Content-Type: application/json" -X POST -d '{"action":"create", "options": {"container_name":"'"$container_name"'", "container_image":"'"$container_image"'", "container_port":"'"$container_port"'", "metadata_labels":"'"$metadata_labels"'", "replicas":"'"$replicas"'", "namespace":"'"$namespace"'", "mount_path":"'"$mount_path"'", "volume_claim":"'"$volume_claim"'", "command":"'"$command"'", "args":"'"$args"'", "env_secret":'$env_secret', "env":'$env', "resources":'$resources'}}' $KUBE_HOST/api/kube/deployments/$deployment_name
# add message box
dialog --title "Deployment created" --msgbox 'New deployment:"'"$deployment_name"'" created in namespace:"'"$namespace"'"' 6 60
else
echo "cancel...going back"
fi
}

# delete deployment
function delete_deployment()
{
dialog --backtitle "Delete deployment" --title "Input - Form" \
--form "\nDelete deployment" 25 60 16 \
"deployment_name:" 1 1 "nginx-deploy" 1 25 25 30  \
"namespace:" 2 1 "ns-staging" 2 25 25 30  > $OUTPUTDEPLOYDELETE \
2>&1 >/dev/tty

if test $? -eq 0
then
# Start retrieving each line from temp file 1 by one with sed and declare variables as inputs
deployment_name=`sed -n 1p $OUTPUTDEPLOYDELETE`
namespace=`sed -n 2p $OUTPUTDEPLOYDELETE`
#debug
#echo $deployment_name
#echo $namespace

# execute curl
curl -i -H "token:$KUBE_TOKEN" -H "Content-Type: application/json" -X DELETE -d '{"action":"delete", "options": {"namespace": "'"$namespace"'"}}' $KUBE_HOST/api/kube/deployments/$deployment_name
# add message box
dialog --title "Deployment deleted" --msgbox 'Deployment:"'"$deployment_name"'" deleted from namespace:"'"$namespace"'"' 6 60
else
echo "cancel...going back"
fi
}


#update deployment
function update_deployment()
{
dialog --backtitle "Update deployment" --title "Input - Form" \
--form "\nUpdate deployment/Outdated" 25 60 16 \
"deployment_name:" 1 1 "nginx-deploy" 1 25 25 30  \
"container_name:" 2 1 "nginx" 2 25 25 30  \
"container_image:" 3 1 "nginx:1.7.9" 3 25 25 60  \
"container_port:" 4 1 "80" 4 25 25 30  \
"metadata_labels:" 5 1 "nginx" 5 25 25 30 \
"replicas:" 6 1 "1" 6 25 25 30 \
"namespace:" 7 1 "ns-staging" 7 25 25 30  > $OUTPUTDEPLOYUPDATE \
2>&1 >/dev/tty

if test $? -eq 0
then
# Start retrieving each line from temp file 1 by one with sed and declare variables as inputs
deployment_name=`sed -n 1p $OUTPUTDEPLOYUPDATE`
container_name=`sed -n 2p $OUTPUTDEPLOYUPDATE`
container_image=`sed -n 3p $OUTPUTDEPLOYUPDATE`
container_port=`sed -n 4p $OUTPUTDEPLOYUPDATE`
metadata_labels=`sed -n 5p $OUTPUTDEPLOYUPDATE`
replicas=`sed -n 6p $OUTPUTDEPLOYUPDATE`
namespace=`sed -n 7p $OUTPUTDEPLOYUPDATE`

# execute curl
curl -i -H "token:$KUBE_TOKEN" -H "Content-Type: application/json" -X POST -d '{"action":"update", "options": {"container_name":"'"$container_name"'", "container_image":"'"$container_image"'", "container_port":"'"$container_port"'", "metadata_labels":"'"$metadata_labels"'", "replicas":"'"$replicas"'", "namespace":"'"$namespace"'"}}' $KUBE_HOST/api/kube/deployments/$deployment_name
# add message box
dialog --title "Deployment updated" --msgbox ' Deployment:"'"$deployment_name"'" updated in namespace:"'"$namespace"'"' 6 60
else
echo "cancel...going back"
fi
}


#scale deployment
function scale_deploy_create()
{
dialog --backtitle "Scale deployment" --title "Input - Form" \
--form "\nScale deployment" 25 60 16 \
"deployment_name" 1 1 "nginx-deploy" 1 25 25 30  \
"max_replicas:" 2 1 "4" 2 25 25 30  \
"cpu_utilization:" 3 1 "80" 3 25 25 30  \
"scale_name:" 4 1 "myscale" 4 25 25 30  \
"namespace:" 5 1 "ns-staging" 5 25 25 30  > $OUTPUTSCALE \
2>&1 >/dev/tty

if test $? -eq 0
then
# Start retrieving each line from temp file 1 by one with sed and declare variables as inputs
deployment_name=`sed -n 1p $OUTPUTSCALE`
max_replicas=`sed -n 2p $OUTPUTSCALE`
cpu_utilization=`sed -n 3p $OUTPUTSCALE`
scale_name=`sed -n 4p $OUTPUTSCALE`
namespace=`sed -n 5p $OUTPUTSCALE`

# execute curl
curl -i -H "token:$KUBE_TOKEN" -H "Content-Type: application/json" -X POST -d '{"action":"create","options": {"namespace":"'"$namespace"'", "deployment_name":"'"$deployment_name"'","max_replicas":"'"$max_replicas"'", "cpu_utilization":"'"$cpu_utilization"'"}}' $KUBE_HOST/api/kube/scale/$scale_name
else
echo "cancel...going back"
fi
}

#scale deployment delete
function scale_deploy_delete()
{
dialog --backtitle "Delete Scale" --title "Input - Form" \
--form "\nDelete scale" 25 60 16 \
"scale_name:" 1 1 "myscale" 1 25 25 30  \
"namespace:" 2 1 "ns-staging" 2 25 25 30  > $OUTPUTSCALEDELETE \
2>&1 >/dev/tty

if test $? -eq 0
then
# Start retrieving each line from temp file 1 by one with sed and declare variables as inputs
scale_name=`sed -n 1p $OUTPUTSCALEDELETE`
namespace=`sed -n 2p $OUTPUTSCALEDELETE`

# execute curl
curl -i -H "token:$KUBE_TOKEN" -H "Content-Type: application/json" -X DELETE -d '{"action":"delete", "options": {"namespace": "'"$namespace"'"}}' $KUBE_HOST/api/kube/scale/$scale_name
else
echo "cancel...going back"
fi
}

#create service
function create_service()
{
dialog --backtitle "Create service" --title "Input - Form" \
--form "\nCreate service" 25 60 16 \
"deployment_name_label:" 1 1 "nginx" 1 25 25 30  \
"port:" 2 1 "80" 2 25 25 30  \
"protocol:" 3 1 "TCP" 3 25 25 30  \
"target_port:" 4 1 "80" 4 25 25 30  \
"service_name:" 5 1 "nginx-service" 5 25 25 30  \
"namespace:" 6 1 "ns-staging" 6 25 25 30  > $OUTPUTSERVICE \
2>&1 >/dev/tty

if test $? -eq 0
then
# Start retrieving each line from temp file 1 by one with sed and declare variables as inputs
deployment_name_label=`sed -n 1p $OUTPUTSERVICE`
port=`sed -n 2p $OUTPUTSERVICE`
protocol=`sed -n 3p $OUTPUTSERVICE`
target_port=`sed -n 4p $OUTPUTSERVICE`
service_name=`sed -n 5p $OUTPUTSERVICE`
namespace=`sed -n 6p $OUTPUTSERVICE`
# execute curl
curl -i -H "token:$KUBE_TOKEN" -H "Content-Type: application/json" -X POST -d '{"action":"create",  "options": {"deployment_name_label":"'"$deployment_name_label"'", "port":"'"$port"'", "protocol":"'"$protocol"'", "target_port":"'"$target_port"'", "namespace":"'"$namespace"'"}}' $KUBE_HOST/api/kube/services/$service_name
# add message box
dialog --title "Service created" --msgbox 'New service:"'"$service_name"'" created in namespace:"'"$namespace"'"' 6 60
else
echo "cancel...going back"
fi
}


# delete service
function delete_service()
{
dialog --backtitle "Delete service" --title "Input - Form" \
--form "\nDelete service" 25 60 16 \
"service_name:" 1 1 "nginx-service" 1 25 25 30  \
"namespace:" 2 1 "ns-staging" 2 25 25 30  > $OUTPUTSERVICEDELETE \
2>&1 >/dev/tty

if test $? -eq 0
then
# Start retrieving each line from temp file 1 by one with sed and declare variables as inputs
service_name=`sed -n 1p $OUTPUTSERVICEDELETE`
namespace=`sed -n 2p $OUTPUTSERVICEDELETE`

# execute curl
curl -i -H "token:$KUBE_TOKEN" -H "Content-Type: application/json" -X DELETE -d '{"action":"delete", "options": {"namespace":"'"$namespace"'"}}' $KUBE_HOST/api/kube/services/$service_name
# add message box
dialog --title "Service deleted" --msgbox 'Service:"'"$service_name"'" deleted from namespace:"'"$namespace"'"' 6 60
else
echo "cancel...going back"
fi
}


#update service
function update_service()
{
dialog --backtitle "patch service" --title "Input - Form" \
--form "\nCreate service" 25 60 16 \
"deployment_name:" 1 1 "nginx-deploy" 1 25 25 30  \
"port:" 2 1 "80" 2 25 25 30  \
"protocol:" 3 1 "TCP" 3 25 25 30  \
"target_port:" 4 1 "80" 4 25 25 30  \
"service_name:" 5 1 "nginx-service" 5 25 25 30  \
"namespace:" 6 1 "ns-staging" 6 25 25 30  > $OUTPUTSERVICEUPDATE \
2>&1 >/dev/tty

if test $? -eq 0
then
# Start retrieving each line from temp file 1 by one with sed and declare variables as inputs
deployment_name=`sed -n 1p $OUTPUTSERVICEUPDATE`
port=`sed -n 2p $OUTPUTSERVICEUPDATE`
protocol=`sed -n 3p $OUTPUTSERVICEUPDATE`
target_port=`sed -n 4p $OUTPUTSERVICEUPDATE`
service_name=`sed -n 5p $OUTPUTSERVICEUPDATE`
namespace=`sed -n 6p $OUTPUTSERVICEUPDATE`
# execute curl
curl -i -H "token:$KUBE_TOKEN" -H "Content-Type: application/json" -X POST -d '{"action":"patch",  "options": {"deployment_name":"'"$deployment_name"'", "port":"'"$port"'", "protocol":"'"$protocol"'", "target_port":"'"$target_port"'", "namespace":"'"$namespace"'"}}' $KUBE_HOST/api/kube/services/$service_name
# add message box
dialog --title "Service updated" --msgbox 'service:"'"$service_name"'" updateted' 6 60
else
echo "cancel...going back"
fi
}


# read service
function read_service()
{
dialog --backtitle "Read service" --title "Input - Form" \
--form "\nRead service" 25 60 16 \
"namespace:" 1 1 "ns-staging" 1 25 25 30  \
"service:" 2 1 "nginx-service" 2 25 25 30  > $OUTPUTSERVICEREAD \
2>&1 >/dev/tty


if test $? -eq 0
then
# Start retrieving each line from temp file 1 by one with sed and declare variables as inputs
namespace=`sed -n 1p $OUTPUTSERVICEREAD`
service_name=`sed -n 2p $OUTPUTSERVICEREAD`

# execute curl
curl -i  -H "token:$KUBE_TOKEN" -H "Content-Type: application/json" -X POST -d  '{"action":"read", "options": {"namespace":"'"$namespace"'"}}' $KUBE_HOST/api/kube/services/$service_name > $SERVICEREAD
exit_status=1
dialog --backtitle "Service" --title "Read Service" \
     --ok-label Close \
     --textbox "$SERVICEREAD" 40 100

else
echo "cancel...going back"
fi
}


#bigdemo

#create deployment
function create_demo_deploy_service()
{
dialog --backtitle "Create deployment/service demo all in one" --title "Input - Form" \
--form "\nCreate deployment/service demo" 25 90 14 \
"deployment_name:" 1 1 "rstudio-deploy" 1 25 40 30  \
"container_name:" 2 1 "rstudio" 2 25 40 30  \
"container_image:" 3 1 "coderollers/rstudio-server/1.1.463:current" 3 25 40 80  \
"container_port:" 4 1 "8787" 4 25 40 30  \
"replicas:" 5 1 "1" 5 25 40 30 \
"mount_path:" 6 1 "/mnt/azure/" 6 25 40 30 \
"volume_claim:" 7 1 "nginx-volumes" 7 25 40 30 \
"command" 8 1 "" 8 25 40 30 \
"args" 9 1 "" 9 25 40 30 \
"env_secret:" 10 1 '{"username":{"mysecret":"username"},"password":{"mysecret":"password"}}' 10 25 40 80 \
"env:" 11 1 '{"key":"val","keyy":"vall"}' 11 25 40 30 \
"resources:" 12 1 '{"limits":{"cpu":"2","memory":"1024Mi"},"requests":{"cpu":"100m","memory":"64Mi"}}' 12 25 40 80 \
"port:" 13 1 "80" 13 25 25 30  \
"protocol:" 14 1 "TCP" 14 25 25 30  \
"service_name:" 15 1 "rstudio-service" 15 25 25 30  \
"namespace:" 16 1 "ns-staging" 16 25 25 30  > $OUTPUTBIGDEMO \
2>&1 >/dev/tty

if test $? -eq 0
then
# Start retrieving each line from temp file 1 by one with sed and declare variables as inputs
deployment_name=`sed -n 1p $OUTPUTBIGDEMO`
container_name=`sed -n 2p $OUTPUTBIGDEMO`
container_image=`sed -n 3p $OUTPUTBIGDEMO`
container_port=`sed -n 4p $OUTPUTBIGDEMO`
metadata_labels=`sed -n 2p $OUTPUTBIGDEMO`
replicas=`sed -n 5p $OUTPUTBIGDEMO`
mount_path=`sed -n 6p $OUTPUTBIGDEMO`
volume_claim=`sed -n 7p $OUTPUTBIGDEMO`
command=`sed -n 8p $OUTPUTBIGDEMO`
args=`sed -n 9p $OUTPUTBIGDEMO`
env_secret=`sed -n 10p $OUTPUTBIGDEMO`
env=`sed -n 11p $OUTPUTBIGDEMO`
resources=`sed -n 12p $OUTPUTBIGDEMO`
deployment_name_label=`sed -n 2p $OUTPUTBIGDEMO`
port=`sed -n 13p $OUTPUTBIGDEMO`
protocol=`sed -n 14p $OUTPUTBIGDEMO`
target_port=`sed -n 4p $OUTPUTBIGDEMO`
service_name=`sed -n 15p $OUTPUTBIGDEMO`
namespace=`sed -n 16p $OUTPUTBIGDEMO`
# execute curl
# create deployment
curl -i -H "token:$KUBE_TOKEN" -H "Content-Type: application/json" -X POST -d '{"action":"create", "options": {"container_name":"'"$container_name"'", "container_image":"'"$container_image"'", "container_port":"'"$container_port"'", "metadata_labels":"'"$metadata_labels"'", "replicas":"'"$replicas"'", "namespace":"'"$namespace"'", "mount_path":"'"$mount_path"'", "volume_claim":"'"$volume_claim"'", "command":"'"$command"'", "args":"'"$args"'", "env_secret":'$env_secret', "env":'$env', "resources":'$resources'}}' $KUBE_HOST/api/kube/deployments/$deployment_name
sleep 2
# create service
curl -i -H "token:$KUBE_TOKEN" -H "Content-Type: application/json" -X POST -d '{"action":"create",  "options": {"deployment_name_label":"'"$deployment_name_label"'", "port":"'"$port"'", "protocol":"'"$protocol"'", "target_port":"'"$target_port"'", "namespace":"'"$namespace"'"}}' $KUBE_HOST/api/kube/services/$service_name
sleep 2
# call websocket
#curl 'http://localhost/push?userid=user&service="'"$service_name"'"&namespace="'"$namespace"'"'
# add message box
dialog --title "Service demo created" --msgbox 'New deployment:"'"$deployment_name"'" and service "'"$service_name"'" created in namespace:"'"$namespace"'"' 6 60
else
echo "cancel...going back"
fi
}


# list pods
function list_pods()
{
dialog --backtitle "List pods" --title "Input - Form" \
--form "\nList pods" 25 60 16 \
"namespace:" 1 1 "ns-staging" 1 25 25 30  \
"label:" 2 1 "nginx" 2 25 25 30  > $OUTPUTLISTPODS \
2>&1 >/dev/tty

# Start retrieving each line from temp file 1 by one with sed and declare variables as inputs
if test $? -eq 0
then
namespace=`sed -n 1p $OUTPUTLISTPODS`
label=`sed -n 2p $OUTPUTLISTPODS`
# execute curl
curl -i -H "token:$KUBE_TOKEN" -H "Content-Type: application/json" -X POST -d '{"options": {"label":"'"$label"'"}}'  "$KUBE_HOST/api/kube/pods/$namespace" > $PODLIST

exit_status=1
dialog --backtitle "Pods" --title "List pods" \
     --ok-label Close \
     --textbox "$PODLIST" 40 100
else
echo "cancel...going back"
fi
}


#create ingress
function create_ingress()
{
dialog --backtitle "Create ingress" --title "Input - Form" \
--form "\nCreate ingress" 25 60 16 \
"ingress_name:" 1 1 "nginx-ingress" 1 25 25 30  \
"service_name:" 2 1 "nginx-service" 2 25 25 30  \
"port:" 3 1 "80" 3 25 25 30  \
"path:" 4 1 "/" 4 25 25 30  \
"rewrite": 5 1 "/" 5 25 25 30  \
"tls:" 6 1 "no" 6 25 25 30  \
"namespace:" 7 1 "ns-staging" 7 25 25 30  > $OUTPUTINGRESS \
2>&1 >/dev/tty


if test $? -eq 0
then
# Start retrieving each line from temp file 1 by one with sed and declare variables as inputs
ingress_name=`sed -n 1p $OUTPUTINGRESS`
service_name=`sed -n 2p $OUTPUTINGRESS`
port=`sed -n 3p $OUTPUTINGRESS`
path=`sed -n 4p $OUTPUTINGRESS`
rewrite=`sed -n 5p $OUTPUTINGRESS`
tls=`sed -n 6p $OUTPUTINGRESS`
namespace=`sed -n 7p $OUTPUTINGRESS`
# execute curl
curl -i  -H "token:$KUBE_TOKEN" -H "Content-Type: application/json" -X POST -d '{"action":"create", "options": {"service_name":"'"$service_name"'", "port":"'"$port"'", "path":"'"$path"'", "rewrite":"'"$rewrite"'", "tls":"'"$tls"'", "namespace":"'"$namespace"'"}}' $KUBE_HOST/api/kube/ingress/$ingress_name
# add message box
dialog --title "Ingress created" --msgbox 'New ingress:"'"$ingress_name"'" created in namespace:"'"$namespace"'"' 6 60
else
echo "cancel...going back"
fi
}


# delete ingress
function delete_ingress()
{
dialog --backtitle "Delete ingress" --title "Input - Form" \
--form "\nDelete ingress" 25 60 16 \
"ingress_name:" 1 1 "nginx-ingress" 1 25 25 30  \
"namespace:" 2 1 "ns-staging" 2 25 25 30  > $OUTPUTINGRESSDELETE \
2>&1 >/dev/tty


if test $? -eq 0
then
# Start retrieving each line from temp file 1 by one with sed and declare variables as inputs
ingress_name=`sed -n 1p $OUTPUTINGRESSDELETE`
namespace=`sed -n 2p $OUTPUTINGRESSDELETE`

# execute curl
curl -i  -H "token:$KUBE_TOKEN" -H "Content-Type: application/json" -X DELETE -d '{"action":"delete", "options": {"namespace":"'"$namespace"'"}}' $KUBE_HOST/api/kube/ingress/$ingress_name
# add message box
dialog --title "Ingress deleted" --msgbox 'Ingress:"'"$ingress_name"'" deleted from namespace:"'"$namespace"'"' 6 60
else
echo "cancel...going back"
fi
}

#create secret
function create_secret()
{
dialog --backtitle "Create secret" --title "Input - Form" \
--form "\nCreate secret" 25 80 16 \
"secret_name:" 1 1 "mysecret" 1 25 25 30  \
"namespace:" 2 1 "ns-staging" 2 25 25 30  \
"data:" 3 1 '{"username":"admin","password":"test"}' 3 25 50 40  > $OUTPUTSECRET \
2>&1 >/dev/tty


if test $? -eq 0
then
# Start retrieving each line from temp file 1 by one with sed and declare variables as inputs
secret_name=`sed -n 1p $OUTPUTSECRET`
namespace=`sed -n 2p $OUTPUTSECRET`
data=`sed -n 3p $OUTPUTSECRET`
# execute curl
curl -i  -H "token:$KUBE_TOKEN" -H "Content-Type: application/json" -X POST -d '{"action":"create","options":{"namespace":"'"$namespace"'","data":'$data'}}' $KUBE_HOST/api/kube/secrets/$secret_name
# add message box
dialog --title "Secret created" --msgbox 'New secret:"'"$secret_name"'" created in namespace:"'"$namespace"'"' 6 60
else
echo "cancel...going back"
fi
}

# delete secret
function delete_secret()
{
dialog --backtitle "Delete secret" --title "Input - Form" \
--form "\nDelete secret" 25 60 16 \
"secret_name:" 1 1 "mysecret" 1 25 25 30  \
"namespace:" 2 1 "ns-staging" 2 25 25 30  > $OUTPUTSECRETDELETE \
2>&1 >/dev/tty


if test $? -eq 0
then
# Start retrieving each line from temp file 1 by one with sed and declare variables as inputs
secret_name=`sed -n 1p $OUTPUTSECRETDELETE`
namespace=`sed -n 2p $OUTPUTSECRETDELETE`

# execute curl
curl -i  -H "token:$KUBE_TOKEN" -H "Content-Type: application/json" -X DELETE -d '{"action":"delete", "options": {"namespace":"'"$namespace"'"}}' $KUBE_HOST/api/kube/secrets/$secret_name
# add message box
dialog --title "Secret deleted" --msgbox 'Secret:"'"$secret_name"'" deleted from namespace:"'"$namespace"'"' 6 60
else
echo "cancel...going back"
fi
}

#create volume claim
function create_volume()
{
dialog --backtitle "Create volume claim" --title "Input - Form" \
--form "\nCreate volume claim" 25 60 16 \
"size:" 1 1 "2Gi" 1 25 25 30  \
"storage_class:" 2 1 "nginx-storage" 2 25 25 30  \
"volume_claim_name:" 3 1 "nginx-volumes" 3 25 25 30  \
"namespace:" 4 1 "ns-staging" 4 25 25 30  > $OUTPUTVOLUMES \
2>&1 >/dev/tty


if test $? -eq 0
then
# Start retrieving each line from temp file 1 by one with sed and declare variables as inputs
volume_size=`sed -n 1p $OUTPUTVOLUMES`
storage_class=`sed -n 2p $OUTPUTVOLUMES`
volume_claim_name=`sed -n 3p $OUTPUTVOLUMES`
namespace=`sed -n 4p $OUTPUTVOLUMES`
# execute curl
curl -i -H "token:$KUBE_TOKEN" -H "Content-Type: application/json" -X POST -d '{"action":"create", "options": {"size":"'"$volume_size"'", "namespace":"'"$namespace"'", "storage_class":"'"$storage_class"'"}}' $KUBE_HOST/api/kube/volumes/$volume_claim_name
# add message box
dialog --title "Volume claim created" --msgbox 'New volume clamim:"'"$volume_claim_name"'" created in namespace:"'"$namespace"'"' 6 60
else
echo "cancel...going back"
fi
}


#delete volume claim and class
function volume_delete()
{
dialog --backtitle "Delete volume claim and class" --title "Input - Form" \
--form "\nDelete volume claim/class" 25 60 16 \
"storage_class:" 1 1 "nginx-storage" 1 25 25 30  \
"volume_claim_name:" 2 1 "nginx-volumes" 2 25 25 30  \
"namespace:" 3 1 "ns-staging" 3 25 25 30  > $OUTPUTVOLUMESDELETE \
2>&1 >/dev/tty


if test $? -eq 0
then
# Start retrieving each line from temp file 1 by one with sed and declare variables as inputs
storage_class=`sed -n 1p $OUTPUTVOLUMESDELETE`
volume_claim_name=`sed -n 2p $OUTPUTVOLUMESDELETE`
namespace=`sed -n 3p $OUTPUTVOLUMESDELETE`
# execute curl
curl -i -H "token:$KUBE_TOKEN" -H "Content-Type: application/json" -X DELETE -d '{"action":"delete", "options": {"namespace":"'"$namespace"'", "volume_class":"'"$storage_class"'"}}' $KUBE_HOST/api/kube/volumes/$volume_claim_name
# add message box
dialog --title "Volume claim/class delete" --msgbox 'volume claim:"'"$volume_claim_name"'" and volume claim:"'"$storage_class"'" deleted in namespace:"'"$namespace"'"' 6 60
else
echo "cancel...going back"
fi
}

# create role binding
function create_role_bindings()
{
dialog --backtitle "Create ROLE binding" --title "Input - Form" \
--form "\nCreate ROLE binding" 25 60 16 \
"name:" 1 1 "user@mail.com" 1 25 25 30  \
"namespace:" 2 1 "ns-staging" 2 25 25 30  > $OUTPUTCREATEROLE \
2>&1 >/dev/tty


if test $? -eq 0
then
# Start retrieving each line from temp file 1 by one with sed and declare variables as inputs
# execute python script
cd ../../
python role_binding.py --username=`sed -n 1p $OUTPUTCREATEROLE` --namespace=`sed -n 2p $OUTPUTCREATEROLE` --action=create
cd utils/nasa_control_center/
# add message box
dialog --title "New role binding created" --msgbox 'Name:"'"$name"'" created in namespace:"'"$namespace"'"' 6 60
else
echo "cancel...going back"
fi
}

# delete role
function delete_role_bindings()
{
dialog --backtitle "Delete ROLE binding" --title "Input - Form" \
--form "\nDelete ROLE binding" 25 60 16 \
"name:" 1 1 "user@mail.com" 1 25 25 30  \
"namespace:" 2 1 "ns-staging" 2 25 25 30  > $OUTPUTDELETEROLE \
2>&1 >/dev/tty


if test $? -eq 0
then
# Start retrieving each line from temp file 1 by one with sed and declare variables as inputs
# execute python script
cd ../../
python role_binding.py --username=`sed -n 1p $OUTPUTDELETEROLE` --namespace=`sed -n 2p $OUTPUTDELETEROLE` --action=delete
cd utils/nasa_control_center/
# add message box
dialog --title "Role binding deleted" --msgbox 'Name:"'"$name"'" from namespace:"'"$namespace"'"' 6 60
else
echo "cancel...going back"
fi
}

# making the forever and after loop
while true
do


# creating the menus
dialog --clear --backtitle "KUBERNETES API" \
--title "[ ACTION - ACTION ]" \
--menu "You can use the UP/DOWN arrow keys to choose the TASK" 30 100 100 \
KUBE_API "Start the kube_api server" \
KILLALL "Kill all daemons" \
LOGS "Get logs for kube api" \
CREATENAMESPACE "Create namespace" \
DELETENAMESPACE "Delete namespace" \
CREATEDEPLOYMENT "Create deployment" \
DELETEDEPLOYMENT "Delete deployment" \
UPDATEDEPLOYMENT "Update deployment" \
SCALEDEPLOYMENT "Scale deployment" \
DELETESCALE "Delete scaling" \
CREATESERVICE "Create service" \
DELETESERVICE "Delete service" \
PATCHSERVICE "Patch service" \
READSERVICE "Read service" \
DEMO "Demo rstudio" \
LISTPODS "List pods" \
CREATEINGRESS "Create ingress" \
DELETEINGRESS "Delete ingress" \
CREATEVOLUME "Create volume claim" \
DELETEVOLUME "Delete volume claim\class" \
CREATESECRET "Create secret" \
DELETESECRET "Delete secret" \
CREATEROLE "Create ROLE bindings" \
DELETEROLE "Delete ROLE bindings" \
DOCKER-UP "Start docker compose" \
DOCKER-DOWN "Shutting down docker compose" \
DOCKER-LOGS "Get logs from docker containers" \
ABOUT "About" \
Exit "Exit to the shell" 2>"${INPUT}"


menuitem=$(<"${INPUT}")

# make decision, we love case
case $menuitem in
KUBE_API) start_api;;
KILLALL) stop_all;;
CREATENAMESPACE) create_namespace;;
DELETENAMESPACE) delete_namespace;;
CREATEDEPLOYMENT) create_deployment;;
DELETEDEPLOYMENT) delete_deployment;;
UPDATEDEPLOYMENT) update_deployment;;
SCALEDEPLOYMENT) scale_deploy_create;;
DELETESCALE) scale_deploy_delete;;
CREATESERVICE) create_service;;
DELETESERVICE) delete_service;;
READSERVICE) read_service;;
PATCHSERVICE) update_service;;
DEMO) create_demo_deploy_service;;
LISTPODS) list_pods;;
CREATEINGRESS) create_ingress;;
DELETEINGRESS) delete_ingress;;
CREATESECRET) create_secret;;
DELETESECRET) delete_secret;;
CREATEVOLUME) create_volume;;
DELETEVOLUME) volume_delete;;
LOGS) logs_aggregator;;
CREATEROLE)  create_role_bindings;;
DELETEROLE) delete_role_bindings;;
DOCKER-LOGS) docker_logs;;
DOCKER-UP) docker_start;;
DOCKER-DOWN) docker_stop;;
ABOUT) about_about;;
Exit) exit_all;;
esac

done
