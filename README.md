# A mini federation using the 'Out of band' profile

This is an extremely simple *federation* with 2 entities. 
One RP and one OP.
As configured both entities belong to the same federations.
There are 2 federations/communities.
The federation is SWAMID and the community is EduGAIN. SWAMID being a member
of EduGAIN.

## Initial setup

1. You have to create the Federation Operators keys. This you do by running
create_fo_bundle.py . This script will create keys for the SWAMID and EduGAIN
federations. Placing the private keys in private/<FO name> and the public in
public/<FO name>. It will also construct a FO bundle directory called 
*fo_bundle*  

2. Change directory to RP and do the RP setup. This is done by running 
create_sms.py . This script will do a couple of things.
- create the entity's private and public signing keys
- create a signed metadata sequence starting with EduGAIN and then passing 
down through SWAMID unto the RP. This sequence will only contain signing keys
. No entity information as such.

3. Change directory to OP and do the OP setup. The process here is the same 
as for the RP with two differences. One is that there are 2 signed metadata 
sequences one to be used for discovery response and one for the registration 
response. The one for discovery response actually contains the entity 
metadata for the OP. The one to be used for registration response only has 
the signing keys.

Noteworthy here is the the signatures have a lifetime of 86400 seconds (1 day).
So if you come back a day later or serveral days later you have to rerun 
RP/create_sms.py and OP/create_sms.py .
Also note that you **MUST** run create_sms.py inside the respective directory.

## Run the entitites

To start the RP:

    cd RP
    ./rp.py -t -k -p 8080 conf

And to start the OP:

    cd OP
    ./server.py -t -k conf
    
The OP will run on port 8100

Once the RP and the OP are running point you Web browser at 
https://localhost:8080 and enter diana@localhost:8100 as you unique identifier.

**Note** That the certificates distributed are self-signed certificates so
your web browser may complain about the connection being unsecure.
 
