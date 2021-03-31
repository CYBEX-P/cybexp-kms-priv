


function print_help {
   echo -e "Add administrator account to the KMS interactively"
   echo -e "Script will ask for username and password."
   echo -e "A container id/name can be specified if multiple containers are running or the wrong container is automatically detected(use \"sudo docker ps --all\" to get a list of cotainers in the system)"
   echo
   echo -e "Usage:"
   echo -e "\t$0" # <backend|admin>"
   echo -e "\t$0 -c <container-id|container-name>" # <backend|admin>"
   echo
   echo -e 'Optional arguments:'
   echo -e '  -c <container-id|container-name>\tuser container id instead of autogenerated one'
   echo
}




DOCKER="sudo docker"
CONTAINER=`$DOCKER ps --all | grep -m 1 cybexp-kms-priv_priv-kms-api | awk '{print $1}'`

POSITIONAL=""
while (( "$#" )); do
   case "$1" in
      -h|--help)
         print_help
         exit 0
         ;;
      -c)
         CONTAINER=$2
         shift 2
         ;;
      -*|--*=) # unsupported flags
         echo "Error: Unsupported flag $1" >&2
         exit 1
         ;;
      *) # preserve positional arguments
         POSITIONAL="$POSITIONAL $1"
         shift
         ;;
   esac
done
# set positional arguments in their proper place
eval set -- "$POSITIONAL"
if [ "$#" -ne 0 ] ; then
   print_help
   exit 1
fi

echo Using container: $CONTAINER

echo -n 'Admin username: ' 
read -s USERNAME
echo
echo -n 'Password: '
read -s PASSWORD
echo

#echo ${USERNAME}:${PASSWORD}
sudo -k # make sudo ask for password again
$DOCKER exec -it $CONTAINER /usr/bin/python3 -u /kms-server/add_account.py $USERNAME $PASSWORD admin #$1


