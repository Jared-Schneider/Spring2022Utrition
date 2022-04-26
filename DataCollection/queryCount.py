from Bio import Entrez
import logging

logging.basicConfig(filename='debug.txt', encoding='utf-8', level=logging.DEBUG, format='[%(asctime)s] [%(levelname)s] --- %(message)s (%(filename)s:%(lineno)s)', datefmt='%Y-%m-%d %H:%M:%S')
log = logging.getLogger('rsIDLogger')

# Entrez info
Entrez.email = 'shah.1440@osu.edu' # provide your email address
Entrez.api_key='b2e5c394041db205513f18b0d4e5cbeb5608'

# set search to dbSNP database
db = 'snp'
# Use Entrez search history to cache results                         
paramEutils = { 'usehistory':'Y' }

# Search
log.debug("Beginning search")
eSearch = Entrez.esearch(db=db, term='("snv"[SCLS] AND ("risk factor"[CLIN] OR "pathogenic"[CLIN] OR "pathogenic likely pathogenic"[CLIN] OR "likely pathogenic"[CLIN] OR "affects"[CLIN] OR "association"[CLIN] OR "confers sensitivity"[CLIN]))', **paramEutils)
log.debug("Completed search")

# get eSearch result as dict object
res = Entrez.read(eSearch)
log.debug("Records matching query: %s", str(res['Count']))

# print/return number of records
print(res['Count'])  
