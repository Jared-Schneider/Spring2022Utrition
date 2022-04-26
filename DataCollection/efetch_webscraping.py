from Bio import Entrez
import sys
import logging

# Entrez info
Entrez.email = 'shah.1440@osu.edu'
Entrez.api_key='b2e5c394041db205513f18b0d4e5cbeb5608'
Entrez.sleep_between_tries=1

logging.basicConfig(filename='debug.txt', encoding='utf-8', level=logging.DEBUG, format='[%(asctime)s] [%(levelname)s] --- %(message)s (%(filename)s:%(lineno)s)', datefmt='%Y-%m-%d %H:%M:%S')
log = logging.getLogger('rsIDLogger')

# Set database to fetch from
db = 'snp'    

# Cleaning up arguments
args = sys.argv[1:]
for i, s in enumerate(args):
    args[i] = s.strip("'")

# eFetch variables
fileRetmax = int(args[1])
batchSize = int(args[2])
fileRetstart = int(args[0])
queryKey = args[4]
webEnv = args[3]

# while loop variables
batchRetstart = fileRetstart
batchCounter = 0

batchNum = fileRetmax/batchSize
log.debug("# of batches: %s", str(batchNum))
while batchCounter < batchNum:
    log.debug("Current batch: %s", str(batchCounter))
    log.debug("Fetching batch info")
    
    # Fetches info from NCBI/dbSNP
    efetch = Entrez.efetch(db=db, query_key=queryKey, WebEnv=webEnv, retstart=batchRetstart, retmax=batchSize, rettype='json', retmode='text')
    log.debug("Fetched batch info")
    
    # Prints info to JSON file
    print(efetch.read())
    log.debug("Printed batch info to JSON")
    
    batchRetstart += batchSize
    batchCounter+=1

