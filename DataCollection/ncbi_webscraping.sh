#!/bin/sh

# Clears debug file
> debug.txt

trap "pkill -P $$" EXIT

#Redirecting output to debug file
exec 1>>debug.txt 2>>debug.txt

#Database Configuration
#TO DO: Change this for your own configurations
DATABASE=utrition_full
USERNAME=postgres
HOSTNAME=localhost
export PGPASSWORD=postgres

#Batch and index variables

# This basically represents how many entries you want to add to the JSON table at once
# In other words, information for how many rsIDs are output through one call of the efetch SCRIPT
# Eg. If number of records matching query is 10,000, maybe you want to add 500 entries into the database at a time
SEARCHBATCHSIZE=30

# Which record to start searching data from [Searching]
RETSTART=0

# Which record to start retrieving data from [Fetching]
STARTBATCH=0

# How many entries should be fetched at a time
# In other words, WITHIN the efetch script, information for how many rsIDs are output through one call of the efetch COMMAND
# Eg. If you want to add 500 entries into the database at a time and you know eFetch can fetch a most of 100 entries at a time before throwing errors, then you'd set batchsize to 100
BATCHSIZE=10
export SEARCHCOUNTER=0

#Retrieving total number of records
# RECORDCOUNT=($(python3 queryCount.py))
RECORDCOUNT=40
echo "Number of records:" $RECORDCOUNT


#Number of times bash while loop repeats
SEARCHBATCHES=$((RECORDCOUNT / SEARCHBATCHSIZE))

#Adding one if the record count and search batch size don't divide perfectly (eg. Record count = 10, search batch size = 3)
if [ $((RECORDCOUNT%SEARCHBATCHSIZE)) -ne 0 ] 
then 
    SEARCHBATCHES=$((SEARCHBATCHES + 1))
fi

#Creates JSON table [This table is not technically marked as 'temporary', but the table is deleted at the end of data collection]
psql -h $HOSTNAME -U $USERNAME $DATABASE -c "CREATE TABLE IF NOT EXISTS jsonRecords ( j jsonb );"

#eSearch
#Information in output: 
    #index 0: Web Environment
    #index 1: Query Key
OUTPUT=($(python3 esearch_webscraping.py -retstart $RETSTART | tr -d '[],'))

# Total number of batches 
while [ $SEARCHCOUNTER -ne $SEARCHBATCHES ]
do
    echo "Starting fetch"
    echo "SEARCHCOUNTER:" $SEARCHCOUNTER
    echo "STARTBATCH:" $STARTBATCH
    
    python3 efetch_webscraping.py $STARTBATCH $SEARCHBATCHSIZE $BATCHSIZE ${OUTPUT[@]} | jq '-c' >> rsid_searchBatch.json
    
    echo "Finished Fetching. Copying to JSON"
    psql -h $HOSTNAME -U $USERNAME $DATABASE -c "copy jsonRecords from '/Users/stuti/Desktop/rsid_searchBatch.json'"
    
    echo "Clearing JSON file contents"
    > rsid_searchBatch.json

    STARTBATCH=$((STARTBATCH + SEARCHBATCHSIZE))
    SEARCHCOUNTER=$((SEARCHCOUNTER + 1))
    
done
echo "Completed all fetching. Beginning DB entry"

# Parses the JSON, cleans the entries/checks for formatting of alleles and rsIDs, and inserts them into the database
psql -h $HOSTNAME -U $USERNAME $DATABASE<< EOF
    CREATE VIEW cleanedRecords AS
        SELECT cast(CONCAT('rs',j->> 'refsnp_id') as varchar(20)) AS rsID, 
                cast(alleleSets->'allele_in_cur_release'->>'deleted_sequence' as char(1)) as ref_allele, 
                cast(alleleSets->'allele_in_cur_release'->>'inserted_sequence' as char(1)) as mutated_Allele, 
                jsonb_array_elements_text(clinical->'disease_names') as disease
            FROM jsonRecords, 
                jsonb_array_elements(j-> 'present_obs_movements') alleleSets,
                jsonb_array_elements(alleleSets->'component_ids') components,
                jsonb_array_elements(j-> 'primary_snapshot_data' -> 'allele_annotations') annotations, 
                jsonb_array_elements(annotations->'clinical') clinical
            WHERE alleleSets->'allele_in_cur_release'->>'deleted_sequence' NOT LIKE alleleSets->'allele_in_cur_release'->>'inserted_sequence'
                AND (components->>'type') LIKE 'clinvar'
                AND (clinical ->> 'accession_version') LIKE (components ->> 'value')
                AND (alleleSets->'allele_in_cur_release'->>'inserted_sequence' = 'A' 
                    OR alleleSets->'allele_in_cur_release'->>'inserted_sequence' = 'G'
                    OR alleleSets->'allele_in_cur_release'->>'inserted_sequence' = 'C'
                    OR alleleSets->'allele_in_cur_release'->>'inserted_sequence' = 'T'
                    OR alleleSets->'allele_in_cur_release'->>'inserted_sequence' = '-'
                    )
                AND (CONCAT('rs',j->> 'refsnp_id') SIMILAR TO 'rs(0|1|2|3|4|5|6|7|8|9)+');

    INSERT INTO disease(name) SELECT DISTINCT disease FROM cleanedRecords WHERE cleanedRecords.disease NOT IN (SELECT name FROM disease);

    INSERT INTO rsid(rsid, allele) SELECT DISTINCT rsid, ref_allele FROM cleanedRecords WHERE cleanedRecords.rsid NOT IN (SELECT rsid FROM rsid);

    INSERT INTO mutated_rsid(rsid, allele, disease_id) SELECT recs.rsid, recs.mutated_allele, dis.id FROM cleanedRecords recs JOIN disease dis ON recs.disease = dis.name LEFT JOIN mutated_rsid m_rsid ON recs.rsid = m_rsid.rsid and recs.mutated_allele = m_rsid.allele WHERE m_rsid.rsid IS NULL GROUP BY recs.rsid,recs.mutated_allele,dis.id;
    
    DROP VIEW cleanedRecords;
    DROP TABLE jsonRecords;

EOF
echo "Completed DB Entry"