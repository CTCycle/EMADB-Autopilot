import os
from collections import defaultdict

from EMADB.app.utils.constants import DOWNLOAD_PATH


# check if files downloaded in the past are still present, then remove them
# -----------------------------------------------------------------------------
def file_remover() -> None:
    xlsx_files = [x for x in os.listdir(DOWNLOAD_PATH) if x.endswith(".xlsx")]
    for filename in xlsx_files:
        file_path = os.path.join(DOWNLOAD_PATH, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)


# aggregate filenames with their corresponding initial letter
# -----------------------------------------------------------------------------
def drug_to_letter_aggregator(drugs: list[str]) -> dict[str, list[str]]:
    unique_drug_names = sorted(set(drugs))
    grouped: defaultdict[str, list[str]] = defaultdict(list)
    for drug in unique_drug_names:
        grouped[drug[0]].append(drug)

    return dict(grouped)
