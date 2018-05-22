# A mini federation using the 'Out of band' profile

This is an extremely simple *federation* with 2 entities. 
One RP and one OP.
As configured both entities belong to the same federations.
There are 2 federations/communities.
The federation is SWAMID and the community is EduGAIN. SWAMID being a member
of EduGAIN.

## Background

An federation entity using the OOB profile is completely dependent on files
in a couple of directories.

Let us look at the RP's setup. The configuration lists 2 main directories

### fo_bundle 

This is where the public keys of every FO this entity belongs to 
are kept. If a new FO is added, it's key just have to be dropped into this
directory and the RP will pick it up immediately. The format of the file
names are:

    <fo_bundle_directory>/<FO identifier>
    
an example being:

    fo_bundle/https%3A%2F%2Fedugain.org  

**Note** that the FO identifier is urlencoded. This is a pattern that is
repeated in other places
The content of a file in the *fo_bundle_directory* is expected to be JWKS
as defined by RFC 7517.

### sms (Signed Metadata Statements)

This where the signed metadata statements this entity will use when constructing
a request (client registration request) or response (discovery response or
client request response). Again if a new Signed Metadata Statement is added 
it's enough to drop it into a file tree. The format of the file tree is:

    <sms_root>/<context>/<FO identifier>
    
an example being:

    sms/registration/https%3A%2F%2Fedugain.org

context is one of *registration*, *discovery* or *response*.
The content of a file in this tree is expected to be a signed JSON Web Token.
 
## Initial setup

1. You have to create the Federation Operators keys. This you do by running
create_fo_bundle.py . This script will create keys for the SWAMID and EduGAIN
federations. Placing the private keys in private/<FO name> and the public in
public/<FO name>. It will also construct a FO bundle directory called 
*fo_bundle* . You **MUST** run the script from the root of the package.

2. Change directory to RP and do the RP setup. This is done by running 
create_sms.py . 

    cd RP
    ./create_sms.py conf
    
This script will do a couple of things.
- create the entity's private and public signing keys
- create a signed metadata sequence starting with EduGAIN and then passing 
down through SWAMID unto the RP. This sequence will only contain signing keys
. No entity information as such.

3. Change directory to OP and do the OP setup. 

    cd OP
    ./create_sms.py conf 
    
The process here is the same 
as for the RP with two differences. One is that there are 2 signed metadata 
sequences one to be used for discovery response and one for the registration 
response. The one for discovery response actually contains the entity 
metadata for the OP. The one to be used for registration response only has 
the signing keys.

Noteworthy here is the the signatures have a lifetime of 86400 seconds (1 day).
So if you come back a day later or several days later you have to rerun 
RP/create_sms.py and OP/create_sms.py to make things work.
Also note that you **MUST** run create_sms.py inside the respective directory.

## Run the entities

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
 
