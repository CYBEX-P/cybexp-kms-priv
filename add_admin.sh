


function print_help {
   echo -e "Add administrator account to the KMS interactively"
   echo -e "Script will ask for username and password."
   echo -e "A container id/name can be specified if multiple containers are running or the wrong container is automatically detected(use \"sudo docker ps --all\" to get a list of cotainers in the system)"
   echo
   echo -e "Usage:"
   # echo -e "\t$0 <backend|admin>"
   # echo -e "\t$0 -c <container-id|container-name> <backend|admin>"
   echo -e "\t$0"
   echo -e "\t$0 -c <container-id|container-name>"
   echo
   echo -e 'Optional arguments:'
   echo -e '  -c <container-id|container-name>\tspecify container ID of KMS, instead of autodetected one'
   echo
}




DOCKER="sudo docker"

POSITIONAL=""
while (( "$#" )); do
   case "$1" in
      -h|--help)
         print_help
         exit 0
         ;;
      -c)
         if [ -n "$2" ] && [ ${2:0:1} != "-" ]; then
            CONTAINER=$2
            shift 2
         else
            echo "Error: Argument for $1 is missing" >&2
            print_help
            exit 1
         fi
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
# if [ "$#" -ne 1 ] ; then
if [ "$#" -ne 0 ] ; then
   print_help
   exit 1
fi

if [ -z "${CONTAINER+xxx}" ]; then
   echo "Container ID not provided, please elevate"
   CONTAINER=`$DOCKER ps --all | grep -m 1 cybexp-kms-priv_priv-kms-api | awk '{print $1}'`
fi


echo Using container: $CONTAINER

# echo -n "$1 username: "
echo -n "Username: "
read USERNAME
echo -n 'Password: '
read -s PASSWORD
echo

#echo ${USERNAME}:${PASSWORD}
sudo -k # make sudo ask for password again
echo "Executing command in container ${CONTAINER}..."
$DOCKER exec -it $CONTAINER /usr/bin/python3 -u /kms-server/add_account.py $USERNAME $PASSWORD admin #$1


