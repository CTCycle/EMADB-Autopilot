import os
from collections import defaultdict

from EMADB.app.constants import DOWNLOAD_PATH


# check if files downloaded in the past are still present, then remove them
#-----------------------------------------------------------------------------
def file_remover():
    xlsx_files = [x for x in os.listdir(DOWNLOAD_PATH) if x.endswith(".xlsx")]
    for filename in xlsx_files:
        file_path = os.path.join(DOWNLOAD_PATH, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)


# aggregate filenames with their corresponding initial letter
#-----------------------------------------------------------------------------
def drug_to_letter_aggregator(drugs):
    # get list of drugs and group them by initial letter
    unique_drug_names = sorted(list(set(drugs)))
    grouped_drugs = defaultdict(list)
    for drug in unique_drug_names:
        grouped_drugs[drug[0]].append(drug)
    grouped_drugs = dict(grouped_drugs)

    return grouped_drugs
